# When More Agents Hurt: Held-Out Evaluation of Coordination Scaling in Cyber-Physical Agent Systems

**Paper ID:** `P5_ScalingLaws`  
**Status:** NeurIPS E&D posture — **evaluation protocol + empirical benchmark**, not a universal CPS scaling law or a deployment-ready predictor. Claims must follow `CLAIM_LOCK_NEURIPS2026.md`, `claim_sources.yaml`, and frozen JSON.

This paper is about **the difference between measuring a pattern and claiming it generalizes**.

We test whether **coordination-scaling regularities** (rising coordination tax, flat or degraded throughput as agents scale) remain **predictive** under strict held-out protocols and **admissible** train-only baselines—not whether a universal CPS scaling law exists.

## Abstract (six sentences)

Many multi-agent CPS discussions assume more agents improve capability, but coordination overhead can dominate. We introduce a frozen MAESTRO thin-slice grid of **7,200** runs to measure throughput, latency, coordination tax, and held-out predictability under strict admissible baselines. Empirically, coordination tax rises sharply from **1** to **8** agents, while throughput often saturates or degrades. Under the main leave-one-scenario-out protocol, regression improves over the global mean but **fails** against the strongest admissible **num-tasks bucket** baseline (`trigger_met` **false**): the bucket baseline is **harder to beat** than the global mean, so the negative trigger is informative, not a trivial baseline artifact. Leave-one-family-out **does** trigger, while regime, agent-count, and fault holdouts **do not** on the current freeze. The contribution is a **reproducible evaluation protocol** that separates empirical coordination-scaling patterns from valid held-out predictive claims — **we do not establish a general scaling law.**

## Introduction

Scaling agent teams in cyber-physical workflows does not guarantee higher throughput: coordination traffic can grow faster than completed work. **This paper is about the difference between measuring a pattern and claiming it generalizes.** We document empirical coordination-scaling patterns on a frozen MAESTRO thin-slice grid, then stress-test predictability under multiple leave-one-out splits with ridge-stabilized linear regression and admissible baselines. The scenario-heldout **failure** to beat the num-tasks bucket baseline is the **methodological core**: apparent structure can evaporate under a strong admissible comparator.

## Methods

1. **Grid:** Six `real_world` scenario identifiers × five coordination regimes × agent counts {1, 2, 4, 8} × fault labels `no_drop` / `drop_005` × 30 seeds → **7,200** rows (`multiscenario_runs/`).
2. **Features:** Fixed P5 feature vector from scenario YAML + trace-derived fields (`impl/src/labtrust_portfolio/scaling.py`).
3. **Responses:** `tasks_completed` (primary); secondary proxies `coordination_tax_proxy`, `error_amplification_proxy` in `secondary_targets`.
4. **Proxies:** Coordination-tax proxy = coordination_messages / max(1, tasks_completed); see `docs/P5_COORDINATION_TAX_PROXY.md`. We call this a **proxy** because it measures message load per completed task inside the MAESTRO trace semantics, not a universal cost or energy measure.
5. **Held-out protocols:** Leave-one-scenario-out (main), leave-one-family-out, leave-one-regime-out, leave-one-agent-count-out, leave-one-fault-setting-out.
6. **Baselines:** Admissible train-only baselines (global mean, num-tasks bucket, regime train mean, etc.) vs oracle diagnostics; see `docs/P5_BASELINE_DISCIPLINE.md`.
7. **Triggers:** `success_criteria_met.trigger_met` uses **admissible** beats only (global, **num-tasks bucket**, regime train mean). Oracle rows are never used for triggers.
8. **Strict nulling:** If any fold cannot fit regression, protocol-level `overall_regression_mae` is null and `trigger_met` is false.

We treat oracle per-scenario means as diagnostic upper bounds, not baselines. The trigger semantics use only train-only admissible baselines. This prevents the study from confusing improvement over a weak global mean with genuine held-out generalization.

## Results (submission order)

1. **Title grounding:** Main Table 1 — regime × family **1→8** deltas for tasks, coordination tax, p95 latency (`regime_agent_summary.json`).
2. **Scenario-heldout negative result:** Main Table 2 — `tasks_completed`; protocol-level **`trigger_met` false** vs num-tasks bucket.
3. **Protocol comparison:** Main Table 3 — same predictor, different held-out axes; generalization is **protocol-dependent**.
4. **Secondary targets:** Main Table 4 — coordination tax is **much more predictable than throughput (`tasks_completed`) or latency-derived error amplification** under scenario-heldout (admissible regression MAE and `trigger_met`); coordination-tax regression **meets** the admissible trigger while `tasks_completed` does **not**; raw MAE scales differ across targets.
5. **Sensitivity:** Appendix — seed caps (`scaling_sensitivity.json`).
6. **Recommendation:** Appendix only — exploratory recommendation artifacts exist, but regime-selection accuracy remains low; we therefore **do not** claim deployment-ready architecture selection (`recommendation_eval.json` `claim_status`).

