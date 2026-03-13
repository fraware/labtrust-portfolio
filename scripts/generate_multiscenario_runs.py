#!/usr/bin/env python3
"""
P5 Scaling: generate MAESTRO runs for multiple scenario families and fault settings.
Writes to datasets/runs/multiscenario_runs/ for scaling_heldout_eval.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "impl" / "src"))
if "LABTRUST_KERNEL_DIR" not in os.environ:
    os.environ["LABTRUST_KERNEL_DIR"] = str(REPO_ROOT / "kernel")


def main() -> int:
    ap = argparse.ArgumentParser(description="P5: Generate multi-scenario MAESTRO runs")
    ap.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "datasets" / "runs" / "multiscenario_runs",
        help="Output directory",
    )
    ap.add_argument(
        "--seeds",
        type=int,
        default=20,
        help="Seeds per (scenario, setting); default 20 for publishable; use 30 for sensitivity",
    )
    ap.add_argument(
        "--fault-mix",
        action="store_true",
        help="Include calibration_invalid fault setting for lab-real fault mix",
    )
    args = ap.parse_args()

    from labtrust_portfolio.thinslice import run_thin_slice
    from labtrust_portfolio.scenario import list_scenario_ids

    scenario_ids = list_scenario_ids()
    if not scenario_ids:
        scenario_ids = [
            "toy_lab_v0", "lab_profile_v0", "warehouse_v0", "traffic_v0", "regime_stress_v0"
        ]
    settings = [
        {"drop_completion_prob": 0.0, "calibration_invalid_prob": 0.0, "delay_fault_prob": 0.0, "label": "no_drop"},
        {"drop_completion_prob": 0.05, "calibration_invalid_prob": 0.0, "delay_fault_prob": 0.0, "label": "drop_005"},
    ]
    if args.fault_mix:
        settings.append({"drop_completion_prob": 0.0, "calibration_invalid_prob": 0.1, "delay_fault_prob": 0.0, "label": "calibration_invalid_01"})
        settings.append({"drop_completion_prob": 0.0, "calibration_invalid_prob": 0.0, "delay_fault_prob": 0.1, "label": "delay_01"})
    args.out.mkdir(parents=True, exist_ok=True)
    count = 0
    for scenario_id in scenario_ids:
        try:
            from labtrust_portfolio.scenario import load_scenario
            load_scenario(scenario_id)
        except (FileNotFoundError, ValueError):
            continue
        for s in settings:
            for seed in range(1, args.seeds + 1):
                run_dir = args.out / scenario_id / s["label"] / f"seed_{seed}"
                run_dir.mkdir(parents=True, exist_ok=True)
                run_thin_slice(
                    run_dir,
                    seed=seed,
                    scenario_id=scenario_id,
                    drop_completion_prob=s["drop_completion_prob"],
                    delay_fault_prob=s.get("delay_fault_prob", 0.0),
                    calibration_invalid_prob=s.get("calibration_invalid_prob", 0.0),
                )
                count += 1
    print(f"Generated {count} runs under {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
