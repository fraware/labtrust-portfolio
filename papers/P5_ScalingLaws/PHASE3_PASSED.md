# Phase 3 passed (P5)

Last verification: **2026-04-20** against artifacts produced by:

`PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/run_paper_experiments.py --paper P5`

## Verified

- **Grid:** 7200 multiscenario rows (6 `real_world` scenarios × 5 regimes × agents 1/2/4/8 × `no_drop` / `drop_005` × 30 seeds). `toy_lab_v0` is excluded from the publishable profile by design.
- **Eval commit:** `scaling_eval/heldout_results.json` `run_manifest.commit` **5b280e800ff309c215bbe52f7854805176a632bc** (regenerate to refresh).
- **Held-out JSON** present for scenario, family, regime, agent_count, and fault_setting modes; `success_criteria_met` uses admissible baselines only; oracle block is separate.
- **Strict family rule** implemented in `scaling_heldout_eval.py` (null fold regression → null protocol MAE where applicable); current family artifact has all folds fitting — **family `trigger_met` is true** on this snapshot.
- **Scenario LOO:** `trigger_met` is **false** on `tasks_completed` because full-feature regression does not beat the num-tasks bucket baseline (see Table 2 / JSON).
- **Ridge-stabilized OLS** for `len(feature_cols) >= 6` documented in `docs/P5_SCALING_SPEC.md` and implemented in `impl/src/labtrust_portfolio/scaling.py`.
- **Sensitivity sweep** and **recommendation eval** JSON exist; **Table 3** uses four decimal places for small metrics (Brier, match rate).
- **Title artifact:** `datasets/runs/scaling_summary/regime_agent_summary.json` (7200 rows) and **Table 8** in `generated_tables.md`.

## Honest scope

Only **leave-one-family-out** satisfies `trigger_met` on the primary target in this freeze; other protocols do not. Manuscript must state that explicitly.
