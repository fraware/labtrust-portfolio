#!/usr/bin/env python3
"""
Generate P1 contract corpus JSON(s) from parameters (e.g. N-writer contention).
Output: one or more JSON files under bench/contracts/corpus/ or --out.
Usage:
  PYTHONPATH=impl/src python scripts/generate_contract_corpus.py --writers 3 --tasks 1 --out bench/contracts/corpus/gen_3writer_1task.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def generate_n_writer_contention(num_writers: int, num_tasks: int = 1, seed_ts: float = 1.0) -> dict:
    """
    Generate one corpus sequence: for each task, first writer allow, rest deny (same task_id).
    Events: task_start per (writer, task); expected_verdicts: allow for first writer per task, deny for others.
    """
    events = []
    expected_verdicts = []
    for t in range(num_tasks):
        task_id = f"t{t + 1}"
        for w in range(num_writers):
            writer_id = f"agent_{w + 1}"
            ts = seed_ts + t * 10.0 + w * 1.0
            events.append({
                "type": "task_start",
                "ts": ts,
                "actor": {"id": writer_id},
                "payload": {"task_id": task_id, "name": f"task_{task_id}", "writer": writer_id},
            })
            expected_verdicts.append("allow" if w == 0 else "deny")
    return {
        "description": f"Generated: {num_writers} writers, {num_tasks} task(s); first writer allow, rest deny per task",
        "initial_state": {"ownership": {}, "_last_ts": {}},
        "events": events,
        "expected_verdicts": expected_verdicts,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate P1 contract corpus JSON from parameters")
    ap.add_argument("--writers", type=int, default=2, help="Number of writers (contention per task)")
    ap.add_argument("--tasks", type=int, default=1, help="Number of tasks")
    ap.add_argument("--out", type=Path, help="Output JSON path (default: bench/contracts/corpus/gen_Wwriter_Ttask.json)")
    ap.add_argument("--seed-ts", type=float, default=1.0, help="Base timestamp for first event")
    args = ap.parse_args()
    data = generate_n_writer_contention(args.writers, args.tasks, args.seed_ts)
    if args.out is None:
        args.out = REPO / "bench" / "contracts" / "corpus" / f"gen_{args.writers}writer_{args.tasks}task.json"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
