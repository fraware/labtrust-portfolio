"""P8 Meta-Coordination adapter: runs scenario and injects regime_switch trace events. v0.2: optional fallback adapter run when switch is decided."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional, TYPE_CHECKING

from ..thinslice import run_thin_slice
from ..meta_controller import decide_switch_with_reason, regime_switch_event
from .base import AdapterResult, run_adapter

if TYPE_CHECKING:
    from .base import MAESTROAdapter


class MetaAdapter:
    """
    Adapter that runs thin-slice and injects regime_switch events into the trace
    when switching criteria are met (e.g. fault count). v0.2: when fallback_adapter
    is set and decide_switch returns a regime, runs the fallback adapter with the
    same scenario/seed/fault_params and records fallback result in trace metadata
    (fallback_tasks_completed) so evaluation can compare two coordination paths.
    """

    def run(
        self,
        scenario_id: str,
        out_dir: Path,
        seed: int = 7,
        fallback_adapter: Optional["MAESTROAdapter"] = None,
        **fault_params: Any,
    ) -> AdapterResult:
        delay_p95_ms = fault_params.get("delay_p95_ms", 50.0)
        drop_completion_prob = fault_params.get("drop_completion_prob", 0.15)
        delay_fault_prob = fault_params.get("delay_fault_prob", 0.0)
        outs = run_thin_slice(
            out_dir,
            seed=seed,
            delay_p95_ms=delay_p95_ms,
            drop_completion_prob=drop_completion_prob,
            scenario_id=scenario_id,
            delay_fault_prob=delay_fault_prob,
        )
        trace_path = outs["trace"]
        report_path = outs["maestro_report"]
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        report = json.loads(report_path.read_text(encoding="utf-8"))

        # Simulate meta-controller: count faults from report, decide switch
        fault_injected = report.get("faults", {}).get("fault_injected", False)
        fault_events = report.get("faults", {}).get("fault_events", [])
        fault_count = len(fault_events)
        p95 = report.get("metrics", {}).get("task_latency_ms_p95", 0.0)
        fault_threshold = fault_params.get("fault_threshold", 1)
        latency_threshold_ms = float(fault_params.get("latency_threshold_ms", 200.0))
        contention_threshold = float(fault_params.get("contention_threshold", 1.5))
        hysteresis_consecutive = fault_params.get("hysteresis_consecutive", 1)
        coord_msgs = float(report.get("metrics", {}).get("coordination_messages", 0.0))
        tasks_completed = float(report.get("metrics", {}).get("tasks_completed", 0.0))
        # Thin-slice proxy for contention: high coordination message pressure per completed task.
        contention_index = coord_msgs / max(tasks_completed, 1.0)
        to_regime, reason = decide_switch_with_reason(
            "centralized",
            fault_count,
            p95,
            contention_index=contention_index,
            fault_threshold=fault_threshold,
            latency_threshold_ms=latency_threshold_ms,
            contention_threshold=contention_threshold,
            hysteresis_consecutive=hysteresis_consecutive,
        )
        events = list(trace.get("events", []))
        if to_regime:
            last = events[-1] if events else {}
            ts = last.get("ts", 0.0) + 0.01
            seq = last.get("seq", -1) + 1
            criteria = {
                "fault_count": int(fault_count),
                "fault_threshold": int(fault_threshold),
                "hysteresis_consecutive": int(hysteresis_consecutive),
                "latency_p95_ms": float(p95),
                "latency_threshold_ms": float(latency_threshold_ms),
                "contention_index": float(contention_index),
                "contention_threshold": float(contention_threshold),
            }
            ev = regime_switch_event(
                seq,
                ts,
                "centralized",
                to_regime,
                reason or "unknown",
                trace.get("final_state_hash", ""),
                criteria=criteria,
            )
            events.append(ev)
            trace["events"] = events
        if "metadata" not in trace:
            trace["metadata"] = {}
        trace["metadata"]["meta_controller"] = True
        trace["metadata"]["regime_switch_count"] = 1 if to_regime else 0
        if to_regime and fallback_adapter is not None:
            fallback_dir = out_dir / "fallback_run"
            fallback_dir.mkdir(parents=True, exist_ok=True)
            fallback_result = run_adapter(
                fallback_adapter, scenario_id, fallback_dir, seed=seed, **fault_params
            )
            fb_rep = fallback_result.maestro_report
            fb_metrics = fb_rep.get("metrics", {})
            fb_faults = fb_rep.get("faults", {})
            fb_safety = fb_rep.get("safety", {})
            trace["metadata"]["fallback_tasks_completed"] = fb_metrics.get("tasks_completed")
            trace["metadata"]["fallback_recovery_ok"] = fb_faults.get("recovery_ok", True)
            trace["metadata"]["fallback_time_to_recovery_ms"] = fb_metrics.get(
                "time_to_recovery_ms"
            )
            trace["metadata"]["fallback_ponr_violation_count"] = int(
                fb_safety.get("ponr_violation_count", 0) or 0
            )
            trace["metadata"]["fallback_safety_violation_count"] = int(
                fb_safety.get("safety_violation_count", 0) or 0
            )
            trace["metadata"]["fallback_run_recorded"] = True
        trace_path.write_text(json.dumps(trace, indent=2) + "\n", encoding="utf-8")

        report["metadata_meta_controller"] = True
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

        return AdapterResult(
            trace=trace,
            maestro_report=report,
            trace_path=trace_path,
            report_path=report_path,
        )