## Discussion

The empirical coordination burden is real on this grid; the predictive generalization claim is **conditional** on which axis is held out and which admissible baseline is treated as strongest.

## Limitations

Thin-slice synthetic environment; proxy metrics; **sparse collapse** (appendix Brier/prevalence are exploratory—do not read low Brier as robust collapse prediction); weak exploratory recommender; **no plant timing / MTTR claim**; **no universal scaling law**.

## Frozen snapshot

Headline numbers match `datasets/runs/scaling_eval/heldout_results.json` `run_manifest.commit` **3c4fd57f189670e73e9336845454ed3bc830d4ff** (refresh via `run_paper_experiments.py --paper P5` or `scaling_heldout_eval.py`).

- **Leave-one-scenario-out (`tasks_completed`):** `overall_regression_mae` **0.5105**, `overall_feat_baseline_mae` **0.3899**, `overall_baseline_mae` **0.7367**, `mean_regression_pi_coverage_95` **0.7707**, `overall_collapse_rate` **0.00292**, **`trigger_met` false**. Hardest fold: **`lab_profile_v0`** (Main Table 2).
- **Leave-one-family-out:** `overall_regression_mae` **0.5185**, **`trigger_met` true**.
- **Leave-one-regime-out:** `overall_regression_mae` **0.2370**, **`trigger_met` false**.
- **Leave-one-agent-count-out / leave-one-fault-setting-out:** `overall_regression_mae` **0.2157** / **0.2264**, **`trigger_met` false**.
- **Sensitivity (scenario LOO, seed caps 10 / 20 / 30):** `overall_regression_mae` **0.5528 → 0.5351 → 0.5105**; **`trigger_met` false** at every cap (`scaling_sensitivity.json`, appendix).
- **Recommendation (exploratory only, not deployment-ready):** `regime_selection_accuracy` **0.0285**, `mean_regret_tasks_completed` **0.1049**, `brier_collapse_on_test_rows` **0.0030** (sparse collapse prevalence — appendix).

**Secondary targets (scenario-heldout bundle):** coordination tax is **much more predictable than throughput (`tasks_completed`) or error amplification** by admissible regression MAE and `trigger_met`; coordination-tax proxy **triggers** admissible beats while throughput does **not** (Main Table 4).

**Title grounding:** Main Table 1 and `datasets/runs/scaling_summary/regime_agent_summary.json` give **1→8** agent deltas by family × regime (absolute deltas in the main export; percent form in appendix).

## Reproducibility

`PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/run_paper_experiments.py --paper P5`

Then refresh markdown tables (defaults resolve regime/fault paths):

`PYTHONPATH=impl/src python scripts/export_scaling_tables.py --results datasets/runs/scaling_eval/heldout_results.json --family-results datasets/runs/scaling_eval_family/heldout_results.json --regime-results datasets/runs/scaling_eval_regime/heldout_results.json --agent-results datasets/runs/scaling_eval_agent_count/heldout_results.json --fault-results datasets/runs/scaling_eval_fault/heldout_results.json --recommend-results datasets/runs/scaling_recommend/recommendation_eval.json --sensitivity-results datasets/runs/sensitivity_sweep/scaling_sensitivity.json --regime-agent-summary datasets/runs/scaling_summary/regime_agent_summary.json --out papers/P5_ScalingLaws/generated_tables.md`

Optional LaTeX snippets: `--out-tex-dir papers/P5_ScalingLaws/neurips2026/tables_tex`

Claim gate: `python scripts/check_p5_claim_sources.py`

`PYTHONPATH=impl/src python scripts/export_scaling_regime_agent_summary.py --runs-dir datasets/runs/multiscenario_runs --out-json datasets/runs/scaling_summary/regime_agent_summary.json --out-md papers/P5_ScalingLaws/regime_agent_summary.md`

## Main tables

Copy numerical tables from **`papers/P5_ScalingLaws/generated_tables.md`**: **Main Tables 1–4** (appendix holds sensitivity, recommendation, oracle diagnostic row, full percent matrix, exploratory `scaling_fit`).

## P4 boundary

See `docs/P5_P4_BOUNDARY.md` — P5 does not re-bundle P4’s anti-gaming benchmark claims.
