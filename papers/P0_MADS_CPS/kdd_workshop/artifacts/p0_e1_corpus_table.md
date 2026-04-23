## Table 1 ù E1 conformance corpus

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

