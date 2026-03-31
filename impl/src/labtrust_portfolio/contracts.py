"""Coordination contract validator: validate(state, event, contract?) -> verdict + reason_codes."""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, FrozenSet, List, Set

ALLOW = "allow"
DENY = "deny"
REASON_SPLIT_BRAIN = "split_brain"
REASON_STALE_WRITE = "stale_write"
REASON_REORDER = "reorder_violation"
REASON_UNKNOWN_KEY = "unknown_key"

_TS_EPS = 1e-9


@dataclass
class ContractVerdict:
    verdict: str  # "allow" | "deny"
    reason_codes: List[str]


def prepare_replay_state(initial_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Copy initial trace state and attach replay fields:
    - _observed_ts_max: high-water timestamp per key (starts from committed _last_ts).
    - _non_owner_task_start_pending: handover-contention ledger (K3).
    """
    state = copy.deepcopy(initial_state)
    last_ts = dict(state.get("_last_ts", {}))
    state["_observed_ts_max"] = dict(last_ts)
    state.setdefault("_non_owner_task_start_pending", {})
    return state


def finalize_event_observation(state: Dict[str, Any], event: Dict[str, Any]) -> None:
    """
    After validate (allow or deny), advance trace-order high-water ts for the key.
    Must be called once per event in trace order.
    """
    payload = event.get("payload", {})
    key = payload.get("task_id") or payload.get("key")
    if not key:
        return
    ts = float(event.get("ts", 0.0))
    obs = state.setdefault("_observed_ts_max", {})
    obs[key] = max(obs.get(key, -1.0), ts)


def load_evaluation_scope(path: Path | str) -> Dict[str, Any]:
    """Load evaluation_scope.json (family allowlists; no gold fields)."""
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8"))


def derive_allowed_keys_synthetic(data: Dict[str, Any]) -> FrozenSet[str]:
    """
    Bench / traces without annotations: in-scope keys = union of initial_state keys
    and every task_id appearing in events (no gold, no manifest).
    """
    events = data.get("events") or []
    keys: Set[str] = set((data.get("initial_state") or {}).get("ownership") or {})
    keys.update((data.get("initial_state") or {}).get("_last_ts") or {})
    for ev in events:
        tid = (ev.get("payload") or {}).get("task_id") or ""
        if tid:
            keys.add(tid)
    return frozenset(keys)


def derive_allowed_keys_for_evaluation(
    data: Dict[str, Any],
    *,
    family_id: str,
    evaluation_scope: Dict[str, Any],
) -> FrozenSet[str]:
    """
    Quasi-real / annotated traces: allowed_keys from evaluation_scope family allowlist
    plus any keys present in initial_state (ownership / _last_ts). Does not use
    expected_verdicts, annotations, or failure_class.
    """
    fam_map = evaluation_scope.get("family_declared_keys") or {}
    if family_id not in fam_map:
        raise KeyError(
            f"family_id {family_id!r} not in evaluation_scope family_declared_keys"
        )
    keys: Set[str] = set(fam_map[family_id])
    init = data.get("initial_state") or {}
    keys.update(init.get("ownership") or {})
    keys.update(init.get("_last_ts") or {})
    return frozenset(keys)


def build_contract_config_from_trace(
    data: Dict[str, Any],
    *,
    family_id: str | None = None,
    evaluation_scope: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Contract options for validate(). Annotated traces require non-gold scope:
    evaluation_scope + family_id (or scenario_family_id on data).
    """
    cfg: Dict[str, Any] = {}
    has_ann = "annotations" in data
    if has_ann:
        fid = family_id or data.get("scenario_family_id")
        if fid is None or evaluation_scope is None:
            raise ValueError(
                "Annotated traces require scenario_family_id on the trace and "
                "evaluation_scope dict (see datasets/contracts_real/evaluation_scope.json)."
            )
        keys = derive_allowed_keys_for_evaluation(
            data, family_id=fid, evaluation_scope=evaluation_scope
        )
        cfg["allowed_keys"] = keys
        return cfg
    keys = derive_allowed_keys_synthetic(data)
    if keys:
        cfg["allowed_keys"] = keys
    return cfg


def validate(
    state: Dict[str, Any],
    event: Dict[str, Any],
    contract: Dict[str, Any] | None = None,
) -> ContractVerdict:
    """
    Pure function on verdict *given current state*; may mutate coordination ledgers
    (_non_owner_task_start_pending) that are replay-internal, not external domain state.

    K1 allowed_keys: if contract['allowed_keys'] is set, deny unknown_key when key not in set.
    K2 trace-order monotonicity: deny reorder_violation when event_ts < _observed_ts_max[key].
    K3 handover contention: after a non-owner task_start (even if denied), a subsequent
    task_end by the prior owner is denied (split_brain).
    """
    if contract is None:
        contract = {}
    reason_codes: List[str] = []
    ownership = state.get("ownership", {})
    last_ts = state.get("_last_ts", {})
    event_ts = float(event.get("ts", 0.0))
    event_type = event.get("type", "")
    payload = event.get("payload", {})
    actor = event.get("actor", {})
    writer = payload.get("writer") or actor.get("id", "agent_1")

    if event_type == "task_start" or event_type == "task_end":
        key = payload.get("task_id", "")
        if not key:
            return ContractVerdict(verdict=DENY, reason_codes=[REASON_UNKNOWN_KEY])

        allowed = contract.get("allowed_keys")
        if allowed is not None and key not in allowed:
            return ContractVerdict(verdict=DENY, reason_codes=[REASON_UNKNOWN_KEY])

        obs = state.get("_observed_ts_max") or {}
        hw = float(obs.get(key, -1.0))
        if event_ts + _TS_EPS < hw:
            reason_codes.append(REASON_REORDER)
            reason_codes.append(REASON_STALE_WRITE)

        owner = ownership.get(key)

        if event_type == "task_start" and owner is not None and owner != writer:
            pend = state.setdefault("_non_owner_task_start_pending", {})
            pend[key] = {"writer": writer, "ts": event_ts}

        if event_type == "task_end":
            pend = (state.get("_non_owner_task_start_pending") or {}).get(key)
            if pend is not None:
                pwriter = pend.get("writer")
                if owner is not None and writer == owner and pwriter is not None and pwriter != writer:
                    reason_codes.append(REASON_SPLIT_BRAIN)

        if owner is not None and owner != writer:
            reason_codes.append(REASON_SPLIT_BRAIN)

        prev_ts = float(last_ts.get(key, -1.0))
        if prev_ts > event_ts + _TS_EPS:
            if REASON_STALE_WRITE not in reason_codes:
                reason_codes.append(REASON_STALE_WRITE)
            if REASON_REORDER not in reason_codes:
                reason_codes.append(REASON_REORDER)

        if contract.get("use_instrument_state_machine"):
            from .instrument_state_machine import apply_instrument_event

            allowed_sm, _ = apply_instrument_event(state, key, event_type)
            if not allowed_sm:
                reason_codes.append("instrument_state_machine")

        if reason_codes:
            seen: Set[str] = set()
            uniq = [x for x in reason_codes if not (x in seen or seen.add(x))]
            return ContractVerdict(verdict=DENY, reason_codes=uniq)
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
    writer = payload.get("writer") or event.get("actor", {}).get("id", "agent_1")
    ts = float(event.get("ts", 0.0))
    event_type = event.get("type", "")
    if key:
        ownership[key] = writer
        last_ts[key] = ts
    out["ownership"] = ownership
    out["_last_ts"] = last_ts
    if key and event_type == "task_start":
        pend = out.get("_non_owner_task_start_pending")
        if isinstance(pend, dict) and key in pend:
            pend = dict(pend)
            del pend[key]
            out["_non_owner_task_start_pending"] = pend
    if key and event_type in ("task_start", "task_end"):
        from .instrument_state_machine import apply_instrument_event

        _, out = apply_instrument_event(out, key, event_type)
    return out
