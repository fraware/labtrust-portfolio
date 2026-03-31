"""Reference contract-enforcing store: apply writes only if validator allows.
Contract type 'single-writer per task' / 'no transition from running without task_end'
is aligned with instrument_state_machine (idle->running on task_start, running->idle on task_end).
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from .contracts import (
    validate,
    apply_event_to_state,
    finalize_event_observation,
    prepare_replay_state,
    ContractVerdict,
    ALLOW,
)


class ContractEnforcingStore:
    """
    In-memory store that applies events only when contract validator allows.
    Bounded overhead: one validation per write.
    """

    def __init__(self, contract: Dict[str, Any] | None = None):
        self._state: Dict[str, Any] = prepare_replay_state({"ownership": {}, "_last_ts": {}})
        self._contract = contract or {}
        self._history: List[Dict[str, Any]] = []

    def write(self, event: Dict[str, Any]) -> Tuple[ContractVerdict, bool]:
        """
        Attempt to apply event. Returns (verdict, applied). If verdict is allow,
        state is updated and applied is True.
        """
        verdict = validate(self._state, event, self._contract)
        if verdict.verdict == ALLOW:
            self._state = apply_event_to_state(self._state, event)
        finalize_event_observation(self._state, event)
        if verdict.verdict != ALLOW:
            return (verdict, False)
        self._history.append(event)
        return (verdict, True)

    @property
    def state(self) -> Dict[str, Any]:
        return dict(self._state)
