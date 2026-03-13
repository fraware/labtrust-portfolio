"""Adapter interface: run scenario, return trace + report."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Protocol


class AdapterResult:
    """Result of running an adapter: paths to trace and report."""

    def __init__(
        self,
        trace: Dict[str, Any],
        maestro_report: Dict[str, Any],
        trace_path: Path,
        report_path: Path,
    ):
        self.trace = trace
        self.maestro_report = maestro_report
        self.trace_path = trace_path
        self.report_path = report_path


class MAESTROAdapter(Protocol):
    """Protocol for MAESTRO adapters: run scenario and produce trace + report."""

    def run(
        self,
        scenario_id: str,
        out_dir: Path,
        seed: int = 7,
        **fault_params: Any,
    ) -> AdapterResult:
        """Run scenario; write trace and report to out_dir; return result."""
        ...


def run_adapter(
    adapter: MAESTROAdapter,
    scenario_id: str,
    out_dir: Path,
    seed: int = 7,
    **fault_params: Any,
) -> AdapterResult:
    """Run an adapter and return the result."""
    return adapter.run(scenario_id, out_dir, seed=seed, **fault_params)
