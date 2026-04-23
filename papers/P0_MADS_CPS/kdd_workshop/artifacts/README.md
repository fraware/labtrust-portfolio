# P0 Workshop Artifacts (Canonical)

This directory is the canonical manuscript-facing artifact set for the P0 KDD workshop package.

## Source of truth policy

- Manuscript and reviewer citations should use files in this directory.
- `datasets/runs/` contains generation-time working outputs, but workshop-facing references are frozen here.
- Provenance is tracked in `../P0_SUBMISSION_LOCK.md`.

## Files

- `p0_e1_corpus_table.md` - E1 conformance corpus table.
- `p0_e2_admissibility_matrix.md` - E2 restricted auditability table.
- `e3_summary.json` - E3 replay-link summary.
- `p0_e3_variance.json` - E3 variance and uncertainty summary.
- `table3.md` - P0 table export combining E3 and E4 views.
- `p0_e4_controller_matrix.json` - E4 matrix payload.
- `p0_e4_admissibility_vs_productivity.json` and `.csv` - E4 admissibility/productivity export.
- `p0_e4_coordination_shock_focus.json` and `.csv` - E4 focused anomaly slice.
- `controller_divergence_table.md` - E4 divergence-focused table.
- `claim_matrix.md` - claim boundary matrix.
- `p0_e5_model_evolution.json` - E5 global synthetic version-shift summary.
- `p0_e5_model_evolution_summary.csv` - E5 compact per-version table.
- `p0_e5_model_evolution_per_seed.jsonl` - E5 per-seed rows used for all E5 aggregation.
- `p0_e5_model_evolution_by_cell.json` and `.csv` - E5 by-cell aggregate by version/controller/scenario/regime.
- `p0_e5_coordination_shock_focus.json` and `.csv` - E5 focus rows and deltas for explicit `rep_cps_scheduling_v0` targets (`baseline` and `coordination_shock`) plus max-delta V0->V2 focus cells.

## Copy status

- These files are frozen workshop copies.
- Where `datasets/runs/` counterparts exist, they are generation-time equivalents rather than manuscript citation targets.
