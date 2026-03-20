#!/usr/bin/env python3
"""
P6 Experiment 11: Replanning after denial.
Run adapter with denial-injection plan; record denials. Then run with safe plan (replan);
report safe recovery, retries, task completion.
Usage: PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/p6_replanning_benchmark.py [--out-dir path]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "impl" / "src"))
if "LABTRUST_KERNEL_DIR" not in os.environ:
    os.environ["LABTRUST_KERNEL_DIR"] = str(REPO / "kernel")

DEFAULT_OUT = REPO / "datasets" / "runs" / "llm_eval"
SCENARIOS = ["toy_lab_v0"]
SEEDS = [1, 2, 3]


def main() -> int:
    ap = argparse.ArgumentParser(description="P6 replanning after denial benchmark")
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    from labtrust_portfolio.adapters.llm_planning_adapter import (
        LLMPlanningAdapter,
        _denial_injection_plan_steps,
        _default_plan_steps,
    )
    from labtrust_portfolio.adapters.base import run_adapter

    results = []
    for scenario_id in SCENARIOS:
        for seed in SEEDS:
            # First run: denial plan (step will be denied)
            run_dir_denial = args.out_dir / "replanning" / "attempt_0_denial" / scenario_id / f"seed_{seed}"
            run_dir_denial.mkdir(parents=True, exist_ok=True)
            adapter_denial = LLMPlanningAdapter(validation_mode="gated", plan_override=_denial_injection_plan_steps())
            res_denial = run_adapter(adapter_denial, scenario_id, run_dir_denial, seed=seed)
            denials_0 = res_denial.maestro_report.get("denials_count", 0)
            # Second run: safe plan (replan - no denial)
            run_dir_safe = args.out_dir / "replanning" / "attempt_1_safe" / scenario_id / f"seed_{seed}"
            run_dir_safe.mkdir(parents=True, exist_ok=True)
            adapter_safe = LLMPlanningAdapter(validation_mode="gated", plan_override=_default_plan_steps())
            res_safe = run_adapter(adapter_safe, scenario_id, run_dir_safe, seed=seed)
            tasks_safe = res_safe.maestro_report.get("metrics", {}).get("tasks_completed", 0)
            results.append({
                "scenario_id": scenario_id,
                "seed": seed,
                "denials_attempt_0": denials_0,
                "safe_recovery": denials_0 > 0 and tasks_safe >= 0,
                "tasks_completed_after_replan": tasks_safe,
            })

    safe_recovery_count = sum(1 for r in results if r.get("safe_recovery"))
    out = {
        "runs": results,
        "safe_recovery_rate": round(100.0 * safe_recovery_count / len(results), 1) if results else 0,
        "total_runs": len(results),
    }

    out_path = args.out_dir / "p6_replanning_benchmark.json"
    out_path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
