# P0 Submission Lock (KDD workshop)

- Commit SHA: 2021c8455c3ba6f92bb28fc63e7a80745766d32a
- Lock timestamp (UTC): 2026-04-23T11:44:39Z
- Tag: not created in this pass (optional recommendation: v0.1-p0-kdd-draft)

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

## Artifact paths used by manuscript package

- datasets/runs/p0_conformance_corpus/
- datasets/runs/e2_redaction_demo/
- datasets/runs/e3_summary.json
- datasets/runs/p0_e3_variance.json
- datasets/runs/p0_e4_controller_matrix.json
- datasets/runs/p0_e4_raw_summary.json
- datasets/runs/p0_e4_normalized_summary.json
- datasets/runs/p0_e4_per_seed.jsonl
- datasets/runs/p0_e4_diagnostics.json
- datasets/runs/p0_e4_controller_pairs.jsonl
- datasets/runs/p0_e4_raw_failure_reasons.json
- datasets/runs/p0_e4_admissibility_vs_productivity.json
- datasets/runs/p0_e4_coordination_shock_focus.json
- datasets/runs/p0_e5_model_evolution.json
- datasets/runs/p0_e5_model_evolution_per_seed.jsonl
- datasets/runs/p0_e5_model_evolution_summary.csv

## Deviations from canonical commands

- None for E1-E4 generation.
- Added export-only script for E4 manuscript readability and one new E5 experiment script.
