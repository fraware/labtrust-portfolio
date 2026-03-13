#!/usr/bin/env python3
"""
Export P3 Replay corpus table: one row per trace from replay_eval summary.json.
Output: markdown table with trace name, expected_replay_ok, expected_divergence_at_seq,
observed replay_ok, observed divergence_at_seq. Regenerate with this script.
Usage: python scripts/export_replay_corpus_table.py [--summary path/to/summary.json]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_SUMMARY = REPO / "datasets" / "runs" / "replay_eval" / "summary.json"


def _fmt(x) -> str:
    if x is None:
        return "—"
    if isinstance(x, bool):
        return "true" if x else "false"
    return str(x)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Export P3 Replay corpus table from summary.json"
    )
    ap.add_argument(
        "--summary",
        type=Path,
        default=DEFAULT_SUMMARY,
        help="Path to replay_eval summary.json",
    )
    ap.add_argument(
        "--include-thin-slice",
        action="store_true",
        default=True,
        help="Include thin_slice row (default True)",
    )
    ap.add_argument(
        "--no-include-thin-slice",
        action="store_false",
        dest="include_thin_slice",
        help="Exclude thin_slice from table",
    )
    args = ap.parse_args()
    if not args.summary.exists():
        print("Run scripts/replay_eval.py first to produce summary.json.")
        return 1
    data = json.loads(args.summary.read_text(encoding="utf-8"))
    per_trace = data.get("per_trace", [])
    if not per_trace:
        print("No per_trace in summary.")
        return 1
    rows = [
        r for r in per_trace
        if args.include_thin_slice or r.get("name") != "thin_slice"
    ]
    n = len(rows)
    lines = [
        "# Table 1 — Corpus and fidelity",
        "",
        f"All corpus traces (from summary.json); N = {n}. Regenerate with export_replay_corpus_table.py.",
        "",
        "| Trace | expected_replay_ok | expected_divergence_at_seq | observed_replay_ok | observed_divergence_at_seq |",
        "|-------|--------------------|----------------------------|---------------------|----------------------------|",
    ]
    for r in rows:
        lines.append(
            f"| {r.get('name', '')} | {_fmt(r.get('expected_replay_ok'))} | "
            f"{_fmt(r.get('expected_divergence_at_seq'))} | "
            f"{_fmt(r.get('replay_ok'))} | {_fmt(r.get('divergence_at_seq'))} |"
        )
    lines.append("")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
