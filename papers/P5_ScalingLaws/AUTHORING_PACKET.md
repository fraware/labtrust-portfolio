# P5 authoring packet (current run)

**Paper:** P5_ScalingLaws  
**Title:** When More Agents Hurt  
**Type:** Conditional (triggered by admissible OOS criteria)

## 1) Question

When agent count and coordination regime vary, can we reliably predict throughput and risk in held-out CPS scenarios without leakage?

## 2) Claims to defend

- **C1:** Coordination behavior (throughput/risk proxies) depends reproducibly on agent count, regime, and task structure.
- **C2:** Predictors generalize out-of-sample and beat admissible baselines on primary target (`tasks_completed`) under scenario and family holdouts.
- **C3:** Regime recommendation is available as a risk-aware artifact, but recommendation-quality metrics must be reported transparently.

## 3) Frozen evidence (latest run)

- Scenario holdout: `datasets/runs/scaling_eval/heldout_results.json`
  - `overall_regression_mae = 0.0962`
  - `overall_baseline_mae = 0.7005`
  - `trigger_met = true`
- Family holdout: `datasets/runs/scaling_eval_family/heldout_results.json`
  - `overall_regression_mae = 0.0774`
  - `trigger_met = true`
- Regime holdout: `datasets/runs/scaling_eval_regime/heldout_results.json`
  - `overall_regression_mae = 0.0952`
  - `trigger_met = false` (feature baseline tie/slight edge)
- Agent-count holdout: `datasets/runs/scaling_eval_agent_count/heldout_results.json`
  - `overall_regression_mae = 0.0952`
  - `trigger_met = false`
- Fault-setting holdout: `datasets/runs/scaling_eval_fault/heldout_results.json`
  - `overall_regression_mae = 0.1000`
  - `trigger_met = false`
- Sensitivity: `datasets/runs/sensitivity_sweep/scaling_sensitivity.json`
  - regression MAE improves from `0.12` (N=10) → `0.11` (N=20) → `0.10` (N=30)
- Recommendation eval: `datasets/runs/scaling_recommend/recommendation_eval.json`
  - `regime_selection_accuracy = 0.0083`
  - `mean_regret_tasks_completed = 0.0458`

## 4) Writing guidance

- Keep C2 scoped to **scenario/family** trigger success.
- Do not overclaim regime-selection quality; report low match-rate and low regret together.
- Explicitly state oracle-vs-admissible split and no-leakage policy.

## 5) Required outputs for draft sync

- `papers/P5_ScalingLaws/DRAFT.md`
- `papers/P5_ScalingLaws/generated_tables.md`
- `papers/P5_ScalingLaws/claims.yaml`
- `papers/P5_ScalingLaws/PHASE3_PASSED.md`
- `papers/P5_ScalingLaws/README.md`
