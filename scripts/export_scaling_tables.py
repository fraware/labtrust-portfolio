#!/usr/bin/env python3
"""
Export P5 Scaling held-out results as markdown tables for the draft.
Reads scaling_eval/heldout_results.json; prints Table 1 and Table 2.
Usage (from repo root):
  python scripts/export_scaling_tables.py
  python scripts/export_scaling_tables.py --results path/to/heldout_results.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS = (
    REPO / "datasets" / "runs" / "scaling_eval" / "heldout_results.json"
)


def _fmt(x: float | int | str | None) -> str:
    if x is None:
        return "-"
    if isinstance(x, (int, float)):
        return f"{x:.2f}" if isinstance(x, float) else str(x)
    return str(x)


def table1(data: dict) -> list[str]:
    """Produce markdown lines for Table 1 (held-out per scenario)."""
    h1 = (
        "| Held-out scenario | train_n | test_n | baseline_mae | per_scenario_mae | "
        "feat_baseline_mae | regression_mae | actuals_mean |"
    )
    h2 = (
        "|-------------------|--------|--------|--------------|------------------|"
        "-------------------|---------------|-------------|"
    )
    lines = ["# Table 1 - Held-out results", "", h1, h2]
    for r in data.get("held_out_results", []):
        row = (
            f"| {r.get('held_out_scenario', '')} | {r.get('train_n', '')} | "
            f"{r.get('test_n', '')} | {_fmt(r.get('baseline_mae'))} | "
            f"{_fmt(r.get('per_scenario_baseline_mae'))} | "
            f"{_fmt(r.get('feat_baseline_mae'))} | "
            f"{_fmt(r.get('regression_mae'))} | {_fmt(r.get('actuals_mean'))} |"
        )
        lines.append(row)
    lines.append("")
    return lines


def table2(data: dict) -> list[str]:
    """Produce markdown lines for Table 2 (baselines summary with CI)."""
    lines = [
        "# Table 2 - Baselines (MAE and 95% CI)",
        "",
        "| Baseline | MAE | CI95 lower | CI95 upper |",
        "|----------|-----|------------|------------|",
    ]
    mae_b = data.get("overall_baseline_mae")
    lo_b = data.get("overall_baseline_mae_ci95_lower")
    hi_b = data.get("overall_baseline_mae_ci95_upper")
    lines.append(f"| Global mean | {_fmt(mae_b)} | {_fmt(lo_b)} | {_fmt(hi_b)} |")
    mae_ps = data.get("overall_per_scenario_baseline_mae")
    if mae_ps is not None:
        lines.append(f"| Per-scenario mean (scenario identity allowed) | {_fmt(mae_ps)} | — | — |")
    mae_f = data.get("overall_feat_baseline_mae")
    lo_f = data.get("overall_feat_baseline_mae_ci95_lower")
    hi_f = data.get("overall_feat_baseline_mae_ci95_upper")
    lines.append(f"| Num-tasks mean | {_fmt(mae_f)} | {_fmt(lo_f)} | {_fmt(hi_f)} |")
    mae_r = data.get("overall_regression_mae")
    lo_r = data.get("overall_regression_mae_ci95_lower")
    hi_r = data.get("overall_regression_mae_ci95_upper")
    if mae_r is not None:
        lines.append(
            f"| Regression (compact features) | {_fmt(mae_r)} | {_fmt(lo_r)} | {_fmt(hi_r)} |"
        )
    else:
        reason = data.get("regression_skipped_reason", "train_n < k or singular")
        lines.append(
            f"| Regression (num_tasks, num_faults) | N/A ({reason}) | — | — |"
        )
        lines.append(f"*Regression: N/A when {reason}; see run_manifest.train_n_total.*")
    lines.append("")
    return lines


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Export P5 Scaling tables for draft"
    )
    ap.add_argument(
        "--results",
        type=Path,
        default=DEFAULT_RESULTS,
        help="Path to heldout_results.json",
    )
    args = ap.parse_args()
    if not args.results.exists():
        print("Run scripts/scaling_heldout_eval.py then re-run this script.")
        return 1
    data = json.loads(args.results.read_text(encoding="utf-8"))
    out = []
    out.extend(table1(data))
    out.extend(table2(data))
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
