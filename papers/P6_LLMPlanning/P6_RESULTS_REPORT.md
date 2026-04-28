# P6 Evaluation Results Report

This report summarizes P6 artifacts by evidence tier and keeps denominators separated.

## Authoritative artifact sets

- **Primary (camera-ready/Table 1b):** `datasets/runs/llm_eval_camera_ready_20260424/`
- **Extended robust package (supplementary):** `datasets/runs/llm_eval_paper_bundle_final/`
- **Freeze hygiene audit:** `datasets/runs/p6_final_audit_20260424/`

Use camera-ready artifacts for the main Table 1b row unless manuscript text explicitly introduces the robust supplementary run with its own denominator.

## 1) Synthetic suites

- Red-team: **15/15** pass (`all_block_unsafe_pass=true`)
- Confusable deputy: **6/6** pass
- Jailbreak-style: **4/4** pass

Validator stack in current run: `allow_list + safe_args + ponr_gate (+ privilege heuristic)`.

## 2) Real-LLM (Table 1b, OpenAI canonical)

Command used:

```bash
python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval_camera_ready_20260424 \
  --real-llm --real-llm-provider auto \
  --real-llm-models gpt-4.1-mini,gpt-4.1 \
  --real-llm-runs 3 --real-llm-suite full
python scripts/export_llm_redteam_table.py --out-dir datasets/runs/llm_eval_camera_ready_20260424
```

Suite size in this mode: **25 cases/model** (15 red-team + 6 confusable + 4 jailbreak).  
Runs per case: **3**.  
Total trials per model: **75**.

| Model | n_pass / n_runs | pass_rate_pct | pass_rate_ci95 (Wilson) | total_latency_ms |
|-------|------------------|---------------|---------------------------|------------------|
| gpt-4.1-mini | 75 / 75 | 100.0 | [95.1, 100.0] | 374704.77 |
| gpt-4.1 | 75 / 75 | 100.0 | [95.1, 100.0] | 319280.22 |

## 3) Adapter latency and denial statistics

From `adapter_latency.json` and `denial_trace_stats.json`:

- scenarios: `toy_lab_v0`, `lab_profile_v0`, `warehouse_v0`
- seeds per scenario: 20
- total runs: 60
- `tail_latency_p95_mean_ms`: **36.70**
- `tail_latency_p95_stdev_ms`: **22.07**
- 95% CI(mean): **[31.12, 42.29]**
- runs_with_denial: **60/60** (denial-injection plan)

## 4) Baselines

Tool-level baseline (`baseline_comparison.json`):

- denials (gated / weak / ungated): **60 / 60 / 0**
- tasks_completed_mean: **3.95 / 3.95 / 3.95**

Argument-level baseline (`baseline_comparison_args.json`):

- denials (gated / weak / ungated): **60 / 0 / 0**
- tasks_completed_mean: **3.95 / 3.95 / 3.95**

Benign suite (`baseline_benign.json`) is available for false-positive reporting.

Task-critical extension (`task_critical_injection.json`):

- replacement (gated): runs 20, denials 20, unsafe_executions 0, tasks_completed_mean 3.95, fallback_exists false
- competition (gated): runs 20, denials 20, unsafe_executions 0, tasks_completed_mean 3.95, fallback_exists true
- args_unsafe (gated): runs 20, denials 20, unsafe_executions 0, tasks_completed_mean 4.95, fallback_exists false
- replacement (ungated reference): runs 20, denials 0, unsafe_executions 20, tasks_completed_mean 3.95, fallback_exists false

## 5) Optional Prime matrix (historical)

Prime results (N=3, separate output directory) remain useful as supplementary cross-provider evidence, but must be labeled with a separate denominator and not mixed with the OpenAI camera-ready table row.

## 6) Supplementary GPT-5.x isolated runs (post-patch, OpenAI)

These runs are intentionally isolated from the canonical camera-ready row and are
for compatibility/behavior characterization only.

| Run directory | Model | n_pass / n_runs | pass_rate_pct | pass_rate_ci95 (Wilson) | Notes |
|---|---|---:|---:|---|---|
| `datasets/runs/llm_eval_openai_gpt54_postpatch_20260424` | `gpt-5.4` | 73 / 75 | 97.3 | [90.8, 99.3] | Full suite, n=3/case, post parser/client patch |
| `datasets/runs/llm_eval_openai_gpt54pro_postpatch2_n3_20260424` | `gpt-5.4-pro` | 54 / 75 | 72.0 | [61.0, 80.9] | Full suite, n=3/case, temperature-retry + timeout patch |

## 6b) Supplementary robust package (verified)

`datasets/runs/llm_eval_paper_bundle_final/` is machine-verified with:

```bash
python scripts/verify_p6_robust_gpt_bundle.py \
  --run-dir datasets/runs/llm_eval_paper_bundle_final \
  --schema full --require-paper-ready \
  --red-team-results datasets/runs/llm_eval_paper_bundle_final/red_team_results.json
```

This bundle is sourced from `datasets/runs/llm_eval_robust_gpt_20260425_two_models_scratch/red_team_results.json` (see `MANIFEST.json` in the bundle). Keep it labeled as supplementary because model set and denominator differ from canonical Table 1b.

## 7) Regeneration checklist

```bash
python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval_camera_ready_20260424 --run-adapter --denial-stats --latency-decomposition --adapter-scenarios toy_lab_v0,lab_profile_v0,warehouse_v0 --adapter-seeds 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20
python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval_camera_ready_20260424 --run-baseline --baseline-scenarios toy_lab_v0,lab_profile_v0,warehouse_v0 --baseline-seeds 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20
python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval_camera_ready_20260424 --run-baseline --baseline-plan args_unsafe --baseline-scenarios toy_lab_v0,lab_profile_v0,warehouse_v0 --baseline-seeds 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20
python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval_camera_ready_20260424 --run-baseline --baseline-plan benign --baseline-scenarios toy_lab_v0,lab_profile_v0,warehouse_v0 --baseline-seeds 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20
python scripts/export_llm_redteam_table.py --out-dir datasets/runs/llm_eval_camera_ready_20260424 --out papers/P6_LLMPlanning/exported_tables.md
python scripts/export_p6_baseline_table.py --out-dir datasets/runs/llm_eval_camera_ready_20260424
python scripts/run_p6_task_critical_injection.py --out-dir datasets/runs/llm_eval_camera_ready_20260424
python scripts/export_p6_artifact_hashes.py --out-dir datasets/runs/llm_eval_camera_ready_20260424 --markdown
python scripts/export_p6_reproducibility_table.py
python scripts/export_p6_final_audit_bundle.py --out-dir datasets/runs/p6_final_audit_20260424
```

## 8) Final engineering audit bundle

After the canonical run directory and any supplementary GPT-5.x directories exist under `datasets/runs/`, materialize the committed freeze at `datasets/runs/p6_final_audit_20260424/`:

```bash
python scripts/export_p6_final_audit_bundle.py --out-dir datasets/runs/p6_final_audit_20260424
```

That bundle includes `FINAL_AUDIT_SUMMARY.md`, `reproducibility_check.json` (frozen `replay_denials.json` counts vs a fresh recursive `trace.json` denied-step scan), `gpt5_failure_audit.*`, `paper_claims_checklist.md`, and related machine-readable rollups. **Paper prose:** cite **60/60** replay verification only as the frozen `replay_denials.json` summary; do not imply no additional denied-step records exist elsewhere in committed traces without reading the audit diff object.
