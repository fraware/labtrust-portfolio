#!/usr/bin/env python3
"""
Generate a minimal real-trace example (real_bucket_example) for P3 corpus.
This is a template/example demonstrating the structure for real-ingest traces.
"""
import json
from pathlib import Path

from labtrust_portfolio.replay import apply_event
from labtrust_portfolio.trace import state_hash

CORPUS = Path(__file__).parent.parent / "bench" / "replay" / "corpus"


def main() -> int:
    CORPUS.mkdir(parents=True, exist_ok=True)

    # Minimal real-trace example: 3 events, all consistent
    events = []
    state = {}

    # Event 0: coordination message
    ev0 = {
        "seq": 0,
        "ts": 0.1,
        "type": "coordination_message",
        "actor": {"kind": "system", "id": "scheduler"},
        "payload": {"detail": "assign_task", "task_id": "task_0"},
    }
    state = apply_event(state, ev0)
    ev0["state_hash_after"] = state_hash(state)
    events.append(ev0)

    # Event 1: task_start
    ev1 = {
        "seq": 1,
        "ts": 0.2,
        "type": "task_start",
        "actor": {"kind": "agent", "id": "agent_1"},
        "payload": {"task_id": "task_0", "name": "task_0"},
    }
    state = apply_event(state, ev1)
    ev1["state_hash_after"] = state_hash(state)
    events.append(ev1)

    # Event 2: task_end
    ev2 = {
        "seq": 2,
        "ts": 0.3,
        "type": "task_end",
        "actor": {"kind": "agent", "id": "agent_1"},
        "payload": {"task_id": "task_0", "name": "task_0"},
    }
    state = apply_event(state, ev2)
    ev2["state_hash_after"] = state_hash(state)
    events.append(ev2)

    final_hash = state_hash(state)

    trace = {
        "version": "0.1",
        "run_id": "real_bucket_example_v0",
        "scenario_id": "real_platform_example",
        "seed": 999,
        "start_time_utc": "2026-03-19T12:00:00.000000Z",
        "events": events,
        "final_state_hash": final_hash,
    }

    trace_path = CORPUS / "real_bucket_example_trace.json"
    trace_path.write_text(json.dumps(trace, indent=2) + "\n", encoding="utf-8")

    expected_path = CORPUS / "real_bucket_example_expected.json"
    expected_path.write_text(
        json.dumps(
            {
                "description": (
                    "Example real-ingest trace (template). "
                    "For actual production traces, replace with redacted partner export "
                    "or production log mapped to TRACE schema. "
                    "This example demonstrates consistent replay (all events match)."
                ),
                "expected_replay_ok": True,
                "expected_divergence_at_seq": None,
                "corpus_category": "real_ingest",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Created {trace_path}")
    print(f"Created {expected_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
