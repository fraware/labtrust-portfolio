"""PONR gatekeeper: admissibility check before release or PONR transition."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Tuple

from .conformance import check_conformance
from .contracts import validate, apply_event_to_state, ALLOW


def check_contracts_on_trace(trace_path: Path) -> Tuple[bool, str | None]:
    """
    Run contract validator on trace events in order. Returns (True, None) if all
    events allowed, else (False, reason). Denies release when contract invalid.
    """
    if not trace_path.exists():
        return (False, "trace.json missing")
    try:
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return (False, str(e))
    state = {"ownership": {}, "_last_ts": {}}
    for ev in trace.get("events", []):
        verdict = validate(state, ev)
        if verdict.verdict != ALLOW:
            return (False, "contract denial at event: " + str(verdict.reason_codes))
        state = apply_event_to_state(state, ev)
    return (True, None)


def allow_release(run_dir: Path, check_contracts: bool = True) -> bool:
    """
    Return True iff the run directory satisfies conformance Tier 2 or higher
    and (when check_contracts) contract validator allows all trace events.
    """
    result = check_conformance(run_dir)
    if not result.passed or result.tier < 2:
        return False
    if check_contracts:
        trace_path = run_dir / "trace.json"
        contract_ok, reason = check_contracts_on_trace(trace_path)
        if not contract_ok:
            return False
    return True
