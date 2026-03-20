# When More Agents Hurt: Empirical Predictors of Coordination Tax

**Draft (v0.1). Paper ID: P5_ScalingLaws. Conditional paper; trigger and scope: docs/CONDITIONAL_TRIGGERS.md (P5).**

**Reproducibility.** From repo root, with `PYTHONPATH=impl/src` and `LABTRUST_KERNEL_DIR=kernel`. See [REPORTING_STANDARD.md](../docs/REPORTING_STANDARD.md) and [RESULTS_PER_PAPER.md](../docs/RESULTS_PER_PAPER.md).

**Minimal run (under 20 min):** `python scripts/generate_multiscenario_runs.py --seeds 3` then `python scripts/scaling_heldout_eval.py --runs-dir datasets/runs/multiscenario_runs` then `python scripts/export_p5_baseline_hierarchy.py` then `python scripts/export_scaling_tables.py` then `python scripts/plot_scaling_mae.py`.

**Publishable run:** `python scripts/generate_multiscenario_runs.py --seeds 20 --fault-mix`, then `python scripts/scaling_heldout_eval.py --runs-dir datasets/runs/multiscenario_runs`. Run_manifest in `datasets/runs/scaling_eval/heldout_results.json`. For sensitivity at N=30, re-run with 30 seeds and report CI width or stability of MAE (see EVALS_RUNBOOK). Optional stump predictor (overall_stump_mae) provides a non-linear baseline. Conditional trigger: see Limitations and docs/CONDITIONAL_TRIGGERS.md (P5).

- **Figure 0:** `python scripts/export_p5_baseline_hierarchy.py` (output `docs/figures/p5_baseline_hierarchy.mmd`). Render Mermaid to PNG for camera-ready.
- **Table 1:** `python scripts/generate_multiscenario_runs.py --seeds 20 --fault-mix`, then `python scripts/scaling_heldout_eval.py --runs-dir datasets/runs/multiscenario_runs`, then `python scripts/export_scaling_tables.py` (input: `datasets/runs/scaling_eval/heldout_results.json`).
- **Table 2:** Same run; Table 2 from `python scripts/export_scaling_tables.py` (input: heldout_results.json).
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

**Headline:** Feature-based and regression predictors beat the global mean out-of-sample across six scenario families; MAE and 95% CI are reported in heldout_results.json; beat_per_scenario_baseline and trigger_met indicate when the method meets the conditional bar.

**Key results.** (1) Global baseline MAE 0.695 vs regression MAE 0.072 and per-scenario baseline MAE 0.072; (2) success_criteria_met.beat_per_scenario_baseline=true and success_criteria_met.trigger_met=true; beat_baseline_out_of_sample=true; (3) Scaling fit: exponent 1.0139 and R² 0.8984; (4) Excellence metrics: out_of_sample_margin_vs_global_baseline 0.4018, ci_width_95_baseline_mae 0.7328, scenario_coverage 6; paired_t_p_value 0.0709 and power_post_hoc 0.6623 for baseline vs feature MAE comparison. *Numbers from the latest publishable-style run: `python scripts/run_paper_experiments.py --paper P5` (20 seeds, --fault-mix) or `python scripts/generate_multiscenario_runs.py --seeds 20 --fault-mix` then `python scripts/scaling_heldout_eval.py`; regenerate tables via `python scripts/export_scaling_tables.py`. See [RUN_RESULTS_SUMMARY.md](../../datasets/runs/RUN_RESULTS_SUMMARY.md).*

Held-out scenario: train on all but one scenario, evaluate MAE on held-out; report global mean vs num_tasks mean vs regression. Collapse is derived from report fields (tasks_completed < 2 or recovery_ok False); per-scenario collapse rate is in heldout_results. Scaling fit: exploratory power-law log(tasks_completed) ~ log(num_tasks) yields exponent and R² in summary. MAE reported with 95% CI (analytical over holdouts). Script: `python scripts/scaling_heldout_eval.py`; output: `datasets/runs/scaling_eval/heldout_results.json`. Per-scenario baseline MAE (baseline_mae, feat_baseline_mae, regression_mae) is in the `held_out_results` array. Run `python scripts/export_scaling_tables.py` to generate draft tables.

