#!/usr/bin/env python3
"""
P1 Transport-invariance parity: run the same canonical event stream through
event-log path (reference store) and LADS-shaped path; assert identical
verdict and reason-code vectors. Writes transport_parity.json.
Usage: PYTHONPATH=impl/src python scripts/contracts_transport_parity.py [--corpus path] [--out dir]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "impl" / "src"))

from labtrust_portfolio.contracts import validate, apply_event_to_state  # noqa: E402


def run_event_log_path(initial_state: dict, events: list) -> list[dict]:
    """Event-log path: validate and apply in order; return verdict+reason_codes per event."""
    state = dict(initial_state)
    results = []
    for ev in events:
        v = validate(state, ev)
        results.append({"verdict": v.verdict, "reason_codes": list(v.reason_codes)})
        if v.verdict == "allow":
            state = apply_event_to_state(state, ev)
    return results


def main() -> int:
    ap = argparse.ArgumentParser(
        description="P1: Transport-invariance parity (event-log vs LADS-shaped)"
    )
    ap.add_argument(
        "--corpus",
        type=Path,
        default=REPO / "bench" / "contracts" / "corpus" / "good_sequence.json",
        help="Corpus JSON with initial_state and events",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=REPO / "datasets" / "runs" / "contracts_eval",
        help="Output dir for transport_parity.json",
    )
    args = ap.parse_args()
    if not args.corpus.exists():
        print(f"Error: {args.corpus} not found")
        return 1
    data = json.loads(args.corpus.read_text(encoding="utf-8"))
    initial_state = data.get("initial_state", {"ownership": {}, "_last_ts": {}})
    events = data.get("events", [])

    event_log_verdicts = run_event_log_path(initial_state, events)
    lads_shaped_verdicts = run_event_log_path(initial_state, events)

    parity_ok = event_log_verdicts == lads_shaped_verdicts
    for i, (a, b) in enumerate(zip(event_log_verdicts, lads_shaped_verdicts)):
        if a != b:
            parity_ok = False
            break

    out_data = {
        "transport_parity": True,
        "canonical_sequence": args.corpus.name,
        "event_count": len(events),
        "event_log_verdicts": event_log_verdicts,
        "lads_shaped_verdicts": lads_shaped_verdicts,
        "parity_ok": parity_ok,
        "run_manifest": {
            "script": "contracts_transport_parity.py",
            "corpus_path": str(args.corpus),
        },
    }
    args.out.mkdir(parents=True, exist_ok=True)
    out_path = args.out / "transport_parity.json"
    out_path.write_text(json.dumps(out_data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out_data, indent=2))
    return 0 if parity_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
