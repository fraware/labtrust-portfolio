#!/usr/bin/env python3
"""
Print a one-line excellence metrics summary across papers (STANDARDS_OF_EXCELLENCE.md).
Reads summary JSONs from datasets/runs/ and prints excellence_metrics when present.
Usage (from repo root):
  python scripts/export_excellence_summary.py
  python scripts/export_excellence_summary.py --json  # output machine-readable JSON
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUNS = REPO / "datasets" / "runs"

# Paper ID -> (label, list of paths to check for excellence_metrics)
PAPER_PATHS = [
    ("P0", "e3_summary.json"),
    ("P1", "contracts_eval/eval.json"),
    ("P2", "rep_cps_eval/summary.json"),
    ("P3", "replay_eval/summary.json"),
    ("P4a", "maestro_fault_sweep/multi_sweep.json"),
    ("P4b", "maestro_antigaming/antigaming_results.json"),
    ("P5", "scaling_eval/heldout_results.json"),
    ("P6a", "llm_eval/red_team_results.json"),
    ("P6b", "llm_eval/adapter_latency.json"),
    ("P7", "assurance_eval/results.json"),
    ("P8", "meta_eval/comparison.json"),
]


def main() -> int:
    ap = argparse.ArgumentParser(description="Export excellence metrics summary across papers")
    ap.add_argument("--json", action="store_true", help="Output as JSON")
    args = ap.parse_args()

    out = {}
    for paper_id, rel_path in PAPER_PATHS:
        path = RUNS / rel_path
        if not path.exists():
            if not args.json:
                print(f"{paper_id}: (missing {rel_path})")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            if not args.json:
                print(f"{paper_id}: (read error {rel_path})")
            continue
        metrics = data.get("excellence_metrics", {})
        if not metrics and not args.json:
            print(f"{paper_id}: (no excellence_metrics)")
            continue
        out[paper_id] = metrics
        if not args.json:
            parts = [f"{k}={v}" for k, v in sorted(metrics.items()) if v is not None]
            print(f"{paper_id}: {'; '.join(parts)}")
    if args.json:
        print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
