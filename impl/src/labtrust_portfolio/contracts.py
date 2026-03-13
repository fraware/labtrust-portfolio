"""Coordination contract validator: validate(state, event) -> verdict + reason_codes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

ALLOW = "allow"
DENY = "deny"
REASON_SPLIT_BRAIN = "split_brain"
REASON_STALE_WRITE = "stale_write"
REASON_REORDER = "reorder_violation"
REASON_UNKNOWN_KEY = "unknown_key"


@dataclass
class ContractVerdict:
    verdict: str  # "allow" | "deny"
    reason_codes: List[str]


def validate(
    state: Dict[str, Any],
    event: Dict[str, Any],
    contract: Dict[str, Any] | None = None,
) -> ContractVerdict:
    """
    Pure function: validate event admissible given state and contract.
    Usable from traces without privileged state.
    Returns verdict and reason_codes.
    """
    if contract is None:
        contract = {}
    reason_codes: List[str] = []
    ownership = state.get("ownership", {})
    last_ts = state.get("_last_ts", {})
    event_ts = event.get("ts", 0.0)
    event_type = event.get("type", "")
    payload = event.get("payload", {})

    if event_type == "task_start" or event_type == "task_end":
        key = payload.get("task_id", "")
        if not key:
            return ContractVerdict(
                verdict=DENY, reason_codes=[REASON_UNKNOWN_KEY]
            )
        owner = ownership.get(key)
        actor = event.get("actor", {})
        writer = payload.get("writer") or actor.get("id", "agent_1")
        if owner is not None and owner != writer:
            reason_codes.append(REASON_SPLIT_BRAIN)
        prev_ts = last_ts.get(key, -1.0)
        if prev_ts > event_ts:
            reason_codes.append(REASON_STALE_WRITE)
            reason_codes.append(REASON_REORDER)
        if contract.get("use_instrument_state_machine"):
            from .instrument_state_machine import apply_instrument_event
            allowed, _ = apply_instrument_event(state, key, event_type)
            if not allowed:
                reason_codes.append("instrument_state_machine")
        if reason_codes:
            return ContractVerdict(verdict=DENY, reason_codes=reason_codes)
        return ContractVerdict(verdict=ALLOW, reason_codes=[])

    if event_type == "coordination_message":
        return ContractVerdict(verdict=ALLOW, reason_codes=[])

    return ContractVerdict(verdict=ALLOW, reason_codes=[])


def apply_event_to_state(
    state: Dict[str, Any],
    event: Dict[str, Any],
) -> Dict[str, Any]:
    """Update state with event for contract store (ownership)."""
    out = dict(state)
    ownership = dict(out.get("ownership", {}))
    last_ts = dict(out.get("_last_ts", {}))
    payload = event.get("payload", {})
    key = payload.get("task_id") or payload.get("key")
    writer = event.get("actor", {}).get("id", "agent_1")
    ts = event.get("ts", 0.0)
    if key:
        ownership[key] = writer
        last_ts[key] = ts
    out["ownership"] = ownership
    out["_last_ts"] = last_ts
    event_type = event.get("type", "")
    if key and event_type in ("task_start", "task_end"):
        from .instrument_state_machine import apply_instrument_event
        _, out = apply_instrument_event(out, key, event_type)
    return out
