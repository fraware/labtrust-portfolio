# P5 authoring packet (rich grid, frozen JSON)

**Paper:** `P5_ScalingLaws`  
**Title:** When More Agents Hurt  
**Type:** Conditional — `trigger_met` is protocol-specific; cite each `heldout_results.json` separately.

## 1) Question

When agent count and coordination regime vary across realistic CPS scenarios, what measurable coordination tax and throughput patterns appear, and can compact predictors generalize out-of-sample under strict no-leakage baselines?

## 2) Claims to defend (see `claims.yaml`)

- **C1:** Coordination outcomes and title-level scaling deltas are reproducible functions of scenario family, regime, and agent count (thin-slice + `regime_agent_summary.json`).
- **C2:** Held-out evaluation separates **admissible** train-only baselines from **oracle** baselines; strict aggregation when any fold has null regression; ridge-stabilized OLS for long feature vectors (`scaling.py`). Trigger success is **not** asserted for every protocol on the current publishable grid.
- **C3:** Regime recommendation / regret artifacts exist; selection accuracy is low — report as exploratory.

## 3) Publishable grid (default `--paper P5`)

Six `real_world` scenarios × five regimes × agent counts `{1,2,4,8}` × fault labels `{no_drop, drop_005}` × 30 seeds → **7200** rows in `datasets/runs/multiscenario_runs/`.

## 4) Frozen evidence (sync to JSON; values from commit `d2532be` artifacts)

| Artifact | `tasks_completed` headline |
|----------|-----------------------------|
| `datasets/runs/scaling_eval/heldout_results.json` (scenario LOO) | `overall_regression_mae` **0.5105**, `overall_feat_baseline_mae` **0.3899**, `overall_baseline_mae` **0.7367**, `trigger_met` **false** (`beat_feature_baseline_out_of_sample` false). `overall_collapse_rate` **0.00292**. |
| `datasets/runs/scaling_eval_family/heldout_results.json` | `overall_regression_mae` **0.5185**, `trigger_met` **true**. |
| `datasets/runs/scaling_eval_regime/heldout_results.json` | `overall_regression_mae` **0.2370**, `trigger_met` **false** (fails num-tasks bucket vs regression margin). |
| `datasets/runs/scaling_eval_agent_count/heldout_results.json` | `overall_regression_mae` **0.2157**, `trigger_met` **false**. |
| `datasets/runs/scaling_eval_fault/heldout_results.json` | `overall_regression_mae` **0.2264**, `trigger_met` **false**. |
| `datasets/runs/sensitivity_sweep/scaling_sensitivity.json` | Scenario LOO, caps 10 / 20 / 30: `overall_regression_mae` **0.5528** → **0.5351** → **0.5105**; all caps **`trigger_met` false**. |
| `datasets/runs/scaling_recommend/recommendation_eval.json` | `regime_selection_accuracy` **0.0285**, `mean_regret_tasks_completed` **0.1049**, `brier_collapse_on_test_rows` **0.0030**. |
| `datasets/runs/scaling_summary/regime_agent_summary.json` | **7200** rows; Table 8 / `regime_agent_summary.md` for regime × agent deltas (1→8). |

## 5) Writing guidance

- Lead with **coordination scaling evidence** (Table 8 + thin-slice metadata); OOS triggers are secondary and protocol-dependent.
- Never merge oracle MAE into trigger prose.
- If any fold has `regression_mae: null`, protocol-level regression MAE is null and `trigger_met` is false per strict rule.
- Cite **exact** paths above; refresh numbers only by re-running `run_paper_experiments.py --paper P5` and regenerating tables.

## 6) Files to keep in lockstep

- `papers/P5_ScalingLaws/DRAFT.md`
- `papers/P5_ScalingLaws/generated_tables.md` (from `export_scaling_tables.py`)
- `papers/P5_ScalingLaws/regime_agent_summary.md` (from `export_scaling_regime_agent_summary.py`)
- `papers/P5_ScalingLaws/claims.yaml`
- `papers/P5_ScalingLaws/PHASE3_PASSED.md`
- `papers/P5_ScalingLaws/README.md`
