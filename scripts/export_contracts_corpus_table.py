#!/usr/bin/env python3
"""
Export P1 corpus table: detection_ok + timestamp-only baseline misses.
Reads datasets/runs/contracts_eval/eval.json. Usage:
  python scripts/export_contracts_corpus_table.py [--eval path]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_EVAL = REPO / "datasets" / "runs" / "contracts_eval" / "eval.json"


def main() -> int:
    ap = argparse.ArgumentParser(description="Export P1 corpus table (detection_ok + baseline)")
    ap.add_argument("--eval", type=Path, default=DEFAULT_EVAL, help="Path to eval.json")
    args = ap.parse_args()
    if not args.eval.exists():
        print(f"Error: {args.eval} not found. Run contracts_eval.py first.")
        return 1
    data = json.loads(args.eval.read_text(encoding="utf-8"))
    sequences = data.get("sequences", [])
    ts_missed = data.get("baseline_timestamp_only_missed", 0)
    ts_denials = data.get("baseline_timestamp_only_denials", 0)
    lines = [
        "# Table 1 — Corpus evaluation. Per-sequence detection_ok and denials; run_manifest in eval.json.",
        "",
        "| Sequence | detection_ok | denials (contract) |",
        "|----------|---------------|-------------------|",
    ]
    for s in sequences:
        seq = s.get("sequence", "")
        ok = "yes" if s.get("detection_ok") else "no"
        denials = s.get("denials", 0)
        lines.append(f"| {seq} | {ok} | {denials} |")
    lines.append("")
    lines.append(f"**Timestamp-only baseline:** denials with timestamp-only policy: {ts_denials}. Violations the contract catches but timestamp-only would allow (missed): {ts_missed}. Run contracts_eval.py with --baseline to populate.")
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
