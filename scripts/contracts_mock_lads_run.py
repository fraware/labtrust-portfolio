#!/usr/bin/env python3
"""
P1 Contracts: run the same validator on a LADS-derived event stream (mock).
Reads a JSON file that mimics LADS transition events (task_start/task_end with ts, actor, payload);
runs validate() and apply_event_to_state; writes result to datasets/runs/contracts_lads_demo/.
Usage: PYTHONPATH=impl/src python scripts/contracts_mock_lads_run.py [--events path] [--out dir]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "impl" / "src"))
if "LABTRUST_KERNEL_DIR" not in os.environ:
    os.environ["LABTRUST_KERNEL_DIR"] = str(REPO / "kernel")

# Default LADS-equivalent event stream (same shape as contract corpus)
DEFAULT_EVENTS = [
    {"type": "task_start", "ts": 1.0, "actor": {"id": "controller_1"}, "payload": {"task_id": "t1", "name": "run", "writer": "controller_1"}},
    {"type": "task_end", "ts": 2.0, "actor": {"id": "controller_1"}, "payload": {"task_id": "t1", "name": "run", "writer": "controller_1"}},
]


def main() -> int:
    ap = argparse.ArgumentParser(description="P1: Run contract validator on mock LADS event stream")
    ap.add_argument(
        "--events",
        type=Path,
        default=None,
        help="JSON file with events array (LADS-equivalent); default: inline stream",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=REPO / "datasets" / "runs" / "contracts_lads_demo",
        help="Output directory for result JSON",
    )
    args = ap.parse_args()
    if args.events and args.events.exists():
        events = json.loads(args.events.read_text(encoding="utf-8"))
        if isinstance(events, dict) and "events" in events:
            events = events["events"]
    else:
        events = DEFAULT_EVENTS

    from labtrust_portfolio.contracts import validate, apply_event_to_state

    state = {"ownership": {}, "_last_ts": {}}
    results = []
    for i, ev in enumerate(events):
        v = validate(state, ev)
        results.append({
            "seq": i,
            "type": ev.get("type"),
            "verdict": v.verdict,
            "reason_codes": v.reason_codes,
        })
        if v.verdict == "allow":
            state = apply_event_to_state(state, ev)

    out_dir = args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    artifact = {
        "lads_mock_run": True,
        "event_count": len(events),
        "verdicts": results,
        "all_allowed": all(r["verdict"] == "allow" for r in results),
        "run_manifest": {"script": "contracts_mock_lads_run.py", "source": "mock LADS-equivalent event stream"},
    }
    out_path = out_dir / "lads_demo_result.json"
    out_path.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(artifact, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
