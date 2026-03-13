#!/usr/bin/env python3
"""
P5 Scaling: build modeling table from MAESTRO runs (e.g. fault sweep output).
Writes datasets/runs/scaling_dataset/modeling_table.json. Usage:
  PYTHONPATH=impl/src python scripts/scaling_build_dataset.py [--runs-dir DIR] [--out FILE]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "impl" / "src"))

from labtrust_portfolio.scaling import build_dataset_from_runs


def main() -> int:
    ap = argparse.ArgumentParser(description="P5: Build scaling dataset from MAESTRO runs")
    ap.add_argument(
        "--runs-dir",
        type=Path,
        default=REPO / "datasets" / "runs" / "maestro_fault_sweep",
        help="Directory containing run subdirs with trace.json and maestro_report.json",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=REPO / "datasets" / "runs" / "scaling_dataset" / "modeling_table.json",
        help="Output JSON path",
    )
    args = ap.parse_args()
    if not args.runs_dir.exists():
        print(f"Runs dir not found: {args.runs_dir}")
        return 1
    rows = build_dataset_from_runs(args.runs_dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"rows": rows, "n": len(rows)}, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} rows to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
