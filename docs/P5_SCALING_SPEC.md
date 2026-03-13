# P5 Scaling Laws: Spec (v0.1)

## Task feature set

- **scenario_id:** Scenario family (toy_lab_v0, lab_profile_v0, warehouse_v0, traffic_v0).
- **num_tasks:** Number of tasks in scenario (from scenario YAML).
- **task_names:** Ordered task names (tool density / depth implied).
- **num_faults:** Number of fault types in scenario.
- **tool_density:** num_tasks / max(1, num_resources); **fault_density:** num_faults / max(1, num_tasks); **sequential_depth_proxy:** num_tasks; **resource_coupling_index:** num_resources (from scenario).
- **seed:** Random seed (for reproducibility).
- **event_count:** From trace (proxy for complexity).

Resource graph structure and deadline tightness can be added in v0.2 from scenario metadata.

## Response variables

- **tasks_completed:** From MAESTRO report metrics.
- **coordination_messages:** From MAESTRO report.
- **task_latency_ms_p95:** Tail latency.

**Collapse:** Collapse is derived from MAESTRO report fields (no new trace schema). Definition: (a) `tasks_completed < threshold` (default 2), or (b) `recovery_ok is False` from report.faults. The dataset builder adds a boolean `collapse` per row. Per-scenario collapse rate is the fraction of runs in that scenario with collapse=True. Current traces may not have explicit failure/recovery events; collapse is therefore a derived proxy. Richer failure/recovery semantics (e.g. MTTR) are future work.

## Out-of-sample kill criteria

- Model must be validated on held-out scenario family or held-out fault mixture.
- Kill if: (1) cannot define measurable influence bounds, (2) model does not beat baseline (e.g. global mean) on held-out data, (3) collapse probability uncalibrated.

## Artifacts

- Feature extractor: `impl/src/labtrust_portfolio/scaling.py` (`extract_features_from_scenario`, `extract_features_from_trace`, `extract_response_from_report`).
- Dataset builder: `build_dataset_from_runs()`; script `scripts/scaling_build_dataset.py`.
- Baseline predictor: `predict_baseline_mean`, `predict_by_scenario` (per-scenario mean baseline), `fit_linear_predictor` (regression on num_tasks, num_faults, tool_density).
- Recommendation CLI: `scripts/scaling_recommend.py` (--scenario, --table, --runs-dir).

**Small N:** For reporting and stable MAE/CI, run `generate_multiscenario_runs.py` with default 20 seeds (or higher) and optionally `--fault-mix` for calibration_invalid; see script docstring. Held-out eval reports `per_scenario_baseline_mae`; kill criterion: beat per-scenario mean out-of-sample (or state explicitly if scenario identity is forbidden).
