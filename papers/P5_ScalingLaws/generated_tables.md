# Generated tables for P5 (P5_ScalingLaws)

## From export_scaling_tables.py

# Table 1 — Held-out results

| Held-out scenario | train_n | test_n | baseline_mae | per_scenario_mae | feat_baseline_mae | regression_mae | actuals_mean |
|-------------------|--------|--------|--------------|------------------|-------------------|---------------|-------------|
| lab_profile_v0 | 400 | 80 | 1.40 | 0.07 | 1.40 | 0.07 | 4.96 |
| regime_stress_v0 | 400 | 80 | 0.26 | 0.07 | 0.07 | 0.07 | 3.96 |
| regime_stress_v1 | 400 | 80 | 0.26 | 0.07 | 0.07 | 0.07 | 3.96 |
| toy_lab_v0 | 400 | 80 | 0.26 | 0.07 | 0.07 | 0.07 | 3.96 |
| traffic_v0 | 400 | 80 | 1.00 | 0.07 | 0.07 | 0.07 | 2.96 |
| warehouse_v0 | 400 | 80 | 1.00 | 0.07 | 0.07 | 0.07 | 2.96 |

# Table 2 — Baselines (MAE and 95% CI)

| Baseline | MAE | CI95 lower | CI95 upper |
|----------|-----|------------|------------|
| Global mean | 0.70 | 0.33 | 1.06 |
| Per-scenario mean (scenario identity allowed) | 0.07 | — | — |
| Num-tasks mean | 0.29 | -0.10 | 0.69 |
| Regression (num_tasks, num_faults) | 0.07 | — | — |

