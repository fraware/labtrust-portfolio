# Generated tables for P0 (P0_MADS-CPS)

## From export_e3_table.py

# Table 1 — E3 replay-link. tasks_completed, p95_latency_ms (ms), match per seed; N seeds (run_manifest in e3_summary.json).

# E3 Replay link (multi-scenario)

## Scenario: toy_lab_v0

| Seed | tasks_completed | coordination_messages | p95_latency_ms | match |
|------|----------------|----------------------|----------------|-------|
| 1 | 4 | 4 | 25.26 | yes |
| 2 | 4 | 4 | 75.59 | yes |
| 3 | 4 | 4 | 28.09 | yes |
| 4 | 4 | 4 | 41.26 | yes |
| 5 | 4 | 4 | 42.64 | yes |
| **Summary (n=5)** | mean 4.00, stdev 0.00 | - | mean 42.57, stdev 20.01 | true |

95% CI: tasks_completed [4, 4]; p95_latency_ms [17.72932831525616, 67.40489309336124]

## Scenario: lab_profile_v0

| Seed | tasks_completed | coordination_messages | p95_latency_ms | match |
|------|----------------|----------------------|----------------|-------|
| 1 | 5 | 5 | 25.03 | yes |
| 2 | 5 | 5 | 71.50 | yes |
| 3 | 5 | 5 | 28.77 | yes |
| 4 | 5 | 5 | 40.41 | yes |
| 5 | 5 | 5 | 46.40 | yes |
| **Summary (n=5)** | mean 5.00, stdev 0.00 | - | mean 42.42, stdev 18.40 | true |

95% CI: tasks_completed [5, 5]; p95_latency_ms [19.57868896825692, 65.26817519704065]

## From export_e2_admissibility_matrix.py

## Table 2 — Verification-mode admissibility matrix (E2)

| Predicate | Full mode | Evaluator mode | Regulator mode | Public/redacted mode |
|-----------|-----------|----------------|----------------|----------------------|
| schema_validation_ok | yes | yes | yes | yes |
| integrity_ok (hashes) | yes | yes | yes | yes |
| replay_ok (L0/L1) | yes | yes (full trace); no (redacted) | yes (full); no (redacted) | no (redacted); N/A (public, replay not required) |
| PONR coverage | yes | yes (full); N/A (redacted, structure only) | yes (full); N/A (redacted) | N/A (redacted) |

Full mode: all artifacts present and unredacted; all predicates checkable. Evaluator and regulator: when trace is redacted, payloads are content-addressed refs; replay is not run, so replay_ok is false; schema and integrity remain checkable. Public/redacted: when redacted, same as evaluator redacted; when public and unredacted, replay is not required by mode so replay_ok may be N/A. See kernel/mads/VERIFICATION_MODES.v0.1.md.

