#!/usr/bin/env python3
"""
Export E3 summary as a markdown table for the draft. Reads datasets/runs/e3_summary.json
and prints a Table 1 (per-seed rows + summary). Usage (from repo root):
  python scripts/export_e3_table.py
  python scripts/export_e3_table.py --summary path/to/e3_summary.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_SUMMARY = REPO / "datasets" / "runs" / "e3_summary.json"


def main() -> int:
    ap = argparse.ArgumentParser(description="Export E3 summary as markdown table")
    ap.add_argument(
        "--summary",
        type=Path,
        default=DEFAULT_SUMMARY,
        help="Path to e3_summary.json",
    )
    ap.add_argument(
        "--compact",
        action="store_true",
        help="Print one table: scenario, n, tasks_completed mean/stdev/CI, p95_latency_ms mean/stdev/CI",
    )
    args = ap.parse_args()
    if not args.summary.exists():
        print(f"Error: {args.summary} not found. Run replay_link_e3.py first.")
        return 1
    data = json.loads(args.summary.read_text(encoding="utf-8"))
    per_scenario = data.get("per_scenario", [])
    if args.compact and per_scenario:
        n = data.get("runs", 0)
        lines = [
            "| Scenario | n | tasks_completed mean (stdev) | 95% CI | p95_latency_ms mean (stdev) | 95% CI |",
            "|----------|---|------------------------------|--------|-----------------------------|--------|",
        ]
        for block in per_scenario:
            sid = block.get("scenario_id", "")
            tc_m = block.get("tasks_completed_mean", 0)
            tc_s = block.get("tasks_completed_stdev", 0)
            p95_m = block.get("p95_latency_ms_mean", 0)
            p95_s = block.get("p95_latency_ms_stdev", 0)
            tc_ci = block.get("tasks_completed_ci_95", [None, None])
            p95_ci = block.get("p95_latency_ms_ci_95", [None, None])
            tc_str = f"{tc_m:.2f} ({tc_s:.2f})" if isinstance(tc_m, (int, float)) else str(tc_m)
            p95_str = f"{p95_m:.2f} ({p95_s:.2f})" if isinstance(p95_m, (int, float)) else str(p95_m)
            tc_ci_str = str(tc_ci) if tc_ci[0] is not None else "-"
            p95_ci_str = str(p95_ci) if p95_ci[0] is not None else "-"
            lines.append(f"| {sid} | {n} | {tc_str} | {tc_ci_str} | {p95_str} | {p95_ci_str} |")
        for line in lines:
            print(line)
        return 0
    if per_scenario:
        n = data.get("runs", 0)
        lines = [
            "# Table 1 — E3 replay-link. tasks_completed, p95_latency_ms (ms), match per seed; N seeds (run_manifest in e3_summary.json).",
            "",
            "# E3 Replay link (multi-scenario)",
            "",
        ]
        for block in per_scenario:
            sid = block.get("scenario_id", "")
            per_run = block.get("per_run", [])
            lines.append(f"## Scenario: {sid}")
            lines.append("")
            lines.append("| Seed | tasks_completed | coordination_messages | p95_latency_ms | match |")
            lines.append("|------|----------------|----------------------|----------------|-------|")
            for r in per_run:
                seed = r.get("seed", "")
                tc = r.get("tasks_completed", "")
                cm = r.get("coordination_messages", "")
                p95 = r.get("p95_latency_ms", "")
                p95_f = f"{p95:.2f}" if isinstance(p95, (int, float)) else str(p95)
                match = "yes" if r.get("match") else "no"
                lines.append(f"| {seed} | {tc} | {cm} | {p95_f} | {match} |")
            tc_mean = block.get("tasks_completed_mean", "")
            tc_stdev = block.get("tasks_completed_stdev", "")
            p95_mean = block.get("p95_latency_ms_mean", "")
            p95_stdev = block.get("p95_latency_ms_stdev", "")
            all_match = "true" if block.get("all_match") else "false"
            tc_f = f"{tc_mean:.2f}" if isinstance(tc_mean, (int, float)) else str(tc_mean)
            tc_sf = f"{tc_stdev:.2f}" if isinstance(tc_stdev, (int, float)) else str(tc_stdev)
            p95_mf = f"{p95_mean:.2f}" if isinstance(p95_mean, (int, float)) else str(p95_mean)
            p95_sf = f"{p95_stdev:.2f}" if isinstance(p95_stdev, (int, float)) else str(p95_stdev)
            lines.append(f"| **Summary (n={n})** | mean {tc_f}, stdev {tc_sf} | - | mean {p95_mf}, stdev {p95_sf} | {all_match} |")
            if "tasks_completed_ci_95" in block and "p95_latency_ms_ci_95" in block:
                lines.append("")
                lines.append("95% CI: tasks_completed " + str(block["tasks_completed_ci_95"]) + "; p95_latency_ms " + str(block["p95_latency_ms_ci_95"]))
            lines.append("")
        for line in lines:
            print(line)
        return 0

    per_run = data.get("per_run", [])
    if not per_run:
        print("Error: no per_run or per_scenario in summary.")
        return 1

    n = data.get("runs", len(per_run))
    lines = [
        "# Table 1 — E3 replay-link. tasks_completed, p95_latency_ms (ms), match per seed; N seeds (run_manifest in e3_summary.json).",
        "",
        "| Seed | tasks_completed | coordination_messages | p95_latency_ms | match |",
        "|------|----------------|----------------------|----------------|-------|",
    ]
    for r in per_run:
        seed = r.get("seed", "")
        tc = r.get("tasks_completed", "")
        cm = r.get("coordination_messages", "")
        p95 = r.get("p95_latency_ms", "")
        p95_f = f"{p95:.2f}" if isinstance(p95, (int, float)) else str(p95)
        match = "yes" if r.get("match") else "no"
        lines.append(f"| {seed} | {tc} | {cm} | {p95_f} | {match} |")

    tc_mean = data.get("tasks_completed_mean", "")
    tc_stdev = data.get("tasks_completed_stdev", "")
    p95_mean = data.get("p95_latency_ms_mean", "")
    p95_stdev = data.get("p95_latency_ms_stdev", "")
    all_match = "true" if data.get("all_match") else "false"
    n = n or data.get("runs", len(per_run))
    tc_f = f"{tc_mean:.2f}" if isinstance(tc_mean, (int, float)) else str(tc_mean)
    tc_sf = f"{tc_stdev:.2f}" if isinstance(tc_stdev, (int, float)) else str(tc_stdev)
    p95_mf = f"{p95_mean:.2f}" if isinstance(p95_mean, (int, float)) else str(p95_mean)
    p95_sf = f"{p95_stdev:.2f}" if isinstance(p95_stdev, (int, float)) else str(p95_stdev)
    lines.append(f"| **Summary (n={n})** | mean {tc_f}, stdev {tc_sf} | - | mean {p95_mf}, stdev {p95_sf} | {all_match} |")

    if "tasks_completed_ci_95" in data and "p95_latency_ms_ci_95" in data:
        tc_ci = data["tasks_completed_ci_95"]
        p95_ci = data["p95_latency_ms_ci_95"]
        lines.append("")
        lines.append("95% CI for mean: tasks_completed " + str(tc_ci) + "; p95_latency_ms " + str(p95_ci))

    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
