# Generated tables for P0 (P0_MADS-CPS)

## From export_e1_corpus_table.py

## Table 1 — E1 conformance corpus

| Case ID | Fault injected | Expected outcome | Observed outcome | Agreement |
|---------|-----------------|------------------|------------------|-----------|
| valid_toy | none | Tier 3 PASS | Tier 3 PASS | yes |
| valid_lab | none | Tier 3 PASS | Tier 3 PASS | yes |
| missing_artifact | missing artifact (maestro_report.json) | Tier 1 FAIL | Tier 1 FAIL | yes |
| schema_invalid | schema-invalid artifact (trace) | Tier 1 FAIL | Tier 1 FAIL | yes |
| hash_mismatch | hash mismatch (state_hash_after corrupted) | Tier 2 FAIL | Tier 2 FAIL | yes |
| replay_mismatch | evidence_bundle.verification.replay_ok=false | Tier 2 FAIL | Tier 2 FAIL | yes |
| missing_ponr | missing PONR event (lab_profile_v0 requires d... | Tier 3 FAIL | Tier 3 FAIL | yes |
| stale_release_manifest | stale/incomplete release manifest (missing re... | Tier 1 FAIL | Tier 1 FAIL | yes |

## From export_e2_admissibility_matrix.py

## Table 2 — E2 admissibility matrix

| Predicate | Full mode | Evaluator mode | Regulator mode | Public/redacted mode |
|-----------|-----------|----------------|----------------|----------------------|
| schema_validation_ok | yes | yes | yes | yes |
| integrity_ok (hashes) | yes | yes | yes | yes |
| replay_ok (L0/L1) | yes | yes (full trace); no (redacted) | yes (full); no (redacted) | no (redacted); N/A (public, replay not required) |
| PONR coverage | yes | yes (full); N/A (redacted, structure only) | yes (full); N/A (redacted) | N/A (redacted) |

Full mode: all artifacts present and unredacted; all predicates checkable. Evaluator and regulator: when trace is redacted, payloads are content-addressed refs; replay is not run, so replay_ok is false; schema and integrity remain checkable. Public/redacted: when redacted, same as evaluator redacted; when public and unredacted, replay is not required by mode so replay_ok may be N/A. See kernel/mads/VERIFICATION_MODES.v0.1.md.

## From export_e3_table.py

## E3 replay-link - per-seed detail (supporting Table 3)

Per-seed rows for trace-to-report replay check; aggregate replay match and latency CIs appear in **Table 3**. Full manifest: `datasets/runs/e3_summary.json` (`run_manifest`).

## Scenario: toy_lab_v0

| Seed | tasks_completed | coordination_messages | p95_latency_ms | match |
|------|----------------|----------------------|----------------|-------|
| 1 | 4 | 4 | 25.26 | yes |
| 2 | 4 | 4 | 75.59 | yes |
| 3 | 4 | 4 | 28.09 | yes |
| 4 | 4 | 4 | 41.26 | yes |
| 5 | 4 | 4 | 42.64 | yes |
| 6 | 4 | 4 | 26.54 | yes |
| 7 | 4 | 4 | 10.68 | yes |
| 8 | 4 | 4 | 19.02 | yes |
| 9 | 4 | 4 | 29.77 | yes |
| 10 | 4 | 4 | 45.64 | yes |
| 11 | 4 | 4 | 11.74 | yes |
| 12 | 4 | 4 | 37.70 | yes |
| 13 | 4 | 4 | 29.20 | yes |
| 14 | 4 | 4 | 43.76 | yes |
| 15 | 4 | 4 | 17.26 | yes |
| 16 | 4 | 4 | 46.90 | yes |
| 17 | 4 | 4 | 42.05 | yes |
| 18 | 4 | 4 | 42.43 | yes |
| 19 | 4 | 4 | 13.74 | yes |
| 20 | 4 | 4 | 78.08 | yes |
| **Summary (n=20)** | mean 4.00, stdev 0.00 | - | mean 35.37, stdev 18.46 | true |

95% CI: tasks_completed [4, 4]; p95_latency_ms [27.11415732757751, 43.62175076100369]

## Scenario: lab_profile_v0

| Seed | tasks_completed | coordination_messages | p95_latency_ms | match |
|------|----------------|----------------------|----------------|-------|
| 1 | 5 | 5 | 41.08 | yes |
| 2 | 5 | 5 | 20.40 | yes |
| 3 | 5 | 5 | 34.94 | yes |
| 4 | 5 | 5 | 31.24 | yes |
| 5 | 5 | 5 | 49.30 | yes |
| 6 | 5 | 5 | 52.13 | yes |
| 7 | 5 | 5 | 42.31 | yes |
| 8 | 5 | 5 | 49.89 | yes |
| 9 | 5 | 5 | 45.28 | yes |
| 10 | 5 | 5 | 54.72 | yes |
| 11 | 5 | 5 | 50.84 | yes |
| 12 | 5 | 5 | 100.07 | yes |
| 13 | 5 | 5 | 35.31 | yes |
| 14 | 5 | 5 | 26.80 | yes |
| 15 | 5 | 5 | 42.48 | yes |
| 16 | 5 | 5 | 18.79 | yes |
| 17 | 5 | 5 | 90.42 | yes |
| 18 | 5 | 5 | 71.00 | yes |
| 19 | 5 | 5 | 78.56 | yes |
| 20 | 5 | 5 | 71.90 | yes |
| **Summary (n=20)** | mean 5.00, stdev 0.00 | - | mean 50.37, stdev 22.13 | true |

95% CI: tasks_completed [5, 5]; p95_latency_ms [40.476976268464604, 60.268873664712]

## From export_p0_table3.py

## Table 3 — E3 + E4 summary (replay-link and controller-independence)

Latency column: mean of per-seed **task_latency_ms_p95** with 95% CI (t-interval on seed-level samples).

| Scenario | Controller | Seeds | Replay match rate | p95 latency mean (95% CI) ms | Conformance rate |
|----------|-------------|-------|-------------------|------------------------------|------------------|
| toy_lab_v0 | thinslice | 20 | 1.00 | 35.37 [27.11, 43.62] | 1.00 |
| lab_profile_v0 | thinslice | 20 | 1.00 | 50.37 [40.48, 60.27] | 1.00 |
| toy_lab_v0 | centralized | 20 | 1.00 | 35.37 [26.73, 44.01] | 1.00 |
| toy_lab_v0 | rep_cps | 20 | 1.00 | 35.37 [26.73, 44.01] | 1.00 |
| lab_profile_v0 | centralized | 20 | 1.00 | 50.37 [40.02, 60.73] | 1.00 |
| lab_profile_v0 | rep_cps | 20 | 1.00 | 50.37 [40.02, 60.73] | 1.00 |

