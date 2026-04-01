# SaT-CPS 2026 P6 -- Experiments runbook

Commands assume repo root, `PYTHONPATH=impl/src`, `LABTRUST_KERNEL_DIR=kernel` (PowerShell: `$env:PYTHONPATH="impl\src"; $env:LABTRUST_KERNEL_DIR="$PWD\kernel"`).

## 1. Purpose

This runbook ties **claims in the SaT-CPS paper** to **exact scripts and artifacts**. Synthetic results are reproducible without API keys. Real-LLM runs require `.env` (see below).

## 2. Environment

| Variable | Role |
|----------|------|
| `PYTHONPATH=impl/src` | Import `labtrust_portfolio` |
| `LABTRUST_KERNEL_DIR=kernel` | Kernel-relative paths |
| `OPENAI_API_KEY` | Real-LLM (OpenAI) in `.env` at repo root |
| `LABTRUST_FIXED_SEED` | Optional; stabilizes bootstrap/stochastic helpers in comparison stats |

## 3. Experiment roadmap (0--12)

| ID | Name | Script / flag | Main artifact(s) |
|----|------|---------------|------------------|
| 0 | Integrity and reproducibility | All evals write `run_manifest`; then `export_p6_artifact_hashes.py`, `export_p6_reproducibility_table.py` | `p6_artifact_hashes.json`, `reproducibility_table.md` |
| 1 | Cross-model real-LLM | `llm_redteam_eval.py --real-llm --real-llm-models a,b` | `red_team_results.json` (`real_llm_models[]`, `cross_model_summary`) |
| 2 | Layer attribution | Synthetic + real runs; `export_p6_layer_attribution.py` | `layer_attribution.md`; per-case `attribution`, `denial_by_layer` in JSON |
| 3 | Failure taxonomy | After real-LLM with `run_details`; `export_p6_failure_analysis.py` | `p6_failure_analysis.json` |
| 4 | Benign / false-positive utility | `--run-baseline --baseline-plan benign` | `baseline_benign.json`; suite: `datasets/p6_benign_suite.json` |
| 5 | Latency decomposition | `--run-adapter --latency-decomposition` | `adapter_latency.json` (`latency_decomposition`) |
| 6 | Concurrency | `p6_concurrency_benchmark.py` | `p6_concurrency_benchmark.json` |
| 7 | Capture-off ablation | `p6_capture_ablation.py` | `p6_capture_ablation.json` |
| 8 | Storage benchmark | `p6_storage_benchmark.py` | `p6_storage_benchmark.json` |
| 9 | Cost model | `p6_cost_model.py` | `p6_cost_model.json` |
| 10 | Policy strictness sweep | `p6_policy_sweep.py` | `p6_policy_sweep.json` |
| 11 | Replanning after denial | `p6_replanning_benchmark.py` | `p6_replanning_benchmark.json` |
| 12 | Adaptive / indirect suite | `p6_adaptive_suite_run.py` | `p6_adaptive_results.json`; suite: `datasets/p6_adaptive_suite.json` |

Experiments 6--12 are **optional** for the core security story; include them when the draft cites deployability or extended threat coverage.

## 4. Core pipeline (no API keys)

### 4.1 Synthetic red-team, confusable deputy, E2E trace

```bash
python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval
```

Writes `red_team_results.json`, `confusable_deputy_results.json`, `e2e_denial_trace.json`.

### 4.2 Adapter latency, denial stats, latency decomposition

```bash
python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval --run-adapter --denial-stats --latency-decomposition \
  --adapter-scenarios toy_lab_v0,lab_profile_v0,warehouse_v0 \
  --adapter-seeds 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20
```

Writes `adapter_latency.json` (with `denial_stats`, optional `latency_decomposition`), `denial_trace_stats.json`.

### 4.3 Baselines: tool-level, argument-level, benign

```bash
python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval --run-baseline \
  --baseline-scenarios toy_lab_v0,lab_profile_v0,warehouse_v0 \
  --baseline-seeds 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20

python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval --run-baseline --baseline-plan args_unsafe \
  --baseline-scenarios toy_lab_v0,lab_profile_v0,warehouse_v0 \
  --baseline-seeds 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20

python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval --run-baseline --baseline-plan benign \
  --baseline-scenarios toy_lab_v0,lab_profile_v0,warehouse_v0 \
  --baseline-seeds 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20
```

Writes `baseline_comparison.json`, `baseline_comparison_args.json`, `baseline_benign.json`.

### 4.4 One-shot alternative

```bash
python scripts/run_paper_experiments.py --paper P6
```

Runs the paper-default bundle (no real-LLM). Use `--quick` for fewer seeds.

## 5. Real-LLM -- OpenAI (canonical Table 1b)

Requires `OPENAI_API_KEY` in `.env`.

```bash
python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval \
  --real-llm --real-llm-models gpt-4.1-mini,gpt-4.1 --real-llm-runs 10 --real-llm-suite full
python scripts/export_llm_redteam_table.py --out-dir datasets/runs/llm_eval
```

