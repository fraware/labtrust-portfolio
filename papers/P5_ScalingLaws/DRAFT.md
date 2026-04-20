# When More Agents Hurt: held-out prediction and coordination scaling in CPS

**Paper ID:** `P5_ScalingLaws`  
**Status:** conditional, evidence-backed on frozen artifacts; publishable path uses the **rich coordination grid** below.

## Abstract-style summary

This study evaluates whether compact predictors can anticipate coordination outcomes in MAESTRO CPS thin-slice runs when coordination regime and agent count vary. The **default publishable** sweep (`run_paper_experiments.py --paper P5`, non-`--quick`) uses six `real_world` scenario ids, **five** coordination regimes (`blackboard`, `centralized`, `decentralized`, `hierarchical`, `market`), **four** agent-count levels (1, 2, 4, 8), **two** fault labels (`no_drop`, `drop_005`) to bound runtime, and 30 seeds — **7200** thin-slice rows before held-out evaluation. Evaluation distinguishes admissible train-only baselines from oracle analysis baselines to prevent leakage.

On the **latest rich-grid run** (terminal log / `heldout_results.json` from that run), **primary `tasks_completed` triggers are not met** on leave-one-scenario-out: `overall_regression_mae` is dominated by a single pathological fold (`rep_cps_scheduling_v0`, regression MAE ~13) while the num-tasks-only ablation stays near ~0.20 MAE, so `trigger_met = false` and `negative_result = true`. **Ridge-style stabilization** is now applied in `scaling._ols_fit` for long P5 feature vectors (`len(feature_cols) >= 6`); **re-run** `python scripts/run_paper_experiments.py --paper P5` after pulling to regenerate frozen JSON and tables with stabilized OLS.

Family holdout uses strict protocol semantics: if any fold cannot fit regression (`regression_mae = null`), then `overall_regression_mae = null`, `trigger_met = false` (e.g. missing fold `lab` in the same run log). Regime holdout in that log beats global/regime/agent baselines but **fails** the admissible trigger because regression does not beat the **num-tasks bucket** baseline (`beat_feature_baseline_out_of_sample = false`).

## Reproducibility

From repo root:

`PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/run_paper_experiments.py --paper P5`

Outputs include:

- `datasets/runs/scaling_eval/heldout_results.json`
- `datasets/runs/scaling_eval_family/heldout_results.json`
- `datasets/runs/scaling_eval_regime/heldout_results.json`
- `datasets/runs/scaling_eval_agent_count/heldout_results.json`
- `datasets/runs/scaling_eval_fault/heldout_results.json`
- `datasets/runs/scaling_summary/regime_agent_summary.json` (track with `git add -f` if your clone ignores `datasets/runs/**`)
- `datasets/runs/sensitivity_sweep/scaling_sensitivity.json`
- `datasets/runs/scaling_recommend/recommendation_eval.json`
- `papers/P5_ScalingLaws/generated_tables.md`
- `docs/figures/p5_fig0_pipeline.png` … `p5_fig5_sensitivity.png`

## Main evidence highlights (rich grid; align to your frozen JSON after re-run)

- **Design:** 7200 rows; regimes × {1,2,4,8} agents; `no_drop` / `drop_005`; `overall_collapse_rate` on scenario holdout ≈ **0.0029** (nonzero in log).
- **Scenario LOO (`tasks_completed`):** `overall_regression_mae` ≈ **2.34**, `overall_feat_baseline_mae` ≈ **0.39**, `trigger_met` **false** — see per-fold table for `rep_cps_scheduling_v0` vs other scenarios.
- **Family LOO:** `overall_regression_mae` **null**, `regression_skipped_reason` cites missing regression on fold `lab`, `trigger_met` **false**.
- **Regime LOO:** `overall_regression_mae` ≈ **0.23**, `trigger_met` **false** (fails vs num-tasks bucket).
- **Regime × agent summary:** cite **Table 8** / `scaling_summary/regime_agent_summary.json` for title-level deltas (throughput vs coordination tax when scaling agents).

## Limits and honest scope

- Primary OLS on the full feature vector can **fail the admissible trigger** on the rich grid until ridge-stabilized artifacts are re-frozen; interpret older drafts that assumed a smaller grid with care.
- Recommendation metrics remain exploratory (low regime match rate in logs).
- Collapse remains sparse but **nonzero** in the rich-grid scenario holdout log; still not a strong collapse-risk paper without a dedicated stress slice.

This paper should claim **disciplined leakage-aware evaluation**, **explicit coordination scaling tables**, and **transparent negative / null trigger results** where the data demand it — not an unconditional “we beat all baselines” story on every protocol.
