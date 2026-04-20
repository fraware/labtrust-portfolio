# MAESTRO baseline comparison (P4)

Scenario: `toy_lab_v0`. Seeds 1..20. MAESTRO_REPORT v0.2.

## Per-seed rows

| Regime | Adapter | Seed | tasks_completed | p95_latency_ms | safety_violations | recovery_ok_seed | msgs/task | run_outcome |
|--------|---------|------|-----------------|----------------|-------------------|------------------|-----------|-------------|
| fault_free | Centralized | 1 | 4 | 25.26 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Centralized | 2 | 4 | 75.59 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Centralized | 3 | 4 | 28.09 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Centralized | 4 | 4 | 41.26 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Centralized | 5 | 4 | 42.64 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Centralized | 6 | 4 | 26.54 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Centralized | 7 | 4 | 10.68 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Centralized | 8 | 4 | 19.02 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Centralized | 9 | 4 | 29.77 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Centralized | 10 | 4 | 45.64 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Centralized | 11 | 4 | 11.74 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Centralized | 12 | 4 | 37.7 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Centralized | 13 | 4 | 29.2 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Centralized | 14 | 4 | 43.76 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Centralized | 15 | 4 | 17.26 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Centralized | 16 | 4 | 46.9 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Centralized | 17 | 4 | 42.05 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Centralized | 18 | 4 | 42.43 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Centralized | 19 | 4 | 13.74 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Centralized | 20 | 4 | 78.08 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Blackboard | 1 | 4 | 25.26 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Blackboard | 2 | 4 | 75.59 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Blackboard | 3 | 4 | 28.09 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Blackboard | 4 | 4 | 41.26 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Blackboard | 5 | 4 | 42.64 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Blackboard | 6 | 4 | 26.54 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Blackboard | 7 | 4 | 10.68 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Blackboard | 8 | 4 | 19.02 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Blackboard | 9 | 4 | 29.77 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Blackboard | 10 | 4 | 45.64 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Blackboard | 11 | 4 | 11.74 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Blackboard | 12 | 4 | 37.7 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Blackboard | 13 | 4 | 29.2 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Blackboard | 14 | 4 | 43.76 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Blackboard | 15 | 4 | 17.26 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Blackboard | 16 | 4 | 46.9 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Blackboard | 17 | 4 | 42.05 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Blackboard | 18 | 4 | 42.43 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Blackboard | 19 | 4 | 13.74 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | Blackboard | 20 | 4 | 78.08 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | RetryHeavy | 1 | 4 | 25.26 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | RetryHeavy | 2 | 4 | 75.59 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | RetryHeavy | 3 | 4 | 28.09 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | RetryHeavy | 4 | 4 | 41.26 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | RetryHeavy | 5 | 4 | 42.64 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | RetryHeavy | 6 | 4 | 26.54 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | RetryHeavy | 7 | 4 | 10.68 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | RetryHeavy | 8 | 4 | 19.02 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | RetryHeavy | 9 | 4 | 29.77 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | RetryHeavy | 10 | 4 | 45.64 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | RetryHeavy | 11 | 4 | 11.74 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | RetryHeavy | 12 | 4 | 37.7 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | RetryHeavy | 13 | 4 | 29.2 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | RetryHeavy | 14 | 4 | 43.76 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | RetryHeavy | 15 | 4 | 17.26 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | RetryHeavy | 16 | 4 | 46.9 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | RetryHeavy | 17 | 4 | 42.05 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | RetryHeavy | 18 | 4 | 42.43 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | RetryHeavy | 19 | 4 | 13.74 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | RetryHeavy | 20 | 4 | 78.08 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | NoRecovery | 1 | 4 | 25.26 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | NoRecovery | 2 | 4 | 75.59 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | NoRecovery | 3 | 4 | 28.09 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | NoRecovery | 4 | 4 | 41.26 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | NoRecovery | 5 | 4 | 42.64 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | NoRecovery | 6 | 4 | 26.54 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | NoRecovery | 7 | 4 | 10.68 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | NoRecovery | 8 | 4 | 19.02 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | NoRecovery | 9 | 4 | 29.77 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | NoRecovery | 10 | 4 | 45.64 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | NoRecovery | 11 | 4 | 11.74 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | NoRecovery | 12 | 4 | 37.7 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | NoRecovery | 13 | 4 | 29.2 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | NoRecovery | 14 | 4 | 43.76 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | NoRecovery | 15 | 4 | 17.26 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | NoRecovery | 16 | 4 | 46.9 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | NoRecovery | 17 | 4 | 42.05 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | NoRecovery | 18 | 4 | 42.43 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | NoRecovery | 19 | 4 | 13.74 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | NoRecovery | 20 | 4 | 78.08 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | ConservativeSafeShutdown | 1 | 4 | 25.26 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | ConservativeSafeShutdown | 2 | 4 | 75.59 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | ConservativeSafeShutdown | 3 | 4 | 28.09 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | ConservativeSafeShutdown | 4 | 4 | 41.26 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | ConservativeSafeShutdown | 5 | 4 | 42.64 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | ConservativeSafeShutdown | 6 | 4 | 26.54 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | ConservativeSafeShutdown | 7 | 4 | 10.68 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | ConservativeSafeShutdown | 8 | 4 | 19.02 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | ConservativeSafeShutdown | 9 | 4 | 29.77 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | ConservativeSafeShutdown | 10 | 4 | 45.64 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | ConservativeSafeShutdown | 11 | 4 | 11.74 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | ConservativeSafeShutdown | 12 | 4 | 37.7 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | ConservativeSafeShutdown | 13 | 4 | 29.2 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | ConservativeSafeShutdown | 14 | 4 | 43.76 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | ConservativeSafeShutdown | 15 | 4 | 17.26 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | ConservativeSafeShutdown | 16 | 4 | 46.9 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | ConservativeSafeShutdown | 17 | 4 | 42.05 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | ConservativeSafeShutdown | 18 | 4 | 42.43 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | ConservativeSafeShutdown | 19 | 4 | 13.74 | 0 | 1.0 | 1.0 | success_safe |
| fault_free | ConservativeSafeShutdown | 20 | 4 | 78.08 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | Centralized | 1 | 4 | 25.26 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | Centralized | 2 | 3 | 79.67 | 0 | 0.0 | 1.3333 | partial_safe |
| drop_0_2 | Centralized | 3 | 3 | 14.97 | 0 | 0.0 | 1.3333 | partial_safe |
| drop_0_2 | Centralized | 4 | 4 | 41.26 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | Centralized | 5 | 3 | 44.31 | 0 | 0.0 | 1.3333 | partial_safe |
| drop_0_2 | Centralized | 6 | 4 | 26.54 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | Centralized | 7 | 1 | 1.26 | 0 | 0.0 | 4.0 | partial_safe |
| drop_0_2 | Centralized | 8 | 2 | 11.03 | 0 | 0.0 | 2.0 | partial_safe |
| drop_0_2 | Centralized | 9 | 2 | 2.78 | 0 | 0.0 | 2.0 | partial_safe |
| drop_0_2 | Centralized | 10 | 4 | 45.64 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | Centralized | 11 | 2 | 9.97 | 0 | 0.0 | 2.0 | partial_safe |
| drop_0_2 | Centralized | 12 | 3 | 26.78 | 0 | 0.0 | 1.3333 | partial_safe |
| drop_0_2 | Centralized | 13 | 3 | 30.0 | 0 | 0.0 | 1.3333 | partial_safe |
| drop_0_2 | Centralized | 14 | 4 | 43.76 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | Centralized | 15 | 4 | 17.26 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | Centralized | 16 | 4 | 46.9 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | Centralized | 17 | 4 | 42.05 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | Centralized | 18 | 4 | 42.43 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | Centralized | 19 | 4 | 13.74 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | Centralized | 20 | 4 | 78.08 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | Blackboard | 1 | 4 | 25.26 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | Blackboard | 2 | 3 | 79.67 | 0 | 0.0 | 1.3333 | partial_safe |
| drop_0_2 | Blackboard | 3 | 3 | 14.97 | 0 | 0.0 | 1.3333 | partial_safe |
| drop_0_2 | Blackboard | 4 | 4 | 41.26 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | Blackboard | 5 | 3 | 44.31 | 0 | 0.0 | 1.3333 | partial_safe |
| drop_0_2 | Blackboard | 6 | 4 | 26.54 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | Blackboard | 7 | 1 | 1.26 | 0 | 0.0 | 4.0 | partial_safe |
| drop_0_2 | Blackboard | 8 | 2 | 11.03 | 0 | 0.0 | 2.0 | partial_safe |
| drop_0_2 | Blackboard | 9 | 2 | 2.78 | 0 | 0.0 | 2.0 | partial_safe |
| drop_0_2 | Blackboard | 10 | 4 | 45.64 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | Blackboard | 11 | 2 | 9.97 | 0 | 0.0 | 2.0 | partial_safe |
| drop_0_2 | Blackboard | 12 | 3 | 26.78 | 0 | 0.0 | 1.3333 | partial_safe |
| drop_0_2 | Blackboard | 13 | 3 | 30.0 | 0 | 0.0 | 1.3333 | partial_safe |
| drop_0_2 | Blackboard | 14 | 4 | 43.76 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | Blackboard | 15 | 4 | 17.26 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | Blackboard | 16 | 4 | 46.9 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | Blackboard | 17 | 4 | 42.05 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | Blackboard | 18 | 4 | 42.43 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | Blackboard | 19 | 4 | 13.74 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | Blackboard | 20 | 4 | 78.08 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | RetryHeavy | 1 | 4 | 25.26 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | RetryHeavy | 2 | 4 | 47.9 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | RetryHeavy | 3 | 4 | 18.11 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | RetryHeavy | 4 | 4 | 41.26 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | RetryHeavy | 5 | 4 | 44.14 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | RetryHeavy | 6 | 4 | 26.54 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | RetryHeavy | 7 | 3 | 8.16 | 0 | 0.0 | 1.3333 | partial_safe |
| drop_0_2 | RetryHeavy | 8 | 4 | 7.35 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | RetryHeavy | 9 | 4 | 19.48 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | RetryHeavy | 10 | 4 | 45.64 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | RetryHeavy | 11 | 4 | 10.34 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | RetryHeavy | 12 | 4 | 26.3 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | RetryHeavy | 13 | 4 | 31.01 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | RetryHeavy | 14 | 4 | 43.76 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | RetryHeavy | 15 | 4 | 17.26 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | RetryHeavy | 16 | 4 | 46.9 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | RetryHeavy | 17 | 4 | 42.05 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | RetryHeavy | 18 | 4 | 42.43 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | RetryHeavy | 19 | 4 | 13.74 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | RetryHeavy | 20 | 4 | 78.08 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | NoRecovery | 1 | 4 | 25.26 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | NoRecovery | 2 | 3 | 79.67 | 0 | 0.0 | 1.3333 | partial_safe |
| drop_0_2 | NoRecovery | 3 | 3 | 14.97 | 0 | 0.0 | 1.3333 | partial_safe |
| drop_0_2 | NoRecovery | 4 | 4 | 41.26 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | NoRecovery | 5 | 3 | 44.31 | 0 | 0.0 | 1.3333 | partial_safe |
| drop_0_2 | NoRecovery | 6 | 4 | 26.54 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | NoRecovery | 7 | 1 | 1.26 | 0 | 0.0 | 4.0 | partial_safe |
| drop_0_2 | NoRecovery | 8 | 2 | 11.03 | 0 | 0.0 | 2.0 | partial_safe |
| drop_0_2 | NoRecovery | 9 | 2 | 2.78 | 0 | 0.0 | 2.0 | partial_safe |
| drop_0_2 | NoRecovery | 10 | 4 | 45.64 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | NoRecovery | 11 | 2 | 9.97 | 0 | 0.0 | 2.0 | partial_safe |
| drop_0_2 | NoRecovery | 12 | 3 | 26.78 | 0 | 0.0 | 1.3333 | partial_safe |
| drop_0_2 | NoRecovery | 13 | 3 | 30.0 | 0 | 0.0 | 1.3333 | partial_safe |
| drop_0_2 | NoRecovery | 14 | 4 | 43.76 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | NoRecovery | 15 | 4 | 17.26 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | NoRecovery | 16 | 4 | 46.9 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | NoRecovery | 17 | 4 | 42.05 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | NoRecovery | 18 | 4 | 42.43 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | NoRecovery | 19 | 4 | 13.74 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | NoRecovery | 20 | 4 | 78.08 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | ConservativeSafeShutdown | 1 | 4 | 25.26 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | ConservativeSafeShutdown | 2 | 0 | 0.0 | 0 | 0.0 | 1.0 | failed_safe_shutdown |
| drop_0_2 | ConservativeSafeShutdown | 3 | 1 | 15.46 | 0 | 0.0 | 2.0 | failed_safe_shutdown |
| drop_0_2 | ConservativeSafeShutdown | 4 | 4 | 41.26 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | ConservativeSafeShutdown | 5 | 1 | 47.65 | 0 | 0.0 | 2.0 | failed_safe_shutdown |
| drop_0_2 | ConservativeSafeShutdown | 6 | 4 | 26.54 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | ConservativeSafeShutdown | 7 | 1 | 1.26 | 0 | 0.0 | 2.0 | failed_safe_shutdown |
| drop_0_2 | ConservativeSafeShutdown | 8 | 0 | 0.0 | 0 | 0.0 | 1.0 | failed_safe_shutdown |
| drop_0_2 | ConservativeSafeShutdown | 9 | 0 | 0.0 | 0 | 0.0 | 1.0 | failed_safe_shutdown |
| drop_0_2 | ConservativeSafeShutdown | 10 | 4 | 45.64 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | ConservativeSafeShutdown | 11 | 1 | 10.46 | 0 | 0.0 | 2.0 | failed_safe_shutdown |
| drop_0_2 | ConservativeSafeShutdown | 12 | 3 | 26.78 | 0 | 0.0 | 1.3333 | failed_safe_shutdown |
| drop_0_2 | ConservativeSafeShutdown | 13 | 1 | 31.59 | 0 | 0.0 | 2.0 | failed_safe_shutdown |
| drop_0_2 | ConservativeSafeShutdown | 14 | 4 | 43.76 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | ConservativeSafeShutdown | 15 | 4 | 17.26 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | ConservativeSafeShutdown | 16 | 4 | 46.9 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | ConservativeSafeShutdown | 17 | 4 | 42.05 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | ConservativeSafeShutdown | 18 | 4 | 42.43 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | ConservativeSafeShutdown | 19 | 4 | 13.74 | 0 | 1.0 | 1.0 | success_safe |
| drop_0_2 | ConservativeSafeShutdown | 20 | 4 | 78.08 | 0 | 1.0 | 1.0 | success_safe |

