#!/usr/bin/env python3
"""
Export P7 negative-control and ablation summaries to CSV for manuscript / LaTeX.

Reads datasets/runs/assurance_eval/negative_results.json (from run_assurance_negative_eval.py).

Writes under papers/P7_StandardsMapping/:
  p7_negative_family_summary.csv
  p7_ablation_summary.csv
  p7_failure_reason_breakdown.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_JSON = REPO / "datasets" / "runs" / "assurance_eval" / "negative_results.json"
OUT_DIR = REPO / "papers" / "P7_StandardsMapping"


def main() -> int:
    ap = argparse.ArgumentParser(description="Export P7 negative-control CSV tables")
    ap.add_argument("--input", type=Path, default=DEFAULT_JSON)
    ap.add_argument("--out-dir", type=Path, default=OUT_DIR)
    args = ap.parse_args()
    if not args.input.exists():
        print(f"Missing {args.input}; run scripts/run_assurance_negative_eval.py", file=sys.stderr)
        return 1
    data = json.loads(args.input.read_text(encoding="utf-8"))
    rows = data.get("rows") or []
    args.out_dir.mkdir(parents=True, exist_ok=True)

    # Table A: per family (full_review only)
    fam_rows: dict[str, dict] = defaultdict(
        lambda: {"n": 0, "rejected": 0, "loc_ok": 0, "examples": []}
    )
    for r in rows:
        if r.get("review_mode") != "full_review":
            continue
        if r.get("expected_outcome") != "reject":
            continue
        f = r.get("family", "")
        fam_rows[f]["n"] += 1
        if not r.get("review_exit_ok"):
            fam_rows[f]["rejected"] += 1
        if r.get("reason_matches_expected"):
            fam_rows[f]["loc_ok"] += 1
        if len(fam_rows[f]["examples"]) < 3:
            fam_rows[f]["examples"].append(r.get("perturbation_id", ""))

    a_path = args.out_dir / "p7_negative_family_summary.csv"
    with a_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "failure_family",
                "n_negative_cases",
                "reject_rate",
                "localization_accuracy",
                "example_perturbation_ids",
            ]
        )
        for fam, v in sorted(fam_rows.items()):
            n = v["n"]
            rr = v["rejected"] / n if n else 0.0
            la = v["loc_ok"] / n if n else 0.0
            w.writerow([fam, n, round(rr, 4), round(la, 4), ";".join(v["examples"])])

    # Table B: ablation by mode
    b_path = args.out_dir / "p7_ablation_summary.csv"
    by_mode = data.get("by_mode") or {}
    with b_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "review_mode",
                "valid_accept_rate",
                "invalid_reject_rate",
                "false_accept_rate",
                "false_reject_rate",
                "localization_accuracy",
            ]
        )
        for mode in sorted(by_mode.keys()):
            m = by_mode[mode]
            w.writerow(
                [
                    mode,
                    m.get("valid_accept_rate"),
                    m.get("invalid_reject_rate"),
                    m.get("false_accept_rate"),
                    m.get("false_reject_rate"),
                    m.get("localization_accuracy"),
                ]
            )

    # Table C: failure reason counts (full_review, rejected cases)
    c_path = args.out_dir / "p7_failure_reason_breakdown.csv"
    ctr: Counter[str] = Counter()
    for r in rows:
        if r.get("review_mode") != "full_review":
            continue
        if r.get("review_exit_ok"):
            continue
        for code in r.get("failure_reason_codes") or []:
            ctr[code] += 1
    with c_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["failure_reason_code", "count_full_review_rejections"])
        for code, cnt in ctr.most_common():
            w.writerow([code, cnt])

    def _rel(p: Path) -> str:
        try:
            return str(p.relative_to(REPO))
        except ValueError:
            return str(p)

    print(f"Wrote {_rel(a_path)}")
    print(f"Wrote {_rel(b_path)}")
    print(f"Wrote {_rel(c_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
