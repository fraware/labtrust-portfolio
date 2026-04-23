# P0 Submission Lock (KDD workshop)

- packaging_commit_sha: `28a226d9bb02450bf4b93349250881146c117e8a`
- artifact_generation_commit_sha: `eef272e691d53d53495dd2ca6e8017a0ccb2a7a9`
- lock_timestamp_utc: `2026-04-23T11:44:39Z`
- tag: not created in this pass (optional recommendation: `v0.1-p0-kdd-draft`)

Provenance note: the workshop artifacts were generated at `artifact_generation_commit_sha` and then frozen/documented at `packaging_commit_sha`; no additional E1-E5 numerical reruns were performed between these commits, and this lock file is the manuscript-facing source of truth for provenance.

## Canonical commands used

Environment:
- PYTHONPATH=impl/src
- LABTRUST_KERNEL_DIR=kernel

E1:
- python scripts/build_p0_conformance_corpus.py --out datasets/runs/p0_conformance_corpus
- python scripts/export_e1_corpus_table.py --corpus datasets/runs/p0_conformance_corpus

E2:
- python scripts/e2_redaction_demo.py --out datasets/runs/e2_redaction_demo
- python scripts/export_e2_admissibility_matrix.py

E3:
- python scripts/produce_p0_e3_release.py --runs 20 --scenarios lab_profile_v0,toy_lab_v0 --standalone-verifier

E4:
- python scripts/run_p0_e4_controller_matrix.py --seeds 20 --scenarios toy_lab_v0,lab_profile_v0,rep_cps_scheduling_v0 --regimes baseline,moderate,stress,coordination_shock --out datasets/runs/p0_e4_controller_matrix.json

E4 manuscript-facing export (new):
- python scripts/export_p0_e4_admissibility_vs_productivity.py

E5 model evolution (new):
- python scripts/run_p0_e5_model_evolution.py --seeds 20 --scenarios toy_lab_v0,lab_profile_v0,rep_cps_scheduling_v0 --regimes baseline,coordination_shock --out datasets/runs/p0_e5_model_evolution.json

E5 focused by-cell export (new):
- python scripts/export_p0_e5_focus_table.py

## Canonical manuscript artifact paths (workshop package)

- papers/P0_MADS_CPS/kdd_workshop/artifacts/e3_summary.json
- papers/P0_MADS_CPS/kdd_workshop/artifacts/p0_e3_variance.json
- papers/P0_MADS_CPS/kdd_workshop/artifacts/p0_e1_corpus_table.md
- papers/P0_MADS_CPS/kdd_workshop/artifacts/p0_e2_admissibility_matrix.md
- papers/P0_MADS_CPS/kdd_workshop/artifacts/table3.md
- papers/P0_MADS_CPS/kdd_workshop/artifacts/p0_e4_controller_matrix.json
- papers/P0_MADS_CPS/kdd_workshop/artifacts/p0_e4_admissibility_vs_productivity.json
- papers/P0_MADS_CPS/kdd_workshop/artifacts/p0_e4_admissibility_vs_productivity.csv
- papers/P0_MADS_CPS/kdd_workshop/artifacts/p0_e4_coordination_shock_focus.json
- papers/P0_MADS_CPS/kdd_workshop/artifacts/p0_e4_coordination_shock_focus.csv
- papers/P0_MADS_CPS/kdd_workshop/artifacts/p0_e5_model_evolution.json
- papers/P0_MADS_CPS/kdd_workshop/artifacts/p0_e5_model_evolution_summary.csv
- papers/P0_MADS_CPS/kdd_workshop/artifacts/p0_e5_model_evolution_per_seed.jsonl
- papers/P0_MADS_CPS/kdd_workshop/artifacts/p0_e5_model_evolution_by_cell.json
- papers/P0_MADS_CPS/kdd_workshop/artifacts/p0_e5_model_evolution_by_cell.csv
- papers/P0_MADS_CPS/kdd_workshop/artifacts/p0_e5_coordination_shock_focus.json
- papers/P0_MADS_CPS/kdd_workshop/artifacts/p0_e5_coordination_shock_focus.csv

## Deviations from canonical commands

- None for E1-E4 generation.
- Added export-only script for E4 manuscript readability, one E5 experiment script, and one E5 by-cell/focus export script.
