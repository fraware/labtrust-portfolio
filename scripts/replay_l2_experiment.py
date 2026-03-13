#!/usr/bin/env python3
"""
P3 Replay: minimal L2-style experiment.
Runs the same logical scenario N times with a synthetic "hardware timestamp" noise model
(small jitter added to ts), runs L0 replay on each trace, and records fraction of runs
that diverge or variance of tasks_completed. Output: datasets/runs/replay_l2_experiment/l2_summary.json.
Usage: PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/replay_l2_experiment.py [--runs N] [--jitter 0.01]
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "impl" / "src"))
if "LABTRUST_KERNEL_DIR" not in os.environ:
    os.environ["LABTRUST_KERNEL_DIR"] = str(REPO / "kernel")


def main() -> int:
    ap = argparse.ArgumentParser(description="P3: L2-style experiment (jittered timestamps)")
    ap.add_argument("--runs", type=int, default=10, help="Number of thin-slice runs with jitter")
    ap.add_argument("--jitter", type=float, default=0.01, help="Max timestamp jitter (seconds)")
    ap.add_argument("--out", type=Path, default=REPO / "datasets" / "runs" / "replay_l2_experiment")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.seed)

    from labtrust_portfolio.thinslice import run_thin_slice
    from labtrust_portfolio.replay import replay_trace

    replay_ok_list = []
    tasks_completed_list = []
    for i in range(args.runs):
        run_dir = args.out / f"run_{i}"
        run_dir.mkdir(parents=True, exist_ok=True)
        run_thin_slice(
            run_dir,
            seed=args.seed + i,
            scenario_id="toy_lab_v0",
            drop_completion_prob=0.0,
        )
        trace_path = run_dir / "trace.json"
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        # Apply jitter to event timestamps (L2-style: hardware timestamp noise)
        for ev in trace.get("events", []):
            ev["ts"] = ev.get("ts", 0) + rng.uniform(-args.jitter, args.jitter)
        trace_path.write_text(json.dumps(trace, indent=2) + "\n", encoding="utf-8")
        ok, _ = replay_trace(trace)
        replay_ok_list.append(ok)
        report_path = run_dir / "maestro_report.json"
        if report_path.exists():
            report = json.loads(report_path.read_text(encoding="utf-8"))
            tasks_completed_list.append(report.get("metrics", {}).get("tasks_completed", 0))

    divergence_count = sum(1 for ok in replay_ok_list if not ok)
    divergence_rate = divergence_count / len(replay_ok_list) if replay_ok_list else 0.0
    outcome_variance = (sum((x - sum(tasks_completed_list) / len(tasks_completed_list)) ** 2 for x in tasks_completed_list) / len(tasks_completed_list)) ** 0.5 if len(tasks_completed_list) > 1 else 0.0

    summary = {
        "l2_style_experiment": True,
        "n_runs": args.runs,
        "jitter_sec": args.jitter,
        "divergence_count": divergence_count,
        "divergence_rate": round(divergence_rate, 4),
        "tasks_completed_mean": sum(tasks_completed_list) / len(tasks_completed_list) if tasks_completed_list else None,
        "tasks_completed_variance": round(outcome_variance, 4) if tasks_completed_list else None,
        "run_manifest": {"script": "replay_l2_experiment.py", "seed": args.seed},
    }
    out_file = args.out / "l2_summary.json"
    out_file.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