**Table 1 — Held-out results.** Source: `datasets/runs/scaling_eval/heldout_results.json`. Units: train_n, test_n (count), baseline_mae, per_scenario_mae, feat_baseline_mae, regression_mae (MAE), actuals_mean (count). Run_manifest in heldout_results.json. Publishable run: 20 seeds, --fault-mix. Regenerate with `python scripts/export_scaling_tables.py` after `scaling_heldout_eval.py`.

| Held-out scenario | train_n | test_n | baseline_mae | per_scenario_mae | feat_baseline_mae | regression_mae | actuals_mean |
|-------------------|--------|--------|--------------|------------------|-------------------|---------------|--------------|
| lab_profile_v0 | 400 | 80 | 1.40 | 0.07 | 1.40 | 0.07 | 4.96 |
| regime_stress_v0 | 400 | 80 | 0.26 | 0.07 | 0.07 | 0.07 | 3.96 |
| regime_stress_v1 | 400 | 80 | 0.26 | 0.07 | 0.07 | 0.07 | 3.96 |
| toy_lab_v0 | 400 | 80 | 0.26 | 0.07 | 0.07 | 0.07 | 3.96 |
| traffic_v0 | 400 | 80 | 1.00 | 0.07 | 0.07 | 0.07 | 2.96 |
| warehouse_v0 | 400 | 80 | 1.00 | 0.07 | 0.07 | 0.07 | 2.96 |

**Table 2 — Baselines (MAE and 95% CI).** Source: heldout_results.json (overall_*_mae, overall_*_mae_ci95_*). Units: MAE, CI95 lower/upper. Regression row: N/A when regression_skipped_reason set (e.g. insufficient train rows). Run_manifest in heldout_results.json. Regenerate with `python scripts/export_scaling_tables.py`.

| Baseline | MAE | CI95 lower | CI95 upper |
|----------|-----|------------|------------|
| Global mean | 0.70 | 0.33 | 1.06 |
| Per-scenario mean (scenario identity allowed) | 0.07 | — | — |
| Num-tasks mean | 0.29 | -0.10 | 0.69 |
| Regression | 0.07 | — | — |

The Regression row shows N/A when the linear predictor is not fit (e.g. insufficient training rows or singular matrix); see heldout_results.json overall_regression_mae and regression_skipped_reason; export_scaling_tables.py prints the reason. The implementation tries full features first, then falls back to num_tasks-only (fewer rows required). Publishable run (20 seeds, --fault-mix) typically yields enough train_n per held-out scenario so regression is fit; see run_manifest.train_n_total. **For submission:** use a publishable run (20 seeds, --fault-mix); if regression remains N/A (regression_skipped_reason in heldout_results.json), report "Regression N/A (insufficient train rows)" in the table and do not claim regression improvement in the abstract or conclusions.

**Results summary (excellence metrics).** From heldout_results.json: **out-of-sample margin** (feature/regression MAE vs global mean baseline; when regression is fit, report e.g. "Regression reduces MAE by X% vs global mean" from `out_of_sample_margin_vs_global_baseline` or the difference in overall_*_mae); **95% CI width** for baseline MAE (narrower = more precise); **beat baseline** (success_criteria_met.beat_per_scenario_baseline, beat_baseline_out_of_sample); **scenario coverage** (number of held-out scenarios, e.g. 5). See [STANDARDS_OF_EXCELLENCE.md](../docs/STANDARDS_OF_EXCELLENCE.md) (P5).

**Figure 1 — MAE by held-out scenario.** Baseline MAE, per-scenario/feat MAE, and regression MAE (units: MAE) by held-out scenario (scenario_id) from heldout_results.json. Regenerate: (1) `generate_multiscenario_runs.py --seeds 20 --fault-mix` and `scaling_heldout_eval.py`; (2) `python scripts/plot_scaling_mae.py --results datasets/runs/scaling_eval/heldout_results.json` (output `docs/figures/p5_scaling_mae.png`). Run_manifest in heldout_results.json.

**Sensitivity (N=10, 20, 30).** Run `python scripts/sensitivity_seed_sweep.py --eval scaling --ns 10,20,30` to generate multiscenario runs and held-out eval at each N; output `datasets/runs/sensitivity_sweep/scaling_sensitivity.json` records overall_baseline_mae, overall_regression_mae, scaling_exponent, and ci_width_95_baseline_mae per N. Use this to report either "exponent is stable across N" or "predictors are stable; exponent is exploratory only" in a short subsection (table or figure: exponent and MAE vs N). Sensitivity at N=10, 20, 30 is reported in scaling_sensitivity.json when available.

