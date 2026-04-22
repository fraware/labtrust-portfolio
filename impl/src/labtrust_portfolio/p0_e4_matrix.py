"""
P0 E4 controller matrix: raw vs normalized evaluation, strong/weak replay, per-seed diagnostics.

Used by scripts/run_p0_e4_controller_matrix.py and tests. Intentionally avoids mutating
raw run directories after the adapter returns.
"""
from __future__ import annotations

import json
import math
import shutil
import statistics
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

from .conformance import SCENARIO_PONR_TASK_NAMES, check_conformance, write_conformance_artifact
from .evidence import build_evidence_bundle
from .hashing import sha256_bytes
from .maestro import maestro_report_from_trace
from .replay import replay_trace
from .release import build_release_manifest
from .schema import validate
from .thinslice import (
    KERNEL_VERSION,
    SCHEMA_EVIDENCE,
    SCHEMA_IDS,
    SCHEMA_MAESTRO,
    SCHEMA_RELEASE,
    SCHEMA_TRACE,
)

MAESTRO_V02_TOP_LEVEL_KEYS = frozenset(
    {
        "version",
        "run_id",
        "scenario_id",
        "run_outcome",
        "metrics",
        "safety",
        "coordination_efficiency",
        "faults",
        "notes",
    }
)

# t_{0.975, df} for 95% CI on mean (df = n-1) — same table as legacy E4 script.
_T_975: dict[int, float] = {
    1: 12.706,
    2: 4.303,
    3: 3.182,
    4: 2.776,
    5: 2.571,
    6: 2.447,
    7: 2.365,
    8: 2.306,
    9: 2.262,
    10: 2.228,
    11: 2.201,
    12: 2.179,
    13: 2.160,
    14: 2.145,
    15: 2.131,
    16: 2.120,
    17: 2.110,
    18: 2.101,
    19: 2.093,
    20: 2.086,
    25: 2.060,
    30: 2.042,
}


def ci95_mean(mean: float, stdev: float, n: int) -> tuple[float, float]:
    if n <= 1 or stdev <= 0:
        return (mean, mean)
    t = _T_975.get(n - 1, 2.0)
    half = t * (stdev / math.sqrt(n))
    return (mean - half, mean + half)


REGIME_FAULT_PARAMS: dict[str, dict[str, Any]] = {
    "baseline": {
        "drop_completion_prob": 0.0,
        "delay_fault_prob": 0.0,
        "delay_p95_ms": 50.0,
    },
    "moderate": {
        "drop_completion_prob": 0.06,
        "delay_fault_prob": 0.06,
        "delay_p95_ms": 52.0,
    },
    "stress": {
        "drop_completion_prob": 0.12,
        "delay_fault_prob": 0.14,
        "delay_p95_ms": 58.0,
        "reordered_event_fault_prob": 0.08,
        "partial_result_fault_prob": 0.03,
    },
}


def file_sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def event_type_histogram(trace: Mapping[str, Any]) -> dict[str, int]:
    c: Counter[str] = Counter()
    for ev in trace.get("events") or []:
        t = ev.get("type")
        if isinstance(t, str):
            c[t] += 1
    return dict(sorted(c.items()))


def final_state_hash_from_trace(trace: Mapping[str, Any]) -> str | None:
    events = trace.get("events") or []
    if not events:
        return None
    last = events[-1]
    h = last.get("state_hash_after")
    return str(h) if h is not None else None


def ponr_witness_task_names(trace: Mapping[str, Any], scenario_id: str) -> list[str]:
    required = set(SCENARIO_PONR_TASK_NAMES.get(scenario_id, []))
    if not required:
        return []
    found: set[str] = set()
    for ev in trace.get("events") or []:
        if ev.get("type") != "task_end":
            continue
        pl = ev.get("payload") or {}
        name = pl.get("name")
        if isinstance(name, str) and name in required:
            found.add(name)
    return sorted(found)


def weak_replay_match(recomputed: Mapping[str, Any], stored: Mapping[str, Any]) -> bool:
    sm = stored.get("metrics") or {}
    rm = recomputed.get("metrics") or {}
    return (
        rm.get("tasks_completed") == sm.get("tasks_completed")
        and rm.get("coordination_messages") == sm.get("coordination_messages")
    )


