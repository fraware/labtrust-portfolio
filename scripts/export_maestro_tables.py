#!/usr/bin/env python3
"""
Export P4 MAESTRO fault sweep and baseline as markdown tables for the draft.
Reads multi_sweep.json and baseline_summary.json; prints Table 1 and Table 2.
Usage (from repo root):
  python scripts/export_maestro_tables.py
  python scripts/export_maestro_tables.py --multi-sweep path/to/multi_sweep.json
  python scripts/export_maestro_tables.py --baseline path/to/baseline_summary.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_MULTI_SWEEP = (
    REPO / "datasets" / "runs" / "maestro_fault_sweep" / "multi_sweep.json"
)
DEFAULT_BASELINE = REPO / "bench" / "maestro" / "baseline_summary.json"


def _fmt(x: float | int | str) -> str:
    if isinstance(x, (int, float)):
        return f"{x:.2f}" if isinstance(x, float) else str(x)
    return str(x)


def table1(multi_sweep_path: Path) -> list[str]:
    """Produce markdown lines for Table 1 (fault sweep)."""
    if not multi_sweep_path.exists():
        return [
            "# Table 1 — Fault sweep",
            "",
            "Run scripts/maestro_fault_sweep.py then re-run this script.",
            "",
        ]
    data = json.loads(multi_sweep_path.read_text(encoding="utf-8"))
    h1 = (
        "| Scenario | Setting | tasks_completed_mean | tasks_completed_stdev | "
        "p95_latency_ms_mean | p95_latency_ms_stdev | steps_after_fault_mean |"
    )
    h2 = (
        "|----------|---------|---------------------|----------------------|"
        "------------------------|-------------------------|------------------------|"
    )
    lines = [
        "# Table 1 — Fault sweep. tasks_completed mean/stdev, p95_latency_ms (ms), and steps_to_completion_after_first_fault (recovery) by scenario and setting; N seeds per cell (run_manifest in multi_sweep.json).",
        "",
        h1,
        h2,
    ]
    for combined in data.get("per_scenario", []):
        scenario = combined.get("scenario", "")
        for summary in combined.get("sweep", []):
            setting = summary.get("setting", "")
            tc_m = summary.get("tasks_completed_mean", "")
            tc_s = summary.get("tasks_completed_stdev", "")
            p95_m = summary.get("p95_latency_ms_mean", "")
            p95_s = summary.get("p95_latency_ms_stdev", "")
            steps_af = summary.get("steps_to_completion_after_first_fault_mean", "—")
            row = (
                f"| {scenario} | {setting} | {_fmt(tc_m)} | {_fmt(tc_s)} | "
                f"{_fmt(p95_m)} | {_fmt(p95_s)} | {_fmt(steps_af)} |"
            )
            lines.append(row)
    return lines + [""]


def table2(baseline_path: Path) -> list[str]:
    """Produce markdown lines for Table 2 (baseline)."""
    if not baseline_path.exists():
        return [
            "# Table 2 — Baseline (Centralized vs Blackboard)",
            "",
            "Run scripts/maestro_baselines.py then re-run this script.",
            "",
        ]
    data = json.loads(baseline_path.read_text(encoding="utf-8"))
    lines = [
        "# Table 2 — Baseline (Centralized vs Blackboard)",
        "",
        "| Adapter | Seed | tasks_completed | coordination_messages | "
        "p95_latency_ms |",
        "|---------|------|----------------|------------------------|----------------|",
    ]
    for row in data.get("rows", []):
        lines.append(
            f"| {row.get('adapter', '')} | {row.get('seed', '')} | "
            f"{row.get('tasks_completed', '')} | "
            f"{row.get('coordination_messages', '')} | "
            f"{row.get('p95_latency_ms', '')} |"
        )
    return lines + [""]


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Export MAESTRO tables for P4 draft"
    )
    ap.add_argument(
        "--multi-sweep",
        type=Path,
        default=DEFAULT_MULTI_SWEEP,
        help="Path to multi_sweep.json",
    )
    ap.add_argument(
        "--baseline",
        type=Path,
        default=DEFAULT_BASELINE,
        help="Path to baseline_summary.json",
    )
    args = ap.parse_args()
    out = []
    out.extend(table1(args.multi_sweep))
    out.extend(table2(args.baseline))
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
