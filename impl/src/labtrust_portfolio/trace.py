from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List
from .hashing import sha256_bytes
import json

def state_hash(state: Dict[str, Any]) -> str:
    b = json.dumps(state, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return sha256_bytes(b)

@dataclass
class TraceEvent:
    seq: int
    ts: float
    type: str
    actor_kind: str
    actor_id: str
    payload: Dict[str, Any]
    state_hash_after: str

    def to_json(self) -> Dict[str, Any]:
        return {
            "seq": self.seq,
            "ts": self.ts,
            "type": self.type,
            "actor": {"kind": self.actor_kind, "id": self.actor_id},
            "payload": self.payload,
            "state_hash_after": self.state_hash_after,
        }

def build_trace(run_id: str, scenario_id: str, seed: int, start_time_utc: str, events: List[TraceEvent], final_state_hash: str, metadata: Dict[str, Any] | None = None) -> Dict[str, Any]:
    t: Dict[str, Any] = {
        "version": "0.1",
        "run_id": run_id,
        "scenario_id": scenario_id,
        "seed": seed,
        "start_time_utc": start_time_utc,
        "events": [e.to_json() for e in events],
        "final_state_hash": final_state_hash,
    }
    if metadata is not None:
        t["metadata"] = metadata
    return t
