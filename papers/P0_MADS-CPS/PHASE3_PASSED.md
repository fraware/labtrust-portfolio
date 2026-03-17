# Phase 3 passed (peer-review revision)

Submission-readiness checklist (docs/STATE_OF_THE_ART_CRITERIA.md section 3) verified after peer-review revision (v0.2).

- **Claim-evidence:** All claims in claims.yaml have artifact_paths and table_id/figure_id; C1–C4 use calibrated wording; evidence maps to E1–E4.
- **Repro:** Minimal run documented in DRAFT Appendix; build_p0_conformance_corpus, export_e1_corpus_table, e2_redaction_demo, export_e2_admissibility_matrix, produce_p0_e3_release, replay_link_e3 (optional --standalone-verifier), run_p0_e4_multi_adapter, export_p0_table3; figures: export_p0_assurance_pipeline, export_p0_tier_lattice, export_p0_redaction_figure.
- **Variance:** Run manifest in e3_summary.json, p0_e4_summary.json, corpus_manifest.json; Table 1 (E1 corpus), Table 2 (4-col admissibility), Table 3 (E3+E4).
- **No kernel redefinition:** Draft cites kernel (NORMATIVE, VERIFICATION_MODES, EVIDENCE_BUNDLE, PONR); formal definitions in paper align with kernel; repro and schema paths in Appendix only.
- **Overclaim:** No certification; "machine-checkable pass/fail under a declared envelope"; "conformance to the proposed assurance bar"; "one class of high-impact transition"; "subset of admissibility checks under redaction."
- **Repro block:** Exact commands in DRAFT Appendix; main text references "artifact contains schema set, reference implementation, conformance checker, reproduction scripts."
