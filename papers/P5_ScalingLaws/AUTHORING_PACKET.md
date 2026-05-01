# P5 authoring packet (NeurIPS E&D freeze)

**Paper:** `P5_ScalingLaws`  
**Title:** When More Agents Hurt: Held-Out Evaluation of Coordination Scaling in Cyber-Physical Agent Systems  
**Type:** Evaluation-protocol paper — **empirical coordination-scaling patterns** + strict held-out tests; **not** a universal CPS scaling law, **not** deployment-ready recommendation.

## 1) Question

When agent count and coordination regime vary across realistic CPS scenarios, what coordination-load and throughput patterns appear in a controlled MAESTRO grid, and **do those patterns yield robust held-out prediction** under admissible train-only baselines?

## 2) Claims to defend (see `claims.yaml` and `CLAIM_LOCK_NEURIPS2026.md`)

- **C1:** Title-grounding regime × agent deltas (coordination tax and throughput) are reproducible from `regime_agent_summary.json` / Main Table 1.
- **C2:** Held-out evaluation separates **admissible** train-only baselines from **oracle** diagnostics; strict aggregation when any fold has null regression; ridge-stabilized regression for the default P5 feature vector. **`trigger_met` is protocol-specific** — scenario-heldout can fail while family-heldout succeeds.
- **C3:** Recommendation / regret artifacts exist but are **exploratory** (`claim_status` in `recommendation_eval.json`); **do not** claim deployment-ready architecture selection.

## 3) Publishable grid (default `--paper P5`)

Six `real_world` scenarios × five regimes × agent counts `{1,2,4,8}` × fault labels `{no_drop, drop_005}` × 30 seeds → **7200** rows in `datasets/runs/multiscenario_runs/`.

## 4) Frozen evidence (sync to JSON)

**Artifact bundle commit:** **`3a7d4f0b17c86cde219852f59dbd36a68b45efb0`** (full tree: JSON + exported tables + hashes). **`run_manifest.commit`** embedded in `scaling_eval/heldout_results.json`: **`ede2b361620270bbaf5e4e343ce6a6c3c2834217`** (HEAD at eval write time). See `FINAL_REPRO_LOG.md` §4.

| Artifact | `tasks_completed` headline |
|----------|-----------------------------|
| `datasets/runs/scaling_eval/heldout_results.json` (scenario LOO) | `overall_regression_mae` **0.5105**, `overall_feat_baseline_mae` **0.3899**, `overall_baseline_mae` **0.7367**, `trigger_met` **false**. |
| `datasets/runs/scaling_eval_family/heldout_results.json` | `overall_regression_mae` **0.5185**, `trigger_met` **true**. |
| `datasets/runs/scaling_eval_regime/heldout_results.json` | `overall_regression_mae` **0.2370**, `trigger_met` **false**. |
| `datasets/runs/scaling_eval_agent_count/heldout_results.json` | `overall_regression_mae` **0.2157**, `trigger_met` **false**. |
| `datasets/runs/scaling_eval_fault/heldout_results.json` | `overall_regression_mae` **0.2264**, `trigger_met` **false**. |
| `datasets/runs/sensitivity_sweep/scaling_sensitivity.json` | Scenario LOO caps 10 / 20 / 30: MAE **0.5528 → 0.5351 → 0.5105**; all **`trigger_met` false**. |
| `datasets/runs/scaling_recommend/recommendation_eval.json` | `regime_selection_accuracy` **0.0285**, exploratory `claim_status`; appendix only for recommendation prose. |
| `datasets/runs/scaling_summary/regime_agent_summary.json` | **7200** rows; Main Table 1 + appendix percent matrix. |

## 5) Writing guidance

- Lead with **coordination-scaling evidence** (Main Table 1) and **evaluation hygiene**; present scenario-heldout **negative result vs num-tasks bucket** as a core methodological finding.
- Never merge oracle MAE into trigger prose.
- If any fold has `regression_mae: null`, protocol-level regression MAE is null and `trigger_met` is false per strict rule.
- Cite **exact** paths above; refresh numbers only by re-running `run_paper_experiments.py --paper P5` and regenerating tables.
- Mention recommendation only as: exploratory recommendation artifacts exist, but regime-selection accuracy remains low; we therefore **do not** claim deployment-ready architecture selection (`claim_status` in `recommendation_eval.json`).

## 6) Files to keep in lockstep

- `papers/P5_ScalingLaws/DRAFT.md`
- `papers/P5_ScalingLaws/generated_tables.md` (from `export_scaling_tables.py`)
- `papers/P5_ScalingLaws/regime_agent_summary.md` (from `export_scaling_regime_agent_summary.py`)
- `papers/P5_ScalingLaws/claims.yaml`
- `papers/P5_ScalingLaws/CLAIM_LOCK_NEURIPS2026.md`
- `papers/P5_ScalingLaws/CLAIM_SOURCE_MAP.md`
- `papers/P5_ScalingLaws/claim_sources.yaml`
- `papers/P5_ScalingLaws/PHASE3_PASSED.md`
- `papers/P5_ScalingLaws/README.md`
