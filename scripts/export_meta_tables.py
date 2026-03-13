#!/usr/bin/env python3
"""
Export P8 Meta-Coordination eval results as markdown tables for the draft.
Reads meta_eval/comparison.json.
Usage (from repo root):
  python scripts/export_meta_tables.py
  python scripts/export_meta_tables.py path/to/comparison.json
  python scripts/export_meta_tables.py --comparison path/to/comparison.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_COMPARISON = (
    REPO / "datasets" / "runs" / "meta_eval" / "comparison.json"
)


def _fmt(x: float | int | str | None) -> str:
    if x is None:
        return "-"
    if isinstance(x, float):
        return f"{x:.2f}"
    return str(x)


def table1(data: dict) -> list[str]:
    """Produce markdown lines for Table 1 (fixed vs meta vs naive)."""
    fixed = data.get("fixed") or {}
    meta = data.get("meta_controller") or {}
    naive = data.get("naive_switch_baseline")
    h1 = (
        "| Regime | tasks_completed_mean | collapse_count | "
        "regime_switch_count_total |"
    )
    h2 = (
        "|--------|---------------------|----------------|"
        "---------------------------|"
    )
    lines = [
        "# Table 1 - Comparison (fixed vs meta vs naive)",
        "",
        "Source: comparison.json. Run meta_eval.py --run-naive to regenerate.",
        "",
        h1,
        h2,
    ]
    row_fixed = (
        f"| fixed (Centralized) | {_fmt(fixed.get('tasks_completed_mean'))} | "
        f"{_fmt(fixed.get('collapse_count'))} | - |"
    )
    meta_switches = sum(
        s.get("regime_switch_count", 0) for s in meta.get("per_seed", [])
    )
    row_meta = (
        f"| meta_controller | {_fmt(meta.get('tasks_completed_mean'))} | "
        f"{_fmt(meta.get('collapse_count'))} | {_fmt(meta_switches)} |"
    )
    lines.append(row_fixed)
    lines.append(row_meta)
    if naive:
        row_naive = (
            f"| naive (fault_threshold=0) | "
            f"{_fmt(naive.get('tasks_completed_mean'))} | - | "
            f"{_fmt(naive.get('regime_switch_count_total'))} |"
        )
        lines.append(row_naive)
    lines.append("")
    return lines


def table2(data: dict) -> list[str]:
    """Produce markdown lines for Table 2 (per-seed summary)."""
    meta = data.get("meta_controller") or {}
    per_seed = meta.get("per_seed") or []
    if not per_seed:
        return []
    h1 = "| seed | tasks_completed | regime_switch_count | collapse |"
    h2 = "|------|----------------|---------------------|---------|"
    lines = ["# Table 2 - Per-seed (meta_controller)", "", h1, h2]
    for s in per_seed:
        seed = s.get("seed", "-")
        tc = _fmt(s.get("tasks_completed"))
        rsc = _fmt(s.get("regime_switch_count"))
        coll = s.get("collapse", False)
        lines.append(f"| {seed} | {tc} | {rsc} | {coll} |")
    lines.append("")
    return lines


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Export P8 meta_eval comparison.json as markdown tables"
    )
    ap.add_argument(
        "comparison_path",
        nargs="?",
        type=Path,
        default=None,
        help="Path to comparison.json (optional)",
    )
    ap.add_argument(
        "--comparison",
        type=Path,
        default=None,
        help="Path to comparison.json (overrides positional path)",
    )
    ap.add_argument(
        "--table2",
        action="store_true",
        help="Also print per-seed Table 2",
    )
    args = ap.parse_args()
    path = args.comparison or args.comparison_path or DEFAULT_COMPARISON
    if not path.is_file():
        print(f"File not found: {path}", file=sys.stderr)
        return 1
    data = json.loads(path.read_text(encoding="utf-8"))
    for line in table1(data):
        print(line)
    if args.table2:
        for line in table2(data):
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
