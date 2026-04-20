#!/usr/bin/env python3
"""
P5 Scaling: generate MAESTRO runs for multiple scenario families and fault
settings. Writes to datasets/runs/multiscenario_runs/ for scaling_heldout_eval.
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "impl" / "src"))
if "LABTRUST_KERNEL_DIR" not in os.environ:
    os.environ["LABTRUST_KERNEL_DIR"] = str(REPO_ROOT / "kernel")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="P5: Generate multi-scenario MAESTRO runs",
    )
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
        help=(
            "Seeds per (scenario, setting); default 20 publishable; "
            "30 for sensitivity"
        ),
    )
    ap.add_argument(
        "--fault-mix",
        action="store_true",
        help="Include calibration_invalid fault setting for lab-real fault mix",
    )
    ap.add_argument(
        "--scenarios",
        type=str,
        default=None,
        metavar="ID1,ID2,...",
        help=(
            "Comma-separated scenario ids (subset). For parallel workers on a "
            "shared disk, partition by scenario and/or seed range."
        ),
    )
    ap.add_argument(
        "--seed-min",
        type=int,
        default=None,
        metavar="N",
        help=(
            "Inclusive lower seed (with --seed-max). Overrides 1..--seeds."
        ),
    )
    ap.add_argument(
        "--seed-max",
        type=int,
        default=None,
        metavar="N",
        help="Inclusive upper seed (with --seed-min).",
    )
    ap.add_argument(
        "--profile",
        choices=("all", "real_world", "core"),
        default="all",
        help=(
            "all: every scenario YAML; real_world: deployment-shaped (no toy_lab); "
            "core: legacy five scenarios only"
        ),
    )
    ap.add_argument(
        "--coordination-grid",
        action="store_true",
        help=(
            "P5 paper mode: sweep coordination_regime x agent_count (otherwise only "
            "centralized, 1 agent for backward compatibility)"
        ),
    )
    ap.add_argument(
        "--p5-lite",
        action="store_true",
        help="With --coordination-grid: fewer regimes and agent counts for CI / smoke",
    )
    ap.add_argument(
        "--agent-counts",
        type=str,
        default="1,2,4,8",
        help="Comma-separated agent counts (used with --coordination-grid)",
    )
    ap.add_argument(
        "--regimes",
        type=str,
        default="",
        help=(
            "Comma-separated coordination regimes; default all valid harness regimes"
        ),
    )
    ap.add_argument(
        "--clean",
        action="store_true",
        help="Delete output directory before generating (avoids mixed layout / stale traces)",
    )
    args = ap.parse_args()

    if args.clean and args.out.exists():
        shutil.rmtree(args.out)

    if (args.seed_min is None) ^ (args.seed_max is None):
        print(
            "Error: use --seed-min and --seed-max together.",
            file=sys.stderr,
        )
        return 1
    if args.seed_min is not None:
        if args.seed_min < 1 or args.seed_max < args.seed_min:
            print(
                "Error: require 1 <= --seed-min <= --seed-max.",
                file=sys.stderr,
            )
            return 1
        seed_range = range(args.seed_min, args.seed_max + 1)
    else:
        seed_range = range(1, args.seeds + 1)

    from labtrust_portfolio.coordination_profile import VALID_REGIMES
    from labtrust_portfolio.thinslice import run_thin_slice
    from labtrust_portfolio.scenario import list_scenario_ids, load_scenario

    default_list = [
        "toy_lab_v0",
        "lab_profile_v0",
        "warehouse_v0",
        "traffic_v0",
        "regime_stress_v0",
        "regime_stress_v1",
        "rep_cps_scheduling_v0",
    ]
    core_list = [
        "toy_lab_v0",
        "lab_profile_v0",
        "warehouse_v0",
        "traffic_v0",
        "regime_stress_v0",
    ]
    real_world_list = [
        "lab_profile_v0",
        "warehouse_v0",
        "traffic_v0",
        "regime_stress_v0",
        "regime_stress_v1",
        "rep_cps_scheduling_v0",
    ]
    if args.scenarios:
        scenario_ids = [
            x.strip() for x in args.scenarios.split(",") if x.strip()
        ]
        if not scenario_ids:
            print("Error: --scenarios is empty.", file=sys.stderr)
            return 1
        for sid in scenario_ids:
            try:
                load_scenario(sid)
            except (FileNotFoundError, ValueError) as e:
                print(
                    f"Error: unknown or invalid scenario {sid!r}: {e}",
                    file=sys.stderr,
                )
                return 1
    elif args.profile == "real_world":
        scenario_ids = real_world_list
    elif args.profile == "core":
        scenario_ids = core_list
    else:
        scenario_ids = list_scenario_ids()
        if not scenario_ids:
            scenario_ids = default_list
    settings = [
        {
            "drop_completion_prob": 0.0,
            "calibration_invalid_prob": 0.0,
            "delay_fault_prob": 0.0,
            "label": "no_drop",
        },
        {
            "drop_completion_prob": 0.05,
            "calibration_invalid_prob": 0.0,
            "delay_fault_prob": 0.0,
            "label": "drop_005",
        },
    ]
    if args.fault_mix:
        settings.append(
            {
                "drop_completion_prob": 0.0,
                "calibration_invalid_prob": 0.1,
                "delay_fault_prob": 0.0,
                "label": "calibration_invalid_01",
            }
        )
        settings.append(
            {
                "drop_completion_prob": 0.0,
                "calibration_invalid_prob": 0.0,
                "delay_fault_prob": 0.1,
                "label": "delay_01",
            }
        )
    if args.coordination_grid:
        if args.p5_lite:
            agent_list = [1, 4]
            regime_list = ["centralized", "hierarchical", "decentralized"]
        else:
            agent_list = [
                int(x.strip())
                for x in args.agent_counts.split(",")
                if x.strip().isdigit()
            ]
            if not agent_list:
                agent_list = [1, 2, 4, 8]
            if args.regimes.strip():
                regime_list = [
                    x.strip()
                    for x in args.regimes.split(",")
                    if x.strip() in VALID_REGIMES
                ]
            else:
                regime_list = list(VALID_REGIMES)
            if not regime_list:
                regime_list = ["centralized"]
    else:
        agent_list = [1]
        regime_list = ["centralized"]

    args.out.mkdir(parents=True, exist_ok=True)
    count = 0
    for scenario_id in scenario_ids:
        try:
            load_scenario(scenario_id)
        except (FileNotFoundError, ValueError):
            continue
        for s in settings:
            for regime in regime_list:
                for ac in agent_list:
                    for seed in seed_range:
                        if args.coordination_grid:
                            run_dir = (
                                args.out
                                / scenario_id
                                / s["label"]
                                / regime
                                / f"agents_{ac}"
                                / f"seed_{seed}"
                            )
                        else:
                            run_dir = args.out / scenario_id / s["label"] / f"seed_{seed}"
                        run_dir.mkdir(parents=True, exist_ok=True)
                        run_thin_slice(
                            run_dir,
                            seed=seed,
                            scenario_id=scenario_id,
                            drop_completion_prob=s["drop_completion_prob"],
                            delay_fault_prob=s.get("delay_fault_prob", 0.0),
                            calibration_invalid_prob=s.get(
                                "calibration_invalid_prob", 0.0
                            ),
                            agent_count=ac,
                            coordination_regime=regime,
                            fault_setting_label=s["label"],
                        )
                        count += 1
    print(f"Generated {count} runs under {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
