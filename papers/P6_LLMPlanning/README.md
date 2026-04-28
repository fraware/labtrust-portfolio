# P6 — Safe LLM Planning

P6 is a CPS runtime-enforcement paper: typed plan steps, deterministic validation, and auditable denial traces at the tool boundary.

## Evidence tiers

- **Canonical Table 1b (primary claim source):** `datasets/runs/llm_eval_camera_ready_20260424`.
  - OpenAI `gpt-4.1-mini` and `gpt-4.1`, full suite, `n_runs=3`, 25 cases/model, 75/75 each.
- **Extended robust package (supplementary, separately labeled):** `datasets/runs/llm_eval_paper_bundle_final`.
  - Source lineage is `MANIFEST.json` (`canonical_reference`) and `README.md`.
  - Gate status is in `ROBUST_GPT_SUMMARY.md`; machine check is `verify_p6_robust_gpt_bundle.py`.
- **Freeze hygiene/audit rollup:** `datasets/runs/p6_final_audit_20260424`.
  - Recomputed aggregates, replay-scope checks, hash inventory, and claim checklist.

## Core artifacts

- `red_team_results.json`, `confusable_deputy_results.json`, `e2e_denial_trace.json`
- `adapter_latency.json`, `denial_trace_stats.json`
- `baseline_comparison.json`, `baseline_comparison_args.json`, `baseline_benign.json`
- `task_critical_injection.json`

## Commands and reporting docs

- Full runbook and exact commands: `sat-cps2026/EXPERIMENTS_RUNBOOK.md`
- Submission guardrails: `sat-cps2026/SUBMISSION_STANDARD.md`
- Acceptance checklist: `sat-cps2026/FINAL_CHECKLIST.md`
- Results narrative: `P6_RESULTS_REPORT.md`
- Cross-paper index: `../../docs/RESULTS_PER_PAPER.md`

## Important reporting rule

Do not merge denominators across evidence tiers. Keep canonical Table 1b numbers tied to `llm_eval_camera_ready_20260424`, and label robust/GPT-5.x rows as separate experiments with their own run ids and denominators.
