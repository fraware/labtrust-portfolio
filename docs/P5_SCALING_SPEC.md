# P5 Scaling Laws: Spec (v0.2)

## Experimental factors

- **scenario_id / scenario_family:** From scenario YAML (`family`: lab, warehouse, traffic, …).
- **fault_setting_label:** Generator folder label (`no_drop`, `drop_005`, optional `calibration_invalid_01`, `delay_01` with `--fault-mix`).
- **agent_count:** 1, 2, 4, 8 (full grid) or `--p5-lite` subset `[1, 4]`.
- **coordination_regime:** `centralized`, `hierarchical`, `blackboard`, `market`, `decentralized` (full grid) or lite subset.
- **seed:** Reproducible RNG for thin-slice faults and delays.

Thin-slice **actually** varies coordination dynamics: extra `coordination_message` events (regime pre-task and intra-task handoffs), actor rotation across `agent_*`, stress-scaled effective drop probability, and metadata from `coordination_profile.coordination_experiment_profile` (shared in `impl/src/labtrust_portfolio/coordination_profile.py`).

## Feature and response columns

From scenario YAML: `num_tasks`, `num_faults`, `tool_density`, `fault_density`, `sequential_depth_proxy`, `resource_coupling_index`.

From trace metadata: `agent_count`, `coordination_regime`, `coordination_topology`, `hierarchy_depth`, `fan_out`, `handoff_factor`, `shared_state_contention`, `deadline_tightness`, `critical_path_length`, `branching_factor`, `queue_contention_index`, `regime_fault_interaction`, `regime_id`, `fault_setting_label`, `seed`, `event_count`.

Responses: `tasks_completed`, `coordination_messages`, `task_latency_ms_p95`, `recovery_ok`, `fault_injected`. Derived: `coordination_tax_proxy`, `error_amplification_proxy`, boolean `collapse`, float `collapse_probability` in `response` for regression.

Default regression feature vector: `DEFAULT_FEATURE_COLS_P5` in `scaling.py` (OLS with Gauss-Jordan inverse for moderate `k`).

## Held-out protocols

Implemented in `build_scaling_holdout_folds` (`scaling.py`), evaluated by `scripts/scaling_heldout_eval.py`:

| Mode | Meaning |
|------|---------|
| `scenario` | Leave-one-scenario-out |
| `family` | Leave-one-family-out |
| `regime` | Leave-one-coordination-regime-out |
| `agent_count` | Leave-one-agent-count-out |
| `fault_setting` | Leave-one-fault-setting-label-out |

**Baselines**

- **Admissible (train-only):** global mean; per-scenario mean with **train rows only** (fallback to train global when held-out scenario never appears in train); num-tasks bucket mean; train-only mean per `coordination_regime`; train-only mean per `agent_count`; linear regression; tree stump on `num_tasks`.
- **Oracle (analysis):** per-scenario mean computed using **all rows including the held-out test rows** for that scenario (`oracle_baselines` in JSON). Never used for `trigger_met`.

**Triggers:** `success_criteria_met.trigger_met` requires regression to beat global, feature, and regime **admissible** baselines out-of-sample (`beat_*_out_of_sample` booleans). `beat_oracle_per_scenario_baseline` is informational. `negative_result` is true when regression fit exists but admissible trigger fails.

## Artifacts and scripts

| Path | Role |
|------|------|
| `scripts/generate_multiscenario_runs.py` | Sweeps scenarios × faults × (optional `--coordination-grid`) × `--clean` |
| `scripts/scaling_heldout_eval.py` | Held-out eval; `--max-seed` for sensitivity subsampling |
| `scripts/scaling_sensitivity_sweep.py` | Caps 10/20/30 → `sensitivity_sweep/scaling_sensitivity.json` |
| `scripts/scaling_recommend_eval.py` | LOFO regime recommendation metrics |
| `scripts/scaling_recommend.py` | CLI counterfactual regime table |
| `scripts/export_scaling_tables.py` | Markdown tables from JSON |
| `scripts/plot_scaling_paper.py` | Figures 0–5 |
| `python scripts/run_paper_experiments.py --paper P5` | Full publishable orchestration |

## Kill / negative-result policy

If `trigger_met` is false, or secondary targets show `negative_result`, the draft must report exploratory / negative scope (see `CONDITIONAL_TRIGGERS.md`).
