# Phase 3 passed

Submission-readiness checklist (docs/STATE_OF_THE_ART_CRITERIA.md section 3) verified on 2026-04-19.

- Claim-evidence: `papers/P4_CPS-MAESTRO/claims.yaml` paths resolve to committed artifacts under `datasets/releases/p4_publishable_v1/` and `datasets/runs/`.
- MAESTRO_REPORT: Publishable runs use **v0.2** (`kernel/eval/MAESTRO_REPORT.v0.2.schema.json`); report derivation is `impl/src/labtrust_portfolio/maestro.py` (`maestro_report_from_trace`).
- Recovery and safety semantics: documented in `bench/maestro/RECOVERY_AND_SAFETY_METRICS.md`; scoring in `bench/maestro/SCORING.md`.
- Repro: Minimal run remains fast (CI uses fewer seeds); publishable sweep uses **20 seeds** and five scenarios (see `datasets/runs/RUN_RESULTS_SUMMARY.md`).
- Variance: `multi_sweep.json` includes `run_manifest` and per-run rows with p99, recovery, and safety aggregates.
- No kernel redefinition: Draft cites schemas and bench specs; does not redefine tiers or PONR admissibility.
- Honest scope: Lab-first benchmark; warehouse/traffic/regime stress are auxiliary micro-scenarios; thin-slice simulation only (no certification, no physical plant).
- Figures: `docs/figures/p4_recovery_curve.png`, `p4_safety_violations.png`, `p4_efficiency_messages.png` with JSON sidecars from `scripts/plot_maestro_recovery.py`.
