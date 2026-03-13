"""
REP-CPS (P2): Reference aggregator and attack harness.
Robust aggregation with rate limiting; compromised-agent update generator for testing.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


def aggregate(
    variable: str,
    updates: List[Dict[str, Any]],
    method: str = "trimmed_mean",
    trim_fraction: float = 0.25,
    rate_limit: Optional[int] = None,
    max_age_sec: Optional[float] = None,
    current_ts: float = 0.0,
) -> float:
    """
    Robust aggregation of updates for one variable. Updates are dicts with
    keys: value (float), ts (float), agent_id (str). Optionally apply
    rate_limit (max updates per agent) and max_age_sec (drop older).
    """
    if not updates:
        return 0.0
    if max_age_sec is not None and current_ts > 0:
        updates = [u for u in updates if (current_ts - u.get("ts", 0)) <= max_age_sec]
    if not updates:
        return 0.0
    if rate_limit is not None:
        by_agent: Dict[str, List[Dict[str, Any]]] = {}
        for u in updates:
            aid = u.get("agent_id", "unknown")
            by_agent.setdefault(aid, []).append(u)
        updates = []
        for agent_updates in by_agent.values():
            updates.extend(sorted(agent_updates, key=lambda x: x.get("ts", 0))[-rate_limit:])
    values = [float(u.get("value", 0)) for u in updates]
    values.sort()
    n = len(values)
    if method == "median":
        return values[n // 2] if n else 0.0
    if method == "trimmed_mean" and trim_fraction > 0 and n > 2:
        k = max(1, int(n * trim_fraction))
        trimmed = values[k : n - k] if (n - 2 * k) > 0 else values
        return sum(trimmed) / len(trimmed) if trimmed else values[n // 2]
    if method == "clipping" and n > 0:
        clip_lo = values[max(0, int(n * 0.1))]
        clip_hi = values[min(n - 1, int(n * 0.9))]
        clipped = [max(clip_lo, min(clip_hi, v)) for v in values]
        return sum(clipped) / len(clipped)
    if method == "median_of_means" and n >= 4:
        bucket_size = max(1, n // 4)
        means = []
        for i in range(0, n, bucket_size):
            bucket = values[i : i + bucket_size]
            if bucket:
                means.append(sum(bucket) / len(bucket))
        means.sort()
        return means[len(means) // 2] if means else values[n // 2]
    return sum(values) / n


def compromised_updates(
    variable: str,
    num_compromised: int,
    extreme_value: float,
    ts: float = 0.0,
    agent_prefix: str = "compromised_",
) -> List[Dict[str, Any]]:
    """
    Attack harness: generate updates that mimic Byzantine agents (all sending
    the same extreme value). Used to test robust aggregation.
    """
    return [
        {"variable": variable, "value": extreme_value, "ts": ts, "agent_id": f"{agent_prefix}{i}"}
        for i in range(num_compromised)
    ]


def auth_hook(update: Dict[str, Any], allowed_agents: Optional[List[str]] = None) -> bool:
    """
    Stub auth hook: accept if agent_id is in allowed_agents (or accept all if None).
    Real implementation would verify signature or attested identity.
    """
    if allowed_agents is None:
        return True
    return update.get("agent_id") in allowed_agents
