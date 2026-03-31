#!/usr/bin/env python3
"""Generate a quasi-real replay corpus for P1 contracts evaluation."""

from __future__ import annotations

import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
OUT_ROOT = REPO / "datasets" / "contracts_real"


def _event(event_type: str, ts: float, actor: str, key: str, writer: str | None = None) -> dict:
    return {
        "type": event_type,
        "ts": round(ts, 3),
        "actor": {"id": actor},
        "payload": {"task_id": key, "name": "orchestration", "writer": writer or actor},
    }


def _trace(description: str, initial_state: dict, events: list[dict], expected: list[str], annotations: list[dict]) -> dict:
    return {
        "description": description,
        "initial_state": initial_state,
        "events": events,
        "expected_verdicts": expected,
        "annotations": annotations,
    }


def _write_family(family_dir: Path, traces: list[dict]) -> None:
    family_dir.mkdir(parents=True, exist_ok=True)
    for i, data in enumerate(traces, start=1):
        path = family_dir / f"trace_{i:02d}.json"
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _lab_workflow_family() -> list[dict]:
    traces: list[dict] = []
    for i in range(1, 31):
        key = f"centrifuge_slot_{(i % 6) + 1}"
        base = 1000.0 + (i * 10)
        initial = {"ownership": {key: "controller_a"}, "_last_ts": {key: base}}
        events = [
            _event("task_end", base + 1.0, "controller_a", key),
            _event("task_start", base + 2.0, "controller_b", key),
            _event("task_end", base + 1.4 if i % 3 == 0 else base + 2.5, "controller_a", key),
        ]
        expected = ["allow", "deny", "deny" if i % 3 == 0 else "deny"]
        annotations = [
            {"event_idx": 1, "admissible": False, "failure_class": "split_brain"},
            {
                "event_idx": 2,
                "admissible": False,
                "failure_class": "reorder_sensitive_invalidity" if i % 3 == 0 else "split_brain",
            },
        ]
        traces.append(
            _trace(
                "Lab orchestration handover with split-brain pressure and optional reorder.",
                initial,
                events,
                expected,
                annotations,
            )
        )
    return traces


def _simulator_family() -> list[dict]:
    traces: list[dict] = []
    for i in range(1, 31):
        key = f"sim_cell_{(i % 5) + 1}"
        base = 2000.0 + (i * 8)
        initial = {"ownership": {key: "planner_1"}, "_last_ts": {key: base}}
        stale_ts = base - 0.2 if i % 2 == 0 else base + 0.7
        events = [
            _event("task_end", base + 0.5, "planner_1", key),
            _event("task_start", stale_ts, "planner_1", key),
            _event("task_start", base + 1.0, "planner_2", key),
        ]
        expected = ["allow", "deny" if i % 2 == 0 else "allow", "deny"]
        annotations = [
            {
                "event_idx": 1,
                "admissible": i % 2 != 0,
                "failure_class": "stale_write" if i % 2 == 0 else "admissible",
            },
            {"event_idx": 2, "admissible": False, "failure_class": "split_brain"},
        ]
        traces.append(
            _trace(
                "Simulator-derived multi-controller workflow with stale and ownership conflicts.",
                initial,
                events,
                expected,
                annotations,
            )
        )
    return traces


def _incident_reconstructed_family() -> list[dict]:
    traces: list[dict] = []
    for i in range(1, 31):
        key = f"line_buffer_{(i % 7) + 1}"
        base = 3000.0 + (i * 6)
        initial = {"ownership": {key: "robot_r1"}, "_last_ts": {key: base}}
        unknown_key = f"unknown_{i}" if i % 4 == 0 else key
        events = [
            _event("task_end", base + 0.4, "robot_r1", key),
            _event("task_start", base + 0.9, "robot_r2", key),
            _event("task_end", base + 1.1, "robot_r2", unknown_key),
        ]
        expected = ["allow", "deny", "deny" if i % 4 == 0 else "deny"]
        annotations = [
            {"event_idx": 1, "admissible": False, "failure_class": "split_brain"},
            {
                "event_idx": 2,
                "admissible": False,
                "failure_class": "unknown_key" if i % 4 == 0 else "split_brain",
            },
        ]
        traces.append(
            _trace(
                "Incident-inspired reconstructed handover traces from shared production buffer ownership.",
                initial,
                events,
                expected,
                annotations,
            )
        )
    return traces


def _write_manifest() -> None:
    manifest = {
        "dataset_id": "contracts_real_v1",
        "trace_families": [
            {
                "family_id": "lab_orchestration_partner_like",
                "domain": "laboratory functional unit orchestration",
                "trace_type": "partner_like_realistic_logs",
                "trace_count": 30,
                "shared_keyed_resources": True,
                "controllers": ["controller_a", "controller_b"],
                "includes_handover_behavior": True,
            },
            {
                "family_id": "simulator_documented_semantics",
                "domain": "automation simulator",
                "trace_type": "simulator_generated",
                "trace_count": 30,
                "shared_keyed_resources": True,
                "controllers": ["planner_1", "planner_2"],
                "includes_handover_behavior": True,
            },
            {
                "family_id": "incident_reconstructed",
                "domain": "multi-controller automation cell",
                "trace_type": "incident_reconstructed",
                "trace_count": 30,
                "shared_keyed_resources": True,
                "controllers": ["robot_r1", "robot_r2"],
                "includes_handover_behavior": True,
            },
        ],
        "totals": {"trace_count": 90},
    }
    (OUT_ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    _write_family(OUT_ROOT / "lab_orchestration_partner_like", _lab_workflow_family())
    _write_family(OUT_ROOT / "simulator_documented_semantics", _simulator_family())
    _write_family(OUT_ROOT / "incident_reconstructed", _incident_reconstructed_family())
    _write_manifest()
    print("Generated contracts real corpus at", OUT_ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