## Aggregate by adapter (mean / stdev)

### drop_0_2

| Adapter | tasks_completed mean | tasks_completed stdev | p95_latency mean | p99_latency mean | safety_viol mean | recovery_rate mean | ttr_ms mean | tts_ms mean | msgs/task mean |
|---------|------------------|------------------|---------------|---------------|---------------|----------------|----------|----------|-------------|
| Centralized | 3.3 | 0.9234 | 32.1845 | 34.355 | 0 | 0.55 | None | 197.631 | 1.3833 |
| Blackboard | 3.3 | 0.9234 | 32.1845 | 34.355 | 0 | 0.55 | None | 197.631 | 1.3833 |
| RetryHeavy | 3.95 | 0.2236 | 31.7855 | 33.7245 | 0 | 0.95 | 62.8048 | 236.3971 | 1.0167 |
| NoRecovery | 3.3 | 0.9234 | 32.1845 | 34.355 | 0 | 0.55 | None | 197.631 | 1.3833 |
| ConservativeSafeShutdown | 2.6 | 1.6983 | 27.806 | 29.3955 | 0 | 0.55 | None | 197.631 | 1.2667 |

### fault_free

| Adapter | tasks_completed mean | tasks_completed stdev | p95_latency mean | p99_latency mean | safety_viol mean | recovery_rate mean | ttr_ms mean | tts_ms mean | msgs/task mean |
|---------|------------------|------------------|---------------|---------------|---------------|----------------|----------|----------|-------------|
| Centralized | 4.0 | 0.0 | 35.3675 | 38.127 | 0 | 1.0 | None | 188.2456 | 1.0 |
| Blackboard | 4.0 | 0.0 | 35.3675 | 38.127 | 0 | 1.0 | None | 188.2456 | 1.0 |
| RetryHeavy | 4.0 | 0.0 | 35.3675 | 38.127 | 0 | 1.0 | None | 188.2456 | 1.0 |
| NoRecovery | 4.0 | 0.0 | 35.3675 | 38.127 | 0 | 1.0 | None | 188.2456 | 1.0 |
| ConservativeSafeShutdown | 4.0 | 0.0 | 35.3675 | 38.127 | 0 | 1.0 | None | 188.2456 | 1.0 |


Generated by `scripts/maestro_baselines.py`.
