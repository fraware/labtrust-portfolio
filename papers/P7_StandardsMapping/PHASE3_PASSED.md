# Phase 3 passed

Submission-readiness checklist (`docs/STATE_OF_THE_ART_CRITERIA.md` section 3) verified on **2026-04-20** against freshly regenerated artifacts (`run_assurance_eval.py`, `run_assurance_robust_eval.py`, `export_assurance_tables.py`, `tests/test_assurance_p7.py`, `render_p7_mermaid_figures.py`).

- **Claim-evidence:** All claims in `claims.yaml` have `artifact_paths` and at least one `table_id` or `figure_id` (C3 includes Table 3 and Figure 0/1 sources).
- **Repro:** Documented one-shot sequence in `DRAFT.md` and `README.md`: baseline eval, mapping flow + GSN Mermaid, export tables, robust matrix (default 20 seeds), optional Mermaid render to PNG/PDF.
- **Variance / manifests:** `datasets/runs/assurance_eval/results.json` includes `run_manifest` (scenario-matched `per_profile`, `table1_primary_scenario` = `lab_profile_v0`). `robust_results.json` includes `run_manifest.seeds` (20), `n_total_runs` (400), `scenario_profile_alignment`, and `scenario_profile_note` for traffic↔medical proxy.
- **Robust matrix (publishable):** `scripts/run_assurance_robust_eval.py` default **20 seeds**, **400 runs** (4 scenarios × 5 fault regimes × 20 seeds). Protocol: `docs/P7_ROBUST_EXPERIMENT_PLAN.md`.
- **Robust completion criteria** (current committed run satisfies):
  - `mapping_check.ok` = true
  - `mapping_check.ponr_coverage_ok` = true
  - `aggregate.evidence_bundle_ok_rate` = 1.0
  - `aggregate.trace_ok_rate` = 1.0
  - `aggregate.review_pass_rate` = 1.0 (≥ 0.95 required)
  - `real_world_proxy.review_pass_rate` = 1.0 (≥ 0.95; scenarios `warehouse_v0`, `traffic_v0`)
- **No kernel redefinition:** Draft cites ASSURANCE_PACK schema and portfolio artifacts; does not redefine tiers or trace semantics.
- **Overclaim guard:** No certification claim; non-goals and K7 (no template theater) in draft; mapping is translation and audit-support only.
- **Figures:** `docs/figures/p7_mapping_flow.mmd`, `p7_gsn.mmd`, `p7_review_stages.mmd` (+ `.png`, `.pdf` when `render_p7_mermaid_figures.py` / mmdc available).
- **Discrimination (C4):** `negative_results.json` from `run_assurance_negative_eval.py`; ablation CSVs from `export_p7_negative_tables.py`; `review_assurance_run.py --review-mode` documented; failure codes in `docs/P7_REVIEW_FAILURE_CODES.md`.
