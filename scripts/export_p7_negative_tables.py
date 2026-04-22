#!/usr/bin/env python3
"""
Export P7 negative-control and ablation summaries to CSV for manuscript / LaTeX.

Reads datasets/runs/assurance_eval/negative_results.json (from run_assurance_negative_eval.py).

Writes under papers/P7_StandardsMapping/:
  p7_negative_family_summary.csv
  p7_ablation_summary.csv
  p7_failure_reason_breakdown.csv
  p7_perturbation_reject_matrix.csv (invalid cases: 1 = reviewer rejects)
  p7_latency_by_mode.csv
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
            uniq_examples = sorted({str(x) for x in v["examples"] if x})
            w.writerow([fam, n, round(rr, 4), round(la, 4), ";".join(uniq_examples)])

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
        mode_rank = {"schema_only": 0, "schema_plus_presence": 1, "full_review": 2}
        for mode in sorted(by_mode.keys(), key=lambda m: mode_rank.get(m, 99)):
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

    # Per-perturbation reject matrix (invalid cases only): 1 = rejected bad evidence
    d_path = args.out_dir / "p7_perturbation_reject_matrix.csv"
    invalid_pids = sorted(
        {str(r["perturbation_id"]) for r in rows if r.get("expected_outcome") == "reject"}
    )
    mode_order = ["schema_only", "schema_plus_presence", "full_review"]
    with d_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "perturbation_id",
                "family",
                "reject_schema_only",
                "reject_schema_plus_presence",
                "reject_full_review",
            ]
        )
        for pid in invalid_pids:
            fam = ""
            by_m: dict[str, bool] = {}
            for r in rows:
                if str(r.get("perturbation_id")) != pid:
                    continue
                fam = str(r.get("family") or "")
                m = str(r.get("review_mode") or "")
                by_m[m] = not bool(r.get("review_exit_ok"))
            w.writerow(
                [
                    pid,
                    fam,
                    int(by_m.get("schema_only", False)),
                    int(by_m.get("schema_plus_presence", False)),
                    int(by_m.get("full_review", False)),
                ]
            )

    # Single-row lift metrics (from aggregate; for captions / LaTeX)
    agg = data.get("aggregate") or {}
    lift_path = args.out_dir / "p7_aggregate_lift_metrics.csv"
    lift_fields = [
        "n_valid",
        "n_invalid",
        "governance_evidence_discrimination_accuracy",
        "invalid_reject_lift_full_minus_schema_only",
        "false_accept_drop_full_vs_schema_only",
        "localization_accuracy_lift_full_minus_schema_only",
        "invalid_reject_lift_full_minus_schema_plus_presence",
    ]
    with lift_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=lift_fields, extrasaction="ignore")
        w.writeheader()
        w.writerow({k: agg.get(k) for k in lift_fields})

    # Latency summary by mode
    lat_path = args.out_dir / "p7_latency_by_mode.csv"
    by_mode = data.get("by_mode") or {}
    with lat_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "review_mode",
                "mean_latency_ms_valid_cases",
                "mean_latency_ms_invalid_cases",
                "median_latency_ms_all_cases",
                "n_valid",
                "n_invalid",
            ]
        )
        for mode in mode_order:
            m = by_mode.get(mode) or {}
            w.writerow(
                [
                    mode,
                    m.get("mean_latency_ms_valid_cases"),
                    m.get("mean_latency_ms_invalid_cases"),
                    m.get("median_latency_ms_all_cases"),
                    m.get("n_valid"),
                    m.get("n_invalid"),
                ]
            )

    def _rel(p: Path) -> str:
        try:
            return str(p.relative_to(REPO))
        except ValueError:
            return str(p)

    print(f"Wrote {_rel(a_path)}")
    print(f"Wrote {_rel(b_path)}")
    print(f"Wrote {_rel(c_path)}")
    print(f"Wrote {_rel(d_path)}")
    print(f"Wrote {_rel(lift_path)}")
    print(f"Wrote {_rel(lat_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
