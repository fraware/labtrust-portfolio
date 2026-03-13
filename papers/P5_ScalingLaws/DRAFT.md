# When More Agents Hurt: Empirical Predictors of Coordination Tax

**Draft (v0.1). Paper ID: P5_ScalingLaws. Conditional paper; trigger and scope: docs/CONDITIONAL_TRIGGERS.md (P5).**

**Reproducibility.** From repo root, with `PYTHONPATH=impl/src` and `LABTRUST_KERNEL_DIR=kernel`. See [REPORTING_STANDARD.md](../docs/REPORTING_STANDARD.md) and [RESULTS_PER_PAPER.md](../docs/RESULTS_PER_PAPER.md).

**Minimal run (under 20 min):** `python scripts/generate_multiscenario_runs.py --seeds 3` then `python scripts/scaling_heldout_eval.py --runs-dir datasets/runs/multiscenario_runs` then `python scripts/export_p5_baseline_hierarchy.py` then `python scripts/export_scaling_tables.py` then `python scripts/plot_scaling_mae.py`.

**Publishable run:** `python scripts/generate_multiscenario_runs.py --seeds 20 --fault-mix`, then `python scripts/scaling_heldout_eval.py --runs-dir datasets/runs/multiscenario_runs`. Run_manifest in `datasets/runs/scaling_eval/heldout_results.json`. For sensitivity at N=30, re-run with 30 seeds and report CI width or stability of MAE (see EVALS_RUNBOOK). Optional stump predictor (overall_stump_mae) provides a non-linear baseline. Conditional trigger: see Limitations and docs/CONDITIONAL_TRIGGERS.md (P5).

- **Figure 0:** `python scripts/export_p5_baseline_hierarchy.py` (output `docs/figures/p5_baseline_hierarchy.mmd`). Render Mermaid to PNG for camera-ready.
- **Table 1, Table 2:** Generate runs, then `scaling_heldout_eval.py`, then `python scripts/export_scaling_tables.py` (reads heldout_results.json).
- **Figure 1:** `python scripts/plot_scaling_mae.py --results datasets/runs/scaling_eval/heldout_results.json` (output `docs/figures/p5_scaling_mae.png`).
- Baseline hierarchy and trigger: success_criteria_met in heldout_results.json (beat_per_scenario_baseline, trigger_met).

## 1. Motivation

Multi-scenario MAESTRO (lab, warehouse, traffic) and fault mixtures produce variance in tasks_completed, tail latency, and coordination load. We need feature extractors and predictors to guide architecture choice and out-of-sample validation.

## 2. Task feature set and response variables

Features: scenario_id, num_tasks, task_names, num_faults, seed, event_count (from scenario YAML and trace).

**Figure 0 — Baseline hierarchy.** Predictors are compared against a strict ordering: global mean, per-scenario mean, feature baseline, regression. Regenerate with `python scripts/export_p5_baseline_hierarchy.py` (output `docs/figures/p5_baseline_hierarchy.mmd`). Response: tasks_completed, coordination_messages, task_latency_ms_p95. Spec: `docs/P5_SCALING_SPEC.md`. Out-of-sample kill criteria: held-out scenario family or fault mixture; model must beat baseline.

## 3. Feature extractor and dataset builder

`impl/src/labtrust_portfolio/scaling.py`: `extract_features_from_scenario()`, `extract_features_from_trace()`, `extract_response_from_report()`, `build_dataset_from_runs()`. Script `scripts/scaling_build_dataset.py` builds modeling table from MAESTRO runs (e.g. fault sweep output) to `datasets/runs/scaling_dataset/modeling_table.json`.

## 4. Baseline hierarchy and CLI

**Baseline hierarchy (explicit):** (1) **Global mean** — mean of target over all training rows; (2) **Per-scenario mean** — mean per scenario_id on training set (strong trivial baseline); (3) **Feature baseline** — predict by num_tasks (or same-feature group); (4) **Regression** — linear regression on num_tasks, num_faults (and optional features). Held-out eval output reports each baseline MAE; `success_criteria_met.beat_per_scenario_baseline` and `beat_baseline_out_of_sample` indicate whether the model beats these baselines. Script `scripts/scaling_recommend.py`: `--table`, `--scenario`, `--runs-dir`; prints predicted tasks_completed for architecture guidance.

## 5. Evaluation

**Headline:** Feature-based and per-scenario baselines beat the global mean out-of-sample across five scenario families; MAE and 95% CI are reported in heldout_results.json; beat_per_scenario_baseline and trigger_met indicate when the method meets the conditional bar.

