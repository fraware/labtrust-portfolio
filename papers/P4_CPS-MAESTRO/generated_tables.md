# Generated tables for P4 (P4_CPS-MAESTRO)

## From export_maestro_tables.py

# Table A - Fault sweep (MAESTRO_REPORT v0.2 aggregates)

| Scenario | Setting | tasks_mean | tasks_stdev | p95_mean | p99_run | ttr_ms_mean | tts_ms_mean | recovery_rate_mean | safety_viol_mean | steps_after_fault_mean |
|----------|---------|------------|-------------|----------|---------|-------------|-------------|----------------------|------------------|--------------------------|
| toy_lab_v0 | no_drop | 4 | 0.00 | 35.37 | 78.08 | n/a | 188.25 | 1.00 | 0 | n/a |
| toy_lab_v0 | drop_005 | 3.85 | 0.37 | 34.83 | 78.08 | n/a | 190.30 | 0.85 | 0 | 6 |
| toy_lab_v0 | drop_02 | 3.30 | 0.92 | 32.18 | 79.67 | n/a | 197.63 | 0.55 | 0 | 7.33 |
| toy_lab_v0 | delay_01 | 4 | 0.00 | 40.55 | 132.78 | 95.74 | 221.27 | 1.00 | 0 | 9 |
| toy_lab_v0 | drop_005_delay_01 | 3.65 | 0.49 | 34.38 | 132.78 | 80.09 | 224.10 | 0.65 | 0 | 6.78 |
| toy_lab_v0 | calibration_invalid_01 | 4 | 0.00 | 37.94 | 132.78 | 39.67 | 231.35 | 1.00 | 0.40 | 12 |
| toy_lab_v0 | recovery_stress_aux | 3.70 | 0.57 | 120.93 | 212.48 | 110.97 | 427.57 | 1.00 | 0.30 | 20.80 |
| lab_profile_v0 | no_drop | 5 | 0.00 | 50.37 | 100.07 | 52.29 | 279.08 | 1.00 | 0 | 12.33 |
| lab_profile_v0 | drop_005 | 4.75 | 0.44 | 49.38 | 100.07 | 60.88 | 283.05 | 0.85 | 0 | 10.62 |
| lab_profile_v0 | drop_02 | 3.70 | 0.80 | 38.74 | 94.80 | 65.13 | 264.57 | 0.35 | 0 | 10.83 |
| lab_profile_v0 | delay_01 | 5 | 0.00 | 59.48 | 130.32 | 72.39 | 329.07 | 1.00 | 0 | 11.71 |
| lab_profile_v0 | drop_005_delay_01 | 4.65 | 0.59 | 51.57 | 130.32 | 89.54 | 344.89 | 0.90 | 0 | 12.20 |
| lab_profile_v0 | calibration_invalid_01 | 5 | 0.00 | 47.09 | 115.94 | 72.89 | 314.43 | 1.00 | 0.55 | 16 |
| lab_profile_v0 | recovery_stress_aux | 4.40 | 0.68 | 131.30 | 249.28 | 101.91 | 554.46 | 1.00 | 0.35 | 25.05 |

# Table B - Baselines (per-seed + regimes)

