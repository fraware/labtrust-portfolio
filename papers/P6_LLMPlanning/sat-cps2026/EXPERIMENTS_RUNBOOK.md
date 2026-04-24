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

Canonical freeze commands below target `datasets/runs/llm_eval_camera_ready_20260424`.
For local scratch reruns, replace `--out` with `datasets/runs/llm_eval` (gitignored by default).

### 4.1 Synthetic red-team, confusable deputy, E2E trace

```bash
python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval_camera_ready_20260424
```

Writes `red_team_results.json`, `confusable_deputy_results.json`, `e2e_denial_trace.json`.

### 4.2 Adapter latency, denial stats, latency decomposition

```bash
python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval_camera_ready_20260424 --run-adapter --denial-stats --latency-decomposition \
  --adapter-scenarios toy_lab_v0,lab_profile_v0,warehouse_v0 \
  --adapter-seeds 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20
```

Writes `adapter_latency.json` (with `denial_stats`, optional `latency_decomposition`), `denial_trace_stats.json`.

### 4.3 Baselines: tool-level, argument-level, benign

```bash
python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval_camera_ready_20260424 --run-baseline \
  --baseline-scenarios toy_lab_v0,lab_profile_v0,warehouse_v0 \
  --baseline-seeds 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20

python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval_camera_ready_20260424 --run-baseline --baseline-plan args_unsafe \
  --baseline-scenarios toy_lab_v0,lab_profile_v0,warehouse_v0 \
  --baseline-seeds 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20

python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval_camera_ready_20260424 --run-baseline --baseline-plan benign \
  --baseline-scenarios toy_lab_v0,lab_profile_v0,warehouse_v0 \
  --baseline-seeds 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20
```

Writes `baseline_comparison.json`, `baseline_comparison_args.json`, `baseline_benign.json`.

### 4.4 One-shot alternative

```bash
python scripts/run_paper_experiments.py --paper P6
```

Runs the paper-default bundle (no real-LLM). Use `--quick` for fewer seeds.

## 5. Real-LLM -- OpenAI (canonical Table 1b, camera-ready)

Requires `OPENAI_API_KEY` in `.env`.

```bash
python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval_camera_ready_20260424 \
  --real-llm --real-llm-models gpt-4.1-mini,gpt-4.1 --real-llm-runs 3 --real-llm-suite full
python scripts/export_llm_redteam_table.py --out-dir datasets/runs/llm_eval_camera_ready_20260424
```

**Camera-ready defaults:** `--out datasets/runs/llm_eval_camera_ready_20260424`, `--real-llm-runs 3`, `--real-llm-suite full` (red-team + confusable deputy + jailbreak-style in the same API loop as Table 1b). Use `--real-llm-suite core` to match older red+confusable-only denominators. Structure of `real_llm` vs `real_llm_models[]` follows `llm_redteam_eval.py`; `run_manifest.suite_mode` and `real_llm_case_count` record the mix.

