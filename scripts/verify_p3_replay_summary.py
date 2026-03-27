#!/usr/bin/env python3
"""
Validate P3 replay_eval summary.json schema and optional consistency with figure sidecar.
Exit 0 if checks pass. Usage:
  python scripts/verify_p3_replay_summary.py [--summary path] [--figure-json path]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_SUMMARY = REPO / "datasets" / "runs" / "replay_eval" / "summary.json"
DEFAULT_FIG = REPO / "docs" / "figures" / "p3_replay_overhead.json"

REQUIRED_TOP = (
    "replay_eval",
    "schema_version",
    "run_manifest",
    "overhead_stats",
    "success_criteria_met",
    "excellence_metrics",
    "corpus_space_summary",
    "per_trace",
)
REQUIRED_OVERHEAD = (
    "n_replays",
    "mean_ms",
    "p95_ms",
    "p99_ms",
    "percentile_method",
)


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify P3 replay_eval summary JSON")
    ap.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    ap.add_argument("--figure-json", type=Path, default=DEFAULT_FIG)
    ap.add_argument(
        "--strict-curve",
        action="store_true",
        help="Require overhead_curve non-empty (use after --overhead-curve run)",
    )
    args = ap.parse_args()
    if not args.summary.exists():
        print(f"Missing {args.summary}", file=sys.stderr)
        return 1
    data = json.loads(args.summary.read_text(encoding="utf-8"))
    for k in REQUIRED_TOP:
        if k not in data:
            print(f"Missing top-level key: {k}", file=sys.stderr)
            return 1
    if data.get("schema_version") != "p3_replay_eval_v0.2":
        print("Unexpected schema_version (expected p3_replay_eval_v0.2)", file=sys.stderr)
        return 1
    css = data.get("corpus_space_summary") or {}
    if not isinstance(css, dict) or not css.get("corpus_traces_n", 0) >= 1:
        print(
            "corpus_space_summary.corpus_traces_n must be >= 1",
            file=sys.stderr,
        )
        return 1
    pt0 = next((r for r in (data.get("per_trace") or []) if r.get("name") != "thin_slice"), None)
    if pt0 is not None:
        for k in ("trace_json_bytes", "state_hash_after_count", "corpus_category"):
            if k not in pt0:
                print(f"per_trace corpus row missing {k}", file=sys.stderr)
                return 1
    # If L1 twin was run, check for l1_twin_summary
    if data.get("l1_twin_ok") is not None:
        l1_summary = data.get("l1_twin_summary")
        if l1_summary is None:
            print("l1_twin_ok present but l1_twin_summary missing", file=sys.stderr)
            return 1
        if not isinstance(l1_summary, dict):
            print("l1_twin_summary must be a dict", file=sys.stderr)
            return 1
        if "n_seeds" not in l1_summary or "all_pass" not in l1_summary:
            print("l1_twin_summary missing required keys (n_seeds, all_pass)", file=sys.stderr)
            return 1
    oh = data.get("overhead_stats") or {}
    for k in REQUIRED_OVERHEAD:
        if k not in oh:
            print(f"Missing overhead_stats.{k}", file=sys.stderr)
            return 1
    scm = data.get("success_criteria_met") or {}
    if not scm.get("fidelity_pass"):
        print("success_criteria_met.fidelity_pass must be true", file=sys.stderr)
        return 1
    if not scm.get("corpus_expected_outcomes_met", True):
        print("corpus_expected_outcomes_met failed", file=sys.stderr)
        return 1
    if args.strict_curve:
        curve = data.get("overhead_curve")
        if not curve:
            print("strict-curve: overhead_curve missing or empty", file=sys.stderr)
            return 1
    if args.figure_json.exists():
        fig = json.loads(args.figure_json.read_text(encoding="utf-8"))
        fc = fig.get("overhead_curve") or []
        sc = data.get("overhead_curve") or []
        if fc and sc and len(fc) != len(sc):
            print(
                "Figure JSON overhead_curve length differs from summary",
                file=sys.stderr,
            )
            return 1
    print("verify_p3_replay_summary: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
