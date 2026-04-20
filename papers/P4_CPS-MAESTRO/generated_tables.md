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
| warehouse_v0 | no_drop | 3 | 0.00 | 25.77 | 80.37 | n/a | 141.55 | 1.00 | 0 | n/a |
| warehouse_v0 | drop_005 | 2.85 | 0.37 | 25.21 | 80.37 | n/a | 139.30 | 0.85 | 0 | 3 |
| warehouse_v0 | drop_02 | 2.45 | 0.76 | 22.79 | 80.37 | n/a | 151.69 | 0.60 | 0 | 5.12 |
| warehouse_v0 | delay_01 | 3 | 0.00 | 36.60 | 136.38 | 102.56 | 172.09 | 1.00 | 0 | 7 |
| warehouse_v0 | drop_005_delay_01 | 2.65 | 0.49 | 29.26 | 136.38 | 84.89 | 173.72 | 0.65 | 0 | 3.88 |
| warehouse_v0 | calibration_invalid_01 | 3 | 0.00 | 39.23 | 136.38 | 38.56 | 179.72 | 1.00 | 0.35 | 9 |
| warehouse_v0 | recovery_stress_aux | 2.80 | 0.52 | 114.87 | 218.07 | 107.29 | 319.89 | 1.00 | 0.25 | 15.63 |
| traffic_v0 | no_drop | 3 | 0.00 | 25.77 | 80.37 | n/a | 141.55 | 1.00 | 0 | n/a |
| traffic_v0 | drop_005 | 2.85 | 0.37 | 25.21 | 80.37 | n/a | 139.30 | 0.85 | 0 | 3 |
| traffic_v0 | drop_02 | 2.45 | 0.76 | 22.79 | 80.37 | n/a | 151.69 | 0.60 | 0 | 5.12 |
| traffic_v0 | delay_01 | 3 | 0.00 | 36.60 | 136.38 | 102.56 | 172.09 | 1.00 | 0 | 7 |
| traffic_v0 | drop_005_delay_01 | 2.65 | 0.49 | 29.26 | 136.38 | 84.89 | 173.72 | 0.65 | 0 | 3.88 |
| traffic_v0 | calibration_invalid_01 | 3 | 0.00 | 39.23 | 136.38 | 38.56 | 179.72 | 1.00 | 0.35 | 9 |
| traffic_v0 | recovery_stress_aux | 2.80 | 0.52 | 114.87 | 218.07 | 107.29 | 319.89 | 1.00 | 0.25 | 15.63 |
| regime_stress_v0 | no_drop | 4 | 0.00 | 35.37 | 78.08 | n/a | 188.25 | 1.00 | 0 | n/a |
| regime_stress_v0 | drop_005 | 3.85 | 0.37 | 34.83 | 78.08 | n/a | 190.30 | 0.85 | 0 | 6 |
| regime_stress_v0 | drop_02 | 3.30 | 0.92 | 32.18 | 79.67 | n/a | 197.63 | 0.55 | 0 | 7.33 |
| regime_stress_v0 | delay_01 | 4 | 0.00 | 40.55 | 132.78 | 95.74 | 221.27 | 1.00 | 0 | 9 |
| regime_stress_v0 | drop_005_delay_01 | 3.65 | 0.49 | 34.38 | 132.78 | 80.09 | 224.10 | 0.65 | 0 | 6.78 |
| regime_stress_v0 | calibration_invalid_01 | 4 | 0.00 | 37.94 | 132.78 | 39.67 | 231.35 | 1.00 | 0.40 | 12 |
| regime_stress_v0 | recovery_stress_aux | 3.70 | 0.57 | 120.93 | 212.48 | 110.97 | 427.57 | 1.00 | 0.30 | 20.80 |

# Table B - Baselines (per-seed + regimes)

