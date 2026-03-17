#!/usr/bin/env python3
"""
Export P6 baseline comparison (gated vs ungated) as markdown table.
Reads baseline_comparison.json; outputs table and summary.
Usage: python scripts/export_p6_baseline_table.py [--out-dir datasets/runs/llm_eval]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO / "datasets" / "runs" / "llm_eval"


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Export P6 baseline comparison (gated vs weak vs ungated) table"
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT,
        help="Directory containing baseline_comparison.json (or baseline file when --baseline-file)",
    )
    ap.add_argument(
        "--baseline-file",
        type=str,
        default=None,
        help="Baseline JSON filename (e.g. baseline_comparison.json or baseline_comparison_args.json); default: baseline_comparison.json",
    )
    args = ap.parse_args()
    filename = args.baseline_file or "baseline_comparison.json"
    path = args.out_dir / filename
    if not path.exists():
        print(f"Run scripts/llm_redteam_eval.py --run-baseline [--baseline-plan args_unsafe] first to produce {filename}.")
        return 1
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("rows", [])
    plan_type = data.get("plan_type", "tool_unsafe")
    has_weak = any("weak_denials" in r for r in rows)
    if has_weak:
        header = "| Scenario | Seed | Gated denials | Weak denials | Ungated denials | Gated tasks_ok | Weak tasks_ok | Ungated tasks_ok |"
        sep = "|----------|------|---------------|--------------|-----------------|----------------|---------------|------------------|"
        caption = (
            "Same scenarios and seeds; plan contains one unsafe step (tool-level: execute_system). "
            "Gated: full validator; weak: allow-list only; ungated: no validation."
        )
        if plan_type == "args_unsafe":
            caption = (
                "Same scenarios and seeds; plan contains allow-listed tool with unsafe args (path traversal). "
                "Gated: full validator (safe_args blocks); weak: allow-list only (allows); ungated: no validation."
            )
        lines = [
            "# Table — Baseline comparison (gated vs weak vs ungated)" + (" — argument-level (args_unsafe)" if plan_type == "args_unsafe" else ""),
            "",
            caption,
            f"Regenerate with export_p6_baseline_table.py [--baseline-file {filename}]. Source: {filename}.",
            "",
            header,
            sep,
        ]
        for r in rows:
            lines.append(
                f"| {r.get('scenario_id', '')} | {r.get('seed', '')} | "
                f"{r.get('gated_denials', '')} | {r.get('weak_denials', '')} | {r.get('ungated_denials', '')} | "
                f"{r.get('gated_tasks_completed', '')} | {r.get('weak_tasks_completed', '')} | {r.get('ungated_tasks_completed', '')} |"
            )
        em = data.get("excellence_metrics", {})
        lines.extend([
            "",
            "Summary:",
            "| Metric | Gated | Weak | Ungated |",
            "|--------|-------|------|---------|",
            f"| Total denials | {em.get('denial_count_gated', '—')} | {em.get('denial_count_weak', '—')} | {em.get('denial_count_ungated', '—')} |",
            f"| Mean tasks_completed | {em.get('tasks_completed_mean_gated', '—')} | {em.get('tasks_completed_mean_weak', '—')} | {em.get('tasks_completed_mean_ungated', '—')} |",
            "",
        ])
    else:
        lines = [
            "# Table — Baseline comparison (gated vs ungated)",
            "",
            "Same scenarios and seeds; plan contains one unsafe step. Gated: full validator; ungated: no validation.",
            f"Regenerate with export_p6_baseline_table.py [--baseline-file {filename}]. Source: {filename}.",
            "",
            "| Scenario | Seed | Gated denials | Ungated denials | Gated tasks_ok | Ungated tasks_ok |",
            "|----------|------|---------------|-----------------|----------------|------------------|",
        ]
        for r in rows:
            lines.append(
                f"| {r.get('scenario_id', '')} | {r.get('seed', '')} | "
                f"{r.get('gated_denials', '')} | {r.get('ungated_denials', '')} | "
                f"{r.get('gated_tasks_completed', '')} | {r.get('ungated_tasks_completed', '')} |"
            )
        em = data.get("excellence_metrics", {})
        lines.extend([
            "",
            "Summary:",
            "| Metric | Gated | Ungated |",
            "|--------|-------|---------|",
            f"| Total denials | {em.get('denial_count_gated', '—')} | {em.get('denial_count_ungated', '—')} |",
            f"| Mean tasks_completed | {em.get('tasks_completed_mean_gated', '—')} | {em.get('tasks_completed_mean_ungated', '—')} |",
            "",
        ])
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
