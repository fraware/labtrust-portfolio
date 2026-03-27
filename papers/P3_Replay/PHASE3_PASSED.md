# Phase 3 passed

Submission-readiness checklist (docs/STATE_OF_THE_ART_CRITERIA.md section 3) verified on 2025-03-11.

- Claim-evidence: All claims in claims.yaml have artifact_paths and at least one table_id or figure_id.
- Repro under 20 min: Minimal run documented (overhead-runs 5); publishable uses overhead-runs 20; run manifest in summary.json.
- Variance: Run manifest (corpus, overhead_runs) in summary.json.
- No kernel redefinition: Draft cites TRACE schema and REPLAY_LEVELS; does not redefine tiers or evidence bundle.
- Overclaim: Replay levels L0/L1/L2 and nondeterminism detection stated; no claim to full determinism on hardware; L2 aspirational.
- Repro block: Figure 0, Table 1, Table 1b, Table 2, Figure 1 each have exact script commands (`export_replay_corpus_table.py --out-md` for Table 1/1b).
