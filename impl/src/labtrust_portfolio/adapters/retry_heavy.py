"""Retry-heavy adapter: thin-slice with explicit retry on drop (architecturally distinct from Centralized)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..thinslice import run_thin_slice
from .base import AdapterResult


class RetryHeavyAdapter:
    """
    Adapter that runs the thin-slice pipeline with retry-on-drop: each task
    is retried up to max_retries_per_task times on drop_completion. This
    yields higher tasks_completed under the same fault settings than
    Centralized (no retries), so adapter comparison is not only fault-parameter
    but coordination/failure-handling strategy.
    """

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
        max_retries_per_task = int(fault_params.get("max_retries_per_task", 2))
        outs = run_thin_slice(
            out_dir,
            seed=seed,
            delay_p95_ms=delay_p95_ms,
            drop_completion_prob=drop_completion_prob,
            scenario_id=scenario_id,
            delay_fault_prob=delay_fault_prob,
            max_retries_per_task=max_retries_per_task,
        )
        trace_path = outs["trace"]
        report_path = outs["maestro_report"]
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if "metadata" not in trace:
            trace["metadata"] = {}
        trace["metadata"]["adapter"] = "retry_heavy"
        trace_path.write_text(json.dumps(trace, indent=2) + "\n", encoding="utf-8")
        return AdapterResult(
            trace=trace,
            maestro_report=report,
            trace_path=trace_path,
            report_path=report_path,
        )
