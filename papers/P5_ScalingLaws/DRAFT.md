# When More Agents Hurt: held-out prediction and coordination scaling in CPS

**Paper ID:** `P5_ScalingLaws`  
**Status:** conditional, evidence-backed on latest frozen artifacts.

## Abstract-style summary

This study evaluates whether compact predictors can anticipate coordination outcomes in MAESTRO CPS thin-slice runs when coordination regime and agent count vary. The dataset spans six real-world scenario ids (`lab_profile_v0`, `regime_stress_v0`, `regime_stress_v1`, `rep_cps_scheduling_v0`, `traffic_v0`, `warehouse_v0`), four fault settings, three coordination regimes (`centralized`, `hierarchical`, `decentralized`), two agent-count levels (1 and 4), and 30 seeds. Evaluation distinguishes admissible train-only baselines from oracle analysis baselines to prevent leakage.

Primary result (`tasks_completed`): leave-one-scenario-out regression MAE is **0.0962** vs global mean MAE **0.7005** (`trigger_met = true`). Family holdout also triggers (`overall_regression_mae = 0.0774`, `trigger_met = true`). Regime-, agent-count-, and fault-setting holdouts are more stringent and currently do not satisfy the same trigger definition (`trigger_met = false`), which is reported explicitly as a limitation rather than hidden.

## Reproducibility

From repo root:

`PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/run_paper_experiments.py --paper P5`

Outputs:

- `datasets/runs/scaling_eval/heldout_results.json`
- `datasets/runs/scaling_eval_family/heldout_results.json`
- `datasets/runs/scaling_eval_regime/heldout_results.json`
- `datasets/runs/scaling_eval_agent_count/heldout_results.json`
- `datasets/runs/scaling_eval_fault/heldout_results.json`
- `datasets/runs/sensitivity_sweep/scaling_sensitivity.json`
- `datasets/runs/scaling_recommend/recommendation_eval.json`
- `papers/P5_ScalingLaws/generated_tables.md`
- `docs/figures/p5_fig0_pipeline.png` ... `p5_fig5_sensitivity.png`

## Main evidence highlights

- Scenario holdout (`scaling_eval`):
  - `overall_regression_mae = 0.0962`
  - `overall_baseline_mae = 0.7005`
  - `mean_regression_pi_coverage_95 = 0.9521`
  - `trigger_met = true`
- Family holdout (`scaling_eval_family`):
  - `overall_regression_mae = 0.0774`
  - `trigger_met = true`
- Sensitivity (`scaling_sensitivity.json`):
  - regression MAE improves monotonically across caps 10/20/30 (`0.12 → 0.11 → 0.10`).
- Recommendation (`recommendation_eval.json`):
  - `regime_selection_accuracy = 0.0083`
  - `mean_regret_tasks_completed = 0.0458`
  - reported as exploratory; not a strong C3 win.

## Limits and honest scope

- No observed collapse events in this run set (`overall_collapse_rate = 0.0` in primary heldout), so collapse calibration remains weakly stressed.
- Strong OOS result is currently for scenario/family holdouts; not all alternate holdouts satisfy trigger criteria.
- Recommendation quality metrics do not support a strong “best-regime selector” claim yet.

This paper should therefore claim strong primary OOS prediction and disciplined leakage-free evaluation, while treating architecture-selection superiority as exploratory.
