# P0 KDD Workshop Package

This folder is the workshop-facing packaging layer for P0 (MADS-CPS). It is built from canonical E1-E4 commands plus one new E5 synthetic model-evolution experiment.

## Scope

- Preserve P0 normative semantics (tiers, admissibility, replay, PONR).
- Regenerate E1-E4 from a coherent repo state.
- Export a sharper E4 admissibility-vs-productivity view.
- Add E5 version-shift sensitivity under fixed scenarios and interface.

## Canonical environment

- `PYTHONPATH=impl/src`
- `LABTRUST_KERNEL_DIR=kernel`

## Canonical command set used

- E1:
  - `python scripts/build_p0_conformance_corpus.py --out datasets/runs/p0_conformance_corpus`
  - `python scripts/export_e1_corpus_table.py --corpus datasets/runs/p0_conformance_corpus`
- E2:
  - `python scripts/e2_redaction_demo.py --out datasets/runs/e2_redaction_demo`
  - `python scripts/export_e2_admissibility_matrix.py`
- E3:
  - `python scripts/produce_p0_e3_release.py --runs 20 --scenarios lab_profile_v0,toy_lab_v0 --standalone-verifier`
- E4:
  - `python scripts/run_p0_e4_controller_matrix.py --seeds 20 --scenarios toy_lab_v0,lab_profile_v0,rep_cps_scheduling_v0 --regimes baseline,moderate,stress,coordination_shock --out datasets/runs/p0_e4_controller_matrix.json`
- E4 manuscript-facing export:
  - `python scripts/export_p0_e4_admissibility_vs_productivity.py`
- E5:
  - `python scripts/run_p0_e5_model_evolution.py --seeds 20 --scenarios toy_lab_v0,lab_profile_v0,rep_cps_scheduling_v0 --regimes baseline,coordination_shock --out datasets/runs/p0_e5_model_evolution.json`
- E5 manuscript-facing focused export:
  - `python scripts/export_p0_e5_focus_table.py`

## Primary files in this package

- `P0_SUBMISSION_LOCK.md` - exact provenance, commands, artifacts, deviations
- `P0_ONE_PARAGRAPH_STATUS.md` - what changed, what new claim is supportable, what remains unsupported
- `artifacts/` - canonical frozen manuscript-facing exports (source of truth for workshop submission)

## Claim boundary

- Supported: replay-link verifiability (E3), baseline invariance and stressed divergence localization (E4), bounded synthetic version-shift sensitivity under fixed interface semantics (E5).
- Not supported: raw universal invariance across all regimes.

## Path policy

- Canonical workshop artifact paths are under `papers/P0_MADS_CPS/kdd_workshop/artifacts/`.
- `datasets/runs/` paths are generation-time working outputs; manuscript citations should reference the frozen workshop copies.
