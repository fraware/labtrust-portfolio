# CPS-MAESTRO: Benchmark + Fault Injection Suite for CPS-Grade Agent Coordination

**Draft (v0.1). Paper ID: P4_CPS-MAESTRO.**

**Reproducibility.** From repo root, with `PYTHONPATH=impl/src` and `LABTRUST_KERNEL_DIR=kernel`. See [REPORTING_STANDARD.md](../docs/REPORTING_STANDARD.md) and [RESULTS_PER_PAPER.md](../docs/RESULTS_PER_PAPER.md). Repro time: `python scripts/repro_time_p4.py` records wall-clock to `datasets/runs/repro_manifest.json` (repro_wall_min). Target: under 20 min for minimal run.

**Minimal run (under 20 min):** `python scripts/maestro_fault_sweep.py --scenarios toy_lab_v0,lab_profile_v0 --seeds 3` then `python scripts/maestro_baselines.py` then `python scripts/export_p4_maestro_flow.py` then `python scripts/export_maestro_tables.py` then `python scripts/plot_maestro_recovery.py`.

**Publishable run:** `--seeds 20` and both scenarios (toy_lab_v0, lab_profile_v0). Run_manifest in `datasets/runs/maestro_fault_sweep/multi_sweep.json`.

- **Figure 0:** `python scripts/export_p4_maestro_flow.py` (output `docs/figures/p4_maestro_flow.mmd`). Render Mermaid to PNG for camera-ready.
- **Table 1:** `python scripts/maestro_fault_sweep.py --scenarios toy_lab_v0,lab_profile_v0` (default 20 seeds; writes multi_sweep.json), then `python scripts/export_maestro_tables.py`.
- **Table 2:** `python scripts/maestro_baselines.py` (writes baseline_summary.json), then `python scripts/export_maestro_tables.py`.
- **Figure 1:** `python scripts/plot_maestro_recovery.py` (output `docs/figures/p4_recovery_curve.png`). Input: multi_sweep.json.
- **Anti-gaming (K4 evidence):** `python scripts/maestro_antigaming_eval.py` writes `datasets/runs/maestro_antigaming/antigaming_results.json` (contains `scoring_proof` and `success_criteria_met.antigaming_penalized`).

## 1. Motivation

Coordination benchmarking often fails due to variance, hidden assumptions, and missing faults. We need standard scenarios, fault models, and scoring so that CPS coordination is measurable and comparable under tail latency, faults, recovery, and cost—especially for autonomous labs.

## 2. Scenario spec and fault model

Scenario format (YAML): id, description, tasks, faults; optional **family** for taxonomy.

**Figure 0 — MAESTRO flow.** Scenario YAML drives the adapter run; adapter produces TRACE and MAESTRO_REPORT. Regenerate with `python scripts/export_p4_maestro_flow.py` (output `docs/figures/p4_maestro_flow.mmd`). See `bench/maestro/SCENARIO_SPEC.md`. The thin-slice pipeline is scenario-driven: task list and scenario_id are loaded from the scenario YAML (e.g. toy_lab_v0, lab_profile_v0, warehouse_v0, traffic_v0, regime_stress_v0). Fault types in v0.1: **drop_completion** (probability of missing task_end; fault_injected emitted), **delay** (injectable with delay_fault_prob; adds latency, fault_injected "delay" then task completes). Fault parameters: drop_completion_prob, delay_p95_ms, delay_fault_prob; fault sweeps can vary fault type and probability.

## 3. Scoring and reporting

Scoring is standardized: tasks_completed, task_latency_ms_p50/p95/p99, coordination_messages, fault_injected, fault_events, recovery_ok. Implemented in `impl` (maestro_report_from_trace). Reports conform to MAESTRO_REPORT schema. Variance is first-class: repeated runs and tail reporting are mandatory.

## 4. Adapter interface and reference adapters

