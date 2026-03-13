#!/usr/bin/env python3
"""
Export P2 REP-CPS convergence table from summary.json (when aggregation_steps > 1).
Reads datasets/runs/rep_cps_eval/summary.json and prints a markdown table for
convergence_achieved_rate, steps_to_convergence_mean, steps_to_convergence_stdev.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser(description="Export P2 convergence table")
    ap.add_argument(
        "--summary",
        type=Path,
        default=REPO_ROOT / "datasets" / "runs" / "rep_cps_eval" / "summary.json",
        help="Path to rep_cps_eval summary.json",
    )
    args = ap.parse_args()
    if not args.summary.exists():
        print(f"Summary not found: {args.summary}")
        return 1
    data = json.loads(args.summary.read_text(encoding="utf-8"))
    steps = data.get("aggregation_steps", 1)
    if steps <= 1:
        print("Convergence table: N/A (aggregation_steps <= 1). Re-run with --aggregation-steps 5.")
        return 0
    rate = data.get("convergence_achieved_rate")
    mean_s = data.get("convergence_steps_to_convergence_mean")
    stdev_s = data.get("convergence_steps_to_convergence_stdev")
    print("## Convergence under multi-step aggregation (source: summary.json)")
    print()
    print("| Metric | Value |")
    print("|--------|-------|")
    print(f"| aggregation_steps | {steps} |")
    print(f"| convergence_achieved_rate | {rate if rate is not None else '—'} |")
    print(f"| steps_to_convergence_mean | {mean_s if mean_s is not None else '—'} |")
    print(f"| steps_to_convergence_stdev | {stdev_s if stdev_s is not None else '—'} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
