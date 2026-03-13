from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import json, random, uuid, math

from .trace import TraceEvent, build_trace, state_hash
from .maestro import maestro_report_from_trace
from .replay import replay_trace
from .evidence import build_evidence_bundle
from .release import build_release_manifest
from .schema import validate
from .scenario import load_scenario, get_scenario_task_names
from .conformance import write_conformance_artifact

KERNEL_VERSION = "0.1"

SCHEMA_TRACE = "trace/TRACE.v0.1.schema.json"
SCHEMA_MAESTRO = "eval/MAESTRO_REPORT.v0.1.schema.json"
SCHEMA_EVIDENCE = "mads/EVIDENCE_BUNDLE.v0.1.schema.json"
SCHEMA_RELEASE = "policy/RELEASE_MANIFEST.v0.1.schema.json"

SCHEMA_IDS = {
    SCHEMA_TRACE: "https://example.org/labtrust/kernel/trace/TRACE.v0.1",
    SCHEMA_MAESTRO: "https://example.org/labtrust/kernel/eval/MAESTRO_REPORT.v0.1",
    SCHEMA_EVIDENCE: "https://example.org/labtrust/kernel/mads/EVIDENCE_BUNDLE.v0.1",
    SCHEMA_RELEASE: "https://example.org/labtrust/kernel/policy/RELEASE_MANIFEST.v0.1",
}

def _task_id(name: str, idx: int) -> str:
    return f"{name}:{idx}"

DEFAULT_TASK_NAMES = ["receive_sample", "centrifuge", "analyze", "report_results"]


def _task_list_for_scenario(scenario_id: Optional[str]) -> List[str]:
    """Resolve task list from scenario YAML or default."""
    if not scenario_id:
        return list(DEFAULT_TASK_NAMES)
    try:
        scenario = load_scenario(scenario_id)
        names = get_scenario_task_names(scenario)
        return names if names else list(DEFAULT_TASK_NAMES)
    except (FileNotFoundError, ValueError):
        return list(DEFAULT_TASK_NAMES)


def run_thin_slice(
    out_dir: Path,
    seed: int = 7,
    delay_p95_ms: float = 50.0,
    drop_completion_prob: float = 0.02,
    scenario_id: Optional[str] = "toy_lab_v0",
    delay_fault_prob: float = 0.0,
    calibration_invalid_prob: float = 0.0,
    max_retries_per_task: int = 0,
) -> Dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)

    rng = random.Random(seed)
    run_id = f"run_{uuid.uuid4().hex[:10]}"
    sid = scenario_id or "toy_lab_v0"
    start_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    lam = -math.log(0.05) / max(1.0, delay_p95_ms)

    def sample_delay_ms() -> float:
        return rng.expovariate(lam)

    state: Dict[str, Any] = {"tasks": {}, "coord_msgs": 0}
    events = []
    ts = 0.0
    seq = 0

    def _apply_state_for_hash(s: Dict[str, Any], ev_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        ns = dict(s)
        tasks = dict(ns.get("tasks", {}))
        if ev_type == "task_start":
            tasks[payload["task_id"]] = {"status": "running", "name": payload.get("name", "")}
        elif ev_type == "task_end":
            tasks[payload["task_id"]] = {"status": "done", "name": payload.get("name", "")}
        ns["tasks"] = tasks
        if ev_type == "coordination_message":
            ns["coord_msgs"] = int(ns.get("coord_msgs", 0)) + 1
        if ev_type == "fault_injected":
            faults = list(ns.get("faults", []))
            faults.append(payload.get("fault", "unknown_fault"))
            ns["faults"] = faults
        return ns

    def emit(ev_type: str, actor_kind: str, actor_id: str, payload: Dict[str, Any]) -> None:
        nonlocal seq, ts, state
        ts += sample_delay_ms() / 1000.0
        state = _apply_state_for_hash(state, ev_type, payload)
        events.append(TraceEvent(seq=seq, ts=ts, type=ev_type, actor_kind=actor_kind, actor_id=actor_id, payload=payload, state_hash_after=state_hash(state)))
        seq += 1

    task_names = _task_list_for_scenario(sid)
    max_retries = max(0, int(max_retries_per_task))

    for i, name in enumerate(task_names):
        tid = _task_id(name, i)
        emit("coordination_message", "system", "scheduler", {"detail": "assign_task", "task_id": tid})
        task_done = False
        for attempt in range(max_retries + 1):
            emit("task_start", "agent", "agent_1", {"task_id": tid, "name": name})

            if delay_fault_prob > 0 and rng.random() < delay_fault_prob:
                emit("fault_injected", "system", "fault_injector", {"fault": "delay", "task_id": tid})
                ts += sample_delay_ms() * 2.0 / 1000.0

            if rng.random() < drop_completion_prob:
                emit("fault_injected", "system", "fault_injector", {"fault": "drop_completion", "task_id": tid})
                if attempt < max_retries:
                    continue
                break

            if calibration_invalid_prob > 0 and rng.random() < calibration_invalid_prob:
                emit("fault_injected", "system", "fault_injector", {"fault": "calibration_invalid", "task_id": tid})

            emit("task_end", "tool", "lab_device_1", {"task_id": tid, "name": name})
            task_done = True
            break
        if not task_done:
            pass  # task dropped after all retries; no task_end

    final_hash = state_hash(state)
    trace = build_trace(run_id, sid, seed, start_time, events, final_hash, metadata={
        "delay_p95_ms": delay_p95_ms,
        "drop_completion_prob": drop_completion_prob,
        "delay_fault_prob": delay_fault_prob,
        "calibration_invalid_prob": calibration_invalid_prob,
        "max_retries_per_task": max_retries,
    })

    trace_path = out_dir / "trace.json"
    maestro_path = out_dir / "maestro_report.json"
    evidence_path = out_dir / "evidence_bundle.json"
    release_path = out_dir / "release_manifest.json"

    trace_path.write_text(json.dumps(trace, indent=2) + "\n", encoding="utf-8")

    maestro = maestro_report_from_trace(run_id, scenario_id, trace)
    maestro_path.write_text(json.dumps(maestro, indent=2) + "\n", encoding="utf-8")

    replay_ok, replay_diag = replay_trace(trace)

    schema_ok = True
    try:
        validate(trace, SCHEMA_TRACE)
        validate(maestro, SCHEMA_MAESTRO)
    except Exception:
        schema_ok = False

    evidence = build_evidence_bundle(
        run_id=run_id,
        kernel_version=KERNEL_VERSION,
        artifacts=[trace_path, maestro_path],
        schema_ids=[SCHEMA_IDS[SCHEMA_TRACE], SCHEMA_IDS[SCHEMA_MAESTRO]],
        schema_validation_ok=schema_ok,
        replay_ok=replay_ok,
        replay_diag=replay_diag,
        verification_mode="evaluator",
    )

    try:
        validate(evidence, SCHEMA_EVIDENCE)
    except Exception:
        schema_ok = False
        evidence["verification"]["schema_validation_ok"] = False

    evidence_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")

    release = build_release_manifest(
        release_id=f"release_{run_id}",
        kernel_version=KERNEL_VERSION,
        artifacts=[trace_path, maestro_path, evidence_path],
    )
    try:
        validate(release, SCHEMA_RELEASE)
    except Exception:
        pass

    release_path.write_text(json.dumps(release, indent=2) + "\n", encoding="utf-8")

    conformance_path = write_conformance_artifact(out_dir)

    return {
        "trace": trace_path,
        "maestro_report": maestro_path,
        "evidence_bundle": evidence_path,
        "release_manifest": release_path,
        "conformance": conformance_path,
    }
