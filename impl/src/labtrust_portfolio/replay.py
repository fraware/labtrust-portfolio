from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .trace import state_hash


def _infer_root_cause_category(ev_type: str, payload: Dict[str, Any]) -> str:
    """Infer root cause category for divergence: scheduler, tool_io, timestamp, unknown."""
    if ev_type == "final":
        return "unknown"
    if "fault" in ev_type.lower() or (payload and "fault" in str(payload).lower()):
        return "scheduler"
    if ev_type in ("task_start", "task_end") and payload:
        if "task_id" in payload or "name" in payload:
            return "tool_io"
    if ev_type in ("coordination_message", "regime_switch"):
        return "scheduler"
    return "timestamp" if ev_type else "unknown"


@dataclass
class DivergenceDiagnostic:
    """Structured diagnostic when replay diverges."""

    seq: int
    expected_hash: str
    got_hash: str
    event_type: str = ""
    root_cause_category: str = ""
    witness_slice: List[Dict[str, Any]] = field(default_factory=list)

    def message(self) -> str:
        return (
            f"seq={self.seq} type={self.event_type!r}: "
            f"expected={self.expected_hash} got={self.got_hash}"
        )


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
    ok, diag = replay_trace_with_diagnostics(trace)
    if ok:
        return (True, "replay ok")
    return (False, diag[0].message() if diag else "replay failed")


def replay_trace_with_diagnostics(
    trace: Dict[str, Any],
    witness_window: int = 2,
) -> Tuple[bool, List[DivergenceDiagnostic]]:
    """
    L0 replay with structured diagnostics on divergence. Returns (ok, list of
    DivergenceDiagnostic); list non-empty only when ok is False.
    witness_window: number of events before/after divergence_at_seq to include in witness_slice.
    """
    diagnostics: List[DivergenceDiagnostic] = []
    state: Dict[str, Any] = {}
    events = trace.get("events", [])
    for i, ev in enumerate(events):
        state = apply_event(state, ev)
        expected = ev.get("state_hash_after", "")
        got = state_hash(state)
        if got != expected:
            lo = max(0, i - witness_window)
            hi = min(len(events), i + witness_window + 1)
            witness_slice = list(events[lo:hi])
            diagnostics.append(
                DivergenceDiagnostic(
                    seq=ev.get("seq", i),
                    expected_hash=expected,
                    got_hash=got,
                    event_type=ev.get("type", ""),
                    root_cause_category=_infer_root_cause_category(
                        ev.get("type", ""), ev.get("payload", {})
                    ),
                    witness_slice=witness_slice,
                )
            )
            return (False, diagnostics)
    final_expected = trace.get("final_state_hash", "")
    final_got = state_hash(state)
    if final_got != final_expected:
        diagnostics.append(
            DivergenceDiagnostic(
                seq=-1,
                expected_hash=final_expected,
                got_hash=final_got,
                event_type="final",
                root_cause_category="unknown",
                witness_slice=events[-witness_window:] if len(events) >= witness_window else list(events),
            )
        )
        return (False, diagnostics)
    return (True, [])


def replay_l1_stub(
    trace: Dict[str, Any],
    twin_config_path: Path,
) -> Tuple[bool, str]:
    """
    L1 stub: run L0 replay then validate twin config. Returns (ok, message).
    Does not run a real simulator; proves the L1 contract (L0 + config).
    """
    ok, diag = replay_trace_with_diagnostics(trace)
    if not ok:
        return (False, diag[0].message() if diag else "L0 replay failed")
    if not twin_config_path.exists():
        return (False, f"twin config not found: {twin_config_path}")
    try:
        import json
        cfg = json.loads(twin_config_path.read_text(encoding="utf-8"))
    except Exception as e:
        return (False, f"twin config invalid: {e}")
    for key in ("build_hash", "env_seed"):
        if key not in cfg:
            return (False, f"twin config missing required key: {key}")
    return (True, "L1 stub ok (L0 + twin config valid)")


def replay_l1_twin(
    trace: Dict[str, Any],
    twin_config_path: Path,
) -> Tuple[bool, str]:
    """
    L1 twin: L0 replay + twin config validation + one deterministic re-run of the
    same control-plane state machine from the trace. For v0.2 the twin uses the
    same apply_event/state_hash logic as L0 so the re-run reproduces state_hash;
    full simulator/physics twin is future work. Returns (ok, message).
    """
    ok, diag = replay_trace_with_diagnostics(trace)
    if not ok:
        return (False, diag[0].message() if diag else "L0 replay failed")
    if not twin_config_path.exists():
        return (False, f"twin config not found: {twin_config_path}")
    try:
        import json as _json
        cfg = _json.loads(twin_config_path.read_text(encoding="utf-8"))
    except Exception as e:
        return (False, f"twin config invalid: {e}")
    for key in ("build_hash", "env_seed"):
        if key not in cfg:
            return (False, f"twin config missing required key: {key}")
    # Deterministic twin re-run: same event sequence, same state machine (L0 logic)
    ok2, diag2 = replay_trace_with_diagnostics(trace)
    if not ok2:
        return (False, f"L1 twin re-run failed: {diag2[0].message() if diag2 else 'unknown'}")
    return (True, "L1 twin ok (L0 + config + deterministic re-run)")
