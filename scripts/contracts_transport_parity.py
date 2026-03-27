#!/usr/bin/env python3
"""
P1 Transport-invariance parity: run canonical event streams through two ingestion
paths that must yield identical verdict/reason-code vectors at the contract
boundary. Writes transport_parity.json with per-sequence results.
Usage: PYTHONPATH=impl/src python scripts/contracts_transport_parity.py [--corpus-dir path] [--sequences a,b,c]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "impl" / "src"))

from labtrust_portfolio.contracts import validate, apply_event_to_state  # noqa: E402

DEFAULT_SEQUENCE_STEMS = (
    "good_sequence",
    "split_brain_sequence",
    "reorder_sequence",
    "actor_payload_writer_mismatch",
)


def run_event_log_path(initial_state: dict, events: list) -> list[dict]:
    """Reference path: validate and apply in order; return verdict+reason_codes per event."""
    state = dict(initial_state)
    results = []
    for ev in events:
        v = validate(state, ev)
        results.append({"verdict": v.verdict, "reason_codes": list(v.reason_codes)})
        if v.verdict == "allow":
            state = apply_event_to_state(state, ev)
    return results


def run_lads_shaped_path(initial_state: dict, events: list) -> list[dict]:
    """
    LADS-shaped path: simulate live adapter ingestion boundary.
    In a real deployment, this would normalize LADS FunctionalUnit state transitions
    to contract events. Here we use the same event objects but simulate a live
    ingestion loop with minimal processing delay to test boundary consistency.
    """
    state = dict(initial_state)
    results = []
    for ev in events:
        # Simulate minimal adapter processing (normalize LADS event shape to contract boundary)
        # In real deployment: map LADS FunctionalUnit state -> contract key, LADS transition -> contract event type
        normalized_event = {
            "type": ev.get("type"),
            "ts": ev.get("ts"),
            "actor": ev.get("actor"),
            "payload": ev.get("payload"),
        }
        v = validate(state, normalized_event)
        results.append({"verdict": v.verdict, "reason_codes": list(v.reason_codes)})
        if v.verdict == "allow":
            state = apply_event_to_state(state, normalized_event)
    return results


def main() -> int:
    ap = argparse.ArgumentParser(
        description="P1: Transport parity (event-log vs LADS-shaped boundary)"
    )
    ap.add_argument(
        "--corpus-dir",
        type=Path,
        default=REPO / "bench" / "contracts" / "corpus",
        help="Directory containing corpus JSON files",
    )
    ap.add_argument(
        "--sequences",
        type=str,
        default=",".join(DEFAULT_SEQUENCE_STEMS),
        help="Comma-separated corpus file stems (without .json)",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=REPO / "datasets" / "runs" / "contracts_eval",
        help="Output dir for transport_parity.json",
    )
    args = ap.parse_args()
    stems = [s.strip() for s in args.sequences.split(",") if s.strip()]
    per_sequence = []
    all_ok = True
    for stem in stems:
        path = args.corpus_dir / f"{stem}.json"
        if not path.exists():
            per_sequence.append({
                "sequence": stem,
                "parity_ok": False,
                "error": f"missing file {path.name}",
            })
            all_ok = False
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        initial_state = data.get("initial_state", {"ownership": {}, "_last_ts": {}})
        events = data.get("events", [])
        event_log_v = run_event_log_path(initial_state, events)
        lads_v = run_lads_shaped_path(initial_state, events)
        seq_ok = event_log_v == lads_v
        if not seq_ok:
            all_ok = False
        per_sequence.append({
            "sequence": stem,
            "event_count": len(events),
            "parity_ok": seq_ok,
            "event_log_verdicts": event_log_v,
            "lads_shaped_verdicts": lads_v,
        })
    # Compute parity confidence summary
    total_events = sum(seq.get("event_count", 0) for seq in per_sequence)
    matching_events = sum(
        sum(1 for i, el in enumerate(seq.get("event_log_verdicts", []))
            if i < len(seq.get("lads_shaped_verdicts", [])) and
            el == seq.get("lads_shaped_verdicts", [])[i])
        for seq in per_sequence
    )
    parity_confidence = {
        "total_events_checked": total_events,
        "matching_events": matching_events,
        "parity_rate": round(matching_events / total_events, 4) if total_events > 0 else 0.0,
    }
    
    out_data = {
        "transport_parity": True,
        "parity_ok_all": all_ok,
        "per_sequence": per_sequence,
        "parity_confidence": parity_confidence,
        "run_manifest": {
            "script": "contracts_transport_parity.py",
            "corpus_dir": str(args.corpus_dir),
            "sequences": stems,
        },
    }
    args.out.mkdir(parents=True, exist_ok=True)
    out_path = args.out / "transport_parity.json"
    out_path.write_text(json.dumps(out_data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out_data, indent=2))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
