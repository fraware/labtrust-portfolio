# P5 - When More Agents Hurt (coordination scaling)

P5 measures how **agent count** and **coordination regime** affect MAESTRO thin-slice outcomes, and evaluates whether compact predictors generalize out-of-sample under strict no-leakage rules.

## One command

`PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/run_paper_experiments.py --paper P5`

- `--quick` runs a CI-sized sweep.
- Default run uses 30 seeds, `real_world` profile, `--fault-mix`, bounded coordination grid (`--p5-lite`), and writes all paper artifacts.

## Main artifacts

- `datasets/runs/scaling_eval/heldout_results.json`
- `datasets/runs/scaling_eval_family/heldout_results.json`
- `datasets/runs/scaling_eval_regime/heldout_results.json`
- `datasets/runs/scaling_eval_agent_count/heldout_results.json`
- `datasets/runs/scaling_eval_fault/heldout_results.json`
- `datasets/runs/sensitivity_sweep/scaling_sensitivity.json`
- `datasets/runs/scaling_recommend/recommendation_eval.json`
- `papers/P5_ScalingLaws/generated_tables.md`
- `docs/figures/p5_fig*.png`

## Trigger semantics (conditional paper)

Go/no-go is `success_criteria_met.trigger_met` from **admissible** baselines only:

- `beat_global_mean_out_of_sample`
- `beat_feature_baseline_out_of_sample`
- `beat_regime_baseline_out_of_sample`

Oracle baselines are reported separately and never drive `trigger_met`.

Spec: `docs/P5_SCALING_SPEC.md`.
