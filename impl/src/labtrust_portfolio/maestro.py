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

def maestro_report_from_trace(run_id: str, scenario_id: str, trace: Dict[str, Any]) -> Dict[str, Any]:
    starts: Dict[str, float] = {}
    latencies_ms: List[float] = []
    coord_msgs = 0
    fault_events: List[str] = []
    recovery_ok = True
    fault_injected = False
    first_fault_seq: int | None = None
    events_after_first_fault = 0
    tasks_completed_after_fault = 0

    for seq, ev in enumerate(trace["events"]):
        et = ev["type"]
        if et == "coordination_message":
            coord_msgs += 1
        if et == "fault_injected":
            fault_injected = True
            if first_fault_seq is None:
                first_fault_seq = seq
            fault_events.append(ev["payload"].get("fault", "unknown_fault"))
        if et == "recovery_failed":
            recovery_ok = False
            fault_events.append("recovery_failed")

        if first_fault_seq is not None:
            events_after_first_fault += 1
        if et == "task_start":
            starts[ev["payload"]["task_id"]] = float(ev["ts"])
        if et == "task_end":
            if first_fault_seq is not None:
                tasks_completed_after_fault += 1
            tid = ev["payload"]["task_id"]
            if tid in starts:
                dt = float(ev["ts"]) - starts[tid]
                latencies_ms.append(max(0.0, dt * 1000.0))

    tasks_completed = len(latencies_ms)
    steps_to_completion_after_first_fault = (
        events_after_first_fault if first_fault_seq is not None else None
    )

    return {
        "version": "0.1",
        "run_id": run_id,
        "scenario_id": scenario_id,
        "metrics": {
            "tasks_completed": tasks_completed,
            "task_latency_ms_p50": percentile(latencies_ms, 0.50),
            "task_latency_ms_p95": percentile(latencies_ms, 0.95),
            "task_latency_ms_p99": percentile(latencies_ms, 0.99),
            "coordination_messages": coord_msgs,
            "tasks_completed_after_fault": tasks_completed_after_fault if first_fault_seq is not None else None,
            "steps_to_completion_after_first_fault": steps_to_completion_after_first_fault,
        },
        "faults": {
            "fault_injected": fault_injected,
            "fault_events": fault_events,
            "recovery_ok": recovery_ok,
        },
        "notes": "Thin-slice MAESTRO report; semantics will expand in v0.2+",
    }