Held-out scenario: train on all but one scenario, evaluate MAE on held-out; report global mean vs num_tasks mean vs regression. Collapse is derived from report fields (tasks_completed < 2 or recovery_ok False); per-scenario collapse rate is in heldout_results. Scaling fit: exploratory power-law log(tasks_completed) ~ log(num_tasks) yields exponent and R² in summary. MAE reported with 95% CI (analytical over holdouts). Script: `scripts/scaling_heldout_eval.py`; output: `datasets/runs/scaling_eval/heldout_results.json`. Per-scenario baseline MAE (baseline_mae, feat_baseline_mae, regression_mae) is in the `held_out_results` array. Run `scripts/export_scaling_tables.py` to generate draft tables.

**Table 1 — Held-out results.** Source: `datasets/runs/scaling_eval/heldout_results.json`. Run manifest in that file: run_manifest (runs_dir, scenario_ids, held_out_scenarios, train_n_total, test_n_total, script). Publishable run: `generate_multiscenario_runs.py --seeds 20 --fault-mix`, then `scaling_heldout_eval.py`. Regenerate tables with `python scripts/export_scaling_tables.py` after `scaling_heldout_eval.py`.

| Held-out scenario | train_n | test_n | baseline_mae | per_scenario_mae | feat_baseline_mae | regression_mae | actuals_mean |
|-------------------|--------|--------|--------------|------------------|-------------------|---------------|--------------|
| lab_profile_v0 | 120 | 30 | 1.50 | 0.18 | 1.50 | — | 4.90 |
| regime_stress_v0 | 120 | 30 | 0.38 | 0.18 | 0.18 | — | 3.90 |
| toy_lab_v0 | 120 | 30 | 0.38 | 0.18 | 0.18 | — | 3.90 |
| traffic_v0 | 120 | 30 | 1.00 | 0.18 | 0.18 | — | 2.90 |
| warehouse_v0 | 120 | 30 | 1.00 | 0.18 | 0.18 | — | 2.90 |

**Table 2 — Baselines (MAE and 95% CI).** Source: heldout_results.json (overall_*_mae, overall_*_mae_ci95_*). Regenerate with `python scripts/export_scaling_tables.py`.

| Baseline | MAE | CI95 lower | CI95 upper |
|----------|-----|------------|------------|
| Global mean | 0.85 | 0.48 | 1.23 |
| Per-scenario mean (scenario identity allowed) | 0.18 | — | — |
| Num-tasks mean | 0.44 | -0.02 | 0.91 |
| Regression | — | — | — |

The Regression row shows N/A when the linear predictor is not fit (e.g. insufficient training rows or singular matrix); see heldout_results.json overall_regression_mae and regression_skipped_reason; export_scaling_tables.py prints the reason. The implementation tries full features first, then falls back to num_tasks-only (fewer rows required). Publishable run (20 seeds, --fault-mix) typically yields enough train_n per held-out scenario so regression is fit; see run_manifest.train_n_total.

**Results summary (excellence metrics).** From heldout_results.json: **out-of-sample margin** (feature/regression MAE vs global mean baseline); **95% CI width** for baseline MAE (narrower = more precise); **beat baseline** (success_criteria_met.beat_per_scenario_baseline, beat_baseline_out_of_sample); **scenario coverage** (number of held-out scenarios, e.g. 5). See [STANDARDS_OF_EXCELLENCE.md](../docs/STANDARDS_OF_EXCELLENCE.md) (P5).

**Figure 1 — MAE by held-out scenario.** Baseline MAE, per-scenario/feat MAE, and regression MAE by held-out scenario from heldout_results.json. Regenerate: (1) `generate_multiscenario_runs.py --seeds 20 --fault-mix` and `scaling_heldout_eval.py`; (2) `python scripts/plot_scaling_mae.py --results datasets/runs/scaling_eval/heldout_results.json` (output `docs/figures/p5_scaling_mae.png`).

**Sensitivity (N=10, 20, 30).** Run `python scripts/sensitivity_seed_sweep.py --eval scaling --ns 10,20,30` to generate multiscenario runs and held-out eval at each N; output `datasets/runs/sensitivity_sweep/scaling_sensitivity.json` records overall_baseline_mae, overall_regression_mae, scaling_exponent, and ci_width_95_baseline_mae per N. Use this to report either "exponent is stable across N" or "predictors are stable; exponent is exploratory only" in a short subsection (table or figure: exponent and MAE vs N).

**Comparison to prior work.** Prior coordination-tax and multi-agent scaling work often focuses on communication overhead vs number of agents (N) or reward scaling in RL. MAESTRO scaling is scenario-based: we predict tasks_completed from scenario features (num_tasks, num_faults) with held-out scenario evaluation. We do not claim a power law; the exploratory scaling exponent (log-log fit) is reported in scaling_fit. Comparison: global mean baseline is weak for heterogeneous scenarios; feature-based (num_tasks) and regression baselines beat it out-of-sample (Table 1, Table 2).