Adapter interface: run(scenario_id, out_dir, seed, **fault_params) -> AdapterResult (trace + report). Two reference adapters: **CentralizedAdapter** (thin-slice pipeline, single coordinator) and **BlackboardAdapter** (same pipeline, different default fault params). Both produce valid TRACE and MAESTRO_REPORT. See `impl/src/labtrust_portfolio/adapters/`. In v0.1 both reference adapters use the same thin-slice pipeline with the same scenario_id; the only difference is default fault parameters (e.g. delay_p95_ms). A true architectural difference (e.g. different coordination algorithms) is not implemented and is future work.

**Comparison to other benchmarks.** Multi-agent RL benchmarks (e.g. SMAC, MAPF) focus on learning and full simulation; MAESTRO focuses on scenario-driven coordination under fault injection and standardized reporting (tasks_completed, p95 latency, variance) rather than full RL or physical hardware. CPS and robotics testbeds often lack a shared fault model and report format; MAESTRO provides a minimal benchmark set with drop/delay faults and MAESTRO_REPORT schema.

| Benchmark type | Domain | Fault model | Metrics |
|----------------|--------|-------------|---------|
| SMAC / MAPF | Multi-agent RL / pathfinding | N/A or env-specific | Win rate, reward |
| CPS testbeds | Simulation / hardware | Varies | Varies |
| **MAESTRO** | Scenario-driven coordination | drop_completion, delay | tasks_completed, p95, variance |

## 5. Scenarios

- **toy_lab_v0:** minimal 4-task lab (receive_sample, centrifuge, analyze, report_results); thin-slice default. Family: lab.
- **lab_profile_v0:** 5 tasks (receive_sample, centrifuge, analyze, report_results, disposition_commit); supports drop_completion and delay. Family: lab.
- **warehouse_v0:** minimal 3-task (pick, move, place); drop_completion and delay. Family: warehouse.
- **traffic_v0:** minimal 3-task (sense, plan, actuate); drop_completion and delay. Family: traffic.
- **regime_stress_v0:** 4-task lab with high fault load for meta-controller (P8). Family: lab.

**Scenario taxonomy (source: scenario YAMLs).** Families: lab (toy_lab_v0, lab_profile_v0, regime_stress_v0), warehouse (warehouse_v0), traffic (traffic_v0). Optional field `family` in each scenario YAML; see SCENARIO_SPEC.md.

One run per scenario is supported by loading the scenario YAML and running the pipeline with that task list (run_thin_slice(scenario_id=...) or adapter.run(scenario_id, ...)).

## 6. Reproducibility

Dataset layout and release process in `bench/maestro/REPRODUCIBILITY.md`. All runs produce admissible evidence bundles; release script copies to datasets/releases with manifest. **Benchmark release v0.1:** Canonical scenario set defined in `bench/maestro/BENCHMARK_RELEASE.v0.1.md` and `benchmark_scenarios.v0.1.json` (toy_lab_v0, lab_profile_v0, warehouse_v0, traffic_v0, regime_stress_v0). For held-out and train/val/test usage, see P5 (scaling_heldout_eval).

## 7. Baseline results and fault sweep

Tables are generated from machine-readable artifacts. The **run manifest** for the fault sweep is in `datasets/runs/maestro_fault_sweep/multi_sweep.json`: top-level key `run_manifest` contains `seeds`, `scenarios`, `fault_settings`, and `fault_params`. Baseline run info is in `bench/maestro/baseline_summary.json`. For publishable tables use `--seeds 10` and both scenarios (`toy_lab_v0`, `lab_profile_v0`). Run `scripts/maestro_fault_sweep.py --scenarios toy_lab_v0,lab_profile_v0 --seeds 10`, then `scripts/maestro_baselines.py`, then `scripts/export_maestro_tables.py` to regenerate the tables below. Figure 1: `scripts/plot_maestro_recovery.py` (reads multi_sweep.json). Sources: `datasets/runs/maestro_fault_sweep/multi_sweep.json`, `bench/maestro/baseline_summary.json`. Benchmark release: `bench/maestro/BENCHMARK_RELEASE.v0.1.md`, `benchmark_scenarios.v0.1.json`.

