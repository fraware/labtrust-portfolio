#!/usr/bin/env python3
"""
Standalone verifier: recompute MAESTRO report from trace only.
No dependency on thinslice or adapters; a third party can run this with trace + kernel.
Usage:
  PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/verify_maestro_from_trace.py TRACE.json [OUTPUT.json]
If OUTPUT.json is omitted, prints report to stdout.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "impl" / "src"))
os.environ.setdefault("LABTRUST_KERNEL_DIR", str(REPO / "kernel"))


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: verify_maestro_from_trace.py TRACE.json [OUTPUT.json]", file=sys.stderr)
        return 1
    trace_path = Path(sys.argv[1])
    if not trace_path.exists():
        print(f"Trace file not found: {trace_path}", file=sys.stderr)
        return 1
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    run_id = trace.get("run_id", "unknown")
    scenario_id = trace.get("scenario_id", "toy_lab_v0")

    from labtrust_portfolio.maestro import maestro_report_from_trace

    report = maestro_report_from_trace(run_id, scenario_id, trace)
    if len(sys.argv) > 2:
        out_path = Path(sys.argv[2])
        out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    else:
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
