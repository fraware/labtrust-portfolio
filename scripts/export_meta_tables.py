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
        naive_per = naive.get("per_seed") or []
        naive_collapse = naive.get("collapse_count")
        if naive_collapse is None and naive_per:
            naive_collapse = sum(1 for s in naive_per if s.get("collapse"))
        naive_cc = _fmt(naive_collapse) if naive_collapse is not None else "-"
        row_naive = (
            f"| naive (fault_threshold=0) | "
            f"{_fmt(naive.get('tasks_completed_mean'))} | {naive_cc} | "
            f"{_fmt(naive.get('regime_switch_count_total'))} |"
        )
        lines.append(row_naive)
    lines.append("")
    return lines


def recovery_safety_lines(data: dict) -> list[str]:
    fix = data.get("fixed") or {}
    meta = data.get("meta_controller") or {}
    if "ponr_violation_count_total" not in fix and "ponr_violation_count_total" not in meta:
        return []
    lines = [
        "## Recovery latency proxy and explicit safety counts",
        "",
        "`time_to_recovery_ms_mean` is from MAESTRO metrics on the evaluated regime.",
        "",
        "| Arm | time_to_recovery_ms_mean | ponr_violation_count_total | "
        "safety_violation_count_total |",
        "|-----|---------------------------|------------------------------|"
        "------------------------------|",
        (
            f"| fixed (Centralized) | {_fmt(fix.get('time_to_recovery_ms_mean'))} | "
            f"{_fmt(fix.get('ponr_violation_count_total'))} | "
            f"{_fmt(fix.get('safety_violation_count_total'))} |"
        ),
        (
            f"| meta_controller | {_fmt(meta.get('time_to_recovery_ms_mean'))} | "
            f"{_fmt(meta.get('ponr_violation_count_total'))} | "
            f"{_fmt(meta.get('safety_violation_count_total'))} |"
        ),
        "",
    ]
    return lines


def interpretation_lines(data: dict) -> list[str]:
    """Camera-ready semantics: strict vs non-inferior collapse (ties allowed)."""
    cpa = data.get("collapse_paired_analysis")
    if not cpa:
        return []
    lines = [
        "## Collapse outcome interpretation (paired seeds)",
        "",
        f"- **Non-inferior on counts (meta <= fixed):** `meta_non_worse_collapse` = "
        f"{data.get('meta_non_worse_collapse', data.get('meta_reduces_collapse'))}",
        f"- **Strict improvement (meta < fixed):** `meta_strictly_reduces_collapse` = "
        f"{data.get('meta_strictly_reduces_collapse', 'n/a')}",
        f"- **McNemar (discordant pairs only) p (two-sided):** "
        f"{cpa.get('mcnemar_exact_p_value_two_sided', 'n/a')}",
        f"- **Wilson 95% CI - fixed collapse rate:** {cpa.get('fixed_collapse_rate_wilson_ci95', 'n/a')}",
        f"- **Wilson 95% CI - meta collapse rate:** {cpa.get('meta_collapse_rate_wilson_ci95', 'n/a')}",
        "",
    ]
    rm = data.get("run_manifest") or {}
    pol = rm.get("stress_selection_policy")
    if pol:
        lines.append("## Stress selection (non-vacuous runs)")
        lines.append("")
        lines.append(f"- **rule_id:** `{pol.get('rule_id', '')}`")
        lines.append(f"- **chosen_drop_completion_prob:** {pol.get('chosen_drop_completion_prob', 'n/a')}")
        src = pol.get("source_path_repo_relative") or pol.get("source_path")
        if src:
            lines.append(f"- **source:** `{src}`")
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


def campaign_table(campaign: dict) -> list[str]:
    """Produce markdown for robustness campaign matrix summary."""
    runs = campaign.get("runs") or []
    if not runs:
        return []
    lines = [
        "# Table 3 - Robustness campaign matrix (C1-C3)",
        "",
        "Source: robustness campaign summary JSON (multi-scenario stress matrix).",
        "",
        "| run_id | scenario_id | profile | drop_completion_prob | fixed_collapse_count | meta_collapse_count | non_worse | strict | no_safety_regression | switch_total | switch_reasons |",
        "|--------|-------------|---------|----------------------|----------------------|---------------------|-----------|--------|----------------------|--------------|----------------|",
    ]
    for row in runs:
        reasons = row.get("switch_reasons") or {}
        reasons_txt = ", ".join(f"{k}:{v}" for k, v in sorted(reasons.items())) if reasons else "-"
        lines.append(
            "| "
            f"{row.get('run_id', '-')} | "
            f"{row.get('scenario_id', '-')} | "
            f"{row.get('profile', '-')} | "
            f"{_fmt(row.get('drop_completion_prob'))} | "
            f"{_fmt(row.get('fixed_collapse_count'))} | "
            f"{_fmt(row.get('meta_collapse_count'))} | "
            f"{_fmt(row.get('meta_non_worse_collapse'))} | "
            f"{_fmt(row.get('meta_strictly_reduces_collapse'))} | "
            f"{_fmt(row.get('no_safety_regression'))} | "
            f"{_fmt(row.get('regime_switch_count_total'))} | "
            f"{reasons_txt} |"
        )
    lines.append("")
    claim_support = campaign.get("claim_support") or {}
    if claim_support:
        lines.append("## Campaign claim-support summary")
        lines.append("")
        for claim_id in ("C1", "C2", "C3"):
            payload = claim_support.get(claim_id)
            if payload is not None:
                lines.append(f"- **{claim_id}:** `{payload}`")
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
    ap.add_argument(
        "--campaign",
        type=Path,
        default=None,
        help="Optional robustness campaign summary JSON; print Table 3 matrix",
    )
    args = ap.parse_args()
    path = args.comparison or args.comparison_path or DEFAULT_COMPARISON
    if not path.is_file():
        print(f"File not found: {path}", file=sys.stderr)
        return 1
    data = json.loads(path.read_text(encoding="utf-8"))
    for line in table1(data):
        print(line)
    for line in recovery_safety_lines(data):
        print(line)
    for line in interpretation_lines(data):
        print(line)
    if args.table2:
        for line in table2(data):
            print(line)
    if args.campaign is not None:
        if not args.campaign.is_file():
            print(f"File not found: {args.campaign}", file=sys.stderr)
            return 1
        campaign_data = json.loads(args.campaign.read_text(encoding="utf-8"))
        for line in campaign_table(campaign_data):
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
