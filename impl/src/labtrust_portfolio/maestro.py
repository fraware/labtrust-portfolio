from __future__ import annotations

from typing import Any, Dict, List
import math


def percentile(values: List[float], q: float) -> float:
    if not values:
        return 0.0
    vs = sorted(values)
    pos = (len(vs) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return vs[lo]
    return vs[lo] * (hi - pos) + vs[hi] * (pos - lo)


def _fault_label(ev: Dict[str, Any]) -> str:
    pl = ev.get("payload") or {}
    return str(pl.get("fault", "unknown_fault"))


def maestro_report_from_trace(run_id: str, scenario_id: str, trace: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build MAESTRO_REPORT v0.2 from a TRACE v0.1 event stream.
    Semantics: bench/maestro/RECOVERY_AND_SAFETY_METRICS.md
    """
    events = trace.get("events") or []
    t0 = float(events[0]["ts"]) if events else 0.0

    starts: Dict[str, float] = {}
    latencies_ms: List[float] = []
    coord_msgs = 0
    coord_msgs_after_fault = 0
    fault_events: List[str] = []
    recovery_ok = True
    fault_injected = False
    first_fault_seq: int | None = None
    first_fault_ts: float | None = None
    events_after_first_fault = 0
    tasks_completed_after_fault = 0

    recovery_attempt_count = 0
    first_recovery_ts: float | None = None
    first_safe_ts: float | None = None
    fault_to_recovery_event_count = 0
    fault_to_safe_state_event_count = 0

    safety_violation_types: List[Dict[str, str]] = []
    ponr_violation_count = 0
    unsafe_completion_count = 0
    constraint_violation_count = 0
    deadline_miss_count = 0
    resource_conflict_count = 0
    invalid_action_count = 0
    blocked_action_count = 0
    duplicate_action_count = 0
    wasted_action_count = 0

    task_started: set[str] = set()
    task_ended: set[str] = set()
    pending_before_fault: int | None = None

    for seq, ev in enumerate(events):
        et = ev.get("type", "")
        ts = float(ev.get("ts", 0.0))

        if et == "coordination_message":
            coord_msgs += 1
            if first_fault_seq is not None:
                coord_msgs_after_fault += 1

        if et == "fault_injected":
            fault_injected = True
            fault_events.append(_fault_label(ev))
            if first_fault_seq is None:
                first_fault_seq = seq
                first_fault_ts = ts
                pending_before_fault = len(task_started) - len(task_ended)

        if et == "recovery_failed":
            recovery_ok = False
            fault_events.append("recovery_failed")

        if et == "recovery_attempt":
            recovery_attempt_count += 1

        if et == "recovery_succeeded":
            if first_fault_seq is not None:
                fault_to_recovery_event_count += 1
            if first_recovery_ts is None:
                first_recovery_ts = ts

        if et == "safe_state_reached":
            if first_safe_ts is None:
                first_safe_ts = ts
            if fault_injected:
                fault_to_safe_state_event_count = max(fault_to_safe_state_event_count, 1)

        if et == "safety_violation":
            pl = ev.get("payload") or {}
            safety_violation_types.append(
                {
                    "type": str(pl.get("violation_type", "unknown")),
                    "detail": str(pl.get("detail", "")),
                }
            )

        if et == "ponr_violation":
            ponr_violation_count += 1

        if et == "unsafe_task_completion":
            unsafe_completion_count += 1

        if et == "constraint_guard_trigger":
            constraint_violation_count += 1

        if et == "deadline_miss":
            deadline_miss_count += 1

        if et == "resource_conflict":
            resource_conflict_count += 1

        if et == "invalid_action":
            invalid_action_count += 1
            wasted_action_count += 1

        if et == "blocked_action":
            blocked_action_count += 1
            wasted_action_count += 1

        if et in ("duplicate_action", "duplicate_completion"):
            duplicate_action_count += 1
            wasted_action_count += 1

        if et == "wasted_action":
            wasted_action_count += 1

        if first_fault_seq is not None:
            events_after_first_fault += 1

        if et == "task_start":
            tid = (ev.get("payload") or {}).get("task_id")
            if isinstance(tid, str):
                starts[tid] = ts
                task_started.add(tid)

        if et == "task_end":
            if first_fault_seq is not None:
                tasks_completed_after_fault += 1
            pl = ev.get("payload") or {}
            tid = pl.get("task_id")
            if isinstance(tid, str) and tid in starts:
                dt = ts - starts[tid]
                latencies_ms.append(max(0.0, dt * 1000.0))
                task_ended.add(tid)

    tasks_completed = len(latencies_ms)
    steps_to_completion_after_first_fault = (
        events_after_first_fault if first_fault_seq is not None else None
    )

    meta = trace.get("metadata") or {}
    planned_raw = meta.get("planned_task_count")
    planned_task_count = int(planned_raw) if planned_raw is not None else tasks_completed

    time_to_first_fault_ms = (
        (first_fault_ts - t0) * 1000.0 if first_fault_ts is not None else None
    )
    time_to_recovery_ms = None
    if first_fault_ts is not None and first_recovery_ts is not None:
        time_to_recovery_ms = max(0.0, (first_recovery_ts - first_fault_ts) * 1000.0)

    time_to_safe_state_ms = None
    if first_safe_ts is not None:
        time_to_safe_state_ms = max(0.0, (first_safe_ts - t0) * 1000.0)

    tasks_recovered_after_fault = tasks_completed_after_fault

    safety_violation_count = len(safety_violation_types)
    unsafe_success_count = 1 if (planned_task_count > 0 and tasks_completed >= planned_task_count and safety_violation_count > 0) else 0

    messages_per_completed_task = coord_msgs / max(1, tasks_completed)
    retries_per_completed_task = recovery_attempt_count / max(1, tasks_completed)

    all_done = planned_task_count > 0 and tasks_completed >= planned_task_count
    any_safety = safety_violation_count > 0 or ponr_violation_count > 0 or unsafe_completion_count > 0

    shutdown_safe = any(ev.get("type") == "safe_shutdown_initiated" for ev in events)

    run_outcome = _classify_run_outcome(
        all_done=all_done,
        any_safety=any_safety,
        recovery_ok=recovery_ok,
        shutdown_safe=shutdown_safe,
    )

    notes = (
        "MAESTRO_REPORT v0.2; thin-slice synthetic trace times (ts) are scenario simulation "
        "timestamps in seconds, not wall-clock unless the harness records wall time in ts."
    )

    return {
        "version": "0.2",
        "run_id": run_id,
        "scenario_id": scenario_id,
        "run_outcome": run_outcome,
        "metrics": {
            "tasks_completed": tasks_completed,
            "planned_task_count": planned_task_count,
            "task_latency_ms_p50": percentile(latencies_ms, 0.50),
            "task_latency_ms_p95": percentile(latencies_ms, 0.95),
            "task_latency_ms_p99": percentile(latencies_ms, 0.99),
            "coordination_messages": coord_msgs,
            "tasks_completed_after_fault": (
                tasks_completed_after_fault if first_fault_seq is not None else None
            ),
            "steps_to_completion_after_first_fault": steps_to_completion_after_first_fault,
            "time_to_first_fault_ms": time_to_first_fault_ms,
            "time_to_recovery_ms": time_to_recovery_ms,
            "time_to_safe_state_ms": time_to_safe_state_ms,
            "recovery_attempt_count": recovery_attempt_count,
            "tasks_pending_at_first_fault": pending_before_fault,
            "tasks_recovered_after_fault": tasks_recovered_after_fault,
            "fault_to_safe_state_event_count": fault_to_safe_state_event_count,
            "fault_to_recovery_event_count": fault_to_recovery_event_count,
        },
        "safety": {
            "safety_violation_count": safety_violation_count,
            "safety_violation_types": safety_violation_types,
            "ponr_violation_count": ponr_violation_count,
            "unsafe_completion_count": unsafe_completion_count,
            "unsafe_success_count": unsafe_success_count,
            "constraint_violation_count": constraint_violation_count,
            "deadline_miss_count": deadline_miss_count,
            "resource_conflict_count": resource_conflict_count,
            "invalid_action_count": invalid_action_count,
            "blocked_action_count": blocked_action_count,
        },
        "coordination_efficiency": {
            "messages_per_completed_task": round(messages_per_completed_task, 4),
            "messages_after_fault": coord_msgs_after_fault,
            "retries_per_completed_task": round(retries_per_completed_task, 4),
            "duplicate_action_count": duplicate_action_count,
            "wasted_action_count": wasted_action_count,
        },
        "faults": {
            "fault_injected": fault_injected,
            "fault_events": fault_events,
            "recovery_ok": recovery_ok,
        },
        "notes": notes,
    }


def _classify_run_outcome(
    *,
    all_done: bool,
    any_safety: bool,
    recovery_ok: bool,
    shutdown_safe: bool,
) -> str:
    if shutdown_safe and not all_done:
        return "failed_safe_shutdown"
    if all_done:
        if any_safety:
            return "success_unsafe"
        if recovery_ok:
            return "success_safe"
        return "failed_unsafe"
    if any_safety:
        return "partial_unsafe"
    if not recovery_ok:
        return "failed_unsafe"
    return "partial_safe"


def maestro_aggregate_recovery_success_rate(reports: List[Dict[str, Any]]) -> float | None:
    """Aggregate recovery_success_rate: fraction of faulted runs that recorded recovery."""
    eligible = 0
    ok = 0
    for r in reports:
        m = r.get("metrics") or {}
        if not r.get("faults", {}).get("fault_injected"):
            continue
        eligible += 1
        if (m.get("fault_to_recovery_event_count") or 0) > 0 or m.get("time_to_recovery_ms") is not None:
            ok += 1
    if eligible == 0:
        return None
    return ok / eligible
