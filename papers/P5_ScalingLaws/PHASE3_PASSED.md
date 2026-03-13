# Phase 3 passed

Submission-readiness checklist (docs/STATE_OF_THE_ART_CRITERIA.md section 3) verified on 2025-03-11.

- Claim-evidence: All claims in claims.yaml have artifact_paths and at least one table_id or figure_id.
- Repro under 20 min: Minimal run documented (--seeds 3); publishable uses --seeds 10; run manifest in heldout_results.json.
- Variance: Run manifest (seeds, scenarios) in heldout_results.json; 10 seeds for publishable tables.
- No kernel redefinition: Draft cites P5_SCALING_SPEC and MAESTRO runs; does not redefine trace or eval schema.
- Overclaim: Conditional paper; trigger and scope stated in Limitations and docs/CONDITIONAL_TRIGGERS.md (P5).
- Repro block: Figure 0, Table 1, Table 2, Figure 1 each have exact script commands.
