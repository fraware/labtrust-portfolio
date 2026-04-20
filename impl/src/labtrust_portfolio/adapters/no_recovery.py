"""NoRecovery baseline: no retries on drop; same thin-slice as Centralized with explicit adapter tag."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..thinslice import run_thin_slice
from .base import AdapterResult


class NoRecoveryAdapter:
    """Explicit no-retry policy (max_retries=0); documents absence of recovery attempts."""

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
        outs = run_thin_slice(
            out_dir,
            seed=seed,
            delay_p95_ms=delay_p95_ms,
            drop_completion_prob=drop_completion_prob,
            scenario_id=scenario_id,
            delay_fault_prob=delay_fault_prob,
            max_retries_per_task=0,
        )
        trace_path = outs["trace"]
        report_path = outs["maestro_report"]
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        report = json.loads(report_path.read_text(encoding="utf-8"))
        trace.setdefault("metadata", {})
        trace["metadata"]["adapter"] = "no_recovery"
        trace_path.write_text(json.dumps(trace, indent=2) + "\n", encoding="utf-8")
        return AdapterResult(
            trace=trace,
            maestro_report=report,
            trace_path=trace_path,
            report_path=report_path,
        )