**Table 1 — Fault sweep.** Settings: no_drop, drop_005, delay_01, drop_005_delay_01, calibration_invalid_01. Per-scenario sweep.json and multi_sweep.json contain per_run and variance. Regenerate with `python scripts/export_maestro_tables.py` after `scripts/maestro_fault_sweep.py`.

| Scenario | Setting | tasks_completed_mean | tasks_completed_stdev | p95_latency_ms_mean | p95_latency_ms_stdev |
|----------|---------|---------------------|----------------------|---------------------|----------------------|
| toy_lab_v0 | no_drop | 4 | 0.00 | 34.45 | 18.08 |
| toy_lab_v0 | drop_005 | 3.70 | 0.48 | 33.38 | 19.13 |
| toy_lab_v0 | delay_01 | 4 | 0.00 | 30.22 | 21.09 |
| toy_lab_v0 | drop_005_delay_01 | 3.50 | 0.53 | 27.07 | 20.51 |
| toy_lab_v0 | calibration_invalid_01 | 4 | 0.00 | 37.46 | 21.32 |
| lab_profile_v0 | no_drop | 5 | 0.00 | 36.97 | 16.16 |
| lab_profile_v0 | drop_005 | 4.70 | 0.48 | 36.32 | 16.76 |
| lab_profile_v0 | delay_01 | 5 | 0.00 | 34.91 | 20.63 |
| lab_profile_v0 | drop_005_delay_01 | 4.50 | 0.53 | 32.71 | 20.95 |
| lab_profile_v0 | calibration_invalid_01 | 5 | 0.00 | 40.19 | 18.49 |

**Table 2 — Baseline (Centralized vs Blackboard).** Reference adapter comparison (same pipeline, different default params). Regenerate with `python scripts/export_maestro_tables.py` after `scripts/maestro_baselines.py`.

| Adapter | Seed | tasks_completed | coordination_messages | p95_latency_ms |
|---------|------|----------------|------------------------|----------------|
| Centralized | 1 | 4 | 4 | 25.26 |
| Centralized | 2 | 4 | 4 | 75.59 |
| Centralized | 3 | 4 | 4 | 28.09 |
| Centralized | 4 | 4 | 4 | 41.26 |
| Centralized | 5 | 4 | 4 | 42.64 |
| Centralized | 6 | 4 | 4 | 26.54 |
| Centralized | 7 | 4 | 4 | 10.68 |
| Centralized | 8 | 4 | 4 | 19.02 |
| Centralized | 9 | 4 | 4 | 29.77 |
| Centralized | 10 | 4 | 4 | 45.64 |
| Blackboard | 1 | 4 | 4 | 25.26 |
| Blackboard | 2 | 4 | 4 | 75.59 |
| Blackboard | 3 | 4 | 4 | 28.09 |
| Blackboard | 4 | 4 | 4 | 41.26 |
| Blackboard | 5 | 4 | 4 | 42.64 |
| Blackboard | 6 | 4 | 4 | 26.54 |
| Blackboard | 7 | 4 | 4 | 10.68 |
| Blackboard | 8 | 4 | 4 | 19.02 |
| Blackboard | 9 | 4 | 4 | 29.77 |
| Blackboard | 10 | 4 | 4 | 45.64 |

**Fault sweep:** Default scenarios toy_lab_v0, lab_profile_v0; four settings (no_drop, drop_005, delay_01, drop_005_delay_01). Output: tasks_completed_mean/stdev, p95_latency_ms_mean/stdev per setting. Variance (stdev across seeds) is reported.

**Figure 1 — Recovery proxy (tasks_completed vs fault setting).** Mean tasks_completed across seeds per fault setting from multi_sweep; proxy for recovery behavior under increasing fault load. Regenerate with `python scripts/plot_maestro_recovery.py` (output `docs/figures/p4_recovery_curve.png`). Not full MTTR or time-to-safe-state; see Limitations.

## 8. Limitations

