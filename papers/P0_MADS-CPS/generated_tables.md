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

## From export_p0_e4_main_table.py

## P0 E4 — Main table (raw conformance, normalized conformance, strong replay)

Strong replay uses the full MAESTRO core slice plus PONR witness coverage when the scenario declares PONR tasks.

| Scenario | Regime | Controller | Raw conf. rate | Norm. conf. rate | Strong replay | Weak replay | p95 mean (95% CI) ms |
|----------|--------|------------|----------------|------------------|----------------|-------------|----------------------|
| lab_profile_v0 | baseline | centralized | 1.00 | 1.00 | 1.00 | 1.00 | 50.37 [40.02, 60.73] |
| lab_profile_v0 | baseline | rep_cps | 1.00 | 1.00 | 1.00 | 1.00 | 50.37 [40.02, 60.73] |
| lab_profile_v0 | coordination_shock | centralized | 0.85 | 0.85 | 0.85 | 1.00 | 156.47 [127.09, 185.85] |
| lab_profile_v0 | coordination_shock | rep_cps | 0.85 | 0.85 | 0.85 | 1.00 | 156.47 [127.09, 185.85] |
| lab_profile_v0 | moderate | centralized | 1.00 | 1.00 | 1.00 | 1.00 | 39.86 [27.99, 51.74] |
| lab_profile_v0 | moderate | rep_cps | 1.00 | 1.00 | 1.00 | 1.00 | 39.86 [27.99, 51.74] |
| lab_profile_v0 | stress | centralized | 0.85 | 0.85 | 0.85 | 1.00 | 66.56 [48.40, 84.71] |
| lab_profile_v0 | stress | rep_cps | 0.85 | 0.85 | 0.85 | 1.00 | 66.56 [48.40, 84.71] |
| rep_cps_scheduling_v0 | baseline | centralized | 1.00 | 1.00 | 1.00 | 1.00 | 35.37 [26.73, 44.01] |
| rep_cps_scheduling_v0 | baseline | rep_cps | 1.00 | 1.00 | 1.00 | 1.00 | 35.37 [26.73, 44.01] |
| rep_cps_scheduling_v0 | coordination_shock | centralized | 1.00 | 1.00 | 1.00 | 1.00 | 147.25 [117.01, 177.49] |
| rep_cps_scheduling_v0 | coordination_shock | rep_cps | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 [0.00, 0.00] |
| rep_cps_scheduling_v0 | moderate | centralized | 1.00 | 1.00 | 1.00 | 1.00 | 34.94 [21.49, 48.40] |
| rep_cps_scheduling_v0 | moderate | rep_cps | 1.00 | 1.00 | 1.00 | 1.00 | 34.94 [21.49, 48.40] |
| rep_cps_scheduling_v0 | stress | centralized | 1.00 | 1.00 | 1.00 | 1.00 | 73.62 [48.74, 98.51] |
| rep_cps_scheduling_v0 | stress | rep_cps | 1.00 | 1.00 | 1.00 | 1.00 | 73.62 [48.74, 98.51] |
| toy_lab_v0 | baseline | centralized | 1.00 | 1.00 | 1.00 | 1.00 | 35.37 [26.73, 44.01] |
| toy_lab_v0 | baseline | rep_cps | 1.00 | 1.00 | 1.00 | 1.00 | 35.37 [26.73, 44.01] |
| toy_lab_v0 | coordination_shock | centralized | 1.00 | 1.00 | 1.00 | 1.00 | 147.25 [117.01, 177.49] |
| toy_lab_v0 | coordination_shock | rep_cps | 1.00 | 1.00 | 1.00 | 1.00 | 147.25 [117.01, 177.49] |
| toy_lab_v0 | moderate | centralized | 1.00 | 1.00 | 1.00 | 1.00 | 34.94 [21.49, 48.40] |
| toy_lab_v0 | moderate | rep_cps | 1.00 | 1.00 | 1.00 | 1.00 | 34.94 [21.49, 48.40] |
| toy_lab_v0 | stress | centralized | 1.00 | 1.00 | 1.00 | 1.00 | 73.62 [48.74, 98.51] |
| toy_lab_v0 | stress | rep_cps | 1.00 | 1.00 | 1.00 | 1.00 | 73.62 [48.74, 98.51] |

## From export_p0_e4_diagnostics_table.py

## P0 E4 — Diagnostics (centralized vs rep_cps)

| Regime | Scenario | Paired seeds | Trace hash = | MAESTRO hash = | Core hash = | Hist = | PONR set = | Final state = | Mean |Δp95| ms | Mean |Δevents| | Mean |Δcoord-msg| | Seeds divergent (trace/maestro) |
|--------|----------|--------------|--------------|----------------|-----------|--------|-----------|---------------|----------------|----------------|--------------------|----------------------------------|
| baseline | lab_profile_v0 | 20 | 0.00 | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.0000 | 0.0000 | 0.0000 | 20 |
| baseline | rep_cps_scheduling_v0 | 20 | 0.00 | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.0000 | 0.0000 | 0.0000 | 20 |
| baseline | toy_lab_v0 | 20 | 0.00 | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.0000 | 0.0000 | 0.0000 | 20 |
| coordination_shock | lab_profile_v0 | 20 | 0.00 | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.0000 | 0.0000 | 0.0000 | 20 |
| coordination_shock | rep_cps_scheduling_v0 | 20 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 147.2510 | 10.7500 | 0.0000 | 20 |
| coordination_shock | toy_lab_v0 | 20 | 0.00 | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.0000 | 0.0000 | 0.0000 | 20 |
| moderate | lab_profile_v0 | 20 | 0.00 | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.0000 | 0.0000 | 0.0000 | 20 |
| moderate | rep_cps_scheduling_v0 | 20 | 0.00 | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.0000 | 0.0000 | 0.0000 | 20 |
| moderate | toy_lab_v0 | 20 | 0.00 | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.0000 | 0.0000 | 0.0000 | 20 |
| stress | lab_profile_v0 | 20 | 0.00 | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.0000 | 0.0000 | 0.0000 | 20 |
| stress | rep_cps_scheduling_v0 | 20 | 0.00 | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.0000 | 0.0000 | 0.0000 | 20 |
| stress | toy_lab_v0 | 20 | 0.00 | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.0000 | 0.0000 | 0.0000 | 20 |

