"""Centralized scheduler adapter: thin-slice pipeline (single coordinator)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..thinslice import run_thin_slice
from ..scenario import scenario_rep_cps_scheduling_dependent
from .base import AdapterResult


class CentralizedAdapter:
    """Adapter that runs the thin-slice pipeline (centralized scheduler)."""

    def run(
        self,
        scenario_id: str,
        out_dir: Path,
        seed: int = 7,
        **fault_params: Any,
    ) -> AdapterResult:
        delay_p95_ms = fault_params.get("delay_p95_ms", 50.0)
        drop_completion_prob = fault_params.get("drop_completion_prob", 0.02)
        delay_fault_prob = fault_params.get("delay_fault_prob", 0.0)
        gate_ok: bool | None = None
        if scenario_rep_cps_scheduling_dependent(scenario_id):
            # Centralized baseline does not consume REP-CPS aggregate; scheduling proceeds
            # unconditionally. This represents a system that does not use REP-CPS at all,
            # not a "weaker REP-CPS" comparator. For fair comparison, see REP-CPS naive
            # in-loop baseline in rep_cps_eval.py which shares the same informational
            # assumption but uses naive mean aggregation.
            gate_ok = True
        outs = run_thin_slice(
            out_dir,
            seed=seed,
            delay_p95_ms=delay_p95_ms,
            drop_completion_prob=drop_completion_prob,
            scenario_id=scenario_id,
            delay_fault_prob=delay_fault_prob,
            rep_cps_safety_gate_ok=gate_ok,
        )
        trace_path = outs["trace"]
        report_path = outs["maestro_report"]
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        report = json.loads(report_path.read_text(encoding="utf-8"))
        return AdapterResult(
            trace=trace,
            maestro_report=report,
            trace_path=trace_path,
            report_path=report_path,
        )
