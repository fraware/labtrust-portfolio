# When More Agents Hurt: held-out prediction and coordination scaling in CPS

**Paper ID:** `P5_ScalingLaws`  
**Status:** conditional — primary OOS trigger is **not** met on scenario holdout for the current publishable freeze; family holdout **does** trigger. Claims must follow `claims.yaml` and the JSON paths below.

## Abstract-style summary

We stress MAESTRO thin-slice runs across **six** `real_world` scenario ids, **five** coordination regimes, **four** agent-count levels (1, 2, 4, 8), and **two** fault labels (`no_drop`, `drop_005`), with **30** seeds (**7200** rows). Features combine scenario YAML fields with trace metadata (`agent_count`, `regime_id`, contention proxies, etc.). Linear predictors use **ridge-stabilized** normal equations when the default P5 feature vector has six or more columns (`impl/src/labtrust_portfolio/scaling.py`).

**Frozen snapshot** (headline numbers match `datasets/runs/scaling_eval/heldout_results.json` `run_manifest.commit` **5b280e800ff309c215bbe52f7854805176a632bc**):

- **Leave-one-scenario-out (`tasks_completed`):** `overall_regression_mae` **0.5105**, `overall_feat_baseline_mae` **0.3899**, `overall_baseline_mae` **0.7367**, `mean_regression_pi_coverage_95` **0.7707**, `overall_collapse_rate` **0.00292**, **`trigger_met` false** (regression does not beat the num-tasks bucket baseline). The hardest single fold remains **`lab_profile_v0`** (high regression MAE vs other scenarios; see Table 1).
- **Leave-one-family-out:** `overall_regression_mae` **0.5185**, **`trigger_met` true** (beats global, num-tasks bucket, and regime train-mean baselines on this protocol).
- **Leave-one-regime-out:** `overall_regression_mae` **0.2370**, **`trigger_met` false** (fails vs num-tasks bucket).
- **Leave-one-agent-count-out / leave-one-fault-setting-out:** `overall_regression_mae` **0.2157** / **0.2264**, **`trigger_met` false** in both cases.
- **Sensitivity (scenario LOO, seed caps 10 / 20 / 30):** `overall_regression_mae` **0.5528 → 0.5351 → 0.5105**; **`trigger_met` false** at every cap (`scaling_sensitivity.json`).
- **Recommendation eval:** `regime_selection_accuracy` **0.0257**, `mean_regret_tasks_completed` **0.1049**, `brier_collapse_on_test_rows` **0.0030** (sparse signal; see Table 3).

**Title grounding:** Table 8 and `datasets/runs/scaling_summary/regime_agent_summary.json` give explicit **1→8** agent deltas by family × regime (e.g. decentralized **traffic** / **warehouse**: about **−3.4%** mean `tasks_completed` with large coordination-tax increases; **centralized** shows near-flat throughput with very large coordination-tax growth).

## Reproducibility

`PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/run_paper_experiments.py --paper P5`

Then refresh markdown tables:

`PYTHONPATH=impl/src python scripts/export_scaling_tables.py --results datasets/runs/scaling_eval/heldout_results.json --family-results datasets/runs/scaling_eval_family/heldout_results.json --agent-results datasets/runs/scaling_eval_agent_count/heldout_results.json --recommend-results datasets/runs/scaling_recommend/recommendation_eval.json --sensitivity-results datasets/runs/sensitivity_sweep/scaling_sensitivity.json --regime-agent-summary datasets/runs/scaling_summary/regime_agent_summary.json --out papers/P5_ScalingLaws/generated_tables.md`

`PYTHONPATH=impl/src python scripts/export_scaling_regime_agent_summary.py --runs-dir datasets/runs/multiscenario_runs --out-json datasets/runs/scaling_summary/regime_agent_summary.json --out-md papers/P5_ScalingLaws/regime_agent_summary.md`

If `datasets/runs/**` is ignored, track frozen JSONs with `git add -f` on each path listed in `papers/P5_ScalingLaws/README.md` (including `scaling_eval*/heldout_results.json` when negated in `.gitignore`).

## Main tables

All numerical tables for the manuscript body should be copied from **`papers/P5_ScalingLaws/generated_tables.md`** (Tables 1–8) so the draft cannot drift from the exporter.

## Limits

- Do not claim universal `trigger_met` across holdout modes on this freeze.
- Recommendation and collapse metrics are weakly informative; the paper is strongest on **coordination tax / scaling** plus **evaluation hygiene**.
