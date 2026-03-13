# Generated tables for P0 (P0_MADS-CPS)

**How to read:** Table 1 shows per-seed E3 replay-link metrics (tasks_completed, p95_latency_ms) and match; summary row gives mean, stdev, and 95% CI. Table 2 shows which admissibility conditions hold for full vs redacted trace.

## From export_e3_table.py

**Table 1 — E3 replay-link (per seed).** tasks_completed, coordination_messages, p95_latency_ms (ms), and match per seed; summary row with mean, stdev, and 95% CI. N seeds per scenario (run_manifest in e3_summary.json).

# E3 Replay link (multi-scenario)

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
| **Summary (n=10)** | mean 4.00, stdev 0.00 | - | mean 34.45, stdev 18.08 | true |

95% CI: tasks_completed [4, 4]; p95_latency_ms [21.512040242650986, 47.383492004789645]

## From export_e2_admissibility_matrix.py

**Table 2 — E2 redaction admissibility matrix.** Which admissibility conditions (schema_validation_ok, integrity_ok, replay_ok, PONR coverage) remain checkable for full trace vs redacted trace (payloads replaced by content-addressed refs).

## E2 Redaction admissibility matrix

| Admissibility condition | Full trace | Redacted trace |
|-------------------------|------------|----------------|
| schema_validation_ok    | yes        | yes            |
| integrity_ok (hashes)    | yes        | yes            |
| replay_ok (L0/L1)       | yes        | no (audit-only)|
| PONR coverage           | yes        | N/A (structure only) |

Redacted trace preserves event order, timestamps, and state_hash_after; payloads are replaced by content-addressed refs. Replay is not run on redacted trace (replay expects full payloads). See kernel/mads/VERIFICATION_MODES.v0.1.md.

