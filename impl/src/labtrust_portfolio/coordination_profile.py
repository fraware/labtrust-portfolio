"""
Deterministic P5 coordination experiment profile: maps (regime, agent_count, num_tasks)
to metadata and message budgets used by thin-slice and feature rows. Single source of truth.
"""
from __future__ import annotations

from typing import Any, Dict, Tuple

VALID_REGIMES: Tuple[str, ...] = (
    "centralized",
    "hierarchical",
    "blackboard",
    "market",
    "decentralized",
)

REGIME_ID: Dict[str, int] = {r: i for i, r in enumerate(VALID_REGIMES)}


def canonical_regime(regime: str | None) -> str:
    r = (regime or "centralized").lower().replace("-", "_")
    return r if r in REGIME_ID else "centralized"


def coordination_experiment_profile(
    coordination_regime: str,
    agent_count: int,
    num_tasks: int,
) -> Dict[str, Any]:
    """
    Reproducible functions of regime and agent_count (no RNG).
    Thin-slice uses pre_task + intra_task coordination_message counts;
    scaling rows copy these fields from trace metadata.
    """
    n = max(1, int(agent_count))
    nt = max(1, int(num_tasks))
    regime = canonical_regime(coordination_regime)
    rid = float(REGIME_ID[regime])

    if regime == "hierarchical":
        depth = min(5, 1 + max(0, (n - 1).bit_length()))
    elif regime == "centralized":
        depth = 2
    else:
        depth = 1

    fan_out = min(6, max(1, (n + 1) // 2))
    handoff_factor = max(1, min(8, n))

    if regime == "blackboard":
        shared_state_contention = float(n) / float(nt)
    elif regime == "decentralized":
        shared_state_contention = float(n * handoff_factor) / float(nt)
    else:
        shared_state_contention = float(n) / float(max(nt, 2))

    queue_contention_index = (float(n) * float(handoff_factor)) / float(nt)
    regime_fault_interaction = 0.1 * rid * float(n - 1) / float(nt)

    if regime == "centralized":
        pre_task = 1 + max(0, n - 1)
    elif regime == "hierarchical":
        pre_task = 1 + depth * fan_out
    elif regime == "blackboard":
        pre_task = 1 + n * 2
    elif regime == "market":
        pre_task = 1 + min(n, 8) * 2
    else:
        pre_task = 1 + min(n * 3, 36)

    intra_task = max(0, handoff_factor - 1)
    latency_stress = 1.0 + 0.04 * float(n - 1) + 0.03 * rid
    drop_stress = min(1.45, 1.0 + 0.06 * rid * float(n - 1) / float(max(n, 1)))

    return {
        "coordination_regime": regime,
        "coordination_topology": regime,
        "agent_count": n,
        "hierarchy_depth": int(depth),
        "fan_out": int(fan_out),
        "handoff_factor": int(handoff_factor),
        "shared_state_contention": round(shared_state_contention, 4),
        "deadline_tightness": 1.0,
        "critical_path_length": int(nt),
        "branching_factor": float(min(4, fan_out)),
        "queue_contention_index": round(queue_contention_index, 4),
        "regime_fault_interaction": round(regime_fault_interaction, 4),
        "regime_id": int(rid),
        "pre_task_coordination_messages": int(pre_task),
        "intra_task_coordination_messages": int(intra_task),
        "latency_stress_multiplier": round(latency_stress, 4),
        "drop_stress_multiplier": round(drop_stress, 4),
    }


def counterfactual_profile_row(
    base: Dict[str, Any],
    coordination_regime: str,
    agent_count: int,
) -> Dict[str, Any]:
    """
    Build feature dict for a counterfactual (scenario tasks unchanged).
    """
    nt = int(base.get("num_tasks", 0) or 0)
    if nt < 1:
        nt = 1
    prof = coordination_experiment_profile(coordination_regime, agent_count, nt)
    out = dict(base)
    out.update(prof)
    return out
