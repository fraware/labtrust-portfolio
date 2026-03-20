#!/usr/bin/env python3
"""
Export P6 cross-model heatmap: per-case pass rate by model and pairwise disagreement matrix.
Reads red_team_results.json; when cross_model_summary is present, outputs markdown tables.
Usage: python scripts/export_p6_cross_model_heatmap.py [--out-dir path] [--out file.md]
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
        description="Export P6 cross-model per-case heatmap and disagreement matrix"
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
        print("Run llm_redteam_eval.py with --real-llm-models first.", file=sys.stderr)
        return 1

    red = json.loads(red_path.read_text(encoding="utf-8"))
    cross = red.get("cross_model_summary")
    if not cross:
        print("No cross_model_summary (need 2+ real-LLM models).", file=sys.stderr)
        return 0

    model_ids = cross.get("model_ids", [])
    per_case = cross.get("per_case_pass_rates", {})
    per_case_var = cross.get("per_case_variance", {})
    disp = cross.get("disagreement_matrix", [])

    lines = [
        "# Cross-model: per-case pass rate (heatmap)",
        "",
        "Pass rate % by case and model. Variance = variance of pass rate across models for that case.",
        "",
    ]
    header = "| Case ID | " + " | ".join(model_ids) + " | variance |"
    sep = "|" + "|".join(["--------"] + ["-------"] * len(model_ids) + ["--------|"])
    lines.append(header)
    lines.append(sep)
    for cid in sorted(per_case.keys()):
        row = per_case[cid]
        vals = [str(row.get(m, "-")) for m in model_ids]
        var_str = str(per_case_var.get(cid, "-"))
        lines.append("| " + cid + " | " + " | ".join(vals) + " | " + var_str + " |")
    lines.extend(["", "# Cross-model: pairwise disagreement matrix", ""])
    lines.append("Count of cases where one model passed (>=50% runs) and the other failed.")
    lines.append("")
    lines.append("|  | " + " | ".join(model_ids) + " |")
    lines.append("|---" + "|".join(["---"] * (len(model_ids) + 1)) + "|")
    for i, mid in enumerate(model_ids):
        row_vals = [str(disp[i][j]) if i < len(disp) and j < len(disp[i]) else "-" for j in range(len(model_ids))]
        lines.append("| " + mid + " | " + " | ".join(row_vals) + " |")
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