**OpenAI GPT-5.x (supplementary, separate `--out`):** `llm_redteam_eval.py` uses the Responses API for `gpt-5*` with `chat.completions` fallback, retries without `temperature` if the API rejects that parameter, and uses bounded HTTP timeouts. Example isolated dirs from 2026-04-24: `datasets/runs/llm_eval_openai_gpt54_postpatch_20260424`, `datasets/runs/llm_eval_openai_gpt54pro_postpatch2_n3_20260424`. Do not merge with camera-ready Table 1b without relabeling. See `papers/P6_LLMPlanning/sat-cps2026/ENGINEERING_TRUTH_PACKAGE_2026-04-24.md`.

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
python scripts/export_llm_redteam_table.py --out-dir datasets/runs/llm_eval_camera_ready_20260424
python scripts/export_p6_baseline_table.py --out-dir datasets/runs/llm_eval_camera_ready_20260424
python scripts/export_p6_baseline_table.py --out-dir datasets/runs/llm_eval_camera_ready_20260424 --baseline-file baseline_comparison_args.json
python scripts/export_p6_baseline_table.py --out-dir datasets/runs/llm_eval_camera_ready_20260424 --baseline-file baseline_benign.json
python scripts/export_p6_firewall_flow.py
python scripts/plot_llm_adapter_latency.py --latency datasets/runs/llm_eval_camera_ready_20260424/adapter_latency.json
python scripts/export_p6_denial_trace_case_study.py --trace <local_trace_path_from_adapter_run>
python scripts/export_p6_artifact_hashes.py --out-dir datasets/runs/llm_eval_camera_ready_20260424 --markdown
python scripts/export_p6_reproducibility_table.py
python scripts/run_p6_task_critical_injection.py --out-dir datasets/runs/llm_eval_camera_ready_20260424
python scripts/export_p6_layer_attribution.py
python scripts/export_p6_failure_analysis.py
python scripts/export_p6_cross_model_heatmap.py
python scripts/export_p6_latency_decomposition.py
python scripts/verify_p6_camera_ready_bundle.py
```

Optional: `--out papers/P6_LLMPlanning/exported_tables.md` on `export_llm_redteam_table.py`.

## 8. Artifact inventory (`datasets/runs/llm_eval_camera_ready_20260424/`)

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
| `task_critical_injection.json` | `run_p6_task_critical_injection.py` (default 20 seeds; includes `fallback_exists`) |
| `P6_CAMERA_READY_SUMMARY.json` | Canonical freeze summary (paper-facing numbers) |
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

## 9. Final engineering audit bundle (submission freeze)

When the canonical camera-ready directory is stable and any supplementary GPT-5.x run directories exist under `datasets/runs/`, materialize the paper-facing **evidence freeze** (recompute summary numbers from raw JSON, SHA256 the cited artifacts, GPT-5.x per-case/per-run forensics, parser stress suite, extended validator replay notes, baseline and task-critical consistency, trace-field inventory, and a paper-claims checklist):

```bash
python scripts/export_p6_final_audit_bundle.py --out-dir datasets/runs/p6_final_audit_20260424
```

The committed bundle is tracked at `datasets/runs/p6_final_audit_20260424/` (same `.gitignore` “explicit allow-list” pattern as `llm_eval_camera_ready_20260424/`). Start from `datasets/runs/p6_final_audit_20260424/README.md` and `FINAL_AUDIT_SUMMARY.md`.

**Replay semantics (important for prose):** `replay_denials.json` under `llm_eval_camera_ready_20260424/` is a **frozen summary artifact** (the camera-ready paper cites **60/60** matches for that snapshot). A full recursive scan of all `trace.json` files under the same run directory can enumerate **additional** `metadata.denied_steps` records when more traces are present than were summarized into `replay_denials.json`. The audit bundle’s `reproducibility_check.json` records both the frozen snapshot and a fresh trace scan (`replay_fresh_trace_scan`) plus `replay_frozen_vs_trace_scan` so reviewers can see the distinction without silently “moving the goalposts.”

**Typed-step JSON parsing (harness correctness):** `_parse_step_from_response` is implemented once in `impl/src/labtrust_portfolio/llm_planning.py` and imported by `scripts/llm_redteam_eval.py` so the eval harness and audit tooling cannot drift on “what counts as a parsed step.”

## 10. Research questions and statistics

- **Q1:** Synthetic separation of safe vs unsafe (Block A).
- **Q2:** Persistence under real LLM outputs (Block B).
- **Q3:** Bounded overhead and replayable denials (Block C).
- **Q4:** Tool vs argument layer contribution (Block D + layer attribution).
- **Q5:** Benign tasks not over-denied (benign baseline).

Pass rates: **95% Wilson score interval**. Latency: mean, stdev, CI for mean where applicable.

## 11. Related documents

- **README.md** (this folder) -- Evidence tiers and quick reference.
- **SUBMISSION_STANDARD.md** -- Five axes, banned words, page budget.
- **FINAL_CHECKLIST.md** -- Acceptance checklist.
- **claims_satcps.yaml** -- C1--C4 evidence pointers.
- **DRAFT_SaT-CPS.md** -- Narrative draft.
- Portfolio: **../P6_RESULTS_REPORT.md**, **../DRAFT.md**, **docs/RESULTS_PER_PAPER.md** (P6).
