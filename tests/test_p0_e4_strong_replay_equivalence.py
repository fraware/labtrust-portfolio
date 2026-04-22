"""Strong replay must be strictly stronger than two-counter weak replay."""

from __future__ import annotations

from labtrust_portfolio.p0_e4_matrix import strong_replay_equivalent, weak_replay_match


def test_strong_false_when_metrics_differ() -> None:
    trace = {"scenario_id": "toy_lab_v0", "events": []}
    stored = {
        "run_outcome": "success_safe",
        "metrics": {
            "tasks_completed": 4,
            "coordination_messages": 1,
            "task_latency_ms_p95": 100.0,
        },
        "safety": {"safety_violation_count": 0, "safety_violation_types": []},
        "coordination_efficiency": {},
        "faults": {"fault_injected": False, "fault_events": [], "recovery_ok": True},
    }
    recomputed = {**stored, "metrics": {**stored["metrics"], "task_latency_ms_p95": 12.3}}
    assert weak_replay_match(recomputed, stored) is True
    assert strong_replay_equivalent(recomputed, stored, trace) is False


def test_strong_requires_ponr_witnesses_when_declared() -> None:
    trace = {
        "scenario_id": "lab_profile_v0",
        "events": [
            {"type": "task_end", "payload": {"name": "receive_sample"}},
        ],
    }
    base = {
        "run_outcome": "partial_safe",
        "metrics": {"tasks_completed": 1, "coordination_messages": 0},
        "safety": {"safety_violation_count": 0, "safety_violation_types": []},
        "coordination_efficiency": {},
        "faults": {"fault_injected": False, "fault_events": [], "recovery_ok": True},
    }
    assert strong_replay_equivalent(base, base, trace) is False
