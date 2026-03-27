#!/usr/bin/env python3
"""
Regenerate selected P3 replay corpus traces with consistent state_hash_after values.

Run from repo root:
  PYTHONPATH=impl/src python scripts/generate_p3_replay_corpus_traces.py

Writes JSON under bench/replay/corpus/ (long_horizon_trap, mixed_failure_trap,
benign_perturbation_pass, field_style_pass_variant_b).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "impl" / "src"))
os.environ.setdefault("LABTRUST_KERNEL_DIR", str(REPO / "kernel"))

from labtrust_portfolio.replay import apply_event  # noqa: E402
from labtrust_portfolio.trace import state_hash  # noqa: E402

CORPUS = REPO / "bench" / "replay" / "corpus"


def _actor(kind: str = "agent", id_: str = "a1") -> dict:
    return {"kind": kind, "id": id_}


def _build_events(
    specs: list[dict],
    wrong_index: int | None = None,
) -> list[dict]:
    state: dict = {}
    out: list[dict] = []
    for i, spec in enumerate(specs):
        ev = {
            "seq": spec.get("seq", i),
            "ts": float(spec.get("ts", i * 0.05)),
            "type": spec["type"],
            "actor": spec.get("actor", _actor()),
            "payload": dict(spec.get("payload", {})),
        }
        state = apply_event(state, ev)
        if wrong_index is not None and i == wrong_index:
            ev["state_hash_after"] = "f" * 64
        else:
            ev["state_hash_after"] = state_hash(state)
        out.append(ev)
    return out


def _wrap(
    run_id: str,
    scenario_id: str,
    seed: int,
    events: list[dict],
    final_wrong: bool = False,
) -> dict:
    state: dict = {}
    for ev in events:
        state = apply_event(state, ev)
    final = state_hash(state)
    if final_wrong:
        final = "e" * 64
    return {
        "version": "0.1",
        "run_id": run_id,
        "scenario_id": scenario_id,
        "seed": seed,
        "start_time_utc": "2020-01-01T00:00:00Z",
        "events": events,
        "final_state_hash": final,
    }


def main() -> int:
    CORPUS.mkdir(parents=True, exist_ok=True)

    # Long horizon: many correct task pairs, first mismatch at last event (seq 20).
    specs_long: list[dict] = []
    specs_long.append(
        {
            "type": "coordination_message",
            "actor": _actor("system", "sched"),
            "payload": {"detail": "warmup"},
        }
    )
    specs_long.append(
        {
            "type": "coordination_message",
            "actor": _actor("system", "sched"),
            "payload": {"detail": "warmup2"},
        }
    )
    for k in range(9):
        tid = f"t{k}"
        specs_long.append(
            {"type": "task_start", "payload": {"task_id": tid, "name": f"job{k}"}}
        )
        specs_long.append(
            {"type": "task_end", "payload": {"task_id": tid, "name": f"job{k}"}}
        )
    assert len(specs_long) == 20
    specs_long.append(
        {"type": "task_start", "payload": {"task_id": "t_bad", "name": "late"}}
    )
    events_long = _build_events(specs_long, wrong_index=20)
    trace_long = _wrap("long_horizon_trap_1", "long_horizon_trap", 1, events_long)
    (CORPUS / "long_horizon_trap_trace.json").write_text(
        json.dumps(trace_long, indent=2) + "\n", encoding="utf-8"
    )
    (CORPUS / "long_horizon_trap_expected.json").write_text(
        json.dumps(
            {
                "expected_replay_ok": False,
                "expected_divergence_at_seq": 20,
                "notes": "First per-event hash mismatch is intentionally late (stress localization index).",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    # Mixed failure: correct coord + task_start, mismatch on task_end at seq 2.
    # A second wrong hash is present at seq 5 in the file but is never reached.
    specs_mix = [
        {
            "type": "coordination_message",
            "actor": _actor("system", "sched"),
            "payload": {"detail": "assign"},
        },
        {
            "type": "task_start",
            "payload": {"task_id": "t0", "name": "mixed"},
        },
        {
            "type": "task_end",
            "payload": {"task_id": "t0", "name": "mixed"},
        },
        {
            "type": "task_start",
            "payload": {"task_id": "t1", "name": "never_reached"},
        },
        {
            "type": "task_end",
            "payload": {"task_id": "t1", "name": "never_reached"},
        },
        {
            "type": "task_start",
            "payload": {"task_id": "t2", "name": "latent"},
        },
    ]
    events_mix = _build_events(specs_mix, wrong_index=2)
    # Intentionally corrupt seq 5 (index 5) — replay stops at seq 2, so this is latent noise.
    events_mix[5]["state_hash_after"] = "c" * 64
    trace_mix = _wrap("mixed_failure_trap_1", "mixed_failure_trap", 2, events_mix)
    (CORPUS / "mixed_failure_trap_trace.json").write_text(
        json.dumps(trace_mix, indent=2) + "\n", encoding="utf-8"
    )
    (CORPUS / "mixed_failure_trap_expected.json").write_text(
        json.dumps(
            {
                "expected_replay_ok": False,
                "expected_divergence_at_seq": 2,
                "notes": "Engine reports the first per-event mismatch; latent inconsistency may exist later in the file.",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    # Benign perturbation pass: extra coordination noise; all hashes consistent.
    specs_benign: list[dict] = []
    for j in range(3):
        specs_benign.append(
            {
                "type": "coordination_message",
                "actor": _actor("system", "sched"),
                "payload": {"detail": f"noop_{j}"},
            }
        )
    specs_benign.append(
        {"type": "task_start", "payload": {"task_id": "t0", "name": "core"}}
    )
    specs_benign.append(
        {"type": "task_end", "payload": {"task_id": "t0", "name": "core"}}
    )
    events_benign = _build_events(specs_benign, wrong_index=None)
    trace_benign = _wrap(
        "benign_perturb_pass_1", "benign_perturbation", 3, events_benign
    )
    (CORPUS / "benign_perturbation_pass_trace.json").write_text(
        json.dumps(trace_benign, indent=2) + "\n", encoding="utf-8"
    )
    (CORPUS / "benign_perturbation_pass_expected.json").write_text(
        json.dumps(
            {
                "expected_replay_ok": True,
                "notes": "Irrelevant coordination events precede the task; replay should still pass.",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    # Second field-style family: short lab-style ordering, alternate actor ids.
    specs_b = [
        {
            "type": "coordination_message",
            "actor": _actor("system", "lab_orchestrator"),
            "payload": {"detail": "assign_task", "task_id": "prep:0"},
        },
        {
            "type": "task_start",
            "actor": _actor("agent", "lab_agent_2"),
            "payload": {"task_id": "prep:0", "name": "prep"},
        },
        {
            "type": "task_end",
            "actor": _actor("tool", "instrument_b"),
            "payload": {"task_id": "prep:0", "name": "prep"},
        },
        {
            "type": "coordination_message",
            "actor": _actor("system", "lab_orchestrator"),
            "payload": {"detail": "assign_task", "task_id": "measure:1"},
        },
        {
            "type": "task_start",
            "actor": _actor("agent", "lab_agent_2"),
            "payload": {"task_id": "measure:1", "name": "measure"},
        },
        {
            "type": "task_end",
            "actor": _actor("tool", "instrument_b"),
            "payload": {"task_id": "measure:1", "name": "measure"},
        },
    ]
    events_b = _build_events(specs_b, wrong_index=None)
    trace_b = _wrap(
        "field_style_pass_variant_b_v0",
        "field_style_lab_record_b",
        88,
        events_b,
    )
    (CORPUS / "field_style_pass_variant_b_trace.json").write_text(
        json.dumps(trace_b, indent=2) + "\n", encoding="utf-8"
    )
    (CORPUS / "field_style_pass_variant_b_expected.json").write_text(
        json.dumps(
            {
                "expected_replay_ok": True,
                "notes": "Second TRACE-conformant pass trace (thin lab-style slice), distinct from field_style_pass.",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print("Wrote long_horizon_trap_*, mixed_failure_trap_*, benign_perturbation_pass_*, field_style_pass_variant_b_*")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
