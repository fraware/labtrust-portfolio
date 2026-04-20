# CPS-MAESTRO: Benchmark + Fault Injection Suite for CPS-Grade Agent Coordination

**Draft (v0.1). Paper ID: P4_CPS-MAESTRO.**

**Reproducibility.** From repo root, with `PYTHONPATH=impl/src` and `LABTRUST_KERNEL_DIR=kernel`. See [REPORTING_STANDARD.md](../docs/REPORTING_STANDARD.md) and [RESULTS_PER_PAPER.md](../docs/RESULTS_PER_PAPER.md). Minimal run target: under 20 min. Repro time optional: `python scripts/repro_time_p4.py` (writes repro_manifest.json).

**Minimal run (under 20 min):** `python scripts/maestro_fault_sweep.py --scenario toy_lab_v0 --seeds 3` then `python scripts/maestro_baselines.py --seeds 3` then `python scripts/export_p4_maestro_flow.py` then `python scripts/export_maestro_tables.py --out papers/P4_CPS-MAESTRO/generated_tables.md` then `python scripts/plot_maestro_recovery.py` then `python scripts/maestro_antigaming_eval.py`.

**Publishable run (frozen in repo):** `maestro_fault_sweep.py` with **20 seeds** and scenarios `toy_lab_v0,lab_profile_v0,warehouse_v0,traffic_v0,regime_stress_v0`; `maestro_baselines.py --seeds 20`; `export_maestro_tables.py`; `plot_maestro_recovery.py`; `maestro_antigaming_eval.py`. Canonical copy: `datasets/releases/p4_publishable_v1/`. Summary: `datasets/runs/RUN_RESULTS_SUMMARY.md`.

- **Figure 0:** `python scripts/export_p4_maestro_flow.py` (output `docs/figures/p4_maestro_flow.mmd`). Render Mermaid to PNG for camera-ready.
- **Tables A–D:** `python scripts/export_maestro_tables.py --out papers/P4_CPS-MAESTRO/generated_tables.md` (reads `multi_sweep.json`, `baseline_summary.json`, `antigaming_results.json`).
- **Figures:** `python scripts/plot_maestro_recovery.py` writes `docs/figures/p4_recovery_curve.png`, `p4_safety_violations.png`, `p4_efficiency_messages.png` plus JSON sidecars.
- **Anti-gaming (K4):** `python scripts/maestro_antigaming_eval.py` writes `datasets/runs/maestro_antigaming/antigaming_results.json` with ranked `composite_score` (`bench/maestro/SCORING.md`).

## 1. Motivation

Coordination benchmarking often fails due to variance, hidden assumptions, and missing faults. We need standard scenarios, fault models, and scoring so that CPS coordination is measurable and comparable under tail latency, faults, recovery, and cost—especially for autonomous labs.

## 2. Scenario spec and fault model

Scenario format (YAML): id, description, tasks, faults; optional **family** for taxonomy.

**Figure 0 — MAESTRO flow.** Scenario YAML drives the adapter run; adapter produces TRACE and MAESTRO_REPORT v0.2. See `bench/maestro/SCENARIO_SPEC.md` and `bench/maestro/RECOVERY_AND_SAFETY_METRICS.md`. The thin-slice harness loads tasks from YAML. Core faults include **drop_completion**, **delay**, **calibration_invalid**; additional injectors (timeout, partial_result, invalid_action_injection, agent_nonresponse, resource spikes, sensor_stale, etc.) are exercised in the `recovery_stress_aux` sweep row and documented in the scenario spec.

## 3. Scoring and reporting

Scoring uses **MAESTRO_REPORT v0.2** (`kernel/eval/MAESTRO_REPORT.v0.2.schema.json`): throughput and latency percentiles, coordination efficiency, explicit safety counters, recovery timing (`time_to_recovery_ms`, `time_to_safe_state_ms` when events are present), `run_outcome`, and structured `safety_violation_types`. Reports are built by `impl/src/labtrust_portfolio/maestro.py` (`maestro_report_from_trace`). Anti-gaming uses a safety-dominant composite score (`impl/src/labtrust_portfolio/maestro_scoring.py`, `bench/maestro/SCORING.md`). Variance remains first-class across seeds.

## 4. Adapter interface and reference adapters

