#!/usr/bin/env python3
"""
P0 E5 model-evolution / upstream-version-shift evaluation.

Design goal:
- Hold fixed artifact schemas and harness structure.
- Vary version condition via adapter configuration wrappers.
- Report conformance/replay/release/prod/safe-nonproductive deltas vs V0.
"""

from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from pathlib import Path
from statistics import mean, stdev
from typing import Any

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "impl" / "src"))
if "LABTRUST_KERNEL_DIR" not in os.environ:
    os.environ["LABTRUST_KERNEL_DIR"] = str(REPO / "kernel")

from labtrust_portfolio.adapters import CentralizedAdapter, REPCPSAdapter, run_adapter
from labtrust_portfolio.adapters.base import AdapterResult
from labtrust_portfolio.p0_e4_matrix import MatrixPaths, run_controller_matrix


class VersionedAdapterWrapper:
    """Adapter wrapper that tags version metadata and allows param overrides."""

    def __init__(
        self,
        base: Any,
        *,
        version_label: str,
        version_type: str,
        override_params: dict[str, Any] | None = None,
    ):
        self.base = base
        self.version_label = version_label
        self.version_type = version_type
        self.override_params = dict(override_params or {})

    def run(
        self,
        scenario_id: str,
        out_dir: Path,
        seed: int = 7,
        **fault_params: Any,
    ) -> AdapterResult:
        fp = dict(fault_params)
        fp.update(self.override_params)
        result = self.base.run(scenario_id, out_dir, seed=seed, **fp)
        # Preserve interface; only provenance tag on trace metadata.
        trace_path = out_dir / "trace.json"
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        meta = dict(trace.get("metadata") or {})
        meta["model_evolution"] = {
            "version_label": self.version_label,
            "version_type": self.version_type,
            "override_params": self.override_params,
        }
        trace["metadata"] = meta
        trace_path.write_text(json.dumps(trace, indent=2) + "\n", encoding="utf-8")
        return result


def _git_head() -> str | None:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(REPO),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return None


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def _safe_mean(values: list[float]) -> float:
    return mean(values) if values else 0.0


def _safe_stdev(values: list[float]) -> float:
    return stdev(values) if len(values) > 1 else 0.0


def _aggregate_version_summary(
    per_seed: list[dict[str, Any]],
    *,
    version_label: str,
    version_type: str,
    n_runs: int,
) -> dict[str, Any]:
    raw_pass = [1.0 if bool(r.get("raw_conformance", {}).get("pass")) else 0.0 for r in per_seed]
    tier = [int(r.get("raw_conformance", {}).get("tier") or 0) for r in per_seed]
    strong = [1.0 if bool(r.get("strong_replay_match")) else 0.0 for r in per_seed]
    productive = [1.0 if bool(r.get("productive_success")) else 0.0 for r in per_seed]
    safe_nonprod = [1.0 if bool(r.get("safe_nonproductive")) else 0.0 for r in per_seed]
    tasks = [float(r.get("tasks_completed") or 0.0) for r in per_seed]
    p95 = [float(r.get("task_latency_ms_p95") or 0.0) for r in per_seed]
    reasons: dict[str, int] = {}
    for r in per_seed:
        for reason in (r.get("raw_conformance", {}).get("reasons") or []):
            key = str(reason)
            reasons[key] = reasons.get(key, 0) + 1
    top_reasons = [k for k, _ in sorted(reasons.items(), key=lambda kv: kv[1], reverse=True)[:5]]
    return {
        "version_label": version_label,
        "version_type": version_type,
        "raw_conformance_rate": _safe_mean(raw_pass),
        "tier2_rate": _safe_mean([1.0 if t >= 2 else 0.0 for t in tier]),
        "tier3_rate": _safe_mean([1.0 if t >= 3 else 0.0 for t in tier]),
        "strong_replay_rate": _safe_mean(strong),
        "release_allow_rate": _safe_mean(raw_pass),
        "productive_success_rate": _safe_mean(productive),
        "safe_nonproductive_rate": _safe_mean(safe_nonprod),
        "tasks_completed_mean": _safe_mean(tasks),
        "tasks_completed_stdev": _safe_stdev(tasks),
        "task_latency_ms_p95_mean": _safe_mean(p95),
        "top_failure_reasons": top_reasons,
        "n_runs": n_runs,
    }


