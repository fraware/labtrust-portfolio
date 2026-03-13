#!/usr/bin/env python3
"""
Export contracts eval as a markdown table for the draft. Reads
datasets/runs/contracts_eval/eval.json and prints Table 1 (per-sequence + summary).
Usage (from repo root):
  python scripts/export_contracts_table.py
  python scripts/export_contracts_table.py --eval path/to/eval.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_EVAL = REPO / "datasets" / "runs" / "contracts_eval" / "eval.json"


def main() -> int:
    ap = argparse.ArgumentParser(description="Export contracts eval as markdown table")
    ap.add_argument(
        "--eval",
        type=Path,
        default=DEFAULT_EVAL,
        help="Path to eval.json",
    )
    args = ap.parse_args()
    if not args.eval.exists():
        print(f"Error: {args.eval} not found. Run contracts_eval.py first.")
        return 1
    data = json.loads(args.eval.read_text(encoding="utf-8"))
    sequences = data.get("sequences", [])
    if not sequences:
        print("Error: no sequences in eval.")
        return 1

    lines = [
        "| Sequence | events | allows | denials | detection_ok | time_per_write_us |",
        "|----------|--------|--------|---------|--------------|-------------------|",
    ]
    total_events = 0
    total_allows = 0
    total_denials = 0
    times: list[float] = []
    for s in sequences:
        seq = s.get("sequence", "")
        ev = s.get("events", 0)
        al = s.get("allows", 0)
        de = s.get("denials", 0)
        ok = s.get("detection_ok", False)
        tpw = s.get("time_per_write_us", 0)
        total_events += ev
        total_allows += al
        total_denials += de
        if ev:
            times.append(tpw)
        lines.append(f"| {seq} | {ev} | {al} | {de} | {ok} | {tpw} |")
    mean_t = sum(times) / len(times) if times else 0
    all_ok = all(s.get("detection_ok", False) for s in sequences)
    lines.append(f"| **Summary** | {total_events} | {total_allows} | {total_denials} | {'all true' if all_ok else 'false'} | mean ~{mean_t:.0f} |")
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
