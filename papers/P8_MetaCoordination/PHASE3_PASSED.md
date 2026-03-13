# Phase 3 passed

Submission-readiness checklist (docs/STATE_OF_THE_ART_CRITERIA.md section 3) verified on 2025-03-11.

- Claim-evidence: All claims in claims.yaml have artifact_paths and at least one table_id or figure_id.
- Repro under 20 min: Minimal run documented; meta_eval then export_meta_tables then Figure 0; collapse_sweep then Figure 1.
- Variance: Run manifest (seeds, scenario, fault_threshold) in comparison.json; collapse_sweep.json for Figure 1.
- No kernel redefinition: Draft cites META_CONTROLLER_SPEC and TRACE schema; does not redefine tiers or evidence.
- Overclaim: Conditional paper; trigger and scope stated in Limitations and docs/CONDITIONAL_TRIGGERS.md (P8).
- Repro block: Figure 0, Table 1, Table 2, Figure 1 each have exact script commands.
