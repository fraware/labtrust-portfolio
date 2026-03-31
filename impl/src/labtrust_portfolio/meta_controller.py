"""
P8 Meta-Coordination: meta-controller reference impl.
State (current regime), switching criteria, decide_switch. PONRs invariant; regime changes auditable.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

REGIMES = ("centralized", "blackboard", "fallback")


def decide_switch(
    current_regime: str,
    fault_count: int,
    latency_p95_ms: float,
    contention_index: float = 0.0,
    fault_threshold: int = 2,
    latency_threshold_ms: float = 200.0,
    contention_threshold: float = 1.5,
    hysteresis_consecutive: int = 1,
) -> Optional[str]:
    """
    Decide whether to switch regime. Returns to_regime or None (no switch).
    Revert is checked first (no hysteresis). Then fault-based switch to fallback
    requires fault_count >= hysteresis_consecutive and fault_count > fault_threshold.
    Latency-based switch to fallback has no hysteresis (latency_p95 > threshold).
    Contention-based switch is triggered when contention_index > contention_threshold.
    """
    to_regime, _ = decide_switch_with_reason(
        current_regime=current_regime,
        fault_count=fault_count,
        latency_p95_ms=latency_p95_ms,
        contention_index=contention_index,
        fault_threshold=fault_threshold,
        latency_threshold_ms=latency_threshold_ms,
        contention_threshold=contention_threshold,
        hysteresis_consecutive=hysteresis_consecutive,
    )
    return to_regime


def decide_switch_with_reason(
    current_regime: str,
    fault_count: int,
    latency_p95_ms: float,
    contention_index: float = 0.0,
    fault_threshold: int = 2,
    latency_threshold_ms: float = 200.0,
    contention_threshold: float = 1.5,
    hysteresis_consecutive: int = 1,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Decide whether to switch regime, returning (to_regime, reason).
    Reasons:
      - "stabilized" for fallback->centralized reversion
      - "fault_threshold" when fault_count trigger fires
      - "latency_threshold" when latency trigger fires
      - "contention_threshold" when contention trigger fires
    """
    if current_regime not in REGIMES:
        current_regime = "centralized"
    # Revert to centralized when in fallback and conditions are low (no hysteresis)
    if (
        current_regime == "fallback"
        and fault_count <= 0
        and latency_p95_ms < latency_threshold_ms * 0.5
        and contention_index < contention_threshold * 0.5
    ):
        return "centralized", "stabilized"
    # Fault-based switch to fallback: require consecutive faults (thrash control)
    if fault_count >= hysteresis_consecutive and fault_count > fault_threshold:
        return "fallback", "fault_threshold"
    # Latency-based switch to fallback: no hysteresis
    if latency_p95_ms > latency_threshold_ms:
        return "fallback", "latency_threshold"
    if contention_index > contention_threshold:
        return "fallback", "contention_threshold"
    return None, None


def regime_switch_event(
    seq: int,
    ts: float,
    from_regime: str,
    to_regime: str,
    reason: str,
    state_hash_after: str,
    criteria: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a regime_switch trace event for audit/replay."""
    payload: Dict[str, Any] = {
        "from_regime": from_regime,
        "to_regime": to_regime,
        "reason": reason,
    }
    if criteria:
        payload["criteria"] = criteria
    return {
        "seq": seq,
        "ts": ts,
        "type": "regime_switch",
        "actor": {"kind": "system", "id": "meta_controller"},
        "payload": payload,
        "state_hash_after": state_hash_after,
    }
