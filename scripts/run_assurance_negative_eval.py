#!/usr/bin/env python3
"""
P7 negative-control and ablation evaluation.

Produces datasets/runs/assurance_eval/negative_results.json with discrimination
metrics across reviewer modes (schema_only, schema_plus_presence, full_review).

Usage:
  PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel \\
    python scripts/run_assurance_negative_eval.py [--out DIR] [--quick] [--mode MODE]

  --mode: run one reviewer mode only, or omit for all three.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "impl" / "src"))
if "LABTRUST_KERNEL_DIR" not in os.environ:
    os.environ["LABTRUST_KERNEL_DIR"] = str(REPO / "kernel")

DEFAULT_OUT = REPO / "datasets" / "runs" / "assurance_eval"
PROFILE_LAB = REPO / "profiles" / "lab" / "v0.1"
LAB_PACK = PROFILE_LAB / "assurance_pack_instantiation.json"
WH_PACK = REPO / "profiles" / "warehouse" / "v0.1" / "assurance_pack_instantiation.json"
MED_PACK = REPO / "profiles" / "medical_v0.1" / "assurance_pack_instantiation.json"

from labtrust_portfolio.assurance_negative_controls import all_case_ids, materialize_case  # noqa: E402
from labtrust_portfolio.assurance_review_pipeline import REVIEW_MODES, review_assurance_pipeline  # noqa: E402


def _localization_ok(
    expected_outcome: str,
    expected_codes: frozenset,
    exit_ok: bool,
    codes: List[str],
) -> bool:
    if expected_outcome == "accept":
        return exit_ok and not codes
    if not exit_ok:
        if not codes:
            return False
        return bool(expected_codes.intersection(codes))
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description="P7 negative controls + ablation eval")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--quick", action="store_true", help="Subset of cases for CI")
    ap.add_argument(
        "--mode",
        choices=[*REVIEW_MODES, "all"],
        default="all",
        help="Reviewer mode (default all three)",
    )
    args = ap.parse_args()
    out_dir = args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    modes = list(REVIEW_MODES) if args.mode == "all" else [args.mode]

    from labtrust_portfolio.thinslice import run_thin_slice

    rows: List[Dict[str, Any]] = []
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        lab_run = base / "base_lab"
        wh_run = base / "base_wh"
        lab_run.mkdir(parents=True)
        wh_run.mkdir(parents=True)
        run_thin_slice(lab_run, seed=7, scenario_id="lab_profile_v0", drop_completion_prob=0.0)
        run_thin_slice(wh_run, seed=7, scenario_id="warehouse_v0", drop_completion_prob=0.0)

        case_ids = all_case_ids(quick=args.quick)
        work_root = base / "cases"
        work_root.mkdir(parents=True)

        for case_id in case_ids:
            seed = 7
            run_dir, pack_path, scenario_id, exp_out, exp_codes, family = materialize_case(
                REPO,
                work_root,
                case_id,
                lab_run,
                wh_run,
                LAB_PACK,
                WH_PACK,
                MED_PACK,
                seed,
            )
            for mode in modes:
                t0 = time.perf_counter()
                outcome = review_assurance_pipeline(
                    run_dir,
                    pack_path,
                    scenario_id,
                    mode,
                    profile_dir=PROFILE_LAB,
                    repo_root=REPO,
                )
                latency_ms = round((time.perf_counter() - t0) * 1000.0, 3)
                codes = outcome.get("failure_reason_codes") or []
                exit_ok = bool(outcome.get("exit_ok"))
                observed = "accept" if exit_ok else "reject"
                loc = _localization_ok(exp_out, exp_codes, exit_ok, codes)
                rows.append(
                    {
                        "scenario_id": scenario_id,
                        "profile": "lab_v0.1",
                        "family": family,
                        "perturbation_id": case_id,
                        "review_mode": mode,
                        "seed": seed,
                        "expected_outcome": exp_out,
                        "observed_outcome": observed,
                        "review_exit_ok": exit_ok,
                        "failure_stage": outcome.get("failure_stage"),
                        "failure_reason_codes": codes,
                        "reason_matches_expected": loc,
                        "review_latency_ms": latency_ms,
                    }
                )

    def _subset(pred) -> List[Dict[str, Any]]:
        return [r for r in rows if pred(r)]

    valid_rows = _subset(lambda r: r["expected_outcome"] == "accept")
    invalid_rows = _subset(lambda r: r["expected_outcome"] == "reject")

    def _rates(mode: str) -> Dict[str, Any]:
        vr = [r for r in valid_rows if r["review_mode"] == mode]
        ir = [r for r in invalid_rows if r["review_mode"] == mode]
        va = sum(1 for r in vr if r["review_exit_ok"])
        ir_rej = sum(1 for r in ir if not r["review_exit_ok"])
        fa = sum(1 for r in ir if r["review_exit_ok"])
        fr = sum(1 for r in vr if not r["review_exit_ok"])
        loc_ok = [r for r in rows if r["review_mode"] == mode and r["expected_outcome"] == "reject"]
        loc_acc = (
            sum(1 for r in loc_ok if r["reason_matches_expected"]) / len(loc_ok)
            if loc_ok
            else None
        )
        return {
            "valid_accept_rate": round(va / len(vr), 4) if vr else None,
            "invalid_reject_rate": round(ir_rej / len(ir), 4) if ir else None,
            "false_accept_rate": round(fa / len(ir), 4) if ir else None,
            "false_reject_rate": round(fr / len(vr), 4) if vr else None,
            "localization_accuracy": round(loc_acc, 4) if loc_acc is not None else None,
            "n_valid": len(vr),
            "n_invalid": len(ir),
        }

    by_family: Dict[str, Any] = {}
    for fam in sorted({r["family"] for r in rows}):
        fr = [r for r in rows if r["family"] == fam and r["review_mode"] == "full_review"]
        if not fr:
            continue
        rej = sum(1 for r in fr if r["expected_outcome"] == "reject" and not r["review_exit_ok"])
        exp_rej = sum(1 for r in fr if r["expected_outcome"] == "reject")
        by_family[fam] = {
            "n": len(fr),
            "reject_rate_on_negatives": round(rej / exp_rej, 4) if exp_rej else None,
            "localization_accuracy": round(
                sum(1 for r in fr if r["expected_outcome"] == "reject" and r["reason_matches_expected"])
                / max(1, exp_rej),
                4,
            )
            if exp_rej
            else None,
        }

    aggregate_full = _rates("full_review")
    v_ar = aggregate_full.get("valid_accept_rate") or 0.0
    ir_rr = aggregate_full.get("invalid_reject_rate") or 0.0
    disc = round((v_ar + ir_rr) / 2.0, 4) if aggregate_full.get("n_invalid") else v_ar

    result = {
        "run_manifest": {
            "script": "run_assurance_negative_eval.py",
            "cases": case_ids,
            "review_modes": modes,
            "quick": args.quick,
            "repo_root": str(REPO),
        },
        "aggregate": {
            **aggregate_full,
            "governance_evidence_discrimination_accuracy": disc,
        },
        "by_mode": {m: _rates(m) for m in REVIEW_MODES},
        "by_family": by_family,
        "rows": rows,
    }

    out_path = out_dir / "negative_results.json"
    out_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["aggregate"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
