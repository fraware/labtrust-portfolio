#!/usr/bin/env python3
"""
Export P7 Assurance eval results as markdown tables for the draft.
Reads assurance_eval/results.json.
Usage (from repo root):
  python scripts/export_assurance_tables.py
  python scripts/export_assurance_tables.py --results path/to/results.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS = (
    REPO / "datasets" / "runs" / "assurance_eval" / "results.json"
)


def _fmt(x: float | int | str | bool | None) -> str:
    if x is None:
        return "-"
    if isinstance(x, bool):
        return "yes" if x else "no"
    if isinstance(x, float):
        return f"{x:.2f}"
    return str(x)


def table1(data: dict) -> list[str]:
    """Produce markdown lines for Table 1 (mapping and review results)."""
    mc = data.get("mapping_check") or {}
    rev = data.get("review") or {}
    ponr = rev.get("ponr_coverage") or {}
    h1 = (
        "| mapping_check_ok | ponr_coverage_ok | review_exit_ok | "
        "ponr_events_count | ponr_coverage_ratio | control_coverage_ratio |"
    )
    h2 = (
        "|------------------|------------------|---------------|"
        "-------------------|---------------------|-------------------------|"
    )
    lines = ["# Table 1 - Mapping and review results", "", h1, h2]
    n_events = len(rev.get("ponr_events", []))
    row = (
        f"| {_fmt(mc.get('ok'))} | {_fmt(mc.get('ponr_coverage_ok'))} | "
        f"{_fmt(rev.get('exit_ok'))} | {n_events} | "
        f"{_fmt(ponr.get('ratio'))} | {_fmt(rev.get('control_coverage_ratio'))} |"
    )
    lines.append(row)
    lines.append("")
    return lines


def table2_reviews(data: dict) -> list[str]:
    """Produce markdown lines for Table 2 (per-scenario review coverage)."""
    reviews = data.get("reviews") or {}
    if not reviews:
        return []
    h1 = "| scenario_id | exit_ok | ponr_coverage_ratio | control_coverage_ratio |"
    h2 = "|-------------|---------|---------------------|-------------------------|"
    lines = ["# Table 2 - Per-scenario review (kernel PONR)", "", h1, h2]
    for sid in sorted(reviews.keys()):
        rev = reviews[sid] or {}
        pc = rev.get("ponr_coverage") or {}
        row = (
            f"| {sid} | {_fmt(rev.get('exit_ok'))} | "
            f"{_fmt(pc.get('ratio'))} | {_fmt(rev.get('control_coverage_ratio'))} |"
        )
        lines.append(row)
    lines.append("")
    return lines


def main() -> int:
    ap = argparse.ArgumentParser(description="Export P7 assurance tables for draft")
    ap.add_argument(
        "--results",
        type=Path,
        default=DEFAULT_RESULTS,
        help="Path to results.json",
    )
    args = ap.parse_args()
    if not args.results.exists():
        print("Run run_assurance_eval.py then re-run this script.")
        return 1
    data = json.loads(args.results.read_text(encoding="utf-8"))
    out = table1(data) + table2_reviews(data)
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
