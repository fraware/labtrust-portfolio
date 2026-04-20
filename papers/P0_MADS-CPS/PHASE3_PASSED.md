# Phase 3 passed (peer-review revision)

Submission-readiness checklist (`docs/STATE_OF_THE_ART_CRITERIA.md` section 3) verified for manuscript draft v0.2 with **MAESTRO_REPORT v0.2** conformance and publishable E3/E4 settings.

- **Claim-evidence:** All claims in `claims.yaml` have `artifact_paths` and table/figure ids; C1–C4 map to E1–E4; C2/C3 cite `kernel/eval/MAESTRO_REPORT.v0.2.schema.json` where schema validation matters.
- **Repro:** Commands in `DRAFT.md` (Reproducibility + Appendix): `build_p0_conformance_corpus`, `export_e1_corpus_table`, `e2_redaction_demo`, `export_e2_admissibility_matrix`, `produce_p0_e3_release.py` / `replay_link_e3.py` with **`--runs 20 --scenarios lab_profile_v0,toy_lab_v0 --standalone-verifier`** (`lab_profile_v0` canonical release scenario; override via `--release-scenario`), `run_p0_e4_multi_adapter.py` with matching seeds/scenarios, `export_p0_table3.py`; figures: `export_p0_assurance_pipeline`, `export_p0_tier_lattice`, `export_p0_redaction_figure`; optional `plot_e3_latency.py`; `generate_paper_artifacts.py --paper P0` for this file.
- **Variance:** `run_manifest` in `datasets/runs/e3_summary.json` and `datasets/runs/p0_e4_summary.json` (optional `version` = git `HEAD` when available); `datasets/runs/p0_conformance_corpus/corpus_manifest.json`; frozen release `datasets/releases/p0_e3_release/` including `conformance.json`.
- **Table export:** `export_e1_corpus_table.py` emits full `fault_injected` strings (no truncation). Regenerate tables after evals: `python scripts/generate_paper_artifacts.py --paper P0`.
- **No kernel redefinition:** Draft cites kernel (NORMATIVE, VERIFICATION_MODES, EVIDENCE_BUNDLE, MAESTRO_REPORT v0.2, PONR); checker implementation in `impl/src/labtrust_portfolio/conformance.py` matches `REQUIRED_ARTIFACTS`.
- **Overclaim:** No certification; machine-checkable pass/fail under a declared envelope; restricted auditability preserves a subset of checks; replay semantics explicit.
- **Repro block:** Exact commands at top of `DRAFT.md` and in Appendix; environment: `PYTHONPATH=impl/src`, `LABTRUST_KERNEL_DIR=kernel`.