Adapter interface: `run(scenario_id, out_dir, seed, **fault_params) -> AdapterResult`. Reference adapters in `impl/src/labtrust_portfolio/adapters/`: **CentralizedAdapter**, **BlackboardAdapter** (same thin-slice harness; different default delay prior—honestly a parameterization, not a separate distributed architecture), **RetryHeavyAdapter** (retry-on-drop), **NoRecoveryAdapter** (explicit zero retries), **ConservativeSafeShutdownAdapter** (stops after first fault). Under `drop_completion_prob=0.2`, RetryHeavy improves completion relative to Centralized/Blackboard/NoRecovery on many seeds; ConservativeSafeShutdown illustrates partial runs and `failed_safe_shutdown` outcomes.

**Comparison to other benchmarks.** Multi-agent RL benchmarks (e.g. SMAC, MAPF) [1] focus on learning and full simulation; CPS and robotics testbeds [2] often lack a shared fault model and report format. MAESTRO focuses on scenario-driven coordination under fault injection and standardized reporting (tasks_completed, p95 latency, variance) rather than full RL or physical hardware; MAESTRO provides a minimal benchmark set with drop/delay faults and MAESTRO_REPORT schema.

| Benchmark type | Domain | Fault model | Metrics |
|----------------|--------|-------------|---------|
| SMAC / MAPF | Multi-agent RL / pathfinding | N/A or env-specific | Win rate, reward |
| CPS testbeds | Simulation / hardware | Varies | Varies |
| **MAESTRO** | Scenario-driven coordination | drop_completion, delay | tasks_completed, p95, variance |

## 5. Scenarios

- **toy_lab_v0:** minimal 4-task lab (receive_sample, centrifuge, analyze, report_results); thin-slice default. Family: lab.
- **lab_profile_v0:** 5 tasks (receive_sample, centrifuge, analyze, report_results, disposition_commit); supports drop_completion and delay. Family: lab.
- **warehouse_v0:** minimal 3-task auxiliary micro-scenario (pick, move, place); drop_completion and delay. Family: warehouse.
- **traffic_v0:** minimal 3-task auxiliary micro-scenario (sense, plan, actuate); drop_completion and delay. Family: traffic.
- **regime_stress_v0:** 4-task lab with high fault load for meta-controller (P8). Family: lab.

**Scenario taxonomy (source: scenario YAMLs).** Families: lab (toy_lab_v0, lab_profile_v0, regime_stress_v0), warehouse (warehouse_v0), traffic (traffic_v0). Optional field `family` in each scenario YAML; see SCENARIO_SPEC.md. Warehouse_v0 and traffic_v0 are minimal (few tasks); not full-scale benchmarks.

One run per scenario is supported by loading the scenario YAML and running the pipeline with that task list (run_thin_slice(scenario_id=...) or adapter.run(scenario_id, ...)).

## 6. Reproducibility

Dataset layout and release process in `bench/maestro/REPRODUCIBILITY.md`. All runs produce admissible evidence bundles; release script copies to datasets/releases with manifest. **Benchmark release v0.1:** Canonical scenario set defined in `bench/maestro/BENCHMARK_RELEASE.v0.1.md` and `benchmark_scenarios.v0.1.json` (toy_lab_v0, lab_profile_v0, warehouse_v0, traffic_v0, regime_stress_v0). For held-out and train/val/test usage, see P5 (scaling_heldout_eval).

## 7. Baseline results and fault sweep

Numeric tables are **not** duplicated here (they go stale). Authoritative publishable tables: `papers/P4_CPS-MAESTRO/generated_tables.md` (produced by `scripts/export_maestro_tables.py`). Machine-readable sources: `datasets/runs/maestro_fault_sweep/multi_sweep.json` (includes `run_manifest`, per-run recovery and safety fields, `maestro_report_version: "0.2"`), `bench/maestro/baseline_summary.json`, `datasets/runs/maestro_antigaming/antigaming_results.json`. Frozen bundle for citations: `datasets/releases/p4_publishable_v1/`. Index: `datasets/runs/RUN_RESULTS_SUMMARY.md`.

**Figures.** `docs/figures/p4_recovery_curve.png` (mean recovery times by sweep row), `docs/figures/p4_safety_violations.png`, `docs/figures/p4_efficiency_messages.png`, with `.json` sidecars from `scripts/plot_maestro_recovery.py`.