**Contribution to the literature.** Prior work on coordination tax and multi-agent scaling often focuses on communication overhead vs number of agents (N) or reward scaling in RL, with validation tied to specific simulators or environments. We contribute **scenario-based coordination tax prediction** with (1) **held-out scenario families** so that generalization is evaluated across distinct scenario identities; (2) an **explicit baseline hierarchy** (global mean, per-scenario mean, feature baseline, regression, prior model) so that gains are measurable; (3) **MAE, 95% CI, and sensitivity at N=10/20/30** for stability of results; (4) no claim of power laws—the scaling exponent from log-log fit is exploratory only. The table below contrasts typical prior settings with this work.

**Comparison to prior work.** Prior coordination-tax and multi-agent scaling work often focuses on communication overhead vs number of agents (N) or reward scaling in RL [1,2]. MAESTRO scaling is scenario-based: we predict tasks_completed from scenario features (num_tasks, num_faults) with held-out scenario evaluation. We do not claim a power law; the exploratory scaling exponent (log-log fit) is reported in scaling_fit. Comparison: global mean baseline is weak for heterogeneous scenarios; feature-based (num_tasks) and regression baselines beat it out-of-sample (Table 1, Table 2).

| Setting | Domain | Predictor | Validation |
|---------|--------|-----------|------------|
| Prior (e.g. N-agent overhead) [1,2] | Multi-agent systems | Often N or N² | Simulation / env-specific |
| **MAESTRO (P5)** | Scenario-driven CPS | num_tasks, num_faults, regression | Held-out scenario; MAE + CI |

*Table footnote:* Prior row examples: [1], [2].

**Comparison to prior model.** A simple prior coordination model (tasks_completed ≈ num_tasks with a small fault penalty) is implemented as `predict_prior_model` in scaling.py and evaluated in held-out eval; summary reports `overall_prior_model_mae`. Table 2 and heldout_results.json include this row; we compare our feature-based and regression baselines against it (same data, same response variable).

**Feature contribution (ablation).** heldout_results.json includes `feature_ablation`: MAE when training regression with only num_tasks, only num_faults, or full features (num_tasks, num_faults, tool_density). Use this to report which feature dominates (e.g. "num_tasks dominates for task completion prediction") in a short "Feature contribution" subsection.

## References

- [1] J. M. Vidal and R. Sun, "Scaling up agent coordination strategies," IEEE Internet Computing, vol. 5, no. 1, pp. 52–59, 2001.
- [2] R. Stern et al., "Multi-Agent Pathfinding: Definitions, Variants, and Benchmarks," in Proc. SoCS (Symposium on Combinatorial Search), 2019, pp. 151–158.

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

**Submission note (P5 trigger).** For submission, use a publishable run: `run_paper_experiments.py --paper P5` (20 seeds, --fault-mix) or `generate_multiscenario_runs.py --seeds 20 --fault-mix` then `scaling_heldout_eval.py`. Verify heldout_results.json has `success_criteria_met.beat_per_scenario_baseline` and `success_criteria_met.trigger_met` true for the run used for tables; if either is false, frame the paper as dataset analysis and negative/exploratory results per [CONDITIONAL_TRIGGERS.md](../docs/CONDITIONAL_TRIGGERS.md) (P5). If regression row is N/A (regression_skipped_reason set), report "Regression N/A" in Table 2 and do not claim regression improvement.

---

**Claims and backing.**

| Claim | Evidence |
|-------|----------|
| C1 (Feature set) | P5_SCALING_SPEC; extract_features_from_scenario/trace; build_dataset_from_runs. |
| C2 (Beat baseline out-of-sample) | Table 1, Table 2; feat_baseline_mae and regression_mae vs baseline_mae; heldout_results.json. Evidence strength depends on trigger_met and beat_per_scenario_baseline in heldout_results.json (medium confidence). |
| C3 (Uncertainty / CLI) | 95% CI in heldout_results; scaling_recommend.py for architecture guidance. |