Scope and fault model: [EXPERIMENTS_AND_LIMITATIONS.md](../docs/EXPERIMENTS_AND_LIMITATIONS.md). Per-paper:

- **Anti-gaming (K4):** Pathological strategies (always_deny, always_wait) are penalized: they score 0 and 1 tasks_completed; legitimate safe completion scores higher. Evidence: `scripts/maestro_antigaming_eval.py` writes `datasets/runs/maestro_antigaming/antigaming_results.json`, which includes `success_criteria_met.antigaming_penalized` and a **scoring_proof** object (always_deny_tasks_completed, always_wait_tasks_completed, legitimate_safe_min, claim) documenting the explicit comparison. Unsafe success (run completes but recovery_ok false or safety violation) is not rewarded; scoring is safety-weighted. See `bench/maestro/SCENARIO_SPEC.md` (Anti-gaming).
- **Simulated tasks:** Tasks are simulated in the thin-slice pipeline; no real robots or devices.
- **Fault injection:** Faults (drop, delay) are probabilistic in code, not physical faults or real network/device failures.
- **Minimal scenarios:** Warehouse and traffic scenarios are minimal YAMLs (few tasks); they are not full-scale benchmarks.
- **Adapters:** Centralized and Blackboard use the same pipeline; no true architectural difference in v0.1.
- **Scoring:** Scoring is automated from the pipeline (maestro_report_from_trace); there is no human or external judge. External validation or human evaluation is future work.
- **Synthetic scenarios:** All scenarios (toy_lab, lab_profile, warehouse, traffic, regime_stress) are synthetic; no real lab or physical plant.
- **Recovery metric is a proxy:** Figure 1 plots tasks_completed vs fault setting as a recovery proxy; not full MTTR or time-to-safe-state.

## 9. Methodology and reproducibility

**Methodology:** Hypothesis—standard scenarios, fault model, and scoring yield stable, comparable metrics across adapters and seeds. Metrics: tasks_completed, coordination_messages, task_latency_ms_p95; variance (stdev) over seeds per setting. Baselines: Centralized vs Blackboard (same scenario, seed band); fault sweep no_drop vs drop_005. Kill criterion: if metrics are not comparable across runs or variance is unreported, the suite fails. Portfolio criteria: `docs/STATE_OF_THE_ART_CRITERIA.md`.

**Reproducibility:** Scenario-driven run: `labtrust_portfolio run-thinslice --out-dir <dir>` or adapter.run(scenario_id, out_dir, seed). Fault sweep (publishable): `python scripts/maestro_fault_sweep.py --scenarios toy_lab_v0,lab_profile_v0 --seeds 10`; run manifest in `datasets/runs/maestro_fault_sweep/multi_sweep.json` (run_manifest). Baselines: `python scripts/maestro_baselines.py`. Tables: `python scripts/export_maestro_tables.py` (reads multi_sweep.json and baseline_summary.json). Figure 1: `python scripts/plot_maestro_recovery.py`. Anti-gaming: `python scripts/maestro_antigaming_eval.py` writes `datasets/runs/maestro_antigaming/antigaming_results.json` (scoring_proof, success_criteria_met.antigaming_penalized). Benchmark set: `bench/maestro/benchmark_scenarios.v0.1.json`. Dataset layout: `bench/maestro/REPRODUCIBILITY.md`, `datasets/README.md`. Integration tests: `tests/test_maestro_p4.py`.

---

**Claims and backing.**

| Claim | Evidence |
|-------|----------|
| C1 (Stable measurements) | MAESTRO_REPORT schema, scenario spec, Table 1 (fault sweep variance). |
| C2 (Variance first-class) | Table 1 stdev; fault_sweep repeated seeds. |
| C3 (Adapter tractable) | MAESTROAdapter protocol, Table 2 (Centralized vs Blackboard). |
| C4 (Third-party usable) | REPRODUCIBILITY.md, CI, baseline_results.md, BENCHMARK_RELEASE.v0.1.md. |