**Publishable defaults:** `--real-llm-runs 10`, `--real-llm-suite full` (red-team + confusable deputy + jailbreak-style in the same API loop as Table 1b). Use `--real-llm-suite core` to match older red+confusable-only denominators. **Historical snapshot (2026-03-17):** 13 cases per model, 5 runs per case (pre-expansion corpora). Structure of `real_llm` vs `real_llm_models[]` follows `llm_redteam_eval.py`; `run_manifest.suite_mode` and `real_llm_case_count` record the mix.

## 6. Real-LLM -- optional Prime Inference (four-model matrix)

If the eval script supports `--real-llm-provider prime` and Prime API keys, you can write a **separate** output directory so you do not overwrite the OpenAI canonical run:

```bash
python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval_prime_matrix_top4_n3 \
  --real-llm --real-llm-provider prime \
  --real-llm-models x-ai/grok-4-fast,google/gemini-2.5-flash,openai/gpt-4.1-mini,qwen/qwen3-30b-a3b-instruct-2507 \
  --real-llm-runs 3
```

**Example snapshot (2026-03-18, N=3, 13 cases/model, 39 trials/model):** grok-4-fast 39/39 (100.0%, Wilson [91.0, 100.0]); gemini-2.5-flash, gpt-4.1-mini, qwen3-30b each 33/39 (84.6%, [70.3, 92.8]); disagreement matrix highlights two argument-level cases. **Do not mix denominators** (39 vs 65) in the same table row without relabeling the experiment.

## 7. Exports (tables, figures, appendix)

```bash
python scripts/export_llm_redteam_table.py --out-dir datasets/runs/llm_eval
python scripts/export_p6_baseline_table.py --out-dir datasets/runs/llm_eval
python scripts/export_p6_baseline_table.py --out-dir datasets/runs/llm_eval --baseline-file baseline_comparison_args.json
python scripts/export_p6_baseline_table.py --out-dir datasets/runs/llm_eval --baseline-file baseline_benign.json
python scripts/export_p6_firewall_flow.py
python scripts/plot_llm_adapter_latency.py --latency datasets/runs/llm_eval/adapter_latency.json
python scripts/export_p6_denial_trace_case_study.py --trace datasets/runs/llm_eval/baseline_runs/gated/toy_lab_v0/seed_1/trace.json
python scripts/export_p6_artifact_hashes.py --out-dir datasets/runs/llm_eval --markdown
python scripts/export_p6_reproducibility_table.py
python scripts/export_p6_layer_attribution.py
python scripts/export_p6_failure_analysis.py
python scripts/export_p6_cross_model_heatmap.py
python scripts/export_p6_latency_decomposition.py
```

Optional: `--out papers/P6_LLMPlanning/exported_tables.md` on `export_llm_redteam_table.py`.

## 8. Artifact inventory (`datasets/runs/llm_eval/`)

| Artifact | Produced by |
|----------|-------------|
| `red_team_results.json` | `llm_redteam_eval.py` (synthetic + optional real_llm / real_llm_models) |
| `confusable_deputy_results.json` | same |
| `e2e_denial_trace.json` | same |
| `adapter_latency.json` | `--run-adapter` (optional `--latency-decomposition`) |
| `denial_trace_stats.json` | `--run-adapter --denial-stats` |
| `baseline_comparison.json` | `--run-baseline` |
| `baseline_comparison_args.json` | `--run-baseline --baseline-plan args_unsafe` |
| `baseline_benign.json` | `--run-baseline --baseline-plan benign` |
| `p6_artifact_hashes.json` | `export_p6_artifact_hashes.py` |
| `p6_failure_analysis.json` | `export_p6_failure_analysis.py` |
| `p6_concurrency_benchmark.json` | `p6_concurrency_benchmark.py` |
| `p6_capture_ablation.json` | `p6_capture_ablation.py` |
| `p6_storage_benchmark.json` | `p6_storage_benchmark.py` |
| `p6_cost_model.json` | `p6_cost_model.py` |
| `p6_policy_sweep.json` | `p6_policy_sweep.py` |
| `p6_replanning_benchmark.json` | `p6_replanning_benchmark.py` |
| `p6_adaptive_results.json` | `p6_adaptive_suite_run.py` |

**Baseline trace metadata:** Gated/weak traces may include `metadata.denied_steps` and `metadata.denial_reason` for case-study export.

## 9. Research questions and statistics

- **Q1:** Synthetic separation of safe vs unsafe (Block A).
- **Q2:** Persistence under real LLM outputs (Block B).
- **Q3:** Bounded overhead and replayable denials (Block C).
- **Q4:** Tool vs argument layer contribution (Block D + layer attribution).
- **Q5:** Benign tasks not over-denied (benign baseline).

Pass rates: **95% Wilson score interval**. Latency: mean, stdev, CI for mean where applicable.

## 10. Related documents

- **README.md** (this folder) -- Evidence tiers and quick reference.
- **SUBMISSION_STANDARD.md** -- Five axes, banned words, page budget.
- **FINAL_CHECKLIST.md** -- Acceptance checklist.
- **claims_satcps.yaml** -- C1--C4 evidence pointers.
- **DRAFT_SaT-CPS.md** -- Narrative draft.
- Portfolio: **../P6_RESULTS_REPORT.md**, **../DRAFT.md**, **docs/RESULTS_PER_PAPER.md** (P6).
