# Generated tables for P4 (P4_CPS-MAESTRO)

## From export_maestro_tables.py

# Table 1 — Fault sweep. tasks_completed mean/stdev, p95_latency_ms (ms), and steps_to_completion_after_first_fault (recovery) by scenario and setting; N seeds per cell (run_manifest in multi_sweep.json).

| Scenario | Setting | tasks_completed_mean | tasks_completed_stdev | p95_latency_ms_mean | p95_latency_ms_stdev | steps_after_fault_mean |
|----------|---------|---------------------|----------------------|------------------------|-------------------------|------------------------|
| toy_lab_v0 | no_drop | 4 | 0.00 | 42.98 | 28.27 | — |
| toy_lab_v0 | drop_005 | 3.67 | 0.58 | 38.60 | 32.44 | 7 |
| toy_lab_v0 | drop_02 | 3.33 | 0.58 | 39.97 | 34.77 | 8.50 |
| toy_lab_v0 | delay_01 | 4 | 0.00 | 36.19 | 34.58 | 11 |
| toy_lab_v0 | drop_005_delay_01 | 3.33 | 0.58 | 36.41 | 35.76 | 7.50 |
| toy_lab_v0 | calibration_invalid_01 | 4 | 0.00 | 44.49 | 33.14 | 10 |
| lab_profile_v0 | no_drop | 5 | 0.00 | 41.77 | 25.82 | — |
| lab_profile_v0 | drop_005 | 4.67 | 0.58 | 39.34 | 27.91 | 10 |
| lab_profile_v0 | drop_02 | 4.33 | 0.58 | 40.70 | 30.26 | 11.50 |
| lab_profile_v0 | delay_01 | 5 | 0.00 | 35.56 | 33.80 | 14 |
| lab_profile_v0 | drop_005_delay_01 | 4.33 | 0.58 | 35.81 | 34.96 | 10.50 |
| lab_profile_v0 | calibration_invalid_01 | 5 | 0.00 | 43.66 | 32.33 | 13 |

# Table 2 — Baseline (Centralized vs Blackboard)

| Adapter | Seed | tasks_completed | coordination_messages | p95_latency_ms |
|---------|------|----------------|------------------------|----------------|
| Centralized | 1 | 4 | 4 | 25.26 |
| Centralized | 2 | 4 | 4 | 75.59 |
| Centralized | 3 | 4 | 4 | 28.09 |
| Blackboard | 1 | 4 | 4 | 25.26 |
| Blackboard | 2 | 4 | 4 | 75.59 |
| Blackboard | 3 | 4 | 4 | 28.09 |
| RetryHeavy | 1 | 4 | 4 | 25.26 |
| RetryHeavy | 2 | 4 | 4 | 75.59 |
| RetryHeavy | 3 | 4 | 4 | 28.09 |

