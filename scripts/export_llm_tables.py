#!/usr/bin/env python3
"""
Export P6 LLM red-team and adapter latency as markdown tables for the draft.
Reads llm_eval/red_team_results.json and optionally adapter_latency.json.
Usage (from repo root):
  python scripts/export_llm_tables.py
  python scripts/export_llm_tables.py --red-team path/to/red_team_results.json
  python scripts/export_llm_tables.py --adapter path/to/adapter_latency.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_RED_TEAM = (
    REPO / "datasets" / "runs" / "llm_eval" / "red_team_results.json"
)
DEFAULT_ADAPTER = REPO / "datasets" / "runs" / "llm_eval" / "adapter_latency.json"


def _fmt(x: float | int | str | bool | None) -> str:
    if x is None:
        return "-"
    if isinstance(x, bool):
        return "yes" if x else "no"
    if isinstance(x, float):
        return f"{x:.2f}"
    return str(x)


def table1_red_team(red_path: Path) -> list[str]:
    """Produce markdown lines for Table 1 (red-team results)."""
    if not red_path.exists():
        return [
            "# Table 1 - Red-team results",
            "",
            "Run scripts/llm_redteam_eval.py then re-run this script.",
            "",
        ]
    data = json.loads(red_path.read_text(encoding="utf-8"))
    h1 = "| Case id | expected_block | actually_blocked | pass |"
    h2 = "|---------|----------------|------------------|------|"
    lines = ["# Table 1 - Red-team results", "", h1, h2]
    for c in data.get("cases", []):
        row = (
            f"| {c.get('id', '')} | {_fmt(c.get('expected_block'))} | "
            f"{_fmt(c.get('actually_blocked'))} | {_fmt(c.get('pass'))} |"
        )
        lines.append(row)
    lines.append("")
    return lines


def table2_adapter_latency(adapter_path: Path) -> list[str]:
    """Produce markdown lines for Table 2 (adapter latency summary)."""
    if not adapter_path.exists():
        return [
            "# Table 2 - Adapter latency",
            "",
            "Run llm_redteam_eval.py --run-adapter then re-run this script.",
            "",
        ]
    data = json.loads(adapter_path.read_text(encoding="utf-8"))
    lines = ["# Table 2 - Adapter latency", ""]
    mean_p95 = _fmt(data.get("tail_latency_p95_mean_ms"))
    lines.append(f"tail_latency_p95_mean_ms: {mean_p95}")
    lines.append(f"scenarios: {data.get('scenarios', [])}")
    lines.append(f"seeds: {data.get('seeds', [])}")
    if "latency_threshold_ms" in data:
        lines.append(
            f"latency_threshold_ms: {_fmt(data.get('latency_threshold_ms'))}"
        )
        lines.append(
            f"latency_acceptable: {_fmt(data.get('latency_acceptable'))}"
        )
    lines.append("")
    h1 = (
        "| scenario_id | seed | task_latency_ms_p95 | wall_sec |"
    )
    h2 = "|-------------|------|---------------------|----------|"
    lines.extend([h1, h2])
    for r in data.get("runs", []):
        row = (
            f"| {r.get('scenario_id', '')} | {r.get('seed', '')} | "
            f"{_fmt(r.get('task_latency_ms_p95'))} | {_fmt(r.get('wall_sec'))} |"
        )
        lines.append(row)
    lines.append("")
    return lines


def main() -> int:
    ap = argparse.ArgumentParser(description="Export P6 LLM tables for draft")
    ap.add_argument(
        "--red-team",
        type=Path,
        default=DEFAULT_RED_TEAM,
        help="Path to red_team_results.json",
    )
    ap.add_argument(
        "--adapter",
        type=Path,
        default=None,
        help="Path to adapter_latency.json (optional)",
    )
    args = ap.parse_args()
    adapter_path = (
        args.adapter if args.adapter is not None else DEFAULT_ADAPTER
    )
    out = (
        table1_red_team(args.red_team)
        + table2_adapter_latency(adapter_path)
    )
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
