# P6 Evaluation Results Report

This report summarizes the current P6 artifacts under `datasets/runs/llm_eval/`.

## 1) Synthetic suites

- Red-team: **15/15** pass (`all_block_unsafe_pass=true`)
- Confusable deputy: **6/6** pass
- Jailbreak-style: **4/4** pass

Validator stack in current run: `allow_list + safe_args + ponr_gate (+ privilege heuristic)`.

## 2) Real-LLM (Table 1b, OpenAI canonical)

Command used:

```bash
python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval \
  --real-llm --real-llm-provider auto \
  --real-llm-models gpt-4.1-mini,gpt-4.1 \
  --real-llm-runs 10 --real-llm-suite full
python scripts/export_llm_redteam_table.py --out-dir datasets/runs/llm_eval
```

Suite size in this mode: **25 cases/model** (15 red-team + 6 confusable + 4 jailbreak).  
Runs per case: **10**.  
Total trials per model: **250**.

| Model | n_pass / n_runs | pass_rate_pct | pass_rate_ci95 (Wilson) | total_latency_ms |
|-------|------------------|---------------|---------------------------|------------------|
| gpt-4.1-mini | 250 / 250 | 100.0 | [98.5, 100.0] | 708031.4 |
| gpt-4.1 | 250 / 250 | 100.0 | [98.5, 100.0] | 620732.1 |

## 3) Adapter latency and denial statistics

From `adapter_latency.json` and `denial_trace_stats.json`:

- scenarios: `toy_lab_v0`, `lab_profile_v0`, `warehouse_v0`
- seeds per scenario: 20
- total runs: 60
- `tail_latency_p95_mean_ms`: **32.07**
- `tail_latency_p95_stdev_ms`: **18.45**
- 95% CI(mean): **[27.41, 36.74]**
- runs_with_denial: **60/60** (denial-injection plan)

## 4) Baselines

Tool-level baseline (`baseline_comparison.json`):

- denials (gated / weak / ungated): **60 / 60 / 0**
- tasks_completed_mean: **3.95 / 3.95 / 3.95**

Argument-level baseline (`baseline_comparison_args.json`):

- denials (gated / weak / ungated): **60 / 0 / 0**
- tasks_completed_mean: **3.95 / 3.95 / 3.95**

Benign suite (`baseline_benign.json`) is available for false-positive reporting.

## 5) Optional Prime matrix (historical)

Prime results (N=3, separate output directory) remain useful as supplementary cross-provider evidence, but must be labeled with a separate denominator and not mixed with the OpenAI N=10 table row.

## 6) Regeneration checklist

```bash
python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval --run-adapter --denial-stats --latency-decomposition --adapter-scenarios toy_lab_v0,lab_profile_v0,warehouse_v0 --adapter-seeds 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20
python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval --run-baseline --baseline-scenarios toy_lab_v0,lab_profile_v0,warehouse_v0 --baseline-seeds 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20
python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval --run-baseline --baseline-plan args_unsafe --baseline-scenarios toy_lab_v0,lab_profile_v0,warehouse_v0 --baseline-seeds 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20
python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval --run-baseline --baseline-plan benign --baseline-scenarios toy_lab_v0,lab_profile_v0,warehouse_v0 --baseline-seeds 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20
python scripts/export_llm_redteam_table.py --out-dir datasets/runs/llm_eval --out papers/P6_LLMPlanning/exported_tables.md
python scripts/export_p6_baseline_table.py --out-dir datasets/runs/llm_eval
python scripts/export_p6_artifact_hashes.py --out-dir datasets/runs/llm_eval --markdown
python scripts/export_p6_reproducibility_table.py
```
