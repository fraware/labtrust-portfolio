"""P8 Meta-Coordination adapter: runs scenario and injects regime_switch trace events."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..thinslice import run_thin_slice
from ..meta_controller import decide_switch, regime_switch_event
from .base import AdapterResult


class MetaAdapter:
    """
    Adapter that runs thin-slice and injects regime_switch events into the trace
    when switching criteria are met (e.g. fault count). Demonstrates
    meta-controller and auditable regime changes.
    """

    def run(
        self,
        scenario_id: str,
        out_dir: Path,
        seed: int = 7,
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
        hysteresis_consecutive = fault_params.get("hysteresis_consecutive", 1)
        to_regime = decide_switch(
            "centralized",
            fault_count,
            p95,
            fault_threshold=fault_threshold,
            hysteresis_consecutive=hysteresis_consecutive,
        )
        events = list(trace.get("events", []))
        if to_regime and fault_count > 0:
            last = events[-1] if events else {}
            ts = last.get("ts", 0.0) + 0.01
            seq = last.get("seq", -1) + 1
            ev = regime_switch_event(
                seq, ts, "centralized", to_regime, "fault_threshold", trace.get("final_state_hash", "")
            )
            events.append(ev)
            trace["events"] = events
        if "metadata" not in trace:
            trace["metadata"] = {}
        trace["metadata"]["meta_controller"] = True
        trace["metadata"]["regime_switch_count"] = 1 if to_regime else 0
        trace_path.write_text(json.dumps(trace, indent=2) + "\n", encoding="utf-8")

        report["metadata_meta_controller"] = True
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

        return AdapterResult(
            trace=trace,
            maestro_report=report,
            trace_path=trace_path,
            report_path=report_path,
        )
