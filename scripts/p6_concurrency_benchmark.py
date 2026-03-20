#!/usr/bin/env python3
"""
P6 Experiment 6: Concurrency and throughput scaling.
Replay workload at 1, 4, 8, 16, 32 concurrent runs; measure decisions/sec, p95/p99 latency,
queueing delay, denial consistency.
Usage: PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/p6_concurrency_benchmark.py [--out-dir path]
"""
from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "impl" / "src"))
if "LABTRUST_KERNEL_DIR" not in os.environ:
    os.environ["LABTRUST_KERNEL_DIR"] = str(REPO / "kernel")

DEFAULT_OUT = REPO / "datasets" / "runs" / "llm_eval"
SCENARIOS = ["toy_lab_v0", "lab_profile_v0", "warehouse_v0"]
SEEDS = list(range(1, 6))  # 5 seeds per scenario = 15 runs per concurrency level


def run_one(args: tuple) -> dict:
    scenario_id, seed, out_dir, run_id = args
    from labtrust_portfolio.adapters.llm_planning_adapter import (
        LLMPlanningAdapter,
        _denial_injection_plan_steps,
    )
    from labtrust_portfolio.adapters.base import run_adapter

    run_dir = out_dir / "concurrency_runs" / f"run_{run_id}"
    run_dir.mkdir(parents=True, exist_ok=True)
    adapter = LLMPlanningAdapter(validation_mode="gated", plan_override=_denial_injection_plan_steps())
    t0 = time.perf_counter()
    result = run_adapter(adapter, scenario_id, run_dir, seed=seed)
    elapsed = time.perf_counter() - t0
    return {
        "scenario_id": scenario_id,
        "seed": seed,
        "run_id": run_id,
        "wall_sec": round(elapsed, 4),
        "denials_count": result.maestro_report.get("denials_count", 0),
        "task_latency_p95": result.maestro_report.get("metrics", {}).get("task_latency_ms_p95", 0),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="P6 concurrency/throughput benchmark")
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--levels", type=str, default="1,4,8,16,32", help="Comma-separated concurrency levels")
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    levels = [int(x.strip()) for x in args.levels.split(",") if x.strip()]
    workload = []
    run_id = 0
    for scenario_id in SCENARIOS:
        for seed in SEEDS:
            workload.append((scenario_id, seed, args.out_dir, run_id))
            run_id += 1
    total_plans = len(workload)

    results_by_level = []
    for concurrency in levels:
        t_start = time.perf_counter()
        runs = []
        with ThreadPoolExecutor(max_workers=concurrency) as ex:
            futures = {ex.submit(run_one, w): w for w in workload}
            for fut in as_completed(futures):
                runs.append(fut.result())
        total_sec = time.perf_counter() - t_start
        plans_per_sec = total_plans / total_sec if total_sec else 0
        p95s = [r["task_latency_p95"] for r in runs if r.get("task_latency_p95")]
        denials = [r["denials_count"] for r in runs]
        results_by_level.append({
            "concurrency": concurrency,
            "total_plans": total_plans,
            "total_sec": round(total_sec, 4),
            "plans_per_sec": round(plans_per_sec, 4),
            "p95_latency_mean_ms": round(statistics.mean(p95s), 4) if p95s else 0,
            "p95_latency_stdev_ms": round(statistics.stdev(p95s), 4) if len(p95s) >= 2 else 0,
            "denials_total": sum(denials),
            "denials_consistent": 1 if all(d == denials[0] for d in denials) else 0,
            "runs": runs,
        })

    out_path = args.out_dir / "p6_concurrency_benchmark.json"
    out_path.write_text(
        json.dumps({"levels": results_by_level, "workload_size": total_plans}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
