from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import json, random, uuid, math

from .trace import TraceEvent, build_trace, state_hash
from .maestro import maestro_report_from_trace
from .replay import replay_trace
from .evidence import build_evidence_bundle
from .hashing import sha256_bytes
from .release import build_release_manifest
from .schema import validate
from .scenario import load_scenario, get_scenario_task_names, get_resource_graph
from .conformance import write_conformance_artifact
from .coordination_profile import coordination_experiment_profile

KERNEL_VERSION = "0.1"

SCHEMA_TRACE = "trace/TRACE.v0.1.schema.json"
SCHEMA_MAESTRO = "eval/MAESTRO_REPORT.v0.2.schema.json"
SCHEMA_EVIDENCE = "mads/EVIDENCE_BUNDLE.v0.1.schema.json"
SCHEMA_RELEASE = "policy/RELEASE_MANIFEST.v0.1.schema.json"

SCHEMA_IDS = {
    SCHEMA_TRACE: "https://example.org/labtrust/kernel/trace/TRACE.v0.1",
    SCHEMA_MAESTRO: "https://example.org/labtrust/kernel/eval/MAESTRO_REPORT.v0.2",
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
    rep_cps_safety_gate_ok: Optional[bool] = None,
    timeout_fault_prob: float = 0.0,
    partial_result_fault_prob: float = 0.0,
    reordered_event_fault_prob: float = 0.0,
    resource_contention_spike_prob: float = 0.0,
    invalid_action_injection_prob: float = 0.0,
    agent_nonresponse_fault_prob: float = 0.0,
    duplicate_completion_prob: float = 0.0,
    conflicting_action_prob: float = 0.0,
    constraint_guard_trigger_prob: float = 0.0,
    sensor_stale_prob: float = 0.0,
    shutdown_after_first_fault: bool = False,
    deadline_miss_prob: float = 0.0,
    **kwargs: Any,
) -> Dict[str, Path]:
    """
    Thin-slice harness: emits TRACE v0.1 and MAESTRO_REPORT v0.2.
    Timestamps `ts` are synthetic scenario seconds (not host wall clock).

    Optional P5 sweep kwargs (from ``generate_multiscenario_runs.py``):
    ``agent_count`` (int), ``coordination_regime`` (str), ``fault_setting_label`` (str).
    These change coordination_message volume, drop stress, actor rotation, and trace metadata.
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    rng = random.Random(seed)
    run_id = f"run_{uuid.uuid4().hex[:10]}"
    sid = scenario_id or "toy_lab_v0"
    start_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    lam = -math.log(0.05) / max(1.0, delay_p95_ms)

    def sample_delay_ms() -> float:
        return rng.expovariate(lam)

    state: Dict[str, Any] = {"tasks": {}, "coord_msgs": 0}
    events: List[TraceEvent] = []
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

    def emit(
        ev_type: str,
        actor_kind: str,
        actor_id: str,
        payload: Dict[str, Any],
        delay_mult: float = 1.0,
    ) -> None:
        nonlocal seq, ts, state
        ts += sample_delay_ms() * max(0.05, float(delay_mult)) / 1000.0
        state = _apply_state_for_hash(state, ev_type, payload)
        events.append(
            TraceEvent(
                seq=seq,
                ts=ts,
                type=ev_type,
                actor_kind=actor_kind,
                actor_id=actor_id,
                payload=payload,
                state_hash_after=state_hash(state),
            )
        )
        seq += 1

    sched_dep = False
    resource_graph: Dict[str, Any] | None = None
    try:
        scenario_data = load_scenario(sid)
        names = get_scenario_task_names(scenario_data)
        task_names = names if names else list(DEFAULT_TASK_NAMES)
        sched_dep = bool(scenario_data.get("rep_cps_scheduling_dependent"))
        resource_graph = get_resource_graph(scenario_data)
    except (FileNotFoundError, ValueError, RuntimeError, OSError):
        task_names = _task_list_for_scenario(sid)
        sched_dep = False
        resource_graph = None

    lab_queue = bool(resource_graph and resource_graph.get("queue_contention"))
    if lab_queue and resource_contention_spike_prob == 0.0:
        resource_contention_spike_prob = max(resource_contention_spike_prob, 0.02)
    block_schedule = sched_dep and rep_cps_safety_gate_ok is False
    max_retries = max(0, int(max_retries_per_task))

    planned_n = len(task_names)
    n_agents = max(1, int(kwargs.get("agent_count", 1) or 1))
    coord_regime = str(kwargs.get("coordination_regime") or "centralized")
    fault_setting_label = str(kwargs.get("fault_setting_label") or "unknown")
    cprof = coordination_experiment_profile(coord_regime, n_agents, planned_n)
    lat_mult = float(cprof["latency_stress_multiplier"])
    effective_drop_p = min(
        0.92,
        float(drop_completion_prob) * float(cprof["drop_stress_multiplier"]),
    )
    calibration_invalidated = False
    run_fault_seen = False
    shutdown_triggered = False

    def inject_auxiliary_faults(
        tid: str,
        name: str,
        task_fault_ctx: Dict[str, bool],
    ) -> Optional[str]:
        """Return 'stop_task' to abort current task attempt, else None."""
        nonlocal run_fault_seen, calibration_invalidated, shutdown_triggered, ts

        def touch_fault(code: str) -> None:
            nonlocal run_fault_seen
            run_fault_seen = True
            task_fault_ctx["had_aux_fault"] = True
            emit("fault_injected", "system", "fault_injector", {"fault": code, "task_id": tid})

        if deadline_miss_prob > 0 and rng.random() < deadline_miss_prob:
            touch_fault("deadline_risk")
            emit("deadline_miss", "system", "scheduler", {"task_id": tid, "detail": "synthetic_deadline"})

        if timeout_fault_prob > 0 and rng.random() < timeout_fault_prob:
            touch_fault("timeout")
            emit("recovery_attempt", "agent", "agent_1", {"task_id": tid, "reason": "timeout_retry"})
            ts += sample_delay_ms() * 3.0 / 1000.0

        if agent_nonresponse_fault_prob > 0 and rng.random() < agent_nonresponse_fault_prob:
            touch_fault("agent_nonresponse")
            emit("worker_stall", "agent", "agent_1", {"task_id": tid, "detail": "no_response_window"})
            emit("recovery_attempt", "agent", "agent_1", {"task_id": tid, "reason": "worker_stall_escalation"})
            ts += sample_delay_ms() * 2.0 / 1000.0

        if invalid_action_injection_prob > 0 and rng.random() < invalid_action_injection_prob:
            touch_fault("invalid_action_injection")
            emit("invalid_action", "agent", "agent_1", {"task_id": tid, "action": "illegal_transition"})
            emit("blocked_action", "system", "guard", {"task_id": tid, "reason": "policy_block"})

        if resource_contention_spike_prob > 0 and rng.random() < resource_contention_spike_prob:
            touch_fault("resource_contention_spike")
            emit(
                "resource_conflict",
                "system",
                "station_controller",
                {"task_id": tid, "resource": "prep_station", "detail": "queue_spike"},
            )

        if sensor_stale_prob > 0 and rng.random() < sensor_stale_prob:
            touch_fault("sensor_stale")
            emit(
                "safety_violation",
                "system",
                "instrument_guard",
                {
                    "violation_type": "stale_state",
                    "detail": "instrument_reading_stale",
                    "task_id": tid,
                },
            )

        if conflicting_action_prob > 0 and rng.random() < conflicting_action_prob:
            touch_fault("conflicting_action")
            emit("wasted_action", "agent", "agent_2", {"task_id": tid, "detail": "superseded_plan_step"})

        if duplicate_completion_prob > 0 and rng.random() < duplicate_completion_prob:
            touch_fault("duplicate_completion")
            emit("duplicate_action", "tool", "lab_device_1", {"task_id": tid, "detail": "duplicate_submit"})

        if partial_result_fault_prob > 0 and rng.random() < partial_result_fault_prob:
            touch_fault("partial_result")
            emit("recovery_attempt", "agent", "agent_1", {"task_id": tid, "reason": "partial_result_rework"})

        if reordered_event_fault_prob > 0 and rng.random() < reordered_event_fault_prob:
            touch_fault("reordered_event")

        if shutdown_after_first_fault and run_fault_seen and not shutdown_triggered:
            shutdown_triggered = True
            emit(
                "safe_shutdown_initiated",
                "system",
                "supervisor",
                {"detail": "conservative_shutdown_after_fault", "task_id": tid},
            )
            return "stop_task"

        return None

    for i, name in enumerate(task_names):
        tid = _task_id(name, i)
        emit(
            "coordination_message",
            "system",
            "scheduler",
            {
                "detail": "assign_task",
                "task_id": tid,
                "regime": cprof["coordination_regime"],
            },
        )
        for k in range(max(0, int(cprof["pre_task_coordination_messages"]) - 1)):
            emit(
                "coordination_message",
                "system",
                "scheduler",
                {
                    "detail": "regime_pre_task",
                    "task_id": tid,
                    "step": k,
                    "regime": cprof["coordination_regime"],
                },
                delay_mult=0.02 * lat_mult,
            )
        task_done = False
        had_fault_this_task = False
        disposition_risk = False
        if name == "disposition_commit" and sid == "lab_profile_v0":
            disposition_risk = calibration_invalidated or (
                constraint_guard_trigger_prob > 0 and rng.random() < constraint_guard_trigger_prob
            )
            if disposition_risk:
                emit(
                    "constraint_guard_trigger",
                    "system",
                    "disposition_gate",
                    {"task_id": tid, "detail": "disposition_commit_blocked_lab"},
                )
                emit(
                    "safety_violation",
                    "system",
                    "ponr_guard",
                    {
                        "violation_type": "disposition_under_risk",
                        "detail": "calibration_or_guard_not_clear",
                    },
                )
                emit(
                    "ponr_violation",
                    "system",
                    "ponr_monitor",
                    {"task_id": tid, "stage": "disposition_commit"},
                )

        for attempt in range(max_retries + 1):
            if shutdown_triggered:
                break

            aux_ctx = {"had_aux_fault": False}
            actor_id = f"agent_{1 + (i % n_agents)}"
            emit("task_start", "agent", actor_id, {"task_id": tid, "name": name})

            if block_schedule:
                emit(
                    "fault_injected",
                    "system",
                    "fault_injector",
                    {"fault": "scheduling_denied_rep_cps_gate", "task_id": tid},
                )
                run_fault_seen = True
                break

            if inject_auxiliary_faults(tid, name, aux_ctx) == "stop_task":
                break
            if aux_ctx["had_aux_fault"]:
                had_fault_this_task = True

            if delay_fault_prob > 0 and rng.random() < delay_fault_prob:
                emit("fault_injected", "system", "fault_injector", {"fault": "delay", "task_id": tid})
                had_fault_this_task = True
                run_fault_seen = True
                ts += sample_delay_ms() * 2.0 / 1000.0

            if rng.random() < effective_drop_p:
                emit("fault_injected", "system", "fault_injector", {"fault": "drop_completion", "task_id": tid})
                had_fault_this_task = True
                run_fault_seen = True
                if attempt < max_retries:
                    emit(
                        "recovery_attempt",
                        "agent",
                        "agent_1",
                        {"task_id": tid, "reason": "retry_after_drop"},
                    )
                    continue
                if shutdown_after_first_fault and run_fault_seen:
                    shutdown_triggered = True
                    emit(
                        "safe_shutdown_initiated",
                        "system",
                        "supervisor",
                        {"detail": "conservative_shutdown_after_fault", "task_id": tid},
                    )
                break

            if calibration_invalid_prob > 0 and rng.random() < calibration_invalid_prob:
                emit(
                    "fault_injected",
                    "system",
                    "fault_injector",
                    {"fault": "calibration_invalid", "task_id": tid},
                )
                had_fault_this_task = True
                run_fault_seen = True
                calibration_invalidated = True
                emit(
                    "safety_violation",
                    "system",
                    "instrument_guard",
                    {
                        "violation_type": "calibration_invalid",
                        "detail": "instrument_calibration_state_invalid",
                        "task_id": tid,
                    },
                )

            aux_ctx2 = {"had_aux_fault": False}
            if inject_auxiliary_faults(tid, name, aux_ctx2) == "stop_task":
                break
            if aux_ctx2["had_aux_fault"]:
                had_fault_this_task = True

            for h in range(int(cprof["intra_task_coordination_messages"])):
                peer = f"agent_{1 + ((i + h + 1) % n_agents)}"
                emit(
                    "coordination_message",
                    "agent",
                    peer,
                    {
                        "detail": "handoff",
                        "task_id": tid,
                        "regime": cprof["coordination_regime"],
                    },
                    delay_mult=0.015 * lat_mult,
                )

            emit("task_end", "tool", "lab_device_1", {"task_id": tid, "name": name})
            if had_fault_this_task:
                emit(
                    "recovery_succeeded",
                    "system",
                    "supervisor",
                    {"task_id": tid, "detail": "task_completed_after_fault"},
                )
            if name in ("centrifuge", "analyze", "report_results") and calibration_invalidated:
                emit(
                    "coordination_message",
                    "system",
                    "qc_coordinator",
                    {"detail": "recalibration_ok", "task_id": tid},
                )
                calibration_invalidated = False

            if disposition_risk:
                emit(
                    "unsafe_task_completion",
                    "tool",
                    "lab_device_1",
                    {"task_id": tid, "detail": "completed_under_prior_violation"},
                )

            task_done = True
            break

        if shutdown_triggered:
            break

    completed_n = sum(1 for e in events if e.type == "task_end")
    all_tasks_done = completed_n >= planned_n and planned_n > 0
    if all_tasks_done and not shutdown_triggered:
        emit("safe_state_reached", "system", "supervisor", {"detail": "all_tasks_terminal_safe"})

    final_hash = state_hash(state)
    trace = build_trace(
        run_id,
        sid,
        seed,
        start_time,
        events,
        final_hash,
        metadata={
            "delay_p95_ms": delay_p95_ms,
            "drop_completion_prob": drop_completion_prob,
            "delay_fault_prob": delay_fault_prob,
            "calibration_invalid_prob": calibration_invalid_prob,
            "max_retries_per_task": max_retries,
            "rep_cps_scheduling_dependent": sched_dep,
            "rep_cps_safety_gate_ok": rep_cps_safety_gate_ok,
            "planned_task_count": planned_n,
            "timeout_fault_prob": timeout_fault_prob,
            "partial_result_fault_prob": partial_result_fault_prob,
            "reordered_event_fault_prob": reordered_event_fault_prob,
            "resource_contention_spike_prob": resource_contention_spike_prob,
            "invalid_action_injection_prob": invalid_action_injection_prob,
            "agent_nonresponse_fault_prob": agent_nonresponse_fault_prob,
            "duplicate_completion_prob": duplicate_completion_prob,
            "conflicting_action_prob": conflicting_action_prob,
            "constraint_guard_trigger_prob": constraint_guard_trigger_prob,
            "sensor_stale_prob": sensor_stale_prob,
            "shutdown_after_first_fault": shutdown_after_first_fault,
            "deadline_miss_prob": deadline_miss_prob,
            "fault_setting_label": fault_setting_label,
            "agent_count": n_agents,
            "coordination_regime": cprof["coordination_regime"],
            "coordination_topology": cprof["coordination_topology"],
            "hierarchy_depth": cprof["hierarchy_depth"],
            "fan_out": cprof["fan_out"],
            "handoff_factor": cprof["handoff_factor"],
            "shared_state_contention": cprof["shared_state_contention"],
            "deadline_tightness": cprof["deadline_tightness"],
            "critical_path_length": cprof["critical_path_length"],
            "branching_factor": cprof["branching_factor"],
            "queue_contention_index": cprof["queue_contention_index"],
            "regime_fault_interaction": cprof["regime_fault_interaction"],
            "regime_id": cprof["regime_id"],
            "effective_drop_completion_prob": round(effective_drop_p, 6),
            "latency_stress_multiplier": cprof["latency_stress_multiplier"],
            "drop_stress_multiplier": cprof["drop_stress_multiplier"],
        },
    )

    trace_path = out_dir / "trace.json"
    maestro_path = out_dir / "maestro_report.json"
    evidence_path = out_dir / "evidence_bundle.json"
    release_path = out_dir / "release_manifest.json"

    trace_text = json.dumps(trace, indent=2) + "\n"
    trace_bytes = trace_text.encode("utf-8")
    trace_path.write_bytes(trace_bytes)
    h_trace = sha256_bytes(trace_bytes)

    maestro = maestro_report_from_trace(run_id, sid, trace)
    maestro_text = json.dumps(maestro, indent=2) + "\n"
    maestro_bytes = maestro_text.encode("utf-8")
    maestro_path.write_bytes(maestro_bytes)
    h_maestro = sha256_bytes(maestro_bytes)

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
        artifact_hashes=[h_trace, h_maestro],
    )

    try:
        validate(evidence, SCHEMA_EVIDENCE)
    except Exception:
        schema_ok = False
        evidence["verification"]["schema_validation_ok"] = False

    evidence_text = json.dumps(evidence, indent=2) + "\n"
    evidence_bytes = evidence_text.encode("utf-8")
    evidence_path.write_bytes(evidence_bytes)
    h_evidence = sha256_bytes(evidence_bytes)

    release = build_release_manifest(
        release_id=f"release_{run_id}",
        kernel_version=KERNEL_VERSION,
        artifacts=[trace_path, maestro_path, evidence_path],
        artifact_hashes=[h_trace, h_maestro, h_evidence],
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
