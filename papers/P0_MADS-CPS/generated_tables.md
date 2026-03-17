# Generated tables for P0 (P0_MADS-CPS)

**Paper title:** MADS-CPS: A Machine-Checkable Minimum Assurance Bar for Agentic Cyber-Physical Workflows.

**How to read:** Table 1 is the E1 conformance challenge set (case ID, fault injected, expected/observed outcome, agreement). Table 2 is the verification-mode admissibility matrix (four columns: full, evaluator, regulator, public/redacted). Table 3 is replay-link and conformance by scenario/controller (E3 + E4). Per-seed E3 table is in the appendix.

## Table 1 — Conformance challenge set (E1)

Regenerate: `python scripts/build_p0_conformance_corpus.py --out datasets/runs/p0_conformance_corpus`, then `python scripts/export_e1_corpus_table.py --corpus datasets/runs/p0_conformance_corpus`.

| Case ID | Fault injected | Expected outcome | Observed outcome | Agreement |
|---------|----------------|------------------|------------------|-----------|
| valid_toy | none | Tier 3 PASS | Tier 3 PASS | yes |
| valid_lab | none | Tier 3 PASS | Tier 3 PASS | yes |
| missing_artifact | missing artifact (maestro_report.json) | Tier 1 FAIL | Tier 1 FAIL | yes |
| schema_invalid | schema-invalid artifact (trace) | Tier 1 FAIL | Tier 1 FAIL | yes |
| hash_mismatch | hash mismatch (state_hash_after corrupted) | Tier 2 FAIL | Tier 2 FAIL | yes |
| replay_mismatch | evidence_bundle.verification.replay_ok=false | Tier 2 FAIL | Tier 2 FAIL | yes |
| missing_ponr | missing PONR event (lab_profile_v0) | Tier 3 FAIL | Tier 3 FAIL | yes |
| stale_release_manifest | stale/incomplete release manifest | Tier 1 FAIL | Tier 1 FAIL | yes |

## Table 2 — Verification-mode admissibility matrix (E2)

Regenerate: `python scripts/e2_redaction_demo.py --out datasets/runs/e2_redaction_demo`, then `python scripts/export_e2_admissibility_matrix.py`.

| Predicate | Full mode | Evaluator mode | Regulator mode | Public/redacted mode |
|-----------|-----------|----------------|----------------|----------------------|
| schema_validation_ok | yes | yes | yes | yes |
| integrity_ok (hashes) | yes | yes | yes | yes |
| replay_ok (L0/L1) | yes | yes (full trace); no (redacted) | yes (full); no (redacted) | no (redacted); N/A (public) |
| PONR coverage | yes | yes (full); N/A (redacted) | yes (full); N/A (redacted) | N/A (redacted) |

## Table 3 — Replay-link and conformance across controllers/scenarios (E3 + E4)

Regenerate E4: `python scripts/run_p0_e4_multi_adapter.py --seeds 10`, then `python scripts/export_p0_table3.py --e4 datasets/runs/p0_e4_summary.json`. Optionally merge E3: `--e3 datasets/runs/e3_summary.json`.

| Scenario | Controller | Seeds | Replay match rate | Latency mean (95% CI) ms | Conformance rate |
|----------|-------------|-------|-------------------|---------------------------|------------------|
| toy_lab_v0 | centralized | 10 | 1.00 | (from run) | 1.00 |
| toy_lab_v0 | rep_cps | 10 | (from run) | (from run) | (from run) |

## Appendix: Per-seed E3 table

Regenerate: `python scripts/produce_p0_e3_release.py --runs 20`, then `python scripts/export_e3_table.py`. Summary row: mean, stdev, 95% CI for tasks_completed and p95_latency_ms; run_manifest in e3_summary.json.
