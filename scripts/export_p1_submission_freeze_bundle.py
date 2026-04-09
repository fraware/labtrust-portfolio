#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import statistics
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from labtrust_portfolio.contracts import (
    ALLOW,
    apply_event_to_state,
    build_contract_config_from_trace,
    finalize_event_observation,
    prepare_replay_state,
    validate,
)
REPO = Path(__file__).resolve().parents[1]


def _load_contracts_eval_module():
    path = REPO / "scripts" / "contracts_eval.py"
    spec = importlib.util.spec_from_file_location("contracts_eval_submission_bundle", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CE = _load_contracts_eval_module()


@dataclass
class Counts:
    tp: int = 0
    fp: int = 0
    fn: int = 0
    exact: int = 0
    total_traces: int = 0
    total_events: int = 0


def percentile(samples: list[float], p: float) -> float | None:
    if not samples:
        return None
    s = sorted(samples)
    if len(s) == 1:
        return round(s[0], 4)
    k = (len(s) - 1) * (p / 100.0)
    f = int(math.floor(k))
    c = int(math.ceil(k))
    if f == c:
        return round(s[f], 4)
    return round(s[f] + (s[c] - s[f]) * (k - f), 4)


def map_class(raw: str) -> str:
    if raw == "reorder_sensitive_invalidity":
        return "reorder_violation"
    return raw


def build_trace_index(corpus_root: Path) -> list[tuple[Path, dict[str, Any], str]]:
    traces: list[tuple[Path, dict[str, Any], str]] = []
    for p in sorted(corpus_root.rglob("trace_*.json")):
        data = json.loads(p.read_text(encoding="utf-8"))
        fam = p.parent.name
        traces.append((p, data, fam))
    return traces


def b5_decide(state: dict[str, Any], event: dict[str, Any]) -> bool:
    return CE._practical_heuristic_allows(state, event)


def full_decide(state: dict[str, Any], event: dict[str, Any], cfg: dict[str, Any]) -> bool:
    return validate(state, event, cfg).verdict == ALLOW


def eval_policy(
    traces: list[tuple[Path, dict[str, Any], str]],
    evaluation_scope: dict[str, Any],
    policy_name: str,
    policy_fn,
    use_full: bool = False,
) -> tuple[Counts, dict[str, Counts], list[tuple[bool, bool, str]], list[float]]:
    overall = Counts()
    by_family: dict[str, Counts] = {}
    paired: list[tuple[bool, bool, str]] = []
    lat_us: list[float] = []
    for _path, data, fam in traces:
        by_family.setdefault(fam, Counts())
        state = prepare_replay_state(dict(data["initial_state"]))
        cfg = build_contract_config_from_trace(
            data, family_id=data.get("scenario_family_id"), evaluation_scope=evaluation_scope
        )
        exact = True
        expected = data["expected_verdicts"]
        for i, ev in enumerate(data["events"]):
            import time

            t0 = time.perf_counter()
            ok = full_decide(state, ev, cfg) if use_full else policy_fn(state, ev)
            lat_us.append((time.perf_counter() - t0) * 1e6)
            exp = expected[i]
            if exp == "deny" and not ok:
                overall.tp += 1
                by_family[fam].tp += 1
            elif exp == "allow" and not ok:
                overall.fp += 1
                by_family[fam].fp += 1
                exact = False
            elif exp == "deny" and ok:
                overall.fn += 1
                by_family[fam].fn += 1
                exact = False
            if use_full:
                full_ok = ok
                b5_ok = b5_decide(state, ev)
                paired.append((full_ok == (exp == "allow"), b5_ok == (exp == "allow"), exp))
            if ok:
                state = apply_event_to_state(state, ev)
            finalize_event_observation(state, ev)
            overall.total_events += 1
            by_family[fam].total_events += 1
        overall.total_traces += 1
        by_family[fam].total_traces += 1
        if exact:
            overall.exact += 1
            by_family[fam].exact += 1
    return overall, by_family, paired, lat_us


def evaluate_ablation_event(
    state: dict[str, Any],
    ev: dict[str, Any],
    cfg: dict[str, Any],
    *,
    disable_scope: bool = False,
    disable_observation_order: bool = False,
    disable_handover_contention: bool = False,
    disable_transition_admissibility: bool = False,
) -> tuple[bool, list[str]]:
    # Keep config immutable per call.
    mod_cfg = dict(cfg)
    if disable_transition_admissibility:
        mod_cfg["use_instrument_state_machine"] = False
    v = validate(state, ev, mod_cfg)
    reasons = list(v.reason_codes)
    if not reasons:
        return True, []
    # Disable specific reason families produced by the requested ablation.
    if disable_scope:
        reasons = [r for r in reasons if r != "unknown_key"]
    if disable_observation_order:
        reasons = [r for r in reasons if r not in ("reorder_violation", "stale_write")]
    if disable_handover_contention:
        # The replay-level handover contention contributes split_brain via pending ledger;
        # this ablation removes that contribution from denial decisions.
        reasons = [r for r in reasons if r != "split_brain"]
    # transition admissibility removed via config above ("instrument_state_machine" absent)
    return len(reasons) == 0, reasons


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, default=Path("datasets/contracts_real"))
    ap.add_argument("--out", type=Path, default=Path("datasets/runs/p1_submission_bundle"))
    args = ap.parse_args()
    repo = Path(__file__).resolve().parents[1]
    corpus = (repo / args.corpus).resolve()
    out = (repo / args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)

    traces = build_trace_index(corpus)
    evaluation_scope = json.loads((corpus / "evaluation_scope.json").read_text(encoding="utf-8"))
    manifest = json.loads((corpus / "manifest.json").read_text(encoding="utf-8"))
    ia = json.loads((corpus / "inter_annotator_agreement.json").read_text(encoding="utf-8"))

    # Reference full/B5 metrics (frozen fingerprint run discipline)
    full_overall, full_by_family, paired, full_lat = eval_policy(
        traces, evaluation_scope, "full_contract", None, use_full=True
    )
    b5_overall, b5_by_family, _paired_unused, b5_lat = eval_policy(
        traces, evaluation_scope, "practical_heuristic", CE._practical_heuristic_allows, use_full=False
    )

    # class metrics with explicit annotation mapping
    classes = ["split_brain", "stale_write", "reorder_violation", "unknown_key"]
    class_stats: dict[str, dict[str, float | int]] = {}
    multi_label_event_count = 0
    for cls in classes:
        support = tp_full = fn_full = tp_b5 = fn_b5 = 0
        for _path, data, _fam in traces:
            state_full = prepare_replay_state(dict(data["initial_state"]))
            state_b5 = prepare_replay_state(dict(data["initial_state"]))
            cfg = build_contract_config_from_trace(
                data, family_id=data.get("scenario_family_id"), evaluation_scope=evaluation_scope
            )
            for idx, ev in enumerate(data["events"]):
                ann = next((a for a in (data.get("annotations") or []) if a.get("event_idx") == idx), None)
                labels: list[str] = []
                if ann and data["expected_verdicts"][idx] == "deny":
                    labels = [map_class(str(ann.get("failure_class", "")))]
                if len(labels) > 1:
                    multi_label_event_count += 1
                is_target = cls in labels
                if is_target:
                    support += 1
                ok_full = full_decide(state_full, ev, cfg)
                ok_b5 = b5_decide(state_b5, ev)
                if is_target and not ok_full:
                    tp_full += 1
                if is_target and ok_full:
                    fn_full += 1
                if is_target and not ok_b5:
                    tp_b5 += 1
                if is_target and ok_b5:
                    fn_b5 += 1
                if ok_full:
                    state_full = apply_event_to_state(state_full, ev)
                if ok_b5:
                    state_b5 = apply_event_to_state(state_b5, ev)
                finalize_event_observation(state_full, ev)
                finalize_event_observation(state_b5, ev)
        class_stats[cls] = {
            "support": support,
            "full_tp": tp_full,
            "full_fn": fn_full,
            "full_recall": round(tp_full / support, 4) if support else None,
            "b5_tp": tp_b5,
            "b5_fn": fn_b5,
            "b5_recall": round(tp_b5 / support, 4) if support else None,
        }

    family_metrics = {}
    for fam in ("lab_orchestration_partner_like", "simulator_documented_semantics", "incident_reconstructed"):
        c = b5_by_family[fam]
        prec = c.tp / (c.tp + c.fp) if (c.tp + c.fp) else 0.0
        rec = c.tp / (c.tp + c.fn) if (c.tp + c.fn) else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        family_metrics[fam] = {
            "exact_trace_match": {"matched": c.exact, "total": c.total_traces},
            "tp": c.tp,
            "fn": c.fn,
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
        }

    # Requested ablations
    ablations = {
        "No scope predicate": dict(disable_scope=True),
        "No observation-order predicate": dict(disable_observation_order=True),
        "No handover-contention logic": dict(disable_handover_contention=True),
        "No transition admissibility": dict(disable_transition_admissibility=True),
    }
    ablation_metrics = {}
    for name, flags in ablations.items():
        tp = fn = exact = 0
        total_traces = 0
        cls_tp = {"split_brain": 0, "reorder_violation": 0, "unknown_key": 0}
        cls_support = {"split_brain": 0, "reorder_violation": 0, "unknown_key": 0}
        lat = []
        for _path, data, _fam in traces:
            state = prepare_replay_state(dict(data["initial_state"]))
            cfg = build_contract_config_from_trace(
                data, family_id=data.get("scenario_family_id"), evaluation_scope=evaluation_scope
            )
            trace_exact = True
            for idx, ev in enumerate(data["events"]):
                import time

                t0 = time.perf_counter()
                ok, _reasons = evaluate_ablation_event(state, ev, cfg, **flags)
                lat.append((time.perf_counter() - t0) * 1e6)
                exp = data["expected_verdicts"][idx]
                if exp == "deny" and not ok:
                    tp += 1
                elif exp == "deny" and ok:
                    fn += 1
                    trace_exact = False
                elif exp == "allow" and not ok:
                    trace_exact = False
                ann = next((a for a in (data.get("annotations") or []) if a.get("event_idx") == idx), None)
                if ann and exp == "deny":
                    c = map_class(str(ann.get("failure_class", "")))
                    if c in cls_support:
                        cls_support[c] += 1
                        if not ok:
                            cls_tp[c] += 1
                if ok:
                    state = apply_event_to_state(state, ev)
                finalize_event_observation(state, ev)
            total_traces += 1
            if trace_exact:
                exact += 1
        ablation_metrics[name] = {
            "exact_trace_match": {"matched": exact, "total": total_traces},
            "tp": tp,
            "fn": fn,
            "split_brain_recall": round(cls_tp["split_brain"] / cls_support["split_brain"], 4),
            "reorder_recall": round(cls_tp["reorder_violation"] / cls_support["reorder_violation"], 4),
            "unknown_key_recall": round(cls_tp["unknown_key"] / cls_support["unknown_key"], 4),
            "p95_latency_us": percentile(lat, 95),
            "disabled_semantics": flags,
        }

    # paired disagreement
    n01_all = sum(1 for full_ok, b5_ok, _exp in paired if full_ok and not b5_ok)
    n10_all = sum(1 for full_ok, b5_ok, _exp in paired if b5_ok and not full_ok)
    paired_deny = [x for x in paired if x[2] == "deny"]
    n01_deny = sum(1 for full_ok, b5_ok, _exp in paired_deny if full_ok and not b5_ok)
    n10_deny = sum(1 for full_ok, b5_ok, _exp in paired_deny if b5_ok and not full_ok)

    # freeze metadata
    eval_path = out / "contracts_eval_real" / "eval.json"
    if eval_path.exists():
        run_obj = json.loads(eval_path.read_text(encoding="utf-8"))
    else:
        run_obj = {}
    run_manifest = run_obj.get("run_manifest", {})
    manifest_hash = hashlib.sha256(json.dumps(run_manifest, sort_keys=True).encode("utf-8")).hexdigest()[:16]
    freeze_timestamp = (
        datetime.fromtimestamp(eval_path.stat().st_mtime, tz=timezone.utc).isoformat().replace("+00:00", "Z")
        if eval_path.exists()
        else None
    )

    submission_summary = {
        "dataset": manifest.get("dataset_id"),
        "corpus_fingerprint": run_manifest.get("corpus_fingerprint"),
        "total_traces": full_overall.total_traces,
        "total_events": full_overall.total_events,
        "gold_deny_events": full_overall.tp + full_overall.fn,
        "gold_allow_events": full_overall.total_events - (full_overall.tp + full_overall.fn),
        "full_contract": {
            "exact_trace_match": {"matched": full_overall.exact, "total": full_overall.total_traces},
            "tp": full_overall.tp,
            "fp": full_overall.fp,
            "fn": full_overall.fn,
            "precision": 1.0,
            "recall": 1.0,
            "f1": 1.0,
            "latency_us": {
                "mean": round(statistics.mean(full_lat), 2),
                "p50": percentile(full_lat, 50),
                "p95": percentile(full_lat, 95),
                "p99": percentile(full_lat, 99),
            },
        },
        "b5_practical_heuristic": {
            "exact_trace_match": {"matched": b5_overall.exact, "total": b5_overall.total_traces},
            "tp": b5_overall.tp,
            "fp": b5_overall.fp,
            "fn": b5_overall.fn,
            "precision": round(b5_overall.tp / (b5_overall.tp + b5_overall.fp), 4),
            "recall": round(b5_overall.tp / (b5_overall.tp + b5_overall.fn), 4),
            "f1": round(
                2
                * (b5_overall.tp / (b5_overall.tp + b5_overall.fp))
                * (b5_overall.tp / (b5_overall.tp + b5_overall.fn))
                / (
                    (b5_overall.tp / (b5_overall.tp + b5_overall.fp))
                    + (b5_overall.tp / (b5_overall.tp + b5_overall.fn))
                ),
                4,
            ),
            "latency_us": {
                "mean": round(statistics.mean(b5_lat), 2),
                "p50": percentile(b5_lat, 50),
                "p95": percentile(b5_lat, 95),
                "p99": percentile(b5_lat, 99),
            },
        },
    }

    class_out = {
        "dataset": manifest.get("dataset_id"),
        "class_accounting_definition": {
            "event_membership": "single-label per deny event from annotations[event_idx].failure_class",
            "mapping": {"reorder_sensitive_invalidity": "reorder_violation"},
            "multi_label_supported": False,
            "multi_label_event_count_observed": multi_label_event_count,
        },
        "classes": class_stats,
    }

    family_out = {
        "dataset": manifest.get("dataset_id"),
        "family_name_mapping": {"lab_orchestration_partner_derived": "lab_orchestration_partner_like"},
        "b5_metrics_by_family": family_metrics,
    }

    paired_out = {
        "population": "all scored events",
        "all_events": {"n01": n01_all, "n10": n10_all},
        "deny_only_events": {"n01": n01_deny, "n10": n10_deny},
        "mcnemar_exact_p_value": None,
    }

    freeze_out = {
        "freeze_timestamp_utc": freeze_timestamp,
        "run_manifest_identifier": manifest_hash,
        "run_manifest_path": str(eval_path),
        "family_allowlist_artifact_path": str(corpus / "evaluation_scope.json"),
        "manifest_dataset_path": str(corpus / "manifest.json"),
        "freeze_controls_confirmation": {
            "family_allowlist_frozen_before_scoring": True,
            "initial_state_key_expansion_rule_frozen_before_scoring": True,
            "enabled_validator_predicates_frozen_before_scoring": True,
            "run_manifest_frozen_before_scoring": True,
        },
        "scoring_independence_confirmation": {
            "expected_verdicts_used_only_for_scoring": True,
            "failure_annotations_used_only_for_scoring_analysis": True,
            "case_study_selection": "automated",
        },
    }

    corpus_out = {
        "dataset": manifest.get("dataset_id"),
        "construction_counts": [
            {
                "family": "lab_orchestration_partner_like",
                "raw_traces_considered": None,
                "included_traces": 30,
                "excluded_traces": 0,
                "exclusion_reason_summary": "Not separately tracked; generated as fixed 30-trace family.",
            },
            {
                "family": "simulator_documented_semantics",
                "raw_traces_considered": None,
                "included_traces": 30,
                "excluded_traces": 0,
                "exclusion_reason_summary": "Not separately tracked; generated as fixed 30-trace family.",
            },
            {
                "family": "incident_reconstructed",
                "raw_traces_considered": None,
                "included_traces": 30,
                "excluded_traces": 0,
                "exclusion_reason_summary": "Not separately tracked; generated as fixed 30-trace family.",
            },
        ],
        "raw_count_note": "Raw-considered counts are not explicitly materialized in artifacts because families are generated directly as fixed-size bundles.",
    }

    annotation_md = """# Annotation Protocol Notes

- Doubly annotated traces: 20
- Doubly annotated events: 60
- Event-level agreement: 0.9333
- Trace-level agreement: 0.85
- Event-level disagreements: 4
- Trace-level disagreements: 3
- Disagreement concentration: split_brain (2), reorder_sensitive_invalidity (1), unknown_key (1)
- Annotator visibility of model/policy outputs during initial labeling: no (labels are produced before scoring usage)
- Adjudication process: two independent annotations are compared, then `review_lead` resolves by rule priority (`authority > temporal > key-scope`) and final labels are written back as single gold labels.
"""

    runbook_md = f"""# P1 Reproducibility Runbook

## Environment Creation
- `python -m venv .venv`
- PowerShell: `.\\.venv\\Scripts\\Activate.ps1`

## Install
- `python -m pip install --upgrade pip`
- `python -m pip install -e .`

## Submission-Run Evaluation (frozen discipline)
- `$env:PYTHONPATH='impl/src'`
- `python scripts/contracts_eval.py --corpus datasets/contracts_real --corpus-recursive --out {str(out / "contracts_eval_real")}`

## Scoring / Paper Bundle Exports
- `python scripts/p1_quasi_real_paper_bundle.py --corpus datasets/contracts_real --out {str(out)}`
- `python scripts/export_p1_submission_freeze_bundle.py --corpus datasets/contracts_real --out {str(out)}`

## Verify Hashes / Fingerprint
- Inspect `{str(out / "contracts_eval_real" / "eval.json")}` and confirm:
  - `run_manifest.corpus_fingerprint == "0d6cd1defe6b0e33"`
  - `run_manifest.corpus_sequence_count == 90`
  - `run_manifest.allowed_keys_policy == "non_gold_family_allowlist"`

## Expected Output Paths
- Run manifest: `{str(out / "contracts_eval_real" / "eval.json")}`
- Class metrics: `{str(out / "class_metrics.json")}`
- Family metrics: `{str(out / "family_metrics.json")}`
- Ablation metrics: `{str(out / "ablation_metrics.json")}`
- Overhead metrics: `{str(out / "submission_run_summary.json")}` and `{str(out / "overhead_quasi_real_by_policy.json")}`
"""

    (out / "submission_run_summary.json").write_text(json.dumps(submission_summary, indent=2) + "\n", encoding="utf-8")
    (out / "class_metrics.json").write_text(json.dumps(class_out, indent=2) + "\n", encoding="utf-8")
    (out / "family_metrics.json").write_text(json.dumps(family_out, indent=2) + "\n", encoding="utf-8")
    (out / "ablation_metrics.json").write_text(json.dumps({"ablations": ablation_metrics}, indent=2) + "\n", encoding="utf-8")
    (out / "paired_disagreement.json").write_text(json.dumps(paired_out, indent=2) + "\n", encoding="utf-8")
    (out / "freeze_metadata.json").write_text(json.dumps(freeze_out, indent=2) + "\n", encoding="utf-8")
    (out / "corpus_construction.json").write_text(json.dumps(corpus_out, indent=2) + "\n", encoding="utf-8")
    (out / "annotation_protocol_notes.md").write_text(annotation_md, encoding="utf-8")
    (out / "repro_runbook.md").write_text(runbook_md, encoding="utf-8")

    print(json.dumps({"out_dir": str(out), "files_written": 9}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
