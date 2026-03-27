"""REP-CPS MAESTRO adapter: thin-slice + aggregation + safety gate."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..thinslice import run_thin_slice
from ..rep_cps import (
    aggregate,
    auth_hook,
    compromised_updates,
    sensitivity_spoof_duplicate_sender_update,
)
from ..scenario import scenario_rep_cps_scheduling_dependent
from .base import AdapterResult


class REPCPSAdapter:
    """
    Thin-slice pipeline with REP-CPS: aggregation, safety gate, TRACE + report.

    If ``rep_cps_scheduling_dependent: true`` in scenario YAML, aggregate and
    gate run *before* thin-slice so scheduling can be withheld when the gate
    denies. Duplicate-sender spoof stresses naive mean vs trimmed mean.
    """

    SAFETY_GATE_MAX_LOAD = 2.0

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
        aggregation_method = fault_params.get(
            "aggregation_method", "trimmed_mean"
        )
        use_compromised = fault_params.get("use_compromised", False)
        allowed_agents = fault_params.get("allowed_agents", None)
        aggregation_steps = int(fault_params.get("aggregation_steps", 1))
        aggregation_epsilon = float(fault_params.get("aggregation_epsilon", 1e-6))
        safety_gate_max_load = float(
            fault_params.get("safety_gate_max_load", REPCPSAdapter.SAFETY_GATE_MAX_LOAD)
        )

        if scenario_rep_cps_scheduling_dependent(scenario_id):
            return self._run_scheduling_dependent(
                scenario_id,
                out_dir,
                seed,
                delay_p95_ms=delay_p95_ms,
                drop_completion_prob=drop_completion_prob,
                delay_fault_prob=delay_fault_prob,
                aggregation_method=aggregation_method,
                use_compromised=use_compromised,
                allowed_agents=allowed_agents,
                aggregation_steps=aggregation_steps,
                aggregation_epsilon=aggregation_epsilon,
                safety_gate_max_load=safety_gate_max_load,
            )

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

        agg_value, converged, steps_to_convergence, step_values = (
            self._aggregate_loop(
                use_compromised=use_compromised,
                allowed_agents=allowed_agents,
                aggregation_method=aggregation_method,
                aggregation_steps=aggregation_steps,
                aggregation_epsilon=aggregation_epsilon,
                inject_spoof=False,
            )
        )
        safety_gate_ok = self._gate_ok(agg_value, safety_gate_max_load)
        self._write_rep_cps_metadata(
            trace_path,
            trace,
            agg_value,
            safety_gate_ok,
            aggregation_steps,
            converged,
            steps_to_convergence,
            step_values,
        )
        report["metadata_rep_cps"] = True
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

        return AdapterResult(
            trace=trace,
            maestro_report=report,
            trace_path=trace_path,
            report_path=report_path,
        )

    def _run_scheduling_dependent(
        self,
        scenario_id: str,
        out_dir: Path,
        seed: int,
        *,
        delay_p95_ms: float,
        drop_completion_prob: float,
        delay_fault_prob: float,
        aggregation_method: str,
        use_compromised: bool,
        allowed_agents: Any,
        aggregation_steps: int,
        aggregation_epsilon: float,
        safety_gate_max_load: float,
    ) -> AdapterResult:
        agg_value, converged, steps_to_convergence, step_values = (
            self._aggregate_loop(
                use_compromised=use_compromised,
                allowed_agents=allowed_agents,
                aggregation_method=aggregation_method,
                aggregation_steps=aggregation_steps,
                aggregation_epsilon=aggregation_epsilon,
                inject_spoof=True,
            )
        )
        safety_gate_ok = self._gate_ok(agg_value, safety_gate_max_load)

        outs = run_thin_slice(
            out_dir,
            seed=seed,
            delay_p95_ms=delay_p95_ms,
            drop_completion_prob=drop_completion_prob,
            scenario_id=scenario_id,
            delay_fault_prob=delay_fault_prob,
            rep_cps_safety_gate_ok=safety_gate_ok,
        )
        trace_path = outs["trace"]
        report_path = outs["maestro_report"]
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        report = json.loads(report_path.read_text(encoding="utf-8"))

        self._write_rep_cps_metadata(
            trace_path,
            trace,
            agg_value,
            safety_gate_ok,
            aggregation_steps,
            converged,
            steps_to_convergence,
            step_values,
        )
        report["metadata_rep_cps"] = True
        report_path.write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )

        return AdapterResult(
            trace=trace,
            maestro_report=report,
            trace_path=trace_path,
            report_path=report_path,
        )

    @staticmethod
    def _gate_ok(agg_value: float | None, safety_gate_max_load: float) -> bool:
        return (
            agg_value is not None
            and float(agg_value) <= safety_gate_max_load
        )

    def _aggregate_loop(
        self,
        *,
        use_compromised: bool,
        allowed_agents: Any,
        aggregation_method: str,
        aggregation_steps: int,
        aggregation_epsilon: float,
        inject_spoof: bool,
        max_age_sec: float | None = None,
        rate_limit: int | None = None,
        current_ts: float = 0.0,
    ) -> tuple[float | None, bool, int | None, list[float]]:
        honest = [
            {"variable": "load", "value": 0.3, "ts": 0.0, "agent_id": "agent_1"},
            {"variable": "load", "value": 0.35, "ts": 0.0, "agent_id": "agent_2"},
        ]
        updates = list(honest)
        if use_compromised:
            updates.extend(
                compromised_updates(
                    "load", num_compromised=2, extreme_value=10.0, ts=0.0
                )
            )
        if inject_spoof:
            updates.append(
                sensitivity_spoof_duplicate_sender_update(
                    "load", "agent_1", poison_value=10.0, ts=0.0
                )
            )
        filtered = [
            u for u in updates if auth_hook(u, allowed_agents=allowed_agents)
        ]

        agg_value: float | None = None
        converged = False
        steps_to_convergence: int | None = None
        step_values: list[float] = []
        for step in range(max(1, aggregation_steps)):
            step_updates = [
                {**u, "ts": u.get("ts", 0.0) + step * 0.01} for u in filtered
            ]
            prev = agg_value
            agg_value = aggregate(
                "load",
                step_updates,
                method=aggregation_method,
                trim_fraction=0.25,
                max_age_sec=max_age_sec,
                rate_limit=rate_limit,
                current_ts=current_ts + step * 0.01,
            )
            if agg_value is not None:
                step_values.append(float(agg_value))
            if (
                prev is not None
                and agg_value is not None
                and abs(agg_value - prev) < aggregation_epsilon
            ):
                converged = True
                steps_to_convergence = step
                break
        if steps_to_convergence is None:
            steps_to_convergence = len(step_values) if step_values else 0
        if agg_value is None and step_values:
            agg_value = step_values[-1]
        if agg_value is None:
            agg_value = aggregate(
                "load",
                filtered,
                method=aggregation_method,
                trim_fraction=0.25,
                max_age_sec=max_age_sec,
                rate_limit=rate_limit,
                current_ts=current_ts,
            )
        return agg_value, converged, steps_to_convergence, step_values

    def _write_rep_cps_metadata(
        self,
        trace_path: Path,
        trace: dict[str, Any],
        agg_value: float | None,
        safety_gate_ok: bool,
        aggregation_steps: int,
        converged: bool,
        steps_to_convergence: int | None,
        step_values: list[float],
    ) -> None:
        if "metadata" not in trace:
            trace["metadata"] = {}
        trace["metadata"]["rep_cps"] = True
        trace["metadata"]["rep_cps_aggregate_load"] = agg_value
        trace["metadata"]["rep_cps_safety_gate_ok"] = safety_gate_ok
        trace["metadata"]["rep_cps_aggregation_steps"] = len(step_values) or 1
        trace["metadata"]["rep_cps_converged"] = converged or (aggregation_steps <= 1)
        if aggregation_steps > 1:
            trace["metadata"]["rep_cps_steps_to_convergence"] = steps_to_convergence
            trace["metadata"]["rep_cps_step_values"] = step_values
        trace_path.write_text(
            json.dumps(trace, indent=2) + "\n", encoding="utf-8"
        )