| Regime | Adapter | Seed | tasks | p95_ms | safety_viol | unsafe_succ | msgs/task | outcome |
|--------|---------|------|-------|--------|-------------|-------------|-----------|---------|
| fault_free | Centralized | 1 | 4 | 25.26 | 0 | 0 | 1.00 | success_safe |
| fault_free | Centralized | 2 | 4 | 75.59 | 0 | 0 | 1.00 | success_safe |
| fault_free | Centralized | 3 | 4 | 28.09 | 0 | 0 | 1.00 | success_safe |
| fault_free | Centralized | 4 | 4 | 41.26 | 0 | 0 | 1.00 | success_safe |
| fault_free | Centralized | 5 | 4 | 42.64 | 0 | 0 | 1.00 | success_safe |
| fault_free | Centralized | 6 | 4 | 26.54 | 0 | 0 | 1.00 | success_safe |
| fault_free | Centralized | 7 | 4 | 10.68 | 0 | 0 | 1.00 | success_safe |
| fault_free | Centralized | 8 | 4 | 19.02 | 0 | 0 | 1.00 | success_safe |
| fault_free | Centralized | 9 | 4 | 29.77 | 0 | 0 | 1.00 | success_safe |
| fault_free | Centralized | 10 | 4 | 45.64 | 0 | 0 | 1.00 | success_safe |
| fault_free | Centralized | 11 | 4 | 11.74 | 0 | 0 | 1.00 | success_safe |
| fault_free | Centralized | 12 | 4 | 37.7 | 0 | 0 | 1.00 | success_safe |
| fault_free | Centralized | 13 | 4 | 29.2 | 0 | 0 | 1.00 | success_safe |
| fault_free | Centralized | 14 | 4 | 43.76 | 0 | 0 | 1.00 | success_safe |
| fault_free | Centralized | 15 | 4 | 17.26 | 0 | 0 | 1.00 | success_safe |
| fault_free | Centralized | 16 | 4 | 46.9 | 0 | 0 | 1.00 | success_safe |
| fault_free | Centralized | 17 | 4 | 42.05 | 0 | 0 | 1.00 | success_safe |
| fault_free | Centralized | 18 | 4 | 42.43 | 0 | 0 | 1.00 | success_safe |
| fault_free | Centralized | 19 | 4 | 13.74 | 0 | 0 | 1.00 | success_safe |
| fault_free | Centralized | 20 | 4 | 78.08 | 0 | 0 | 1.00 | success_safe |
| fault_free | Blackboard | 1 | 4 | 25.26 | 0 | 0 | 1.00 | success_safe |
| fault_free | Blackboard | 2 | 4 | 75.59 | 0 | 0 | 1.00 | success_safe |
| fault_free | Blackboard | 3 | 4 | 28.09 | 0 | 0 | 1.00 | success_safe |
| fault_free | Blackboard | 4 | 4 | 41.26 | 0 | 0 | 1.00 | success_safe |
| fault_free | Blackboard | 5 | 4 | 42.64 | 0 | 0 | 1.00 | success_safe |
| fault_free | Blackboard | 6 | 4 | 26.54 | 0 | 0 | 1.00 | success_safe |
| fault_free | Blackboard | 7 | 4 | 10.68 | 0 | 0 | 1.00 | success_safe |
| fault_free | Blackboard | 8 | 4 | 19.02 | 0 | 0 | 1.00 | success_safe |
| fault_free | Blackboard | 9 | 4 | 29.77 | 0 | 0 | 1.00 | success_safe |
| fault_free | Blackboard | 10 | 4 | 45.64 | 0 | 0 | 1.00 | success_safe |
| fault_free | Blackboard | 11 | 4 | 11.74 | 0 | 0 | 1.00 | success_safe |
| fault_free | Blackboard | 12 | 4 | 37.7 | 0 | 0 | 1.00 | success_safe |
| fault_free | Blackboard | 13 | 4 | 29.2 | 0 | 0 | 1.00 | success_safe |
| fault_free | Blackboard | 14 | 4 | 43.76 | 0 | 0 | 1.00 | success_safe |
| fault_free | Blackboard | 15 | 4 | 17.26 | 0 | 0 | 1.00 | success_safe |
| fault_free | Blackboard | 16 | 4 | 46.9 | 0 | 0 | 1.00 | success_safe |
| fault_free | Blackboard | 17 | 4 | 42.05 | 0 | 0 | 1.00 | success_safe |
| fault_free | Blackboard | 18 | 4 | 42.43 | 0 | 0 | 1.00 | success_safe |
| fault_free | Blackboard | 19 | 4 | 13.74 | 0 | 0 | 1.00 | success_safe |
| fault_free | Blackboard | 20 | 4 | 78.08 | 0 | 0 | 1.00 | success_safe |
| fault_free | RetryHeavy | 1 | 4 | 25.26 | 0 | 0 | 1.00 | success_safe |
| fault_free | RetryHeavy | 2 | 4 | 75.59 | 0 | 0 | 1.00 | success_safe |
| fault_free | RetryHeavy | 3 | 4 | 28.09 | 0 | 0 | 1.00 | success_safe |
| fault_free | RetryHeavy | 4 | 4 | 41.26 | 0 | 0 | 1.00 | success_safe |
| fault_free | RetryHeavy | 5 | 4 | 42.64 | 0 | 0 | 1.00 | success_safe |
| fault_free | RetryHeavy | 6 | 4 | 26.54 | 0 | 0 | 1.00 | success_safe |
| fault_free | RetryHeavy | 7 | 4 | 10.68 | 0 | 0 | 1.00 | success_safe |
| fault_free | RetryHeavy | 8 | 4 | 19.02 | 0 | 0 | 1.00 | success_safe |
| fault_free | RetryHeavy | 9 | 4 | 29.77 | 0 | 0 | 1.00 | success_safe |
| fault_free | RetryHeavy | 10 | 4 | 45.64 | 0 | 0 | 1.00 | success_safe |
| fault_free | RetryHeavy | 11 | 4 | 11.74 | 0 | 0 | 1.00 | success_safe |
| fault_free | RetryHeavy | 12 | 4 | 37.7 | 0 | 0 | 1.00 | success_safe |
| fault_free | RetryHeavy | 13 | 4 | 29.2 | 0 | 0 | 1.00 | success_safe |
| fault_free | RetryHeavy | 14 | 4 | 43.76 | 0 | 0 | 1.00 | success_safe |
| fault_free | RetryHeavy | 15 | 4 | 17.26 | 0 | 0 | 1.00 | success_safe |
| fault_free | RetryHeavy | 16 | 4 | 46.9 | 0 | 0 | 1.00 | success_safe |
| fault_free | RetryHeavy | 17 | 4 | 42.05 | 0 | 0 | 1.00 | success_safe |
| fault_free | RetryHeavy | 18 | 4 | 42.43 | 0 | 0 | 1.00 | success_safe |
| fault_free | RetryHeavy | 19 | 4 | 13.74 | 0 | 0 | 1.00 | success_safe |
| fault_free | RetryHeavy | 20 | 4 | 78.08 | 0 | 0 | 1.00 | success_safe |
| fault_free | NoRecovery | 1 | 4 | 25.26 | 0 | 0 | 1.00 | success_safe |
| fault_free | NoRecovery | 2 | 4 | 75.59 | 0 | 0 | 1.00 | success_safe |
| fault_free | NoRecovery | 3 | 4 | 28.09 | 0 | 0 | 1.00 | success_safe |
| fault_free | NoRecovery | 4 | 4 | 41.26 | 0 | 0 | 1.00 | success_safe |
| fault_free | NoRecovery | 5 | 4 | 42.64 | 0 | 0 | 1.00 | success_safe |
| fault_free | NoRecovery | 6 | 4 | 26.54 | 0 | 0 | 1.00 | success_safe |
| fault_free | NoRecovery | 7 | 4 | 10.68 | 0 | 0 | 1.00 | success_safe |
| fault_free | NoRecovery | 8 | 4 | 19.02 | 0 | 0 | 1.00 | success_safe |
| fault_free | NoRecovery | 9 | 4 | 29.77 | 0 | 0 | 1.00 | success_safe |
| fault_free | NoRecovery | 10 | 4 | 45.64 | 0 | 0 | 1.00 | success_safe |
| fault_free | NoRecovery | 11 | 4 | 11.74 | 0 | 0 | 1.00 | success_safe |
| fault_free | NoRecovery | 12 | 4 | 37.7 | 0 | 0 | 1.00 | success_safe |
| fault_free | NoRecovery | 13 | 4 | 29.2 | 0 | 0 | 1.00 | success_safe |
| fault_free | NoRecovery | 14 | 4 | 43.76 | 0 | 0 | 1.00 | success_safe |
| fault_free | NoRecovery | 15 | 4 | 17.26 | 0 | 0 | 1.00 | success_safe |
| fault_free | NoRecovery | 16 | 4 | 46.9 | 0 | 0 | 1.00 | success_safe |
| fault_free | NoRecovery | 17 | 4 | 42.05 | 0 | 0 | 1.00 | success_safe |
| fault_free | NoRecovery | 18 | 4 | 42.43 | 0 | 0 | 1.00 | success_safe |
| fault_free | NoRecovery | 19 | 4 | 13.74 | 0 | 0 | 1.00 | success_safe |
| fault_free | NoRecovery | 20 | 4 | 78.08 | 0 | 0 | 1.00 | success_safe |
| fault_free | ConservativeSafeShutdown | 1 | 4 | 25.26 | 0 | 0 | 1.00 | success_safe |
| fault_free | ConservativeSafeShutdown | 2 | 4 | 75.59 | 0 | 0 | 1.00 | success_safe |
| fault_free | ConservativeSafeShutdown | 3 | 4 | 28.09 | 0 | 0 | 1.00 | success_safe |
| fault_free | ConservativeSafeShutdown | 4 | 4 | 41.26 | 0 | 0 | 1.00 | success_safe |
| fault_free | ConservativeSafeShutdown | 5 | 4 | 42.64 | 0 | 0 | 1.00 | success_safe |
| fault_free | ConservativeSafeShutdown | 6 | 4 | 26.54 | 0 | 0 | 1.00 | success_safe |
| fault_free | ConservativeSafeShutdown | 7 | 4 | 10.68 | 0 | 0 | 1.00 | success_safe |
| fault_free | ConservativeSafeShutdown | 8 | 4 | 19.02 | 0 | 0 | 1.00 | success_safe |
| fault_free | ConservativeSafeShutdown | 9 | 4 | 29.77 | 0 | 0 | 1.00 | success_safe |
| fault_free | ConservativeSafeShutdown | 10 | 4 | 45.64 | 0 | 0 | 1.00 | success_safe |
| fault_free | ConservativeSafeShutdown | 11 | 4 | 11.74 | 0 | 0 | 1.00 | success_safe |
| fault_free | ConservativeSafeShutdown | 12 | 4 | 37.7 | 0 | 0 | 1.00 | success_safe |
| fault_free | ConservativeSafeShutdown | 13 | 4 | 29.2 | 0 | 0 | 1.00 | success_safe |
| fault_free | ConservativeSafeShutdown | 14 | 4 | 43.76 | 0 | 0 | 1.00 | success_safe |
| fault_free | ConservativeSafeShutdown | 15 | 4 | 17.26 | 0 | 0 | 1.00 | success_safe |
| fault_free | ConservativeSafeShutdown | 16 | 4 | 46.9 | 0 | 0 | 1.00 | success_safe |
| fault_free | ConservativeSafeShutdown | 17 | 4 | 42.05 | 0 | 0 | 1.00 | success_safe |
| fault_free | ConservativeSafeShutdown | 18 | 4 | 42.43 | 0 | 0 | 1.00 | success_safe |
| fault_free | ConservativeSafeShutdown | 19 | 4 | 13.74 | 0 | 0 | 1.00 | success_safe |
| fault_free | ConservativeSafeShutdown | 20 | 4 | 78.08 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | Centralized | 1 | 4 | 25.26 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | Centralized | 2 | 3 | 79.67 | 0 | 0 | 1.33 | partial_safe |
| drop_0_2 | Centralized | 3 | 3 | 14.97 | 0 | 0 | 1.33 | partial_safe |
| drop_0_2 | Centralized | 4 | 4 | 41.26 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | Centralized | 5 | 3 | 44.31 | 0 | 0 | 1.33 | partial_safe |
| drop_0_2 | Centralized | 6 | 4 | 26.54 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | Centralized | 7 | 1 | 1.26 | 0 | 0 | 4.00 | partial_safe |
| drop_0_2 | Centralized | 8 | 2 | 11.03 | 0 | 0 | 2.00 | partial_safe |
| drop_0_2 | Centralized | 9 | 2 | 2.78 | 0 | 0 | 2.00 | partial_safe |
| drop_0_2 | Centralized | 10 | 4 | 45.64 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | Centralized | 11 | 2 | 9.97 | 0 | 0 | 2.00 | partial_safe |
| drop_0_2 | Centralized | 12 | 3 | 26.78 | 0 | 0 | 1.33 | partial_safe |
| drop_0_2 | Centralized | 13 | 3 | 30.0 | 0 | 0 | 1.33 | partial_safe |
| drop_0_2 | Centralized | 14 | 4 | 43.76 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | Centralized | 15 | 4 | 17.26 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | Centralized | 16 | 4 | 46.9 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | Centralized | 17 | 4 | 42.05 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | Centralized | 18 | 4 | 42.43 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | Centralized | 19 | 4 | 13.74 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | Centralized | 20 | 4 | 78.08 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | Blackboard | 1 | 4 | 25.26 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | Blackboard | 2 | 3 | 79.67 | 0 | 0 | 1.33 | partial_safe |
| drop_0_2 | Blackboard | 3 | 3 | 14.97 | 0 | 0 | 1.33 | partial_safe |
| drop_0_2 | Blackboard | 4 | 4 | 41.26 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | Blackboard | 5 | 3 | 44.31 | 0 | 0 | 1.33 | partial_safe |
| drop_0_2 | Blackboard | 6 | 4 | 26.54 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | Blackboard | 7 | 1 | 1.26 | 0 | 0 | 4.00 | partial_safe |
| drop_0_2 | Blackboard | 8 | 2 | 11.03 | 0 | 0 | 2.00 | partial_safe |
| drop_0_2 | Blackboard | 9 | 2 | 2.78 | 0 | 0 | 2.00 | partial_safe |
| drop_0_2 | Blackboard | 10 | 4 | 45.64 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | Blackboard | 11 | 2 | 9.97 | 0 | 0 | 2.00 | partial_safe |
| drop_0_2 | Blackboard | 12 | 3 | 26.78 | 0 | 0 | 1.33 | partial_safe |
| drop_0_2 | Blackboard | 13 | 3 | 30.0 | 0 | 0 | 1.33 | partial_safe |
| drop_0_2 | Blackboard | 14 | 4 | 43.76 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | Blackboard | 15 | 4 | 17.26 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | Blackboard | 16 | 4 | 46.9 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | Blackboard | 17 | 4 | 42.05 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | Blackboard | 18 | 4 | 42.43 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | Blackboard | 19 | 4 | 13.74 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | Blackboard | 20 | 4 | 78.08 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | RetryHeavy | 1 | 4 | 25.26 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | RetryHeavy | 2 | 4 | 47.9 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | RetryHeavy | 3 | 4 | 18.11 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | RetryHeavy | 4 | 4 | 41.26 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | RetryHeavy | 5 | 4 | 44.14 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | RetryHeavy | 6 | 4 | 26.54 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | RetryHeavy | 7 | 3 | 8.16 | 0 | 0 | 1.33 | partial_safe |
| drop_0_2 | RetryHeavy | 8 | 4 | 7.35 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | RetryHeavy | 9 | 4 | 19.48 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | RetryHeavy | 10 | 4 | 45.64 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | RetryHeavy | 11 | 4 | 10.34 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | RetryHeavy | 12 | 4 | 26.3 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | RetryHeavy | 13 | 4 | 31.01 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | RetryHeavy | 14 | 4 | 43.76 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | RetryHeavy | 15 | 4 | 17.26 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | RetryHeavy | 16 | 4 | 46.9 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | RetryHeavy | 17 | 4 | 42.05 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | RetryHeavy | 18 | 4 | 42.43 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | RetryHeavy | 19 | 4 | 13.74 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | RetryHeavy | 20 | 4 | 78.08 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | NoRecovery | 1 | 4 | 25.26 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | NoRecovery | 2 | 3 | 79.67 | 0 | 0 | 1.33 | partial_safe |
| drop_0_2 | NoRecovery | 3 | 3 | 14.97 | 0 | 0 | 1.33 | partial_safe |
| drop_0_2 | NoRecovery | 4 | 4 | 41.26 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | NoRecovery | 5 | 3 | 44.31 | 0 | 0 | 1.33 | partial_safe |
| drop_0_2 | NoRecovery | 6 | 4 | 26.54 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | NoRecovery | 7 | 1 | 1.26 | 0 | 0 | 4.00 | partial_safe |
| drop_0_2 | NoRecovery | 8 | 2 | 11.03 | 0 | 0 | 2.00 | partial_safe |
| drop_0_2 | NoRecovery | 9 | 2 | 2.78 | 0 | 0 | 2.00 | partial_safe |
| drop_0_2 | NoRecovery | 10 | 4 | 45.64 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | NoRecovery | 11 | 2 | 9.97 | 0 | 0 | 2.00 | partial_safe |
| drop_0_2 | NoRecovery | 12 | 3 | 26.78 | 0 | 0 | 1.33 | partial_safe |
| drop_0_2 | NoRecovery | 13 | 3 | 30.0 | 0 | 0 | 1.33 | partial_safe |
| drop_0_2 | NoRecovery | 14 | 4 | 43.76 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | NoRecovery | 15 | 4 | 17.26 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | NoRecovery | 16 | 4 | 46.9 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | NoRecovery | 17 | 4 | 42.05 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | NoRecovery | 18 | 4 | 42.43 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | NoRecovery | 19 | 4 | 13.74 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | NoRecovery | 20 | 4 | 78.08 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | ConservativeSafeShutdown | 1 | 4 | 25.26 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | ConservativeSafeShutdown | 2 | 0 | 0.0 | 0 | 0 | 1.00 | failed_safe_shutdown |
| drop_0_2 | ConservativeSafeShutdown | 3 | 1 | 15.46 | 0 | 0 | 2.00 | failed_safe_shutdown |
| drop_0_2 | ConservativeSafeShutdown | 4 | 4 | 41.26 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | ConservativeSafeShutdown | 5 | 1 | 47.65 | 0 | 0 | 2.00 | failed_safe_shutdown |
| drop_0_2 | ConservativeSafeShutdown | 6 | 4 | 26.54 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | ConservativeSafeShutdown | 7 | 1 | 1.26 | 0 | 0 | 2.00 | failed_safe_shutdown |
| drop_0_2 | ConservativeSafeShutdown | 8 | 0 | 0.0 | 0 | 0 | 1.00 | failed_safe_shutdown |
| drop_0_2 | ConservativeSafeShutdown | 9 | 0 | 0.0 | 0 | 0 | 1.00 | failed_safe_shutdown |
| drop_0_2 | ConservativeSafeShutdown | 10 | 4 | 45.64 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | ConservativeSafeShutdown | 11 | 1 | 10.46 | 0 | 0 | 2.00 | failed_safe_shutdown |
| drop_0_2 | ConservativeSafeShutdown | 12 | 3 | 26.78 | 0 | 0 | 1.33 | failed_safe_shutdown |
| drop_0_2 | ConservativeSafeShutdown | 13 | 1 | 31.59 | 0 | 0 | 2.00 | failed_safe_shutdown |
| drop_0_2 | ConservativeSafeShutdown | 14 | 4 | 43.76 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | ConservativeSafeShutdown | 15 | 4 | 17.26 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | ConservativeSafeShutdown | 16 | 4 | 46.9 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | ConservativeSafeShutdown | 17 | 4 | 42.05 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | ConservativeSafeShutdown | 18 | 4 | 42.43 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | ConservativeSafeShutdown | 19 | 4 | 13.74 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | ConservativeSafeShutdown | 20 | 4 | 78.08 | 0 | 0 | 1.00 | success_safe |

