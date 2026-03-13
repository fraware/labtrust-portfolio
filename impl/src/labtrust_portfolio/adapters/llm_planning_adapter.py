"""P6 LLM Planning MAESTRO adapter: runs scenario with typed plan validation in trace."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..thinslice import run_thin_slice
from ..llm_planning import validate_plan, policy_check_step, capture_tool_call
from .base import AdapterResult


class LLMPlanningAdapter:
    """
    Adapter that runs thin-slice and injects a synthetic typed plan into trace
    metadata (plan_id, validation result). Demonstrates plan validation and
    deterministic capture in MAESTRO pipeline.
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

        # Synthetic typed plan and validation
        typed_plan = {
            "version": "0.1",
            "plan_id": f"plan_{scenario_id}_{seed}",
            "steps": [
                {"seq": 0, "tool": "query_status", "args": {}, "validators": ["allow_list"]},
            ],
        }
        ok, errs = validate_plan(typed_plan)
        policy_ok = all(policy_check_step(s, ["query_status", "submit_result"]) for s in typed_plan["steps"])
        captured = [capture_tool_call(s["tool"], s["args"], ["allow_list"]) for s in typed_plan["steps"]]
        if "metadata" not in trace:
            trace["metadata"] = {}
        trace["metadata"]["typed_plan"] = typed_plan
        trace["metadata"]["typed_plan_valid"] = ok and policy_ok
        trace["metadata"]["typed_plan_captured"] = captured
        trace_path.write_text(json.dumps(trace, indent=2) + "\n", encoding="utf-8")

        report["metadata_typed_plan"] = True
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

        return AdapterResult(
            trace=trace,
            maestro_report=report,
            trace_path=trace_path,
            report_path=report_path,
        )
