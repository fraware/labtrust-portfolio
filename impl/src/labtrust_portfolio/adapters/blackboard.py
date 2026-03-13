"""Blackboard / event-sourced adapter: same pipeline, different scenario id."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from ..thinslice import run_thin_slice
from .base import AdapterResult


class BlackboardAdapter:
    """
    Adapter that runs the thin-slice pipeline with blackboard-style scenario.
    Uses same trace format; scenario_id may differ (e.g. lab_profile_v0).
    """

    def run(
        self,
        scenario_id: str,
        out_dir: Path,
        seed: int = 7,
        **fault_params: Any,
    ) -> AdapterResult:
        delay_p95_ms = fault_params.get("delay_p95_ms", 55.0)
        drop_completion_prob = fault_params.get("drop_completion_prob", 0.02)
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
        return AdapterResult(
            trace=trace,
            maestro_report=report,
            trace_path=trace_path,
            report_path=report_path,
        )
