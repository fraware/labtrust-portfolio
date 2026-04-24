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
| **ENGINEERING_TRUTH_PACKAGE_2026-04-24.md** | Implementation truth audit (schema, safe_args, traces, replay) |
| **CLAIM_ARTIFACT_MATRIX_FREEZE_2026-04-24.md** | Pre-submit claim-to-artifact matrix |
| **FREEZE_SUBMISSION_NOTES_2026-04-24.md** | One-page freeze snapshot (canonical run, denominators, non-merge rules) |
| **FREEZE_VERIFICATION_REPORT_2026-04-24.json** | Machine-readable existence + consistency checks |

## Evidence tiers (how to cite without overclaiming)

1. **Primary (validator correctness):** Synthetic suite in `red_team_results.json`, `confusable_deputy_results.json` -- 15 red-team, 6 confusable deputy, 4 jailbreak-style cases. This is the main security evidence for "firewall blocks released unsafe forms."
2. **Canonical real-LLM (OpenAI, Table 1b):** Run `llm_redteam_eval.py --real-llm --real-llm-models gpt-4.1-mini,gpt-4.1 --real-llm-runs 3 --real-llm-suite full`. Camera-ready snapshot (`llm_eval_camera_ready_20260424`): **75/75 passes per model** (100.0%, 95% Wilson CI [95.1, 100.0]); **25 cases per model** (15 red-team + 6 confusable deputy + 4 jailbreak-style), N=3 runs/case. Always report denominator and suite_mode from run_manifest.
3. **Optional cross-provider matrix (Prime Inference):** If enabled in the eval script, a separate output directory (e.g. `datasets/runs/llm_eval_prime_matrix_top4_n3/`) can hold N=3 runs/case and four models. Treat as **supplementary** unless you regenerate and promote it to the main paper; keep denominators explicitly separated from OpenAI runs. See **EXPERIMENTS_RUNBOOK.md** for commands.
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

Real-LLM (Table 1b, OpenAI): add API key to `.env` and run the first eval with `--real-llm --real-llm-models gpt-4.1-mini,gpt-4.1 --real-llm-runs 3 --real-llm-suite full` (see EXPERIMENTS_RUNBOOK.md).