| Regime | Adapter | Seed | tasks | p95_ms | safety_viol | unsafe_succ | msgs/task | outcome |
|--------|---------|------|-------|--------|-------------|-------------|-----------|---------|
| fault_free | Centralized | 1 | 4 | 25.26 | 0 | 0 | 1.00 | success_safe |
| fault_free | Centralized | 2 | 4 | 75.59 | 0 | 0 | 1.00 | success_safe |
| fault_free | Blackboard | 1 | 4 | 25.26 | 0 | 0 | 1.00 | success_safe |
| fault_free | Blackboard | 2 | 4 | 75.59 | 0 | 0 | 1.00 | success_safe |
| fault_free | RetryHeavy | 1 | 4 | 25.26 | 0 | 0 | 1.00 | success_safe |
| fault_free | RetryHeavy | 2 | 4 | 75.59 | 0 | 0 | 1.00 | success_safe |
| fault_free | NoRecovery | 1 | 4 | 25.26 | 0 | 0 | 1.00 | success_safe |
| fault_free | NoRecovery | 2 | 4 | 75.59 | 0 | 0 | 1.00 | success_safe |
| fault_free | ConservativeSafeShutdown | 1 | 4 | 25.26 | 0 | 0 | 1.00 | success_safe |
| fault_free | ConservativeSafeShutdown | 2 | 4 | 75.59 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | Centralized | 1 | 4 | 25.26 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | Centralized | 2 | 3 | 79.67 | 0 | 0 | 1.33 | partial_safe |
| drop_0_2 | Blackboard | 1 | 4 | 25.26 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | Blackboard | 2 | 3 | 79.67 | 0 | 0 | 1.33 | partial_safe |
| drop_0_2 | RetryHeavy | 1 | 4 | 25.26 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | RetryHeavy | 2 | 4 | 47.9 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | NoRecovery | 1 | 4 | 25.26 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | NoRecovery | 2 | 3 | 79.67 | 0 | 0 | 1.33 | partial_safe |
| drop_0_2 | ConservativeSafeShutdown | 1 | 4 | 25.26 | 0 | 0 | 1.00 | success_safe |
| drop_0_2 | ConservativeSafeShutdown | 2 | 0 | 0.0 | 0 | 0 | 1.00 | failed_safe_shutdown |

## Baseline aggregates (by regime)

### drop_0_2

| Adapter | tasks_mean | tasks_stdev | p95_mean | p99_mean | safety_mean | recovery_mean | ttr_mean | tts_mean | msgs/task_mean |
|---------|---------|---------|-------|-------|-----------|-----------|-------|-------|-------------|
| Centralized | 3.50 | 0.71 | 52.47 | 56.01 | 0 | 0.50 | n/a | 144.90 | 1.17 |
| Blackboard | 3.50 | 0.71 | 52.47 | 56.01 | 0 | 0.50 | n/a | 144.90 | 1.17 |
| RetryHeavy | 4.00 | 0.00 | 36.58 | 37.62 | 0 | 1.00 | 74.04 | 291.21 | 1.00 |
| NoRecovery | 3.50 | 0.71 | 52.47 | 56.01 | 0 | 0.50 | n/a | 144.90 | 1.17 |
| ConservativeSafeShutdown | 2.00 | 2.83 | 12.63 | 12.90 | 0 | 0.50 | n/a | 144.90 | 1.00 |

### fault_free

| Adapter | tasks_mean | tasks_stdev | p95_mean | p99_mean | safety_mean | recovery_mean | ttr_mean | tts_mean | msgs/task_mean |
|---------|---------|---------|-------|-------|-----------|-----------|-------|-------|-------------|
| Centralized | 4.00 | 0.00 | 50.42 | 55.60 | 0 | 1.00 | n/a | 221.78 | 1.00 |
| Blackboard | 4.00 | 0.00 | 50.42 | 55.60 | 0 | 1.00 | n/a | 221.78 | 1.00 |
| RetryHeavy | 4.00 | 0.00 | 50.42 | 55.60 | 0 | 1.00 | n/a | 221.78 | 1.00 |
| NoRecovery | 4.00 | 0.00 | 50.42 | 55.60 | 0 | 1.00 | n/a | 221.78 | 1.00 |
| ConservativeSafeShutdown | 4.00 | 0.00 | 50.42 | 55.60 | 0 | 1.00 | n/a | 221.78 | 1.00 |

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

