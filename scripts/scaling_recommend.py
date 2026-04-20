#!/usr/bin/env python3
"""
P5 Scaling: regime / architecture recommendation CLI.
Predicts tasks_completed and collapse risk per coordination regime (counterfactual features),
with uncertainty bands from train residuals. Does not leak held-out rows (pass train-only
rows when evaluating LOSO).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "impl" / "src"))

from labtrust_portfolio.coordination_profile import VALID_REGIMES
from labtrust_portfolio.scaling import (
    build_dataset_from_runs,
    extract_features_from_scenario,
    regime_recommendation_bundle,
)


def main() -> int:
    ap = argparse.ArgumentParser(description="P5: Architecture / regime recommendation")
    ap.add_argument(
        "--table",
        type=Path,
        default=REPO / "datasets" / "runs" / "scaling_dataset" / "modeling_table.json",
        help="Modeling table JSON (rows with features + response)",
    )
    ap.add_argument(
        "--runs-dir",
        type=Path,
        default=None,
        help="If table missing, build from this runs dir",
    )
    ap.add_argument(
        "--scenario",
        type=str,
        required=True,
        help="Scenario id (task structure)",
    )
    ap.add_argument(
        "--agent-count",
        type=int,
        default=4,
        help="Agent count for counterfactual sweep",
    )
    ap.add_argument(
        "--fault-setting-label",
        type=str,
        default="no_drop",
        help="Fault mix label (metadata; matches generator folder)",
    )
    ap.add_argument(
        "--collapse-threshold",
        type=float,
        default=0.35,
        help="Mark predicted collapse above this as unsafe_regimes_predicted",
    )
    args = ap.parse_args()

    rows: list = []
    if args.table.exists():
        data = json.loads(args.table.read_text(encoding="utf-8"))
        rows = data.get("rows", [])
    if not rows and args.runs_dir and args.runs_dir.exists():
        rows = build_dataset_from_runs(args.runs_dir)
    if not rows:
        print("No data: provide --table or --runs-dir with MAESTRO runs")
        return 1

    feats = extract_features_from_scenario(args.scenario)
    template = {**feats, "fault_setting_label": args.fault_setting_label}
    bundle = regime_recommendation_bundle(
        rows,
        template,
        agent_count=args.agent_count,
        regimes=VALID_REGIMES,
        collapse_threshold=args.collapse_threshold,
    )
    print(json.dumps(bundle, indent=2))
    rec = bundle.get("recommended_regime")
    unsafe = bundle.get("unsafe_regimes_predicted") or []
    print(
        f"\nRecommended regime: {rec}\n"
        f"Unsafe (pred collapse > {args.collapse_threshold}): {unsafe}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
