# P0 Supplementary Package

This package contains the frozen evidence and paper-facing exports for P0 (MADS-CPS), with claims bounded by the claim matrix.

## What E3 proves

`e3_summary.json` demonstrates externally verifiable replay-link under an independent verifier path, using strong replay semantics.

## What E4 proves

`p0_e4_controller_matrix.json` with raw/normalized summaries and diagnostics shows:

- where controller invariance holds at the evidence layer (notably baseline rows),
- and where controller divergence appears under harder stress (`coordination_shock` in `rep_cps_scheduling_v0`).

## What normalization does

`normalization_diff.json` records normalization provenance. Normalization is constrained to adapter-only MAESTRO top-level removals used for normalized-interface evaluation, not hidden evidence repair on the raw path.

## What the anomaly regime demonstrates

`controller_divergence_table.md` and `coordination_shock_note.md` explain the assurance-valid safe-nonproductive outcome (`partial_safe`, zero completed tasks) under `coordination_shock + rep_cps_scheduling_v0`: admissibility and replay can hold while productivity collapses.

## What is not claimed

Per `claim_matrix.md`, raw universal invariance across all regimes is not supported and is explicitly not claimed.
