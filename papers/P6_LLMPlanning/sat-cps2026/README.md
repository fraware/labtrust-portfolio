# P6 SaT-CPS 2026 venue pack

This folder is the **submission-facing bundle** for the workshop paper (ACM proceedings, 10-page target). It is separate from the portfolio-wide P6 draft (`../DRAFT.md`, `../claims.yaml`) but should stay **numerically and procedurally consistent** with the repo eval pipeline.

## What is in this folder

| File | Role |
|------|------|
| **SUBMISSION_STANDARD.md** | Five acceptance axes, banned wording, page budget |
| **ROLES.md** | Four ownership lanes (security story, evaluation, artifacts, ACM) |
| **FINAL_CHECKLIST.md** | Pre-submit sign-off checklist |
| **REVIEW_PROTOCOL.md** | Three internal reviews before submission |
| **claims_satcps.yaml** | Four venue claims (C1--C4) with evidence pointers |
| **EXPERIMENTS_RUNBOOK.md** | Commands, artifacts, experiment roadmap (0--12), exports |
| **DRAFT_SaT-CPS.md** | Markdown source aligned with the venue narrative (sync with `main.tex` as needed) |
| **main.tex** | ACM `acmart` sigconf stub (abstract and section skeleton) |
| **references.bib** | Bibliography for LaTeX |
| **reproducibility_table.md** | Example or exported appendix table (regenerate via scripts; not authoritative alone) |
| **layer_attribution.md** | Example or exported layer-attribution table (from `export_p6_layer_attribution.py`) |

## Evidence tiers (how to cite without overclaiming)

1. **Primary (validator correctness):** Synthetic suite in `red_team_results.json`, `confusable_deputy_results.json` -- 9 red-team, 4 confusable deputy, 2 jailbreak-style cases. This is the main security evidence for "firewall blocks released unsafe forms."
2. **Canonical real-LLM (OpenAI, Table 1b):** Run `llm_redteam_eval.py --real-llm --real-llm-models gpt-4.1-mini,gpt-4.1 --real-llm-runs 5`. Reported snapshot (2026-03-17): **55/65 passes per model** (84.6%, 95% Wilson CI [73.9, 91.4]); **13 cases per model** (9 red-team + 4 confusable deputy; jailbreak-style evaluated separately in synthetic/jailbreak table). Both models score **0/5** on `rt_allowed_tool_disallowed_args` and **0/5** on `rt_allowed_tool_denylist_key` in that run.
3. **Optional cross-provider matrix (Prime Inference):** If enabled in the eval script, a separate output directory (e.g. `datasets/runs/llm_eval_prime_matrix_top4_n3/`) can hold N=3 runs/case and four models. Treat as **supplementary** unless you regenerate and promote it to the main paper; numbers differ from the OpenAI canonical run (denominator 39 vs 65). See **EXPERIMENTS_RUNBOOK.md** for commands.
4. **Deployability and extensions (experiments 6--12):** Concurrency, capture-off ablation, storage, cost model, policy sweep, replanning, adaptive suite -- optional JSON artifacts under `datasets/runs/llm_eval/` or adjacent paths; support deployment claims only when those JSONs exist for the cited tag.

## Run manifest and reproducibility

All summary JSONs under `datasets/runs/llm_eval/` include `run_manifest` with at least `timestamp_iso`, `evaluator_version`, `policy_version`. Real-LLM runs add `prompt_template_hash` where applicable. For an appendix mapping **table/claim to artifact hash**, run:

```text
python scripts/export_p6_artifact_hashes.py --out-dir datasets/runs/llm_eval
python scripts/export_p6_reproducibility_table.py
```

Further exports: `export_p6_layer_attribution.py`, `export_p6_failure_analysis.py`, `export_p6_cross_model_heatmap.py`, `export_p6_latency_decomposition.py` (see EXPERIMENTS_RUNBOOK.md).

## Related paths in the repo

- Portfolio P6 folder: `papers/P6_LLMPlanning/` (`README.md`, `P6_RESULTS_REPORT.md`, `DRAFT.md`, `claims.yaml`, `AUTHORING_PACKET.md`)
- Implementation: `impl/src/labtrust_portfolio/llm_planning.py`, `adapters/llm_planning_adapter.py`, `reproducibility.py`
- Datasets: `datasets/p6_benign_suite.json`, `datasets/p6_adaptive_suite.json`
- Cross-repo docs: `docs/RESULTS_PER_PAPER.md` (P6 section), `docs/EVALS_RUNBOOK.md`, `docs/CONDITIONAL_TRIGGERS.md` (P6)

## Quick command reference (publishable, non-LLM core)

From repo root with `PYTHONPATH=impl/src` and `LABTRUST_KERNEL_DIR=kernel`:

```bash
python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval --run-adapter --denial-stats --latency-decomposition --adapter-scenarios toy_lab_v0,lab_profile_v0,warehouse_v0 --adapter-seeds 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20
python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval --run-baseline --baseline-scenarios toy_lab_v0,lab_profile_v0,warehouse_v0 --baseline-seeds 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20
python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval --run-baseline --baseline-plan args_unsafe --baseline-scenarios toy_lab_v0,lab_profile_v0,warehouse_v0 --baseline-seeds 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20
python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval --run-baseline --baseline-plan benign --baseline-scenarios toy_lab_v0,lab_profile_v0,warehouse_v0 --baseline-seeds 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20
```

Real-LLM (Table 1b, OpenAI): add API key to `.env` and run the first eval with `--real-llm --real-llm-models gpt-4.1-mini,gpt-4.1 --real-llm-runs 5` (see EXPERIMENTS_RUNBOOK.md).
