#!/usr/bin/env python3
"""
P6 Experiment 7: Capture-off ablation.
Compare gated+capture vs gated without capture; report latency delta, throughput delta, denial coverage unchanged.
Usage: PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/p6_capture_ablation.py [--out-dir path]
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "impl" / "src"))
if "LABTRUST_KERNEL_DIR" not in os.environ:
    os.environ["LABTRUST_KERNEL_DIR"] = str(REPO / "kernel")

DEFAULT_OUT = REPO / "datasets" / "runs" / "llm_eval"
SCENARIOS = ["toy_lab_v0"]
SEEDS = [1, 2, 3, 4, 5]


def main() -> int:
    ap = argparse.ArgumentParser(description="P6 capture-off ablation")
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    from labtrust_portfolio.adapters.llm_planning_adapter import (
        LLMPlanningAdapter,
        _denial_injection_plan_steps,
    )
    from labtrust_portfolio.adapters.base import run_adapter

    plan = _denial_injection_plan_steps()
    results_capture_on = []
    results_capture_off = []
    for scenario_id in SCENARIOS:
        for seed in SEEDS:
            for capture_off, results in [(False, results_capture_on), (True, results_capture_off)]:
                run_dir = args.out_dir / "capture_ablation" / ("no_capture" if capture_off else "capture") / scenario_id / f"seed_{seed}"
                run_dir.mkdir(parents=True, exist_ok=True)
                adapter = LLMPlanningAdapter(
                    validation_mode="gated",
                    plan_override=plan,
                    capture_off=capture_off,
                )
                t0 = time.perf_counter()
                result = run_adapter(adapter, scenario_id, run_dir, seed=seed)
                elapsed = time.perf_counter() - t0
                results.append({
                    "scenario_id": scenario_id,
                    "seed": seed,
                    "wall_sec": round(elapsed, 6),
                    "denials_count": result.maestro_report.get("denials_count", 0),
                })

    wall_on = [r["wall_sec"] for r in results_capture_on]
    wall_off = [r["wall_sec"] for r in results_capture_off]
    denials_on = [r["denials_count"] for r in results_capture_on]
    denials_off = [r["denials_count"] for r in results_capture_off]
    out = {
        "capture_on": {
            "mean_wall_sec": round(statistics.mean(wall_on), 6) if wall_on else 0,
            "stdev_wall_sec": round(statistics.stdev(wall_on), 6) if len(wall_on) >= 2 else 0,
            "denials_total": sum(denials_on),
            "runs": len(wall_on),
        },
        "capture_off": {
            "mean_wall_sec": round(statistics.mean(wall_off), 6) if wall_off else 0,
            "stdev_wall_sec": round(statistics.stdev(wall_off), 6) if len(wall_off) >= 2 else 0,
            "denials_total": sum(denials_off),
            "runs": len(wall_off),
        },
        "latency_delta_sec": round((statistics.mean(wall_on) - statistics.mean(wall_off)), 6) if wall_on and wall_off else 0,
        "denial_coverage_unchanged": sum(denials_on) == sum(denials_off),
    }

    out_path = args.out_dir / "p6_capture_ablation.json"
    out_path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
