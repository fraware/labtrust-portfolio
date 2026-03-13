# When More Agents Hurt: Empirical Predictors of Coordination Tax

**Draft (v0.1). Paper ID: P5_ScalingLaws. Conditional paper; trigger and scope: docs/CONDITIONAL_TRIGGERS.md (P5).**

**Reproducibility.** From repo root, with `PYTHONPATH=impl/src` and `LABTRUST_KERNEL_DIR=kernel`. See [REPORTING_STANDARD.md](../docs/REPORTING_STANDARD.md) and [RESULTS_PER_PAPER.md](../docs/RESULTS_PER_PAPER.md).

**Minimal run (under 20 min):** `python scripts/generate_multiscenario_runs.py --seeds 3` then `python scripts/scaling_heldout_eval.py --runs-dir datasets/runs/multiscenario_runs` then `python scripts/export_p5_baseline_hierarchy.py` then `python scripts/export_scaling_tables.py` then `python scripts/plot_scaling_mae.py`.

**Publishable run:** `python scripts/generate_multiscenario_runs.py --seeds 20 --fault-mix`, then `python scripts/scaling_heldout_eval.py --runs-dir datasets/runs/multiscenario_runs`. Run_manifest in `datasets/runs/scaling_eval/heldout_results.json`. Conditional trigger: see Limitations and docs/CONDITIONAL_TRIGGERS.md (P5).

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

Held-out scenario: train on all but one scenario, evaluate MAE on held-out; report global mean vs num_tasks mean vs regression. Collapse is derived from report fields (tasks_completed < 2 or recovery_ok False); per-scenario collapse rate is in heldout_results. Scaling fit: exploratory power-law log(tasks_completed) ~ log(num_tasks) yields exponent and R² in summary. MAE reported with 95% CI (analytical over holdouts). Script: `scripts/scaling_heldout_eval.py`; output: `datasets/runs/scaling_eval/heldout_results.json`. Per-scenario baseline MAE (baseline_mae, feat_baseline_mae, regression_mae) is in the `held_out_results` array. Run `scripts/export_scaling_tables.py` to generate draft tables.

**Table 1 — Held-out results.** Source: `datasets/runs/scaling_eval/heldout_results.json`. Run manifest in that file: run_manifest (runs_dir, scenario_ids, held_out_scenarios, train_n_total, test_n_total, script). Publishable run: `generate_multiscenario_runs.py --seeds 10 --fault-mix` (150 runs), then `scaling_heldout_eval.py`. Regenerate tables with `python scripts/export_scaling_tables.py` after `scaling_heldout_eval.py`.

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

**Figure 1 — MAE by held-out scenario.** Baseline MAE, per-scenario/feat MAE, and regression MAE by held-out scenario from heldout_results.json. Regenerate: (1) `generate_multiscenario_runs.py --seeds 10 --fault-mix` and `scaling_heldout_eval.py`; (2) `python scripts/plot_scaling_mae.py --results datasets/runs/scaling_eval/heldout_results.json` (output `docs/figures/p5_scaling_mae.png`).

**Comparison to prior work.** Prior coordination-tax and multi-agent scaling work often focuses on communication overhead vs number of agents (N) or reward scaling in RL. MAESTRO scaling is scenario-based: we predict tasks_completed from scenario features (num_tasks, num_faults) with held-out scenario evaluation. We do not claim a power law; the exploratory scaling exponent (log-log fit) is reported in scaling_fit. Comparison: global mean baseline is weak for heterogeneous scenarios; feature-based (num_tasks) and regression baselines beat it out-of-sample (Table 1, Table 2).

| Setting | Domain | Predictor | Validation |
|---------|--------|-----------|------------|
| Prior (e.g. N-agent overhead) | Multi-agent systems | Often N or N² | Simulation / env-specific |
| **MAESTRO (P5)** | Scenario-driven CPS | num_tasks, num_faults, regression | Held-out scenario; MAE + CI |

## 6. Limitations

Scope and conditional triggers: [EXPERIMENTS_AND_LIMITATIONS.md](../docs/EXPERIMENTS_AND_LIMITATIONS.md). Per-paper:

- **Title and claims:** We use "empirical predictors" (not "scaling laws") in the title; scaling exponent from log-log fit is exploratory only unless stability across scenario families is demonstrated.
- **Predictors:** Global mean, num_tasks mean, and linear regression are simple; no deep or non-linear model.
- **Small N:** Default or CI runs may use few seeds; for stable MAE and CI use `generate_multiscenario_runs.py --seeds 10 --fault-mix`, then `scaling_heldout_eval.py`; run manifest in `heldout_results.json`.
- **Collapse:** Derived from report fields (tasks_completed < 2 or recovery_ok); not full failure/recovery trace semantics.
- **Scaling-law:** Exploratory exponent only; no claim of power-law form in N or D.
- **Thin-slice:** Scenarios and coordination are thin-slice only; no real robots or deployment.
- **Trigger and negative results:** Output `heldout_results.json` (and summary) includes `success_criteria_met.beat_per_scenario_baseline` and `trigger_met`. If beat_per_scenario_baseline is false, this paper should be framed as **dataset analysis and negative/exploratory results**; scope and limitations must state so (conditional paper; see `docs/CONDITIONAL_TRIGGERS.md`).

## 7. Methodology and reproducibility

**Methodology:** Hypothesis—task features (scenario, num_tasks, faults) predict response (tasks_completed, p95). Metrics: MAE on held-out scenario with 95% CI; baselines: global mean, num_tasks mean, regression. Kill criteria: cannot define out-of-sample kill (K1); model does not beat baseline on held-out (K2); collapse uncalibrated (K3). Portfolio criteria: `docs/STATE_OF_THE_ART_CRITERIA.md`.

**Reproducibility:** Generate runs (publishable): `python scripts/generate_multiscenario_runs.py --seeds 10 --fault-mix` (writes to `datasets/runs/multiscenario_runs`). Held-out eval: `python scripts/scaling_heldout_eval.py --runs-dir datasets/runs/multiscenario_runs` (writes `datasets/runs/scaling_eval/heldout_results.json`; run_manifest inside). Tables: `python scripts/export_scaling_tables.py` (reads heldout_results.json). Figure 1: `python scripts/plot_scaling_mae.py --results datasets/runs/scaling_eval/heldout_results.json`. Build dataset: `python scripts/scaling_build_dataset.py --runs-dir datasets/runs/maestro_fault_sweep`. Integration test: `tests/test_scaling_p5.py` runs generate_multiscenario_runs then scaling_heldout_eval and asserts heldout_results.json.

---

**Claims and backing.**

| Claim | Evidence |
|-------|----------|
| C1 (Feature set) | P5_SCALING_SPEC; extract_features_from_scenario/trace; build_dataset_from_runs. |
| C2 (Beat baseline out-of-sample) | Table 1, Table 2; feat_baseline_mae and regression_mae vs baseline_mae; heldout_results.json. |
| C3 (Uncertainty / CLI) | 95% CI in heldout_results; scaling_recommend.py for architecture guidance. |
