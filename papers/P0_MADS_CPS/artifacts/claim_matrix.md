## P0 E4 Claim Matrix

| Claim | Artifact path | Supporting regimes/scenarios | Layer | Status |
|-------|---------------|------------------------------|-------|--------|
| raw controller invariance in baseline | `datasets/runs/p0_e4_raw_summary.json` | baseline: toy_lab_v0, lab_profile_v0, rep_cps_scheduling_v0 | raw-only | supported |
| normalized interface invariance in baseline and moderate | `datasets/runs/p0_e4_normalized_summary.json` | baseline+moderate: toy_lab_v0, lab_profile_v0, rep_cps_scheduling_v0 | normalized-only | supported |
| controller divergence under harder coordination stress | `datasets/runs/p0_e4_diagnostics.json; datasets/runs/p0_e4_controller_pairs.jsonl` | coordination_shock: rep_cps_scheduling_v0 | both | supported |
| raw universal invariance across all regimes | `datasets/runs/p0_e4_raw_summary.json; datasets/runs/p0_e4_raw_failure_reasons.json` | stress+coordination_shock rows | raw-only | not supported |

