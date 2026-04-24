# Robust real-LLM evaluation package (`llm_eval_robust_gpt_20260424`)

## 1. Purpose

This directory packages **audits and metadata** so GPT-family real-LLM rows can be defended scientifically: independence of the frozen canonical 75/75 runs, parser labels on stored transcripts, negative controls for audit logic, and explicit gaps where the harness still needs API-backed reruns (prompt variants, N≥5 runs/case, stress suite execution).

## 2. Models evaluated (artifacts)

- **Tier A (canonical, frozen):** `gpt-4.1-mini`, `gpt-4.1` — source: `datasets/runs/llm_eval_camera_ready_20260424/red_team_results.json`.
- **Tier B (robust reruns):** `gpt-5.4`, `gpt-5.4-pro` — **not** produced in this commit; exploratory aggregates remain under `datasets/runs/llm_eval_openai_gpt54*_20260424/`.

## 3. Suites

- **canonical_25:** 15 red-team + 6 confusable deputy + 4 jailbreak-style (full suite).
- **real_llm_stress_35+:** case definitions in `datasets/cases/p6_real_llm_stress_cases.json` — **not executed** here; reported separately when run.

## 4. Prompt variants

Defined in spec: canonical, strict_json, json_schema, minimal_instruction, verbose_instruction, adversarial_context, tool_return_injection, benign_paraphrase, unsafe_paraphrase. Only **canonical** is populated from committed JSON; others require eval harness extension.

## 5. Run counts

- Canonical: 25 cases × 3 runs = **75** trials per Tier-A model.
- Target robust rerun: 25 × **5–10** runs per model × variants (not run in CI).

## 6. Manifest hashes

See `MANIFEST.json` and `canonical_independence_audit.json` (`same_case_set_sha256`, `prompt_template_hash`).

## 7. How to reproduce this bundle

```bash
python scripts/p6_robust_gpt_materialize.py
```

## 8. How to verify aggregate scores

Re-sum `expected_matched` from `parsed_outputs.jsonl` and compare to `n_pass_total` in canonical `red_team_results.json` per model. `statistical_summary.json` includes `scoring_consistency` rows.

## 9. Known limitations

- Canonical JSON does not include OpenAI `response.id` / request id fields (harness did not capture them at collection time). Independence is established via distinct per-model timestamps, distinct raw bodies where stored, and distinct latency series.
- Only **six** trials per model include `raw_response` in the committed canonical file (two argument-level cases × three runs). Other trials are aggregate-only in JSON.
- Prompt variants and stress suite execution are **out of scope** for this materializer (no API calls).

## 10. Paper eligibility

- Tier A rows: **eligible** as frozen controlled check (narrow claim).
- Tier B / variants / stress: **not eligible** until raw transcripts, parser labels, scoring equality, and inclusion criteria in `paper_table_recommended.csv` are satisfied.

## 11. Full robust rerun (future)

```bash
PYTHONPATH=impl/src python scripts/llm_redteam_eval.py \
  --out datasets/runs/llm_eval_robust_gpt_20260424_evalscratch \
  --real-llm --real-llm-models gpt-5.4,gpt-5.4-pro \
  --real-llm-runs 10 --real-llm-suite full \
  --store-real-llm-transcripts

python scripts/audit_llm_results.py \
  --run-dir datasets/runs/llm_eval_robust_gpt_20260424_evalscratch

python scripts/p6_robust_gpt_materialize.py --merge-audit DIR
```

(`--merge-audit` can be added when scratch reruns exist.)

Files that cannot yet be produced with full spec content: extra prompt-variant aggregates, executed `stress_results.json` beyond case counts, and Tier-B rows — reasons are above.
