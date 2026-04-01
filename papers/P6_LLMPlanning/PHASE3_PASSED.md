# Phase 3 passed

Submission-readiness checklist (docs/STATE_OF_THE_ART_CRITERIA.md section 3) verified on 2025-03-11.

- Claim-evidence: All claims in claims.yaml have artifact_paths and at least one table_id or figure_id (Table 1, Table 1b, Table 2, Baseline table, Figure 0, Figure 1).
- Repro under 20 min: Minimal run documented (adapter-seeds 3); run manifest in red_team_results.json and adapter_latency.json. Full publishable: --real-llm-runs 10 --real-llm-suite full, 3 scenarios, 20 seeds, --run-baseline (3-way), optional --baseline-plan args_unsafe and benign, optional --latency-decomposition.
- Variance: Scenarios and seeds in adapter_latency.json; red-team from eval; real-LLM multi-run with pass_rate and Wilson CI (OpenAI canonical: gpt-4.1-mini, gpt-4.1).
- No kernel redefinition: Draft cites TYPED_PLAN schema and MAESTRO; does not redefine tiers or trace.
- Overclaim: Conditional paper; trigger and scope in Limitations and docs/CONDITIONAL_TRIGGERS.md (P6). Containment only, not elimination. Real-LLM: synthetic table remains primary validator evidence; Table 1b documents pass_rate and CI.
- Repro block: Figure 0 (export_p6_firewall_flow.py), Table 1 and Table 1b (llm_redteam_eval.py then export_llm_redteam_table.py), Table 2 (adapter_latency.json), Baseline (llm_redteam_eval.py --run-baseline then export_p6_baseline_table.py; optional --baseline-file for args_unsafe and baseline_benign), Figure 1 (plot_llm_adapter_latency.py), appendix reproducibility (export_p6_artifact_hashes.py, export_p6_reproducibility_table.py).

**SaT-CPS 2026:** Additional venue-specific checklist and runbook: `sat-cps2026/FINAL_CHECKLIST.md`, `sat-cps2026/EXPERIMENTS_RUNBOOK.md`, `sat-cps2026/README.md`.