def _strong_maestro_slice(r: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "run_outcome": r.get("run_outcome"),
        "metrics": r.get("metrics"),
        "safety": r.get("safety"),
        "coordination_efficiency": r.get("coordination_efficiency"),
        "faults": r.get("faults"),
    }


def strong_replay_equivalent(
    recomputed: Mapping[str, Any],
    stored: Mapping[str, Any],
    trace: Mapping[str, Any],
) -> bool:
    if _strong_maestro_slice(recomputed) != _strong_maestro_slice(stored):
        return False
    ponr_expected = set(SCENARIO_PONR_TASK_NAMES.get(str(trace.get("scenario_id") or ""), []))
    if ponr_expected:
        got = set(ponr_witness_task_names(trace, str(trace.get("scenario_id") or "")))
        if got != ponr_expected:
            return False
    return True


def canonical_maestro_replay_hash(report: Mapping[str, Any]) -> str:
    payload = json.dumps(
        _strong_maestro_slice(report),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return sha256_bytes(payload.encode("utf-8"))


def strip_maestro_to_v02(
    maestro: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Return schema-shaped MAESTRO and a list of removal records (provenance)."""
    removed: list[dict[str, Any]] = []
    out: dict[str, Any] = {}
    for k, v in maestro.items():
        if k in MAESTRO_V02_TOP_LEVEL_KEYS:
            out[k] = v
        else:
            removed.append(
                {
                    "key": k,
                    "reason_code": "adapter_only_top_level_field",
                    "detail": "Removed non–MAESTRO_REPORT.v0.2 top-level key before normalized-interface evaluation.",
                }
            )
    return out, removed


def refresh_evidence_and_release(run_dir: Path) -> dict[str, Any]:
    """
    Rebuild evidence_bundle.json and release_manifest.json from trace.json + maestro_report.json
    on disk, then rewrite conformance.json. Does not modify trace or MAESTRO on disk.
    """
    run_dir = run_dir.resolve()
    trace_path = run_dir / "trace.json"
    maestro_path = run_dir / "maestro_report.json"
    evidence_path = run_dir / "evidence_bundle.json"
    release_path = run_dir / "release_manifest.json"

    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    maestro = json.loads(maestro_path.read_text(encoding="utf-8"))

    replay_ok, replay_diag = replay_trace(trace)

    schema_ok = True
    try:
        validate(trace, SCHEMA_TRACE)
        validate(maestro, SCHEMA_MAESTRO)
    except Exception:
        schema_ok = False

    h_trace = sha256_bytes(trace_path.read_bytes())
    h_maestro = sha256_bytes(maestro_path.read_bytes())

    evidence = build_evidence_bundle(
        run_id=str(trace["run_id"]),
        kernel_version=KERNEL_VERSION,
        artifacts=[trace_path, maestro_path],
        schema_ids=[SCHEMA_IDS[SCHEMA_TRACE], SCHEMA_IDS[SCHEMA_MAESTRO]],
        schema_validation_ok=schema_ok,
        replay_ok=replay_ok,
        replay_diag=replay_diag,
        verification_mode="evaluator",
        artifact_hashes=[h_trace, h_maestro],
    )
    try:
        validate(evidence, SCHEMA_EVIDENCE)
    except Exception:
        evidence.setdefault("verification", {})
        evidence["verification"]["schema_validation_ok"] = False

    evidence_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    h_evidence = sha256_bytes(evidence_path.read_bytes())

    release = build_release_manifest(
        release_id=f"release_{trace['run_id']}",
        kernel_version=KERNEL_VERSION,
        artifacts=[trace_path, maestro_path, evidence_path],
        artifact_hashes=[h_trace, h_maestro, h_evidence],
    )
    try:
        validate(release, SCHEMA_RELEASE)
    except Exception:
        pass
    release_path.write_text(json.dumps(release, indent=2) + "\n", encoding="utf-8")
    write_conformance_artifact(run_dir)
    return {
        "replay_ok": bool(replay_ok),
        "schema_validation_ok": bool(evidence.get("verification", {}).get("schema_validation_ok")),
        "replay_diag": replay_diag,
    }


def copy_run_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


@dataclass
class MatrixPaths:
    repo_root: Path
    runs_parent: Path  # e.g. datasets/runs
    raw_runs_root: Path
    norm_runs_root: Path
    per_seed_jsonl: Path
    raw_summary: Path
    normalized_summary: Path
    normalization_diff: Path
    controller_matrix: Path
    diagnostics: Path


def default_matrix_paths(repo_root: Path, runs_dir: Path | None = None) -> MatrixPaths:
    base = runs_dir or (repo_root / "datasets" / "runs")
    root = base / "p0_e4_matrix"
    return MatrixPaths(
        repo_root=repo_root,
        runs_parent=base,
        raw_runs_root=root / "raw",
        norm_runs_root=root / "normalized",
        per_seed_jsonl=base / "p0_e4_per_seed.jsonl",
        raw_summary=base / "p0_e4_raw_summary.json",
        normalized_summary=base / "p0_e4_normalized_summary.json",
        normalization_diff=base / "p0_e4_normalization_diff.json",
        controller_matrix=base / "p0_e4_controller_matrix.json",
        diagnostics=base / "p0_e4_diagnostics.json",
    )


def _rel(p: Path, repo: Path) -> str:
    try:
        return p.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        return str(p).replace("\\", "/")


def run_controller_matrix(
    *,
    repo_root: Path,
    scenarios: list[str],
    controllers: list[tuple[str, Any]],
    seeds: list[int],
    regimes: list[str],
    paths: MatrixPaths,
    run_adapter_fn: Callable[..., Any],
    git_sha: str | None = None,
) -> dict[str, Any]:
    """
    Execute the full matrix. Writes per-seed JSONL (overwrite), summaries, matrix bundle,
    and controller-pair diagnostics.
    """
    paths.raw_runs_root.mkdir(parents=True, exist_ok=True)
    paths.norm_runs_root.mkdir(parents=True, exist_ok=True)
    paths.per_seed_jsonl.parent.mkdir(parents=True, exist_ok=True)

    per_seed_lines: list[dict[str, Any]] = []
    norm_diff_records: list[dict[str, Any]] = []

    for regime in regimes:
        fault_params = dict(REGIME_FAULT_PARAMS.get(regime, REGIME_FAULT_PARAMS["baseline"]))
        for scenario_id in scenarios:
            for controller_name, adapter in controllers:
                for seed in seeds:
                    raw_dir = (
                        paths.raw_runs_root
                        / regime
                        / scenario_id
                        / controller_name
                        / f"seed_{seed}"
                    )
                    if raw_dir.exists():
                        shutil.rmtree(raw_dir)
                    raw_dir.mkdir(parents=True, exist_ok=True)

                    run_adapter_fn(
                        adapter, scenario_id, raw_dir, seed=seed, **fault_params
                    )

                    trace_path = raw_dir / "trace.json"
                    maestro_path = raw_dir / "maestro_report.json"
                    evidence_path = raw_dir / "evidence_bundle.json"
                    release_path = raw_dir / "release_manifest.json"

                    trace = json.loads(trace_path.read_text(encoding="utf-8"))
                    stored = json.loads(maestro_path.read_text(encoding="utf-8"))
                    recomputed = maestro_report_from_trace(
                        str(trace["run_id"]),
                        str(trace.get("scenario_id") or scenario_id),
                        trace,
                    )

                    raw_conf = check_conformance(raw_dir)
                    # run_thin_slice may have written conformance.json before the adapter
                    # mutated MAESTRO; persist the checker outcome for the actual raw tree.
                    write_conformance_artifact(raw_dir)
                    weak = weak_replay_match(recomputed, stored)
                    strong = strong_replay_equivalent(recomputed, stored, trace)

                    h_trace = file_sha256(trace_path)
                    h_maestro = file_sha256(maestro_path)
                    h_evidence = file_sha256(evidence_path) if evidence_path.exists() else None
                    h_release = file_sha256(release_path) if release_path.exists() else None

                    sm = stored.get("metrics") or {}
                    record: dict[str, Any] = {
                        "regime": regime,
                        "scenario": scenario_id,
                        "controller": controller_name,
                        "seed": seed,
                        "fault_params": fault_params,
                        "raw_run_dir": _rel(raw_dir, repo_root),
                        "raw_trace_sha256": h_trace,
                        "raw_maestro_sha256": h_maestro,
                        "raw_evidence_bundle_sha256": h_evidence,
                        "raw_release_manifest_sha256": h_release,
                        "tasks_completed": sm.get("tasks_completed"),
                        "coordination_messages": sm.get("coordination_messages"),
                        "task_latency_ms_p95": sm.get("task_latency_ms_p95"),
                        "trace_event_count": len(trace.get("events") or []),
                        "event_type_histogram": event_type_histogram(trace),
                        "ponr_witness_task_names": ponr_witness_task_names(trace, scenario_id),
                        "final_state_hash_after": final_state_hash_from_trace(trace),
                        "raw_conformance": raw_conf.to_dict(),
                        "weak_replay_match": weak,
                        "strong_replay_match": strong,
                        "canonical_maestro_replay_sha256": canonical_maestro_replay_hash(stored),
                    }

                    norm_dir = (
                        paths.norm_runs_root
                        / regime
                        / scenario_id
                        / controller_name
                        / f"seed_{seed}"
                    )
                    copy_run_tree(raw_dir, norm_dir)
                    maestro_norm_path = norm_dir / "maestro_report.json"
                    maestro_before = json.loads(maestro_norm_path.read_text(encoding="utf-8"))
                    stripped, removals = strip_maestro_to_v02(maestro_before)
                    maestro_norm_path.write_text(
                        json.dumps(stripped, indent=2) + "\n", encoding="utf-8"
                    )
                    refresh_evidence_and_release(norm_dir)
                    norm_conf = check_conformance(norm_dir)

                    record["normalized_run_dir"] = _rel(norm_dir, repo_root)
                    record["normalized_maestro_sha256"] = file_sha256(maestro_norm_path)
                    record["normalized_evidence_bundle_sha256"] = file_sha256(
                        norm_dir / "evidence_bundle.json"
                    )
                    record["normalized_conformance"] = norm_conf.to_dict()

                    diff_entry = {
                        "regime": regime,
                        "scenario": scenario_id,
                        "controller": controller_name,
                        "seed": seed,
                        "keys_removed": removals,
                        "keys_added": [],
                        "keys_modified": [],
                        "normalized_artifact": _rel(maestro_norm_path, repo_root),
                    }
                    norm_diff_records.append(diff_entry)
                    per_seed_lines.append(record)

    paths.per_seed_jsonl.write_text(
        "\n".join(json.dumps(r, sort_keys=True) for r in per_seed_lines) + ("\n" if per_seed_lines else ""),
        encoding="utf-8",
    )

    def build_summary_rows(
        rows: list[dict[str, Any]],
        *,
        conformance_field: str,
        conformance_rate_key: str,
    ) -> list[dict[str, Any]]:
        groups: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
        for r in rows:
            g = (r["regime"], r["scenario"], r["controller"])
            groups.setdefault(g, []).append(r)
        out_rows: list[dict[str, Any]] = []
        for (regime, scenario, controller), rs in sorted(groups.items()):
            n = len(rs)
            conf_pass = sum(1 for x in rs if (x.get(conformance_field) or {}).get("pass"))
            weak_m = sum(1 for x in rs if x["weak_replay_match"])
            strong_m = sum(1 for x in rs if x["strong_replay_match"])
            p95s = [float(x.get("task_latency_ms_p95") or 0.0) for x in rs]
            mean_lat = statistics.mean(p95s) if p95s else 0.0
            stdev_lat = statistics.stdev(p95s) if len(p95s) > 1 else 0.0
            ci = ci95_mean(mean_lat, stdev_lat, n)
            out_rows.append(
                {
                    "regime": regime,
                    "scenario": scenario,
                    "controller": controller,
                    "n_seeds": n,
                    conformance_rate_key: conf_pass / n if n else 0.0,
                    "weak_replay_match_rate": weak_m / n if n else 0.0,
                    "strong_replay_match_rate": strong_m / n if n else 0.0,
                    "p95_latency_ms_mean": mean_lat,
                    "p95_latency_ms_ci_95": list(ci),
                }
            )
        return out_rows

    raw_summary_rows = build_summary_rows(
        per_seed_lines,
        conformance_field="raw_conformance",
        conformance_rate_key="raw_conformance_rate",
    )
    normalized_summary_rows = build_summary_rows(
        per_seed_lines,
        conformance_field="normalized_conformance",
        conformance_rate_key="normalized_conformance_rate",
    )

    paths.raw_summary.write_text(
        json.dumps(
            {
                "experiment": "P0_E4_raw_interface",
                "rows": raw_summary_rows,
                "seeds": seeds,
                "regimes": regimes,
                "scenarios": scenarios,
                "controllers": [c[0] for c in controllers],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    paths.normalized_summary.write_text(
        json.dumps(
            {
                "experiment": "P0_E4_normalized_interface",
                "rows": normalized_summary_rows,
                "seeds": seeds,
                "regimes": regimes,
                "scenarios": scenarios,
                "controllers": [c[0] for c in controllers],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    removal_counts: dict[str, int] = {}
    for d in norm_diff_records:
        for item in d.get("keys_removed", []):
            rc = str(item.get("reason_code", "unknown"))
            removal_counts[rc] = removal_counts.get(rc, 0) + 1

    paths.normalization_diff.write_text(
        json.dumps(
            {
                "records": norm_diff_records,
                "aggregate": {
                    "n_runs": len(norm_diff_records),
                    "removal_reason_counts": removal_counts,
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    diagnostics = build_controller_pair_diagnostics(
        per_seed_lines,
        controllers=[c[0] for c in controllers],
    )

    matrix_bundle = {
        "version": 1,
        "experiment": "P0_E4_controller_matrix",
        "git_sha": git_sha,
        "seeds": seeds,
        "regimes": regimes,
        "scenarios": scenarios,
        "controllers": [c[0] for c in controllers],
        "paths": {
            "per_seed_jsonl": _rel(paths.per_seed_jsonl, repo_root),
            "raw_summary": _rel(paths.raw_summary, repo_root),
            "normalized_summary": _rel(paths.normalized_summary, repo_root),
            "normalization_diff": _rel(paths.normalization_diff, repo_root),
            "raw_runs_root": _rel(paths.raw_runs_root, repo_root),
            "normalized_runs_root": _rel(paths.norm_runs_root, repo_root),
        },
        "raw_summary_rows": raw_summary_rows,
        "normalized_summary_rows": normalized_summary_rows,
        "diagnostics": diagnostics,
    }
    _warn = controller_rows_all_identical_warning(raw_summary_rows)
    if _warn:
        matrix_bundle["warning_artifacts"] = [_warn]
    paths.diagnostics.write_text(json.dumps(diagnostics, indent=2) + "\n", encoding="utf-8")
    paths.controller_matrix.write_text(json.dumps(matrix_bundle, indent=2) + "\n", encoding="utf-8")
    return matrix_bundle


def build_controller_pair_diagnostics(
    per_seed: list[dict[str, Any]],
    *,
    controllers: list[str],
) -> dict[str, Any]:
    """Pairwise diagnostics for the first two controllers (expected: centralized vs rep_cps)."""
    if len(controllers) < 2:
        return {"pairs": [], "note": "Need at least two controllers for pairwise diagnostics."}
    a, b = controllers[0], controllers[1]
    pairs_out: list[dict[str, Any]] = []
    by_reg_sc: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for r in per_seed:
        by_reg_sc.setdefault((r["regime"], r["scenario"]), []).append(r)

    for (regime, scenario), rows in sorted(by_reg_sc.items()):
        by_seed: dict[int, dict[str, dict[str, Any]]] = {}
        for r in rows:
            by_seed.setdefault(int(r["seed"]), {})[str(r["controller"])] = r
        n = 0
        trace_same = 0
        maestro_same = 0
        evidence_same = 0
        final_same = 0
        latency_diffs: list[float] = []
        divergent_seeds: list[int] = []
        for seed, mp in sorted(by_seed.items()):
            ra, rb = mp.get(a), mp.get(b)
            if not ra or not rb:
                continue
            n += 1
            if ra["raw_trace_sha256"] == rb["raw_trace_sha256"]:
                trace_same += 1
            if ra["raw_maestro_sha256"] == rb["raw_maestro_sha256"]:
                maestro_same += 1
            ev_a = ra.get("raw_evidence_bundle_sha256")
            ev_b = rb.get("raw_evidence_bundle_sha256")
            if ev_a and ev_b and ev_a == ev_b:
                evidence_same += 1
            fa = ra.get("final_state_hash_after")
            fb = rb.get("final_state_hash_after")
            if fa and fb and fa == fb:
                final_same += 1
            la = float(ra.get("task_latency_ms_p95") or 0.0)
            lb = float(rb.get("task_latency_ms_p95") or 0.0)
            latency_diffs.append(abs(la - lb))
            if (
                ra["raw_trace_sha256"] != rb["raw_trace_sha256"]
                or ra["raw_maestro_sha256"] != rb["raw_maestro_sha256"]
            ):
                divergent_seeds.append(seed)
        pairs_out.append(
            {
                "regime": regime,
                "scenario": scenario,
                "controller_pair": [a, b],
                "n_paired_seeds": n,
                "trace_hash_equality_rate": trace_same / n if n else 0.0,
                "maestro_hash_equality_rate": maestro_same / n if n else 0.0,
                "evidence_hash_equality_rate": evidence_same / n if n else 0.0,
                "final_state_hash_equality_rate": final_same / n if n else 0.0,
                "mean_abs_p95_latency_diff_ms": statistics.mean(latency_diffs) if latency_diffs else 0.0,
                "seeds_with_trace_or_maestro_divergence": divergent_seeds,
                "n_seeds_with_divergence": len(set(divergent_seeds)),
            }
        )
    return {"controller_a": a, "controller_b": b, "pairs": pairs_out}


def raw_summary_has_non_baseline_regimes(raw_summary_path: Path) -> bool:
    """True if p0_e4_raw_summary.json exists and lists any regime other than baseline."""
    if not raw_summary_path.exists():
        return False
    try:
        data = json.loads(raw_summary_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    for r in data.get("rows", []):
        if r.get("regime") and r["regime"] != "baseline":
            return True
    return False


def legacy_summary_from_raw_summary_if_complete(
    raw_summary_path: Path,
    *,
    scenarios: list[str],
    seeds: list[int],
    controllers: list[str],
    script_name: str,
    git_sha: str | None,
) -> dict[str, Any] | None:
    """
    If datasets/runs/p0_e4_raw_summary.json already has baseline rows for every
    (scenario, controller) with n_seeds == len(seeds), build legacy p0_e4_summary.json
    without re-running adapters (avoids clobbering a multi-regime matrix).
    """
    if not raw_summary_path.exists():
        return None
    try:
        data = json.loads(raw_summary_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    rows = [r for r in data.get("rows", []) if r.get("regime") == "baseline"]
    n_exp = len(seeds)
    for sid in scenarios:
        for ctrl in controllers:
            hit = next(
                (r for r in rows if r.get("scenario") == sid and r.get("controller") == ctrl),
                None,
            )
            if not hit or int(hit.get("n_seeds", 0)) != n_exp:
                return None
    return legacy_e4_summary_from_matrix(
        rows,
        scenarios=scenarios,
        seeds=seeds,
        controllers=controllers,
        script_name=script_name,
        git_sha=git_sha,
    )


def legacy_e4_summary_from_matrix(
    raw_summary_rows: list[dict[str, Any]],
    *,
    scenarios: list[str],
    seeds: list[int],
    controllers: list[str],
    script_name: str,
    git_sha: str | None,
) -> dict[str, Any]:
    """Shape compatible with historical p0_e4_summary.json (baseline regime only)."""
    rows = [r for r in raw_summary_rows if r.get("regime") == "baseline"]
    per_adapter: list[dict[str, Any]] = []
    for scenario_id in scenarios:
        for ctrl in controllers:
            hit = next(
                (r for r in rows if r["scenario"] == scenario_id and r["controller"] == ctrl),
                None,
            )
            if not hit:
                continue
            per_adapter.append(
                {
                    "scenario": scenario_id,
                    "controller": ctrl,
                    "seeds": list(seeds),
                    "replay_match_rate": hit["strong_replay_match_rate"],
                    "weak_replay_match_rate": hit["weak_replay_match_rate"],
                    "conformance_rate": hit["raw_conformance_rate"],
                    "p95_latency_ms_mean": hit["p95_latency_ms_mean"],
                    "p95_latency_ms_ci_95": hit["p95_latency_ms_ci_95"],
                }
            )
    return {
        "experiment": "E4_algorithm_independence",
        "scenarios": scenarios,
        "per_adapter": per_adapter,
        "run_manifest": {
            "seeds": seeds,
            "scenario_ids": scenarios,
            "controllers": controllers,
            "fault_settings": REGIME_FAULT_PARAMS["baseline"],
            "regime": "baseline",
            "script": script_name,
            "version": git_sha,
            "replay_definition": "Table 3 primary row uses strong_replay_match_rate; weak_replay_match_rate is diagnostic only.",
        },
    }


def recompute_raw_summary_from_jsonl(
    jsonl_path: Path,
) -> list[dict[str, Any]]:
    """Re-read per-seed JSONL and rebuild raw_summary_rows (for integrity tests)."""
    rows: list[dict[str, Any]] = []
    if not jsonl_path.exists():
        return rows
    for line in jsonl_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for r in rows:
        groups.setdefault((r["regime"], r["scenario"], r["controller"]), []).append(r)
    out: list[dict[str, Any]] = []
    for (regime, scenario, controller), rs in sorted(groups.items()):
        n = len(rs)
        raw_pass = sum(1 for x in rs if x["raw_conformance"].get("pass"))
        weak_m = sum(1 for x in rs if x["weak_replay_match"])
        strong_m = sum(1 for x in rs if x["strong_replay_match"])
        p95s = [float(x.get("task_latency_ms_p95") or 0.0) for x in rs]
        mean_lat = statistics.mean(p95s) if p95s else 0.0
        stdev_lat = statistics.stdev(p95s) if len(p95s) > 1 else 0.0
        ci = ci95_mean(mean_lat, stdev_lat, n)
        out.append(
            {
                "regime": regime,
                "scenario": scenario,
                "controller": controller,
                "n_seeds": n,
                "raw_conformance_rate": raw_pass / n if n else 0.0,
                "weak_replay_match_rate": weak_m / n if n else 0.0,
                "strong_replay_match_rate": strong_m / n if n else 0.0,
                "p95_latency_ms_mean": mean_lat,
                "p95_latency_ms_ci_95": list(ci),
            }
        )
    return out


def controller_rows_all_identical_warning(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    """If every aggregate row shares the same numeric fingerprint, emit a warning dict."""
    if len(rows) < 2:
        return None

    def fingerprint(r: dict[str, Any]) -> tuple[Any, ...]:
        return (
            round(float(r.get("raw_conformance_rate", 0.0)), 6),
            round(float(r.get("strong_replay_match_rate", 0.0)), 6),
            round(float(r.get("p95_latency_ms_mean", 0.0)), 6),
            tuple(round(x, 4) for x in (r.get("p95_latency_ms_ci_95") or [0, 0])[:2]),
        )

    fps = {fingerprint(r) for r in rows}
    if len(fps) == 1:
        return {
            "warning": "all_summary_rows_identical_numeric_fingerprint",
            "detail": "Inspect per-seed trace_sha256 / maestro_sha256 in p0_e4_per_seed.jsonl to verify genuine identity vs metric collapse.",
            "n_rows": len(rows),
        }
    return None
