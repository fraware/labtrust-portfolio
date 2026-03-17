# SaT-CPS 2026 P6 --  Experiments runbook



## Collect latest red-team state (minimal)



From repo root, with `PYTHONPATH=impl/src` and `LABTRUST_KERNEL_DIR=kernel` set:



1. **Refresh synthetic red-team (9 cases) and confusable deputy:**  

   `python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval`  

   Writes `red_team_results.json`, `confusable_deputy_results.json`, `e2e_denial_trace.json`.



2. **Export tables and figure:**  

   `python scripts/export_llm_redteam_table.py --out-dir datasets/runs/llm_eval`  

   Optionally write tables to a file: add `--out papers/P6_LLMPlanning/exported_tables.md`.  

   `python scripts/export_p6_firewall_flow.py`  

   Table output is printed to stdout (and to file if `--out` is set); figure written to `docs/figures/p6_firewall_flow.mmd`.



3. **Optional --  denial-trace case study** (needs a gated baseline trace with a denial):  

   `python scripts/export_p6_denial_trace_case_study.py --trace datasets/runs/llm_eval/baseline_runs/gated/toy_lab_v0/seed_1/trace.json`



Real-LLM (Table 1b) requires `.env` API keys; see "Real-LLM" section below.



## Collected results (no API keys required)



The following were run and artifacts written to `datasets/runs/llm_eval/`:



| Experiment | Command | Artifacts |

|------------|---------|-----------|

| Red-team (synthetic) | (always run) | red_team_results.json, confusable_deputy_results.json, e2e_denial_trace.json |

| Adapter latency + denial stats | `--run-adapter --denial-stats` | adapter_latency.json (with denial_stats), denial_trace_stats.json |

| Baseline (tool-level) | `--run-baseline` | baseline_comparison.json (plan_type: tool_unsafe; gated 60, weak 60, ungated 0) |

| Baseline (argument-level) | `--run-baseline --baseline-plan args_unsafe` | baseline_comparison_args.json (gated 60, weak 0, ungated 0) |



**Publishable configuration:** 3 scenarios (toy_lab_v0, lab_profile_v0, warehouse_v0), 20 seeds each (60 runs per baseline).



**One-shot (all non-LLM experiments):**

```bash

# From repo root; set PYTHONPATH=impl/src and LABTRUST_KERNEL_DIR=kernel

python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval --run-adapter --denial-stats --run-baseline --adapter-scenarios toy_lab_v0,lab_profile_v0,warehouse_v0 --adapter-seeds 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20

python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval --run-baseline --baseline-plan args_unsafe --baseline-scenarios toy_lab_v0,lab_profile_v0,warehouse_v0 --baseline-seeds 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20

```



**Exports:**

```bash

python scripts/export_llm_redteam_table.py --out-dir datasets/runs/llm_eval

# Optional: write tables to file

python scripts/export_llm_redteam_table.py --out-dir datasets/runs/llm_eval --out papers/P6_LLMPlanning/exported_tables.md

python scripts/export_p6_baseline_table.py --out-dir datasets/runs/llm_eval

python scripts/export_p6_baseline_table.py --out-dir datasets/runs/llm_eval --baseline-file baseline_comparison_args.json

python scripts/export_p6_firewall_flow.py

python scripts/export_p6_denial_trace_case_study.py --trace datasets/runs/llm_eval/baseline_runs/gated/toy_lab_v0/seed_1/trace.json

```



Alternatively: `python scripts/run_paper_experiments.py --paper P6` runs the above (without real-LLM); use `--quick` for fewer seeds.



## Real-LLM (Table 1b) --  run manually



Requires API keys in `.env`. Not run by automation.



**Multi-model (OpenAI):** Set `OPENAI_API_KEY` in `.env`.

```bash

python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval --real-llm --real-llm-models gpt-4.1-mini,gpt-4.1 --real-llm-runs 5

```



This writes `real_llm` (single model) or `real_llm_models` (multi-model) in red_team_results.json. Re-run export_llm_redteam_table.py after to refresh Table 1b (multi-model: one subsection per model + combined summary table).







**Latest run snapshot (5 runs/case, 13 cases/model; 2026-03-17):** gpt-4.1-mini 55/65 (84.6%, Wilson [73.9, 91.4]); gpt-4.1 55/65 (84.6%, [73.9, 91.4]).



## Summary of current artifacts



- **red_team_results.json:** Synthetic 9/9 pass; real-LLM results in `real_llm_models[]` (latest 2026-03-17: gpt-4.1-mini 84.6%, gpt-4.1 84.6%; 65 runs/model).

- **adapter_latency.json:** 60 runs, tail_latency_p95_mean_ms ~32 ms, denial_stats (60/60 denials), 3 scenarios x 20 seeds.

- **baseline_comparison.json:** 60 rows, plan_type tool_unsafe; gated 60, weak 60, ungated 0; tasks_completed_mean 3.95 (all modes).

- **baseline_comparison_args.json:** 60 rows, plan_type args_unsafe; gated 60, weak 0, ungated 0; tasks_completed_mean 3.95.

- **denial_trace_stats.json:** total_runs 60, runs_with_denial 60, per_scenario (runs, denials, tasks_completed_mean).

- **e2e_denial_trace.json:** Claim and blocked-step example.

- **Baseline trace metadata:** When run with the current adapter, gated/weak traces include `metadata.denied_steps` (step + reason) and `metadata.denial_reason` for the first denied step; used by export_p6_denial_trace_case_study.py.



## Related documents



- **SUBMISSION_STANDARD.md** --  Five axes, banned words, page budget.

- **claims_satcps.yaml** --  Four claims and evidence pointers.

- **DRAFT_SaT-CPS.md** --  Venue draft (title, abstract, intro, threat model, four blocks, failure case, baseline wording).







