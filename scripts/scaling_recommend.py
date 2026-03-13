#!/usr/bin/env python3
"""
P5 Scaling: architecture recommendation CLI. Reads modeling table (or builds from runs),
prints suggested scenario or baseline prediction. Usage:
  PYTHONPATH=impl/src python scripts/scaling_recommend.py [--table FILE] [--scenario ID]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "impl" / "src"))

from labtrust_portfolio.scaling import (
    extract_features_from_scenario,
    predict_baseline_mean,
    predict_by_scenario,
    build_dataset_from_runs,
)


def main() -> int:
    ap = argparse.ArgumentParser(description="P5: Architecture recommendation")
    ap.add_argument(
        "--table",
        type=Path,
        default=REPO / "datasets" / "runs" / "scaling_dataset" / "modeling_table.json",
        help="Modeling table JSON (rows with features + response)",
    )
    ap.add_argument(
        "--scenario",
        type=str,
        default=None,
        help="Recommend for this scenario id; else print global baseline",
    )
    ap.add_argument(
        "--runs-dir",
        type=Path,
        default=None,
        help="If table missing, build from this runs dir",
    )
    args = ap.parse_args()

    rows = []
    if args.table.exists():
        data = json.loads(args.table.read_text(encoding="utf-8"))
        rows = data.get("rows", [])
    if not rows and args.runs_dir and args.runs_dir.exists():
        rows = build_dataset_from_runs(args.runs_dir)
    if not rows:
        print("No data: provide --table or --runs-dir with MAESTRO runs")
        return 1

    if args.scenario:
        feats = extract_features_from_scenario(args.scenario)
        pred = predict_by_scenario(rows, args.scenario, "tasks_completed")
        print(f"Scenario: {args.scenario} (num_tasks={feats['num_tasks']})")
        print(f"Predicted tasks_completed (mean over same scenario): {pred:.2f}")
    else:
        pred = predict_baseline_mean(rows, "tasks_completed")
        print(f"Global mean tasks_completed: {pred:.2f}")
        print("Use --scenario <id> for per-scenario recommendation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
