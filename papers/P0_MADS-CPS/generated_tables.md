# Generated tables for P0 (P0_MADS-CPS)

Regenerate from repo root (`PYTHONPATH=impl/src`, `LABTRUST_KERNEL_DIR=kernel`): `python scripts/generate_paper_artifacts.py --paper P0`.

Tier 1 includes `maestro_report.json` validation against `kernel/eval/MAESTRO_REPORT.v0.2.schema.json`.

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
| missing_ponr | missing PONR event (lab_profile_v0 requires disposition_commit) | Tier 3 FAIL | Tier 3 FAIL | yes |
| stale_release_manifest | stale/incomplete release manifest (missing release_id) | Tier 1 FAIL | Tier 1 FAIL | yes |

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
| **Summary (n=10)** | mean 4.00, stdev 0.00 | - | mean 34.45, stdev 18.08 | true |

95% CI: tasks_completed [4, 4]; p95_latency_ms [21.512040242650986, 47.383492004789645]

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
| **Summary (n=10)** | mean 5.00, stdev 0.00 | - | mean 42.13, stdev 10.66 | true |

95% CI: tasks_completed [5, 5]; p95_latency_ms [34.500820989131796, 49.75828767450659]

## From export_p0_e4_main_table.py

## P0 E4 — Main table (raw conformance, normalized conformance, strong replay)

Strong replay uses the full MAESTRO core slice plus PONR witness coverage when the scenario declares PONR tasks.

| Scenario | Regime | Controller | Raw conf. rate | Norm. conf. rate | Strong replay | Weak replay | p95 mean (95% CI) ms |
|----------|--------|------------|----------------|------------------|----------------|-------------|----------------------|
| lab_profile_v0 | baseline | centralized | 1.00 | 1.00 | 1.00 | 1.00 | 35.39 [21.97, 48.82] |
| lab_profile_v0 | baseline | rep_cps | 0.00 | 1.00 | 1.00 | 1.00 | 35.39 [21.97, 48.82] |
| lab_profile_v0 | moderate | centralized | 1.00 | 1.00 | 1.00 | 1.00 | 28.97 [13.82, 44.11] |
| lab_profile_v0 | moderate | rep_cps | 0.00 | 1.00 | 1.00 | 1.00 | 28.97 [13.82, 44.11] |
| lab_profile_v0 | stress | centralized | 1.00 | 1.00 | 1.00 | 1.00 | 66.65 [27.53, 105.78] |
| lab_profile_v0 | stress | rep_cps | 0.00 | 1.00 | 1.00 | 1.00 | 66.65 [27.53, 105.78] |
| toy_lab_v0 | baseline | centralized | 1.00 | 1.00 | 1.00 | 1.00 | 42.57 [17.73, 67.40] |
| toy_lab_v0 | baseline | rep_cps | 0.00 | 1.00 | 1.00 | 1.00 | 42.57 [17.73, 67.40] |
| toy_lab_v0 | moderate | centralized | 1.00 | 1.00 | 1.00 | 1.00 | 30.65 [-4.75, 66.06] |
| toy_lab_v0 | moderate | rep_cps | 0.00 | 1.00 | 1.00 | 1.00 | 30.65 [-4.75, 66.06] |
| toy_lab_v0 | stress | centralized | 1.00 | 1.00 | 1.00 | 1.00 | 71.02 [26.20, 115.84] |
| toy_lab_v0 | stress | rep_cps | 0.00 | 1.00 | 1.00 | 1.00 | 71.02 [26.20, 115.84] |

## From export_p0_e4_diagnostics_table.py

## P0 E4 — Diagnostics (centralized vs rep_cps)

| Regime | Scenario | Paired seeds | Trace hash = | MAESTRO hash = | Evidence hash = | Final state = | Mean |Δp95| ms | Seeds divergent (trace/maestro) |
|--------|----------|--------------|--------------|----------------|-----------------|---------------|----------------|----------------------------------|
| baseline | lab_profile_v0 | 5 | 0.00 | 0.00 | 0.00 | 1.00 | 0.0000 | 5 |
| baseline | toy_lab_v0 | 5 | 0.00 | 0.00 | 0.00 | 1.00 | 0.0000 | 5 |
| moderate | lab_profile_v0 | 5 | 0.00 | 0.00 | 0.00 | 1.00 | 0.0000 | 5 |
| moderate | toy_lab_v0 | 5 | 0.00 | 0.00 | 0.00 | 1.00 | 0.0000 | 5 |
| stress | lab_profile_v0 | 5 | 0.00 | 0.00 | 0.00 | 1.00 | 0.0000 | 5 |
| stress | toy_lab_v0 | 5 | 0.00 | 0.00 | 0.00 | 1.00 | 0.0000 | 5 |

## From export_p0_table3.py

## Table 3 — E3 + E4 summary (replay-link and controller-independence)

Latency column: mean of per-seed **task_latency_ms_p95** with 95% CI (t-interval on seed-level samples).
Replay match rate: **strong** replay (E3 when present in summary; E4 from p0_e4_raw_summary baseline rows, else legacy summary).

| Scenario | Controller | Seeds | Replay match rate | p95 latency mean (95% CI) ms | Conformance rate |
|----------|-------------|-------|-------------------|------------------------------|------------------|
| toy_lab_v0 | thinslice | 10 | 1.00 | 34.45 [21.51, 47.38] | 1.00 |
| lab_profile_v0 | thinslice | 10 | 1.00 | 42.13 [34.50, 49.76] | 1.00 |
| lab_profile_v0 | centralized | 5 | 1.00 | 35.39 [21.97, 48.82] | 1.00 |
| lab_profile_v0 | rep_cps | 5 | 1.00 | 35.39 [21.97, 48.82] | 0.00 |
| toy_lab_v0 | centralized | 5 | 1.00 | 42.57 [17.73, 67.40] | 1.00 |
| toy_lab_v0 | rep_cps | 5 | 1.00 | 42.57 [17.73, 67.40] | 0.00 |

