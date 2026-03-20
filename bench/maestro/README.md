# CPS-MAESTRO (benchmark scaffolding)

MAESTRO is the evaluation substrate: scenarios, adapters, scoring, variance-aware reporting.

- **Reference scenario:** **lab_profile_v0** (`scenarios/lab_profile_v0.yaml`) is the portfolio anchor; it supports faults: drop_completion, delay, calibration_invalid. See [SCENARIO_SPEC.md](SCENARIO_SPEC.md) (including Anti-gaming).
- **Scenarios:** YAMLs under `scenarios/` (toy_lab_v0, lab_profile_v0, warehouse_v0, traffic_v0, regime_stress_v0, regime_stress_v1) with optional `family` (lab, warehouse, traffic). The second regime-stress id is used by P8 publishable evals alongside v0 (see `scripts/meta_eval.py --scenario`).
- **Benchmark release:** Canonical v0.1 set in [BENCHMARK_RELEASE.v0.1.md](BENCHMARK_RELEASE.v0.1.md) and [benchmark_scenarios.v0.1.json](benchmark_scenarios.v0.1.json).
- **Fault sweep:** `scripts/maestro_fault_sweep.py` writes `datasets/runs/maestro_fault_sweep/multi_sweep.json` (includes calibration_invalid_01).
- **Anti-gaming:** `scripts/maestro_antigaming_eval.py` writes `datasets/runs/maestro_antigaming/antigaming_results.json` with `scoring_proof` (always_deny/always_wait score 0/1; legitimate safe completion scores higher; unsafe success not rewarded). See SCENARIO_SPEC Anti-gaming and P4 AUTHORING_PACKET K4.
- **Baselines:** `scripts/maestro_baselines.py` writes `baseline_results.md` and `baseline_summary.json` (Centralized, Blackboard, RetryHeavy). Draft tables: `scripts/export_maestro_tables.py`.
- **Reproducibility:** [REPRODUCIBILITY.md](REPRODUCIBILITY.md). Thin-slice report generator: `kernel/eval/MAESTRO_REPORT.v0.1`.
- **Adapter cost:** Coarse implementation cost (LOC estimate, hours estimate) per reference adapter in [adapter_costs.json](adapter_costs.json). Used to back adoption claims; see REPRODUCIBILITY for run instructions.

## MAESTRO adoption (external use)

We invite external groups to run MAESTRO with their own adapter or a fork of the reference adapters and report results.

1. **Add an external adapter:** Implement the same interface `run(scenario_id, out_dir, seed, **fault_params) -> AdapterResult` (trace + maestro_report). Place it in your fork or in `impl/src/labtrust_portfolio/adapters/` and register it in `maestro_baselines.py` or your own script.
2. **Run one scenario and one fault setting:** e.g. `maestro_fault_sweep.py --scenario toy_lab_v0 --seeds 5` or run your adapter on `toy_lab_v0` with `drop_completion_prob=0.05` and record TRACE + MAESTRO_REPORT.
3. **Submit a results snippet:** Provide `run_manifest` (scenario_id, seeds, script or adapter name) and key metrics (e.g. `tasks_completed_mean`, `tasks_completed_stdev`). When an external result exists, P4 DRAFT can add a short "External use" sentence and optional table row or footnote. Contact: see repo README or PORTFOLIO_BOARD.