| Setting | Domain | Predictor | Validation |
|---------|--------|-----------|------------|
| Prior (e.g. N-agent overhead) | Multi-agent systems | Often N or N² | Simulation / env-specific |
| **MAESTRO (P5)** | Scenario-driven CPS | num_tasks, num_faults, regression | Held-out scenario; MAE + CI |

**Comparison to prior model.** A simple prior coordination model (tasks_completed ≈ num_tasks with a small fault penalty) is implemented as `predict_prior_model` in scaling.py and evaluated in held-out eval; summary reports `overall_prior_model_mae`. Table 2 and heldout_results.json include this row; we compare our feature-based and regression baselines against it (same data, same response variable).

**Feature contribution (ablation).** heldout_results.json includes `feature_ablation`: MAE when training regression with only num_tasks, only num_faults, or full features (num_tasks, num_faults, tool_density). Use this to report which feature dominates (e.g. "num_tasks dominates for task completion prediction") in a short "Feature contribution" subsection.

## 6. Limitations

Scope and conditional triggers: [EXPERIMENTS_AND_LIMITATIONS.md](../docs/EXPERIMENTS_AND_LIMITATIONS.md). Per-paper:

- **Title and claims:** We use "empirical predictors" (not "scaling laws") in the title; scaling exponent from log-log fit is exploratory only unless stability across scenario families is demonstrated.
- **Predictors:** Global mean, num_tasks mean, and linear regression are simple; no deep or non-linear model.
- **Small N:** Default or CI runs may use few seeds; for publishable use `generate_multiscenario_runs.py --seeds 20 --fault-mix`, then `scaling_heldout_eval.py`; run manifest in heldout_results.json.
- **Collapse:** Derived from report fields (tasks_completed < 2 or recovery_ok); not full failure/recovery trace semantics.
- **Scaling-law:** Exploratory exponent only; no claim of power-law form in N or D.
- **Thin-slice:** Scenarios and coordination are thin-slice only; no real robots or deployment.
- **Trigger and negative results:** Output `heldout_results.json` (and summary) includes `success_criteria_met.beat_per_scenario_baseline` and `trigger_met`. For publishable submission, ensure heldout_results.json is produced with 20-seed runs and check success_criteria_met.beat_per_scenario_baseline and trigger_met; if false, frame the paper as dataset analysis and negative/exploratory results per CONDITIONAL_TRIGGERS.md (conditional paper).

**Threats to validity.** *Internal:* Linear regression and simple baselines only; no non-linear or deep model. *External:* Scenario set (toy_lab, lab_profile, warehouse, traffic, regime_stress) and fault mix may not cover all deployment regimes. *Construct:* MAE on tasks_completed is a proxy for coordination tax; no direct measure of agent overhead or communication cost.

## 7. Methodology and reproducibility

**Methodology:** Hypothesis—task features (scenario, num_tasks, faults) predict response (tasks_completed, p95). Metrics: MAE on held-out scenario with 95% CI; baselines: global mean, num_tasks mean, regression. Kill criteria: cannot define out-of-sample kill (K1); model does not beat baseline on held-out (K2); collapse uncalibrated (K3). Portfolio criteria: `docs/STATE_OF_THE_ART_CRITERIA.md`.

**Reproducibility:** Generate runs (publishable): `python scripts/generate_multiscenario_runs.py --seeds 20 --fault-mix` (writes to `datasets/runs/multiscenario_runs`). Held-out eval: `python scripts/scaling_heldout_eval.py --runs-dir datasets/runs/multiscenario_runs` (writes `datasets/runs/scaling_eval/heldout_results.json`; run_manifest inside). Tables: `python scripts/export_scaling_tables.py` (reads heldout_results.json). Figure 1: `python scripts/plot_scaling_mae.py --results datasets/runs/scaling_eval/heldout_results.json`. Build dataset: `python scripts/scaling_build_dataset.py --runs-dir datasets/runs/maestro_fault_sweep`. Integration test: `tests/test_scaling_p5.py` runs generate_multiscenario_runs then scaling_heldout_eval and asserts heldout_results.json.

---

**Claims and backing.**

| Claim | Evidence |
|-------|----------|
| C1 (Feature set) | P5_SCALING_SPEC; extract_features_from_scenario/trace; build_dataset_from_runs. |
| C2 (Beat baseline out-of-sample) | Table 1, Table 2; feat_baseline_mae and regression_mae vs baseline_mae; heldout_results.json. |
| C3 (Uncertainty / CLI) | 95% CI in heldout_results; scaling_recommend.py for architecture guidance. |