## Baseline aggregates (by regime)

### drop_0_2

| Adapter | tasks_mean | tasks_stdev | p95_mean | p99_mean | safety_mean | recovery_mean | ttr_mean | tts_mean | msgs/task_mean |
|---------|---------|---------|-------|-------|-----------|-----------|-------|-------|-------------|
| Centralized | 3.30 | 0.92 | 32.18 | 34.35 | 0 | 0.55 | n/a | 197.63 | 1.38 |
| Blackboard | 3.30 | 0.92 | 32.18 | 34.35 | 0 | 0.55 | n/a | 197.63 | 1.38 |
| RetryHeavy | 3.95 | 0.22 | 31.79 | 33.72 | 0 | 0.95 | 62.80 | 236.40 | 1.02 |
| NoRecovery | 3.30 | 0.92 | 32.18 | 34.35 | 0 | 0.55 | n/a | 197.63 | 1.38 |
| ConservativeSafeShutdown | 2.60 | 1.70 | 27.81 | 29.40 | 0 | 0.55 | n/a | 197.63 | 1.27 |

### fault_free

| Adapter | tasks_mean | tasks_stdev | p95_mean | p99_mean | safety_mean | recovery_mean | ttr_mean | tts_mean | msgs/task_mean |
|---------|---------|---------|-------|-------|-----------|-----------|-------|-------|-------------|
| Centralized | 4.00 | 0.00 | 35.37 | 38.13 | 0 | 1.00 | n/a | 188.25 | 1.00 |
| Blackboard | 4.00 | 0.00 | 35.37 | 38.13 | 0 | 1.00 | n/a | 188.25 | 1.00 |
| RetryHeavy | 4.00 | 0.00 | 35.37 | 38.13 | 0 | 1.00 | n/a | 188.25 | 1.00 |
| NoRecovery | 4.00 | 0.00 | 35.37 | 38.13 | 0 | 1.00 | n/a | 188.25 | 1.00 |
| ConservativeSafeShutdown | 4.00 | 0.00 | 35.37 | 38.13 | 0 | 1.00 | n/a | 188.25 | 1.00 |

