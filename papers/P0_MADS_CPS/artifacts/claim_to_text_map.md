Refresh stamp: 2026-04-22T11:30:15Z

## P0 Claim-To-Text Map

- **Claim text:** "Replay-link is externally verifiable by an independent verifier."
  - **Evidence artifacts:** `datasets/runs/e3_summary.json`, `datasets/runs/p0_e3_variance.json`
  - **Export artifact:** `papers/P0_MADS_CPS/artifacts/table3.md`

- **Claim text:** "Raw controller invariance holds in baseline regime under the declared envelope."
  - **Evidence artifacts:** `datasets/runs/p0_e4_raw_summary.json`
  - **Support rows:** baseline rows for `toy_lab_v0`, `lab_profile_v0`, `rep_cps_scheduling_v0`
  - **Export artifact:** `papers/P0_MADS_CPS/artifacts/table3.md`

- **Claim text:** "Normalized-interface controller invariance holds in baseline and moderate regimes."
  - **Evidence artifacts:** `datasets/runs/p0_e4_normalized_summary.json`, `datasets/runs/p0_e4_normalization_diff.json`
  - **Export artifact:** `papers/P0_MADS_CPS/artifacts/table3.md`

- **Claim text:** "Controller divergence appears under harder coordination stress."
  - **Evidence artifacts:** `datasets/runs/p0_e4_diagnostics.json`, `datasets/runs/p0_e4_controller_pairs.jsonl`
  - **Focused regime/scenario:** `coordination_shock` + `rep_cps_scheduling_v0`
  - **Export artifact:** `papers/P0_MADS_CPS/artifacts/controller_divergence_table.md`

- **Claim text:** "Safe-nonproductive outcomes can remain assurance-valid."
  - **Evidence artifacts:** `papers/P0_MADS_CPS/artifacts/controller_divergence_table.md`, `docs/P0_E4_COORDINATION_SHOCK_NOTE.md`, `papers/P0_MADS_CPS/artifacts/coordination_shock_note_short.md`

- **Claim text:** "Raw universal invariance across all regimes is not claimed."
  - **Evidence artifacts:** `papers/P0_MADS_CPS/artifacts/claim_matrix.md`, `datasets/runs/p0_e4_raw_failure_reasons.json`
  - **Status:** explicitly `not supported` in claim matrix export.

