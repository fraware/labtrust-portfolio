"""
Minimal instrument/station state machine for P1 contract alignment.
States: idle | running | calibration | cleaning.
Transitions keyed by event type (task_start, task_end) map to allowed next state.
Contract "no transition from running without task_end" is aligned with this machine.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

INSTRUMENT_STATES = ("idle", "running", "calibration", "cleaning")

# Allowed (current_state, event_type) -> next_state. None = invalid transition.
_TRANSITIONS: Dict[Tuple[str, str], Optional[str]] = {
    ("idle", "task_start"): "running",
    ("idle", "task_end"): None,
    ("running", "task_start"): None,
    ("running", "task_end"): "idle",
    ("calibration", "task_start"): None,
    ("calibration", "task_end"): None,
    ("cleaning", "task_start"): None,
    ("cleaning", "task_end"): None,
}


def next_state(
    current_state: str,
    event_type: str,
) -> Optional[str]:
    """
    Return allowed next instrument state for (current_state, event_type), or None if invalid.
    Uses minimal machine: task_start only from idle->running; task_end only from running->idle.
    """
    if current_state not in INSTRUMENT_STATES:
        current_state = "idle"
    key = (current_state, event_type)
    return _TRANSITIONS.get(key)


def apply_instrument_event(
    state: Dict[str, Any],
    task_id: str,
    event_type: str,
) -> Tuple[bool, Dict[str, Any]]:
    """
    Apply event to per-task instrument state. state[key] = instrument state per task_id.
    Returns (allowed, new_state). Used to align contract with state machine.
    """
    out = dict(state)
    task_states = dict(out.get("_instrument_state", {}))
    current = task_states.get(task_id, "idle")
    next_s = next_state(current, event_type)
    if next_s is None:
        return (False, out)
    task_states[task_id] = next_s
    out["_instrument_state"] = task_states
    return (True, out)