## From export_p0_table3.py

## Table 3a — E3 replay-link (strong)

E3 row uses strong replay fields only (`all_strong_match` required).

| Scenario | Controller | Seeds | Replay match rate | p95 latency mean (95% CI) ms | Conformance rate |
|----------|-------------|-------|-------------------|------------------------------|------------------|
| toy_lab_v0 | thinslice | 20 | 1.00 | 35.37 [27.11, 43.62] | 1.00 |
| lab_profile_v0 | thinslice | 20 | 1.00 | 50.37 [40.48, 60.27] | 1.00 |

## Table 3b — E4 raw vs normalized controller invariance

Replay rate is strong replay from controller-matrix summaries.

| Scenario | Regime | Controller | Seeds | Raw conformance | Normalized conformance | Strong replay | p95 latency mean (95% CI) ms |
|----------|--------|------------|-------|-----------------|------------------------|---------------|------------------------------|
| lab_profile_v0 | baseline | centralized | 20 | 1.00 | 1.00 | 1.00 | 50.37 [40.02, 60.73] |
| lab_profile_v0 | baseline | rep_cps | 20 | 1.00 | 1.00 | 1.00 | 50.37 [40.02, 60.73] |
| lab_profile_v0 | coordination_shock | centralized | 20 | 0.85 | 0.85 | 0.85 | 156.47 [127.09, 185.85] |
| lab_profile_v0 | coordination_shock | rep_cps | 20 | 0.85 | 0.85 | 0.85 | 156.47 [127.09, 185.85] |
| lab_profile_v0 | moderate | centralized | 20 | 1.00 | 1.00 | 1.00 | 39.86 [27.99, 51.74] |
| lab_profile_v0 | moderate | rep_cps | 20 | 1.00 | 1.00 | 1.00 | 39.86 [27.99, 51.74] |
| lab_profile_v0 | stress | centralized | 20 | 0.85 | 0.85 | 0.85 | 66.56 [48.40, 84.71] |
| lab_profile_v0 | stress | rep_cps | 20 | 0.85 | 0.85 | 0.85 | 66.56 [48.40, 84.71] |
| rep_cps_scheduling_v0 | baseline | centralized | 20 | 1.00 | 1.00 | 1.00 | 35.37 [26.73, 44.01] |
| rep_cps_scheduling_v0 | baseline | rep_cps | 20 | 1.00 | 1.00 | 1.00 | 35.37 [26.73, 44.01] |
| rep_cps_scheduling_v0 | coordination_shock | centralized | 20 | 1.00 | 1.00 | 1.00 | 147.25 [117.01, 177.49] |
| rep_cps_scheduling_v0 | coordination_shock | rep_cps | 20 | 1.00 | 1.00 | 1.00 | 0.00 [0.00, 0.00] |
| rep_cps_scheduling_v0 | moderate | centralized | 20 | 1.00 | 1.00 | 1.00 | 34.94 [21.49, 48.40] |
| rep_cps_scheduling_v0 | moderate | rep_cps | 20 | 1.00 | 1.00 | 1.00 | 34.94 [21.49, 48.40] |
| rep_cps_scheduling_v0 | stress | centralized | 20 | 1.00 | 1.00 | 1.00 | 73.62 [48.74, 98.51] |
| rep_cps_scheduling_v0 | stress | rep_cps | 20 | 1.00 | 1.00 | 1.00 | 73.62 [48.74, 98.51] |
| toy_lab_v0 | baseline | centralized | 20 | 1.00 | 1.00 | 1.00 | 35.37 [26.73, 44.01] |
| toy_lab_v0 | baseline | rep_cps | 20 | 1.00 | 1.00 | 1.00 | 35.37 [26.73, 44.01] |
| toy_lab_v0 | coordination_shock | centralized | 20 | 1.00 | 1.00 | 1.00 | 147.25 [117.01, 177.49] |
| toy_lab_v0 | coordination_shock | rep_cps | 20 | 1.00 | 1.00 | 1.00 | 147.25 [117.01, 177.49] |
| toy_lab_v0 | moderate | centralized | 20 | 1.00 | 1.00 | 1.00 | 34.94 [21.49, 48.40] |
| toy_lab_v0 | moderate | rep_cps | 20 | 1.00 | 1.00 | 1.00 | 34.94 [21.49, 48.40] |
| toy_lab_v0 | stress | centralized | 20 | 1.00 | 1.00 | 1.00 | 73.62 [48.74, 98.51] |
| toy_lab_v0 | stress | rep_cps | 20 | 1.00 | 1.00 | 1.00 | 73.62 [48.74, 98.51] |