# Table C - Scenario and fault coverage

| scenario | family | tasks_n | resource_graph | fault_classes_in_spec | safe_state_semantics |
|----------|--------|---------|----------------|------------------------|----------------------|
| lab_profile_v0 | lab | 5 | yes | drop_completion, delay, calibration_invalid | yes (trace safe_state_reached when all tasks complete cleanly) |
| regime_stress_v0 | lab | 4 | no | drop_completion, delay | yes (trace safe_state_reached when all tasks complete cleanly) |
| regime_stress_v1 | lab | 4 | no | drop_completion, delay | yes (trace safe_state_reached when all tasks complete cleanly) |
| rep_cps_scheduling_v0 | lab | 4 | no | drop_completion | yes (trace safe_state_reached when all tasks complete cleanly) |
| toy_lab_v0 | lab | 4 | no | drop_completion | yes (trace safe_state_reached when all tasks complete cleanly) |
| traffic_v0 | traffic | 3 | no | drop_completion, delay | yes (trace safe_state_reached when all tasks complete cleanly) |
| warehouse_v0 | warehouse | 3 | no | drop_completion, delay | yes (trace safe_state_reached when all tasks complete cleanly) |

# Table D - Anti-gaming / scoring robustness

| strategy | tasks_completed | safety_violations | unsafe_success | composite_score | rank |
|----------|-----------------|-------------------|----------------|-----------------|------|
| legitimate_safe | 4 | 0 | 0 | 4.00 | 1 |
| always_deny | 0 | 0 | 0 | 0.00 | 2 |
| always_wait | 0 | 0 | 0 | 0.00 | 3 |
| unsafe_high_completion | 4 | 6 | 1 | -346.00 | 4 |

