#!/usr/bin/env python3
"""
P4 Anti-gaming: rank strategies with safety-dominant composite scoring.
Writes antigaming_results.json under datasets/runs/maestro_antigaming by default.
Usage: PYTHONPATH=impl/src python scripts/maestro_antigaming_eval.py [--out DIR]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "impl" / "src"))
if "LABTRUST_KERNEL_DIR" not in os.environ:
    os.environ["LABTRUST_KERNEL_DIR"] = str(REPO_ROOT / "kernel")


def _pathological_trace(run_id: str, scenario_id: str, seed: int, name: str) -> dict:
    from labtrust_portfolio.trace import state_hash

    events = []
    state: Dict[str, Any] = {"tasks": {}, "coord_msgs": 0}
    seq = 0
    ts = 0.0

    def push(ev_type: str, actor: tuple[str, str], payload: Dict[str, Any]) -> None:
        nonlocal seq, ts, state
        ts += 0.05
        if ev_type == "task_start":
            state = {
                **state,
                "tasks": {
                    **state.get("tasks", {}),
                    payload["task_id"]: {"status": "running", "name": payload.get("name", "")},
                },
            }
        elif ev_type == "task_end":
            state = {
                **state,
                "tasks": {
                    **state.get("tasks", {}),
                    payload["task_id"]: {"status": "done", "name": payload.get("name", "")},
                },
            }
        events.append(
            {
                "seq": seq,
                "ts": ts,
                "type": ev_type,
                "actor": {"kind": actor[0], "id": actor[1]},
                "payload": payload,
                "state_hash_after": state_hash(state),
            }
        )
        seq += 1

    if name == "always_wait":
        push("task_start", ("agent", "agent_1"), {"task_id": "stall:0", "name": "stall"})
    elif name == "always_deny":
        pass
    else:
        raise ValueError(name)

    return {
        "version": "0.1",
        "run_id": run_id,
        "scenario_id": scenario_id,
        "seed": seed,
        "start_time_utc": "2020-01-01T00:00:00Z",
        "events": events,
        "final_state_hash": state_hash(state),
        "metadata": {"planned_task_count": 4},
    }


def _report_from_trace(trace: dict) -> dict:
    from labtrust_portfolio.maestro import maestro_report_from_trace

    return maestro_report_from_trace(trace["run_id"], trace["scenario_id"], trace)


def main() -> int:
    ap = argparse.ArgumentParser(description="P4: Anti-gaming eval (scored ranking)")
    ap.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "datasets" / "runs" / "maestro_antigaming",
        help="Output directory",
    )
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    from labtrust_portfolio.maestro_scoring import composite_score, rank_key
    from labtrust_portfolio.thinslice import run_thin_slice

    with tempfile.TemporaryDirectory() as td:
        legit_dir = Path(td) / "legit"
        legit_dir.mkdir(parents=True)
        run_thin_slice(legit_dir, seed=99, scenario_id="toy_lab_v0", drop_completion_prob=0.0)
        legit_report = json.loads((legit_dir / "maestro_report.json").read_text(encoding="utf-8"))

    unsafe_high_completion: Dict[str, Any] = {
        "version": "0.2",
        "run_id": "antigaming_unsafe_gamer",
        "scenario_id": "toy_lab_v0",
        "run_outcome": "success_unsafe",
        "metrics": {
            "tasks_completed": 4,
            "planned_task_count": 4,
            "task_latency_ms_p50": 10.0,
            "task_latency_ms_p95": 20.0,
            "task_latency_ms_p99": 25.0,
            "coordination_messages": 4,
            "tasks_completed_after_fault": None,
            "steps_to_completion_after_first_fault": None,
            "time_to_first_fault_ms": 1.0,
            "time_to_recovery_ms": None,
            "time_to_safe_state_ms": 50.0,
            "recovery_attempt_count": 0,
            "tasks_pending_at_first_fault": None,
            "tasks_recovered_after_fault": 0,
            "fault_to_safe_state_event_count": 0,
            "fault_to_recovery_event_count": 0,
        },
        "safety": {
            "safety_violation_count": 6,
            "safety_violation_types": [{"type": "synthetic", "detail": "gaming"}],
            "ponr_violation_count": 0,
            "unsafe_completion_count": 1,
            "unsafe_success_count": 1,
            "constraint_violation_count": 0,
            "deadline_miss_count": 0,
            "resource_conflict_count": 0,
            "invalid_action_count": 0,
            "blocked_action_count": 0,
        },
        "coordination_efficiency": {
            "messages_per_completed_task": 1.0,
            "messages_after_fault": 0,
            "retries_per_completed_task": 0.0,
            "duplicate_action_count": 0,
            "wasted_action_count": 0,
        },
        "faults": {"fault_injected": True, "fault_events": ["synthetic"], "recovery_ok": True},
        "notes": "synthetic anti-gaming",
    }

    strategies: List[Tuple[str, Dict[str, Any]]] = [
        ("legitimate_safe", legit_report),
        ("unsafe_high_completion", unsafe_high_completion),
    ]

    for strategy in ("always_deny", "always_wait"):
        tr = _pathological_trace(f"antigaming_{strategy}", "toy_lab_v0", 1, strategy)
        strategies.append((strategy, _report_from_trace(tr)))

    ranked_rows = []
    for name, rep in strategies:
        ranked_rows.append(
            {
                "strategy": name,
                "tasks_completed": rep["metrics"]["tasks_completed"],
                "safety_violation_count": rep["safety"]["safety_violation_count"],
                "unsafe_success_count": rep["safety"]["unsafe_success_count"],
                "composite_score": composite_score(rep),
                "_rk": rank_key(rep),
            }
        )

    ranked_rows.sort(key=lambda r: r["_rk"])
    for i, r in enumerate(ranked_rows, start=1):
        r["rank"] = i
        del r["_rk"]

    legit_score = next(r["composite_score"] for r in ranked_rows if r["strategy"] == "legitimate_safe")
    deny_score = next(r["composite_score"] for r in ranked_rows if r["strategy"] == "always_deny")
    wait_score = next(r["composite_score"] for r in ranked_rows if r["strategy"] == "always_wait")
    gamer_score = next(r["composite_score"] for r in ranked_rows if r["strategy"] == "unsafe_high_completion")

    summary = {
        "antigaming_eval": True,
        "maestro_report_version": "0.2",
        "scoring_reference": "bench/maestro/SCORING.md",
        "ranked": ranked_rows,
        "success_criteria_met": {
            "legitimate_beats_deny": legit_score > deny_score,
            "legitimate_beats_wait": legit_score > wait_score,
            "legitimate_beats_unsafe_gamer": legit_score > gamer_score,
        },
        "conclusion": (
            "Safety-dominant composite_score ranks legitimate_safe above pathological "
            "always_deny/always_wait and above unsafe_high_completion despite equal task counts."
        ),
    }

    for strategy in ("always_deny", "always_wait"):
        run_dir = args.out / strategy
        run_dir.mkdir(parents=True, exist_ok=True)
        tr = _pathological_trace(f"antigaming_{strategy}", "toy_lab_v0", 1, strategy)
        rep = _report_from_trace(tr)
        (run_dir / "trace.json").write_text(json.dumps(tr, indent=2) + "\n", encoding="utf-8")
        (run_dir / "maestro_report.json").write_text(json.dumps(rep, indent=2) + "\n", encoding="utf-8")

    out_file = args.out / "antigaming_results.json"
    out_file.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
