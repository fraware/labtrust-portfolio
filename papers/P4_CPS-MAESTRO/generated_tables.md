# Generated tables for P4 (P4_CPS-MAESTRO)

## From export_maestro_tables.py

# Table 1 — Fault sweep

| Scenario | Setting | tasks_completed_mean | tasks_completed_stdev | p95_latency_ms_mean | p95_latency_ms_stdev |
|----------|---------|---------------------|----------------------|------------------------|-------------------------|
| toy_lab_v0 | no_drop | 4 | 0.00 | 34.45 | 18.08 |
| toy_lab_v0 | drop_005 | 3.70 | 0.48 | 33.38 | 19.13 |
| toy_lab_v0 | delay_01 | 4 | 0.00 | 30.22 | 21.09 |
| toy_lab_v0 | drop_005_delay_01 | 3.50 | 0.53 | 27.07 | 20.51 |
| toy_lab_v0 | calibration_invalid_01 | 4 | 0.00 | 37.46 | 21.32 |
| lab_profile_v0 | no_drop | 5 | 0.00 | 36.97 | 16.16 |
| lab_profile_v0 | drop_005 | 4.70 | 0.48 | 36.32 | 16.76 |
| lab_profile_v0 | delay_01 | 5 | 0.00 | 34.91 | 20.63 |
| lab_profile_v0 | drop_005_delay_01 | 4.50 | 0.53 | 32.71 | 20.95 |
| lab_profile_v0 | calibration_invalid_01 | 5 | 0.00 | 40.19 | 18.49 |

# Table 2 — Baseline (Centralized vs Blackboard)

| Adapter | Seed | tasks_completed | coordination_messages | p95_latency_ms |
|---------|------|----------------|------------------------|----------------|
| Centralized | 1 | 4 | 4 | 25.26 |
| Centralized | 2 | 4 | 4 | 75.59 |
| Centralized | 3 | 4 | 4 | 28.09 |
| Centralized | 4 | 4 | 4 | 41.26 |
| Centralized | 5 | 4 | 4 | 42.64 |
| Centralized | 6 | 4 | 4 | 26.54 |
| Centralized | 7 | 4 | 4 | 10.68 |
| Centralized | 8 | 4 | 4 | 19.02 |
| Centralized | 9 | 4 | 4 | 29.77 |
| Centralized | 10 | 4 | 4 | 45.64 |
| Blackboard | 1 | 4 | 4 | 25.26 |
| Blackboard | 2 | 4 | 4 | 75.59 |
| Blackboard | 3 | 4 | 4 | 28.09 |
| Blackboard | 4 | 4 | 4 | 41.26 |
| Blackboard | 5 | 4 | 4 | 42.64 |
| Blackboard | 6 | 4 | 4 | 26.54 |
| Blackboard | 7 | 4 | 4 | 10.68 |
| Blackboard | 8 | 4 | 4 | 19.02 |
| Blackboard | 9 | 4 | 4 | 29.77 |
| Blackboard | 10 | 4 | 4 | 45.64 |

