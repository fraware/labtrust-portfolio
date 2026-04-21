#!/usr/bin/env python3
"""
P8 Force collapses: sweep drop_prob (and optionally seeds) until fixed regime
collapses in some seeds. Writes collapse_sweep.json with per (drop_prob, seed):
tasks_completed, collapsed (bool). Use to document the point at which collapse appears.
Usage: PYTHONPATH=impl/src python scripts/meta_collapse_sweep.py [--drop-probs 0.15,0.2,0.25,0.3] [--seeds 5] [--out DIR]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "impl" / "src"))
if "LABTRUST_KERNEL_DIR" not in os.environ:
    os.environ["LABTRUST_KERNEL_DIR"] = str(REPO_ROOT / "kernel")

META_EVAL_SCENARIO_DEFAULT = "regime_stress_v0"
ALLOWED_META_SCENARIOS = frozenset(
    {
        "regime_stress_v0",
        "regime_stress_v1",
        "lab_profile_v0",
        "warehouse_v0",
        "traffic_v0",
    }
)
DEFAULT_COLLAPSE_THRESHOLD = 2


def main() -> int:
    ap = argparse.ArgumentParser(description="P8: Sweep drop_prob until fixed regime collapses")
    ap.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "datasets" / "runs" / "meta_eval",
        help="Output directory",
    )
    ap.add_argument(
        "--scenario",
        type=str,
        default=META_EVAL_SCENARIO_DEFAULT,
        help="MAESTRO scenario id (default: regime_stress_v0; also regime_stress_v1)",
    )
    ap.add_argument(
        "--drop-probs",
        type=str,
        default="0.15,0.2,0.25,0.3",
        help="Comma-separated drop_completion_prob values to sweep",
    )
    ap.add_argument(
        "--seeds",
        type=str,
        default="1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20",
        help="Comma-separated seeds; default 20 for publishable; use 30 for sensitivity; CI may use fewer",
    )
    ap.add_argument(
        "--collapse-threshold",
        type=int,
        default=DEFAULT_COLLAPSE_THRESHOLD,
        help="tasks_completed below this => collapse",
    )
    args = ap.parse_args()
    if args.scenario not in ALLOWED_META_SCENARIOS:
        print(
            f"Unsupported --scenario {args.scenario!r}; allowed: {sorted(ALLOWED_META_SCENARIOS)}",
            file=sys.stderr,
        )
        return 2

    from labtrust_portfolio.adapters.centralized import CentralizedAdapter
    from labtrust_portfolio.adapters.base import run_adapter

    drop_probs = [float(x.strip()) for x in args.drop_probs.split(",") if x.strip()]
    seeds = [int(x.strip()) for x in args.seeds.split(",") if x.strip()]
    args.out.mkdir(parents=True, exist_ok=True)

    adapter = CentralizedAdapter()
    results = []
    for drop_prob in drop_probs:
        for seed in seeds:
            run_dir = args.out / "collapse_sweep" / f"drop_{drop_prob}" / f"seed_{seed}"
            run_dir.mkdir(parents=True, exist_ok=True)
            result = run_adapter(
                adapter,
                args.scenario,
                run_dir,
                seed=seed,
                drop_completion_prob=drop_prob,
                delay_fault_prob=0.0,
            )
            tc = result.maestro_report.get("metrics", {}).get("tasks_completed", 0)
            recovery_ok = result.maestro_report.get("faults", {}).get("recovery_ok", True)
            collapsed = (tc < args.collapse_threshold) or (recovery_ok is False)
            results.append({
                "drop_prob": drop_prob,
                "seed": seed,
                "tasks_completed": tc,
                "recovery_ok": recovery_ok,
                "collapsed": collapsed,
            })

    collapse_count = sum(1 for r in results if r["collapsed"])
    summary = {
        "schema_version": "p8_collapse_sweep_v0.2",
        "collapse_sweep": True,
        "scenario_id": args.scenario,
        "collapse_threshold": args.collapse_threshold,
        "collapse_definition": f"tasks_completed < {args.collapse_threshold} or recovery_ok false",
        "drop_probs": drop_probs,
        "seeds": seeds,
        "collapse_count": collapse_count,
        "per_run": results,
        "run_manifest": {
            "seeds": seeds,
            "scenario_id": args.scenario,
            "drop_probs": drop_probs,
            "collapse_threshold": args.collapse_threshold,
            "script": "meta_collapse_sweep.py",
            "schema_version": "p8_collapse_sweep_v0.2",
        },
        "success_criteria_met": {"sweep_completed": True},
    }
    out_file = args.out / "collapse_sweep.json"
    out_file.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
