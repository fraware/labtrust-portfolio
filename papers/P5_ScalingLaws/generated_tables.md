# Generated tables for P5 (P5_ScalingLaws)

**How to read:** P5 contributes scenario-based coordination tax prediction with held-out validation and comparison to prior model; sensitivity at N=10, 20, 30 in scaling_sensitivity.json. Table 1 shows per held-out scenario train_n, test_n, baseline MAE, per-scenario MAE, feature baseline MAE, regression MAE (when fit), and actuals_mean. Table 2 gives overall MAE and 95% CI for each baseline (regression row from overall_regression_mae or N/A when regression_skipped_reason set). Units: MAE in tasks_completed; CI in same units.

## From export_scaling_tables.py

**Table 1 — Held-out results.** Per held-out scenario: train_n, test_n, baseline_mae, per_scenario_mae, feat_baseline_mae, regression_mae, actuals_mean. Source: heldout_results.json; run_manifest in same file.

# Table 1 — Held-out results

| Held-out scenario | train_n | test_n | baseline_mae | per_scenario_mae | feat_baseline_mae | regression_mae | actuals_mean |
|-------------------|--------|--------|--------------|------------------|-------------------|---------------|-------------|
| lab_profile_v0 | 80 | 20 | 1.50 | 0.26 | 1.50 | — | 4.85 |
| regime_stress_v0 | 80 | 20 | 0.43 | 0.25 | 0.25 | — | 3.85 |
| toy_lab_v0 | 80 | 20 | 0.43 | 0.25 | 0.25 | — | 3.85 |
| traffic_v0 | 80 | 20 | 1.00 | 0.25 | 0.25 | — | 2.85 |
| warehouse_v0 | 80 | 20 | 1.00 | 0.25 | 0.25 | — | 2.85 |

**Table 2 — Baselines (MAE and 95% CI).** Overall MAE and 95% CI (lower, upper) for global mean, per-scenario mean, num-tasks mean, and regression. Source: heldout_results.json (overall_*_mae, overall_*_mae_ci95_*).

# Table 2 — Baselines (MAE and 95% CI)

| Baseline | MAE | CI95 lower | CI95 upper |
|----------|-----|------------|------------|
| Global mean | 0.87 | 0.52 | 1.23 |
| Per-scenario mean (scenario identity allowed) | 0.26 | — | — |
| Num-tasks mean | 0.50 | 0.07 | 0.94 |

