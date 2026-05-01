# P5 baseline discipline (admissible vs oracle)

P5 held-out evaluation compares predictors under **strict leakage rules**. Trigger semantics use **admissible** baselines only; **oracle** values are reported as diagnostics.

## Admissible baselines

Baselines that may determine `success_criteria_met.trigger_met` (together with the ridge-stabilized regression on the fixed P5 feature vector):

- **Global train mean** applied out-of-sample (`overall_baseline_mae`).
- **Train-only** structure that does not peek at held-out labels: per-scenario train means where defined without test leakage, regime train mean, agent-count train mean.
- **Num-tasks bucket** baseline (`overall_feat_baseline_mae` / `feat_baseline_mae` per fold) — the strongest coarse admissible structure on this grid for many protocols.
- **Regression** and **stump** (reported; not oracle).

## Oracle baselines

Reported **only** as diagnostic upper bounds or analysis contrast:

- **Per-scenario mean using held-out labels** (same-scenario test averages that require knowing the scenario’s test distribution).
- Any baseline **fitted using all rows** before an honest train/test split.
- **`oracle_baselines.per_scenario_mean_including_test_mae`** in `heldout_results.json`.

Oracle numbers answer “how much signal exists with hindsight?” — they **must not** be described as the fairness bar for generalization.

## Paper-ready sentence

We treat oracle per-scenario means as diagnostic upper bounds, not baselines. Trigger semantics use only train-only admissible baselines. This prevents the study from confusing improvement over a weak global mean with genuine held-out generalization.