def _version_defs() -> list[dict[str, Any]]:
    return [
        {
            "version_label": "V0_stable_baseline",
            "version_type": "stable",
            "centralized_override_params": {},
            "rep_cps_override_params": {},
            "comparison_kind": "synthetic_version_shift",
        },
        {
            "version_label": "V1_benign_update",
            "version_type": "benign_update",
            "centralized_override_params": {"delay_p95_ms": 52.0},
            "rep_cps_override_params": {"delay_p95_ms": 52.0},
            "comparison_kind": "synthetic_version_shift",
        },
        {
            "version_label": "V2_regressive_update",
            "version_type": "regressive_update",
            "centralized_override_params": {},
            # Intentionally stricter gate to induce measurable safe-nonproductive shift
            # in scheduling-sensitive rows while preserving output interface.
            "rep_cps_override_params": {"safety_gate_max_load": 0.2},
            "comparison_kind": "synthetic_version_shift",
        },
    ]


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Run P0 E5 model-evolution evaluation")
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument(
        "--scenarios",
        type=str,
        default="toy_lab_v0,lab_profile_v0,rep_cps_scheduling_v0",
    )
    ap.add_argument(
        "--regimes",
        type=str,
        default="baseline,coordination_shock",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=REPO / "datasets" / "runs" / "p0_e5_model_evolution.json",
    )
    args = ap.parse_args()

    scenarios = [s.strip() for s in args.scenarios.split(",") if s.strip()]
    regimes = [r.strip() for r in args.regimes.split(",") if r.strip()]
    seeds = list(range(1, args.seeds + 1))

    out_json = args.out
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_stem = out_json.stem
    per_seed_path = out_json.parent / f"{out_stem}_per_seed.jsonl"
    summary_csv = out_json.parent / f"{out_stem}_summary.csv"

    git_sha = os.environ.get("GIT_SHA") or _git_head()
    versions = _version_defs()

    all_per_seed: list[dict[str, Any]] = []
    version_summaries: list[dict[str, Any]] = []

    for v in versions:
        label = str(v["version_label"])
        version_root = out_json.parent / "p0_e5_model_evolution" / label
        paths = MatrixPaths(
            repo_root=REPO,
            runs_parent=out_json.parent,
            raw_runs_root=version_root / "raw",
            norm_runs_root=version_root / "normalized",
            per_seed_jsonl=version_root / "p0_e4_per_seed.jsonl",
            raw_summary=version_root / "p0_e4_raw_summary.json",
            normalized_summary=version_root / "p0_e4_normalized_summary.json",
            normalization_diff=version_root / "p0_e4_normalization_diff.json",
            controller_matrix=version_root / "p0_e4_controller_matrix.json",
            diagnostics=version_root / "p0_e4_diagnostics.json",
            controller_pairs_jsonl=version_root / "p0_e4_controller_pairs.jsonl",
            raw_failure_reasons=version_root / "p0_e4_raw_failure_reasons.json",
        )
        controllers = [
            (
                "centralized",
                VersionedAdapterWrapper(
                    CentralizedAdapter(),
                    version_label=label,
                    version_type=str(v["version_type"]),
                    override_params=dict(v["centralized_override_params"]),
                ),
            ),
            (
                "rep_cps",
                VersionedAdapterWrapper(
                    REPCPSAdapter(),
                    version_label=label,
                    version_type=str(v["version_type"]),
                    override_params=dict(v["rep_cps_override_params"]),
                ),
            ),
        ]
        run_controller_matrix(
            repo_root=REPO,
            scenarios=scenarios,
            controllers=controllers,
            seeds=seeds,
            regimes=regimes,
            paths=paths,
            run_adapter_fn=run_adapter,
            git_sha=git_sha,
        )
        version_per_seed = _load_jsonl(paths.per_seed_jsonl)
        for row in version_per_seed:
            row["version_label"] = label
            row["version_type"] = str(v["version_type"])
            row["comparison_kind"] = str(v["comparison_kind"])
        all_per_seed.extend(version_per_seed)

        version_summaries.append(
            _aggregate_version_summary(
                version_per_seed,
                version_label=label,
                version_type=str(v["version_type"]),
                n_runs=len(version_per_seed),
            )
        )

    # Pairwise deltas vs V0
    base = next(x for x in version_summaries if x["version_label"] == "V0_stable_baseline")
    deltas: list[dict[str, Any]] = []
    for cur in version_summaries:
        if cur["version_label"] == base["version_label"]:
            continue
        deltas.append(
            {
                "version_label": cur["version_label"],
                "vs_version": base["version_label"],
                "delta_raw_conformance_rate": cur["raw_conformance_rate"] - base["raw_conformance_rate"],
                "delta_strong_replay_rate": cur["strong_replay_rate"] - base["strong_replay_rate"],
                "delta_release_allow_rate": cur["release_allow_rate"] - base["release_allow_rate"],
                "delta_productive_success_rate": cur["productive_success_rate"] - base["productive_success_rate"],
                "delta_safe_nonproductive_rate": cur["safe_nonproductive_rate"] - base["safe_nonproductive_rate"],
                "delta_tasks_completed_mean": cur["tasks_completed_mean"] - base["tasks_completed_mean"],
            }
        )

    payload = {
        "experiment": "P0_E5_model_evolution",
        "run_manifest": {
            "commit_sha": git_sha,
            "script": "run_p0_e5_model_evolution.py",
            "scenarios": scenarios,
            "regimes": regimes,
            "seeds": seeds,
            "seed_count": len(seeds),
            "version_conditions": versions,
            "comparison_mode": "synthetic_version_shift",
            "artifact_interface": "fixed_mads_cps_interface",
        },
        "per_version_summary": version_summaries,
        "pairwise_deltas_vs_v0": deltas,
        "paths": {
            "per_seed_jsonl": str(per_seed_path).replace("\\", "/"),
            "summary_csv": str(summary_csv).replace("\\", "/"),
        },
    }
    out_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    per_seed_path.write_text(
        "\n".join(json.dumps(r, sort_keys=True) for r in all_per_seed) + ("\n" if all_per_seed else ""),
        encoding="utf-8",
    )

    fields = [
        "version_label",
        "version_type",
        "raw_conformance_rate",
        "tier2_rate",
        "tier3_rate",
        "strong_replay_rate",
        "release_allow_rate",
        "productive_success_rate",
        "safe_nonproductive_rate",
        "tasks_completed_mean",
        "tasks_completed_stdev",
        "task_latency_ms_p95_mean",
        "n_runs",
    ]
    with summary_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in version_summaries:
            writer.writerow({k: row.get(k) for k in fields})

    print(
        json.dumps(
            {
                "wrote": [
                    str(out_json),
                    str(per_seed_path),
                    str(summary_csv),
                ],
                "n_per_seed_rows": len(all_per_seed),
                "n_versions": len(version_summaries),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
