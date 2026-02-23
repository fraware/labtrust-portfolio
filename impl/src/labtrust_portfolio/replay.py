from __future__ import annotations

from typing import Any, Dict, Tuple
from .trace import state_hash

def apply_event(state: Dict[str, Any], ev: Dict[str, Any]) -> Dict[str, Any]:
    s = dict(state)
    t = ev["type"]
    payload = ev.get("payload", {})

    tasks = dict(s.get("tasks", {}))
    if t == "task_start":
        tasks[payload["task_id"]] = {"status": "running", "name": payload.get("name", "")}
    elif t == "task_end":
        tasks[payload["task_id"]] = {"status": "done", "name": payload.get("name", "")}
    s["tasks"] = tasks

    if t == "coordination_message":
        s["coord_msgs"] = int(s.get("coord_msgs", 0)) + 1

    if t == "fault_injected":
        faults = list(s.get("faults", []))
        faults.append(payload.get("fault", "unknown_fault"))
        s["faults"] = faults

    return s

def replay_trace(trace: Dict[str, Any]) -> Tuple[bool, str]:
    state: Dict[str, Any] = {}
    for ev in trace["events"]:
        state = apply_event(state, ev)
        expected = ev["state_hash_after"]
        got = state_hash(state)
        if got != expected:
            return (False, f"state hash mismatch at seq={ev['seq']}: expected={expected} got={got}")
    final_expected = trace["final_state_hash"]
    final_got = state_hash(state)
    if final_got != final_expected:
        return (False, f"final state hash mismatch: expected={final_expected} got={final_got}")
    return (True, "replay ok")
