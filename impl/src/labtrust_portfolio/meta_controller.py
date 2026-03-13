"""
P8 Meta-Coordination: meta-controller reference impl.
State (current regime), switching criteria, decide_switch. PONRs invariant; regime changes auditable.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

REGIMES = ("centralized", "blackboard", "fallback")


def decide_switch(
    current_regime: str,
    fault_count: int,
    latency_p95_ms: float,
    fault_threshold: int = 2,
    latency_threshold_ms: float = 200.0,
    hysteresis_consecutive: int = 1,
) -> Optional[str]:
    """
    Decide whether to switch regime. Returns to_regime or None (no switch).
    Revert is checked first (no hysteresis). Then fault-based switch to fallback
    requires fault_count >= hysteresis_consecutive and fault_count > fault_threshold.
    Latency-based switch to fallback has no hysteresis (latency_p95 > threshold).
    """
    if current_regime not in REGIMES:
        current_regime = "centralized"
    # Revert to centralized when in fallback and conditions are low (no hysteresis)
    if current_regime == "fallback" and fault_count <= 0 and latency_p95_ms < latency_threshold_ms * 0.5:
        return "centralized"
    # Fault-based switch to fallback: require consecutive faults (thrash control)
    if fault_count >= hysteresis_consecutive and fault_count > fault_threshold:
        return "fallback"
    # Latency-based switch to fallback: no hysteresis
    if latency_p95_ms > latency_threshold_ms:
        return "fallback"
    return None


def regime_switch_event(
    seq: int,
    ts: float,
    from_regime: str,
    to_regime: str,
    reason: str,
    state_hash_after: str,
) -> Dict[str, Any]:
    """Build a regime_switch trace event for audit/replay."""
    return {
        "seq": seq,
        "ts": ts,
        "type": "regime_switch",
        "actor": {"kind": "system", "id": "meta_controller"},
        "payload": {"from_regime": from_regime, "to_regime": to_regime, "reason": reason},
        "state_hash_after": state_hash_after,
    }