## References

- [1] M. Samvelyan et al., "The StarCraft Multi-Agent Challenge," in Proc. AAMAS, 2019; extended in NeurIPS Deep RL Workshop, 2019. arXiv:1902.04043.
- [2] J. Song et al., "When Cyber-Physical Systems Meet AI: A Benchmark, an Evaluation, and a Way Forward," in Proc. ICSE-SEIP, 2021.

## 8. Limitations

Scope and fault model: [EXPERIMENTS_AND_LIMITATIONS.md](../docs/EXPERIMENTS_AND_LIMITATIONS.md). Per-paper:

- **Anti-gaming (K4):** `antigaming_results.json` ranks strategies using `composite_score` (`bench/maestro/SCORING.md`); legitimate_safe beats always_deny, always_wait, and a synthetic unsafe_high_completion gamer. See `bench/maestro/SCENARIO_SPEC.md` (Anti-gaming).
- **Simulated tasks:** Tasks are simulated in the thin-slice pipeline; no real robots or devices.
- **Fault injection:** Faults (drop, delay) are probabilistic in code, not physical faults or real network/device failures.
- **Minimal scenarios:** Warehouse and traffic scenarios are minimal YAMLs (few tasks); they are not full-scale benchmarks.
- **Adapters:** Centralized and Blackboard share the same thin-slice harness (parameterization only).
- **Scoring:** Automated from TRACE via `maestro_report_from_trace`; composite ranking in `maestro_scoring.py`. No human judge.
- **Synthetic scenarios:** All scenarios (toy_lab, lab_profile, warehouse, traffic, regime_stress) are synthetic; no real lab or physical plant.
- **Recovery metric is a proxy:** Figure 1 plots tasks_completed vs fault setting as a recovery proxy; not full MTTR or time-to-safe-state.

## 9. Methodology and reproducibility

**Methodology:** Hypothesis—standard scenarios, fault model, and scoring yield stable, comparable metrics across adapters and seeds. Metrics: tasks_completed, coordination_messages, task_latency_ms_p95; variance (stdev) over seeds per setting. Baselines: Centralized vs Blackboard (same scenario, seed band); fault sweep no_drop vs drop_005. Kill criterion: if metrics are not comparable across runs or variance is unreported, the suite fails. Portfolio criteria: `docs/STATE_OF_THE_ART_CRITERIA.md`.

**Reproducibility:** Scenario-driven run: `labtrust_portfolio run-thinslice --out-dir <dir>` or `adapter.run(scenario_id, out_dir, seed, **fault_params)`. Publishable sweep: `python scripts/maestro_fault_sweep.py --scenarios toy_lab_v0,lab_profile_v0,warehouse_v0,traffic_v0,regime_stress_v0 --seeds 20` (see `RUN_RESULTS_SUMMARY.md`). Baselines: `python scripts/maestro_baselines.py --seeds 20`. Tables: `python scripts/export_maestro_tables.py --out papers/P4_CPS-MAESTRO/generated_tables.md`. Figures: `python scripts/plot_maestro_recovery.py`. Anti-gaming: `python scripts/maestro_antigaming_eval.py` (`ranked` + `success_criteria_met` + `scoring_reference`). Benchmark set: `bench/maestro/benchmark_scenarios.v0.1.json`. Dataset layout: `bench/maestro/REPRODUCIBILITY.md`, `datasets/README.md`. Integration tests: `tests/test_maestro_p4.py`.

**Submission note.** Publishable evidence is frozen under `datasets/releases/p4_publishable_v1/` with 20 seeds and five scenarios; regenerate with the commands above before amending the bundle.

---

**Claims and backing.**

| Claim | Evidence |
|-------|----------|
| C1 (Stable measurements) | MAESTRO_REPORT v0.2 schema, scenario spec, Table A (fault sweep variance). |
| C2 (Variance first-class) | Table A stdev; fault_sweep repeated seeds. |
| C3 (Adapter tractable) | MAESTROAdapter protocol, Table B baselines (five adapters, two regimes). |
| C4 (Third-party usable) | REPRODUCIBILITY.md, CI, baseline_results.md, BENCHMARK_RELEASE.v0.1.md. |
