#!/usr/bin/env python3
"""
P4 MAESTRO fault sweep: run thin-slice (or adapter) for a scenario with multiple
seeds and two fault settings (e.g. drop_completion_prob 0 vs 0.05). Output
metrics and variance to datasets/runs/maestro_fault_sweep. Usage:
  PYTHONPATH=impl/src python scripts/maestro_fault_sweep.py [--scenario ID] [--seeds N] [--out DIR]
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "impl" / "src"))
if "LABTRUST_KERNEL_DIR" not in os.environ:
    os.environ["LABTRUST_KERNEL_DIR"] = str(REPO_ROOT / "kernel")


def main() -> int:
    ap = argparse.ArgumentParser(description="P4: Fault sweep for MAESTRO scenario")
    ap.add_argument(
        "--scenario",
        type=str,
        default=None,
        help="Single scenario id (if set, run only this)",
    )
    ap.add_argument(
        "--scenarios",
        type=str,
        default="toy_lab_v0,lab_profile_v0",
        help="Comma-separated scenario ids (used if --scenario not set)",
    )
    ap.add_argument(
        "--all-scenarios",
        action="store_true",
        help="Run over all 5 scenarios (toy_lab_v0, lab_profile_v0, warehouse_v0, traffic_v0, regime_stress_v0); overrides --scenarios",
    )
    ap.add_argument(
        "--seeds",
        type=int,
        default=20,
        help="Number of seeds (1..N); default 20 for publishable; use 30 for sensitivity; CI may override with fewer",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "datasets" / "runs" / "maestro_fault_sweep",
        help="Output directory for sweep results",
    )
    args = ap.parse_args()

    from labtrust_portfolio.thinslice import run_thin_slice
    from labtrust_portfolio.scenario import list_scenario_ids

    args.out.mkdir(parents=True, exist_ok=True)
    if args.all_scenarios:
        all_ids = list_scenario_ids()
        scenarios = all_ids if all_ids else [
            "toy_lab_v0", "lab_profile_v0", "warehouse_v0", "traffic_v0", "regime_stress_v0"
        ]
    elif args.scenario:
        scenarios = [args.scenario]
    else:
        scenarios = [x.strip() for x in args.scenarios.split(",") if x.strip()]
    if not scenarios:
        scenarios = ["toy_lab_v0"]
    settings = [
        {"drop_completion_prob": 0.0, "delay_fault_prob": 0.0, "calibration_invalid_prob": 0.0, "label": "no_drop"},
        {"drop_completion_prob": 0.05, "delay_fault_prob": 0.0, "calibration_invalid_prob": 0.0, "label": "drop_005"},
        {"drop_completion_prob": 0.2, "delay_fault_prob": 0.0, "calibration_invalid_prob": 0.0, "label": "drop_02"},
        {"drop_completion_prob": 0.0, "delay_fault_prob": 0.1, "calibration_invalid_prob": 0.0, "label": "delay_01"},
        {"drop_completion_prob": 0.05, "delay_fault_prob": 0.1, "calibration_invalid_prob": 0.0, "label": "drop_005_delay_01"},
        {"drop_completion_prob": 0.0, "delay_fault_prob": 0.0, "calibration_invalid_prob": 0.1, "label": "calibration_invalid_01"},
    ]
    run_manifest = {
        "seeds": list(range(1, args.seeds + 1)),
        "seed_count": args.seeds,
        "scenarios": scenarios,
        "fault_settings": [s["label"] for s in settings],
        "fault_params": [
            {
                "drop_completion_prob": s["drop_completion_prob"],
                "delay_fault_prob": s.get("delay_fault_prob", 0.0),
                "calibration_invalid_prob": s.get("calibration_invalid_prob", 0.0),
            }
            for s in settings
        ],
    }
    multi_sweep = {
        "scenarios": scenarios,
        "run_manifest": run_manifest,
        "per_scenario": [],
        "success_criteria_met": {"run_manifest_present": True},
    }

    # Excellence metrics (STANDARDS_OF_EXCELLENCE.md) - populated after loop
    n_settings = len(settings)

    for scenario_id in scenarios:
        all_results = []
        for s in settings:
            runs = []
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
                report_path = run_dir / "maestro_report.json"
                data = json.loads(report_path.read_text(encoding="utf-8"))
                m = data["metrics"]
                runs.append(
                    {
                        "seed": seed,
                        "tasks_completed": m["tasks_completed"],
                        "coordination_messages": m["coordination_messages"],
                        "p95_latency_ms": m["task_latency_ms_p95"],
                    }
                )
            tasks = [r["tasks_completed"] for r in runs]
            p95s = [r["p95_latency_ms"] for r in runs]
            n = len(p95s)
            p99_idx = min(int(0.99 * n), n - 1) if n > 0 else -1
            p99_latency = sorted(p95s)[p99_idx] if p99_idx >= 0 else 0.0
            summary = {
                "scenario": scenario_id,
                "setting": s["label"],
                "drop_completion_prob": s["drop_completion_prob"],
                "delay_fault_prob": s.get("delay_fault_prob", 0.0),
                "tasks_completed_mean": statistics.mean(tasks),
                "tasks_completed_stdev": (
                    statistics.stdev(tasks) if len(tasks) > 1 else 0.0
                ),
                "p95_latency_ms_mean": statistics.mean(p95s),
                "p95_latency_ms_stdev": (
                    statistics.stdev(p95s) if len(p95s) > 1 else 0.0
                ),
                "p95_latency_ms_p99": p99_latency,
                "per_run": runs,
            }
            all_results.append(summary)
            (args.out / scenario_id / f"{s['label']}_summary.json").write_text(
                json.dumps(summary, indent=2) + "\n", encoding="utf-8"
            )
        combined = {"scenario": scenario_id, "sweep": all_results}
        (args.out / scenario_id / "sweep.json").write_text(
            json.dumps(combined, indent=2) + "\n", encoding="utf-8"
        )
        multi_sweep["per_scenario"].append(combined)
    multi_sweep["excellence_metrics"] = {
        "fault_coverage": n_settings,
        "scenario_diversity": len(scenarios),
        "variance_reported": True,
        "n_seeds_per_setting": args.seeds,
    }
    (args.out / "multi_sweep.json").write_text(
        json.dumps(multi_sweep, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(multi_sweep, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
