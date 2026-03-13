#!/usr/bin/env python3
"""
Export P6 LLM red-team and confusable deputy results as markdown tables.
Reads red_team_results.json and confusable_deputy_results.json; outputs
Table 1 (red-team, all 8 cases) and Table 2 (confusable deputy, all 4 cases).
Usage: python scripts/export_llm_redteam_table.py [--out-dir datasets/runs/llm_eval]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO / "datasets" / "runs" / "llm_eval"


def _fmt(x) -> str:
    if x is None:
        return "—"
    if isinstance(x, bool):
        return "yes" if x else "no"
    return str(x)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Export P6 red-team and confusable deputy tables"
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT,
        help="Directory containing red_team_results.json and confusable_deputy_results.json",
    )
    args = ap.parse_args()
    red_path = args.out_dir / "red_team_results.json"
    conf_path = args.out_dir / "confusable_deputy_results.json"
    if not red_path.exists():
        print("Run scripts/llm_redteam_eval.py first to produce red_team_results.json.")
        return 1
    red = json.loads(red_path.read_text(encoding="utf-8"))
    cases = red.get("cases", [])
    lines = [
        "# Table 1 — Red-team (full 8 cases)",
        "",
        "Validator v0.2: allow_list + safe_args (path traversal, dangerous patterns). Regenerate with export_llm_redteam_table.py.",
        "",
        "| Case ID | expected_block | actually_blocked | pass |",
        "|---------|----------------|------------------|------|",
    ]
    for c in cases:
        lines.append(
            f"| {c.get('id', '')} | {_fmt(c.get('expected_block'))} | "
            f"{_fmt(c.get('actually_blocked'))} | {_fmt(c.get('pass'))} |"
        )
    lines.append("")
    # Table 1b — Real-LLM (when run with --real-llm)
    real_llm = red.get("real_llm", {})
    if real_llm and real_llm.get("real_llm_used"):
        run_manifest = red.get("run_manifest", {})
        model_id = run_manifest.get("real_llm_model_id") or real_llm.get("model_id", "—")
        lines.extend([
            "# Table 1b — Real-LLM (optional; run with --real-llm and .env keys)",
            "",
            "| Model | all_block_unsafe_pass | latency_ms |",
            "|-------|------------------------|------------|",
            f"| {model_id} | {_fmt(real_llm.get('all_block_unsafe_pass'))} | {_fmt(real_llm.get('latency_ms'))} |",
            "",
        ])
    elif real_llm and real_llm.get("error"):
        lines.extend([
            "# Table 1b — Real-LLM",
            "",
            "Error (e.g. missing .env keys): " + str(real_llm.get("error", "")),
            "",
        ])
    # Jailbreak-style cases (when present)
    jb = red.get("jailbreak_style", {})
    if jb and jb.get("cases"):
        lines.extend([
            "# Table — Jailbreak-style cases",
            "",
            "Containment, not elimination. Validator blocks steps whose args contain jailbreak-style phrases (ignore previous instructions, disregard instruction).",
            "",
            "| Case ID | expected_block | actually_blocked | pass |",
            "|---------|----------------|------------------|------|",
        ])
        for c in jb["cases"]:
            lines.append(
                f"| {c.get('id', '')} | {_fmt(c.get('expected_block'))} | "
                f"{_fmt(c.get('actually_blocked'))} | {_fmt(c.get('pass'))} |"
            )
        lines.append("")
    if conf_path.exists():
        conf = json.loads(conf_path.read_text(encoding="utf-8"))
        cd_cases = conf.get("confusable_deputy_cases", [])
        lines.extend([
            "# Table 2 — Confusable deputy (full 4 cases)",
            "",
            "| Case ID | expected_block | actually_blocked | pass |",
            "|---------|----------------|------------------|------|",
        ])
        for c in cd_cases:
            lines.append(
                f"| {c.get('id', '')} | {_fmt(c.get('expected_block'))} | "
                f"{_fmt(c.get('actually_blocked'))} | {_fmt(c.get('pass'))} |"
            )
        lines.append("")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
