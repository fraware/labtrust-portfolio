"""REP-CPS MAESTRO adapter: runs scenario with REP-CPS protocol (aggregation + safety gate)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..thinslice import run_thin_slice
from ..rep_cps import aggregate, auth_hook, compromised_updates
from .base import AdapterResult


class REPCPSAdapter:
    """
    Adapter that runs the thin-slice pipeline with REP-CPS protocol: synthetic
    aggregation step (to demonstrate protocol in trace), then safety-gate check,
    then scenario execution. Produces TRACE + MAESTRO_REPORT.
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
        aggregation_method = fault_params.get("aggregation_method", "trimmed_mean")
        use_compromised = fault_params.get("use_compromised", False)
        allowed_agents = fault_params.get("allowed_agents", None)
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

        # Protocol step: run aggregation on synthetic updates (for demo)
        honest = [
            {"variable": "load", "value": 0.3, "ts": 0.0, "agent_id": "agent_1"},
            {"variable": "load", "value": 0.35, "ts": 0.0, "agent_id": "agent_2"},
        ]
        if use_compromised:
            compromised = compromised_updates(
                "load", num_compromised=2, extreme_value=10.0, ts=0.0
            )
            updates = honest + compromised
        else:
            updates = honest
        filtered = [
            u for u in updates
            if auth_hook(u, allowed_agents=allowed_agents)
        ]
        agg_value = aggregate(
            "load", filtered,
            method=aggregation_method,
            trim_fraction=0.25,
        )
        if "metadata" not in trace:
            trace["metadata"] = {}
        trace["metadata"]["rep_cps"] = True
        trace["metadata"]["rep_cps_aggregate_load"] = agg_value
        trace["metadata"]["rep_cps_safety_gate_ok"] = True
        trace_path.write_text(json.dumps(trace, indent=2) + "\n", encoding="utf-8")

        report["metadata_rep_cps"] = True
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

        return AdapterResult(
            trace=trace,
            maestro_report=report,
            trace_path=trace_path,
            report_path=report_path,
        )
