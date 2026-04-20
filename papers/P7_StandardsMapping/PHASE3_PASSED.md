# Phase 3 passed

Submission-readiness checklist (`docs/STATE_OF_THE_ART_CRITERIA.md` section 3) verified on **2026-03-31**.

- Claim-evidence: All claims in `claims.yaml` have `artifact_paths` and at least one `table_id` or `figure_id`.
- Repro under 20 min: Minimal run documented; `run_assurance_eval` then export tables then Figure 0 and Figure 1.
- Variance: Results from assurance eval; run manifest in `datasets/runs/assurance_eval/results.json` where applicable.
- Robust matrix (publishable): `scripts/run_assurance_robust_eval.py` writes `datasets/runs/assurance_eval/robust_results.json` (default **20 seeds**, 400 runs in the standard matrix). Full protocol and criteria: `docs/P7_ROBUST_EXPERIMENT_PLAN.md`.
- **Robust matrix completion criteria** (must hold when claiming a publishable robust run):
  - `mapping_check.ok`
  - `mapping_check.ponr_coverage_ok` (when applicable)
  - `aggregate.evidence_bundle_ok_rate = 1.0`
  - `aggregate.trace_ok_rate = 1.0`
  - `aggregate.review_pass_rate >= 0.95` over the full scenario x fault-regime x seed matrix
  - `real_world_proxy.review_pass_rate >= 0.95` (runs restricted to `warehouse_v0` and `traffic_v0`)
- No kernel redefinition: Draft cites ASSURANCE_PACK schema and portfolio artifacts (P0, P3); does not redefine tiers or trace.
- Overclaim: No certification claim; Non-goals and K7 (no template theater) in draft; mapping is translation layer only.
- Repro block: Figure 0, Table 1, Table 2, Figure 1, and one-command audit each have exact script commands.
