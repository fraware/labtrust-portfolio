#!/usr/bin/env python3
"""
Export P6 validator-layer attribution: per-case attribution and denial_by_layer summary.
Reads red_team_results.json, confusable_deputy_results.json, jailbreak from red_team;
outputs markdown table (stacked bar data) for appendix.
Usage: python scripts/export_p6_layer_attribution.py [--out-dir path] [--out file.md]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO / "datasets" / "runs" / "llm_eval"


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Export P6 layer attribution table (denial by allow_list / safe_args / both)"
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help="Directory containing red_team_results.json",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Write markdown to this file (default: stdout)",
    )
    args = ap.parse_args()

    red_path = args.out_dir / "red_team_results.json"
    if not red_path.exists():
        print("Run llm_redteam_eval.py first.", file=sys.stderr)
        return 1

    red = json.loads(red_path.read_text(encoding="utf-8"))
    lines = [
        "# Validator-layer attribution",
        "",
        "Per-case attribution: which layer(s) caused denial (allow_list_only, safe_args_only, both, admitted).",
        "",
        "## Red-team cases (Table 1)",
        "",
        "| Case ID | expected_block | actually_blocked | attribution |",
        "|---------|----------------|------------------|-------------|",
    ]
    for c in red.get("cases", []):
        lines.append(
            f"| {c.get('id', '')} | {c.get('expected_block', '')} | "
            f"{c.get('actually_blocked', '')} | {c.get('attribution', '')} |"
        )
    dbl = red.get("denial_by_layer", {})
    lines.extend([
        "",
        "**Denial by layer (red-team):** " + ", ".join(f"{k}: {dbl.get(k, 0)}" for k in ["allow_list_only", "safe_args_only", "both", "admitted"]) + ".",
        "",
        "## Confusable deputy (Table 1)",
        "",
    ])
    conf_path = args.out_dir / "confusable_deputy_results.json"
    if conf_path.exists():
        conf = json.loads(conf_path.read_text(encoding="utf-8"))
        lines.extend([
            "| Case ID | expected_block | actually_blocked | attribution |",
            "|---------|----------------|------------------|-------------|",
        ])
        for c in conf.get("confusable_deputy_cases", []):
            lines.append(
                f"| {c.get('id', '')} | {c.get('expected_block', '')} | "
                f"{c.get('actually_blocked', '')} | {c.get('attribution', '')} |"
            )
        dbl_c = conf.get("denial_by_layer", {})
        lines.append("")
        lines.append("**Denial by layer (confusable deputy):** " + ", ".join(f"{k}: {dbl_c.get(k, 0)}" for k in ["allow_list_only", "safe_args_only", "both", "admitted"]) + ".")
        lines.append("")
    jb = red.get("jailbreak_style", {})
    if jb.get("cases"):
        lines.extend([
            "## Jailbreak-style cases",
            "",
            "| Case ID | expected_block | actually_blocked | attribution |",
            "|---------|----------------|------------------|-------------|",
        ])
        for c in jb["cases"]:
            lines.append(
                f"| {c.get('id', '')} | {c.get('expected_block', '')} | "
                f"{c.get('actually_blocked', '')} | {c.get('attribution', '')} |"
            )
        dbl_j = jb.get("denial_by_layer", {})
        lines.append("")
        lines.append("**Denial by layer (jailbreak):** " + ", ".join(f"{k}: {dbl_j.get(k, 0)}" for k in ["allow_list_only", "safe_args_only", "both", "admitted"]) + ".")
    lines.append("")
    text = "\n".join(lines)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
