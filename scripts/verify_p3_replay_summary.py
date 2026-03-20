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
