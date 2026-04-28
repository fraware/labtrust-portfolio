# Robust real-LLM evaluation package (`llm_eval_paper_bundle_final`)

This directory is produced by ``scripts/p6_robust_gpt_full_package.py`` from a completed
``red_team_results.json`` (API-backed eval). It is **immutable** relative to prior
``llm_eval_robust_gpt_20260424`` historical evidence.

**Source input for this export:** ``datasets/runs/llm_eval_robust_gpt_20260425_two_models_scratch/red_team_results.json`` (also ``MANIFEST.json`` → ``canonical_reference``). A copy of that file is written to this directory as ``red_team_results.json`` for self-contained audit/verify.

## Reproduce

```bash
PYTHONPATH=impl/src python scripts/llm_redteam_eval.py \
  --out llm_eval_paper_bundle_final_scratch \
  --real-llm --real-llm-models gpt-4.1-mini,gpt-4.1,gpt-5.4,gpt-5.4-pro \
  --real-llm-runs 5 --real-llm-suite full \
  --store-real-llm-transcripts --store-api-metadata \
  --real-llm-prompt-variants canonical,strict_json,json_schema,adversarial_context,tool_return_injection,unsafe_paraphrase,benign_paraphrase \
  --real-llm-stress-json datasets/cases/p6_real_llm_stress_cases.json \
  --disable-cache --fail-on-missing-raw-output --fail-on-scoring-mismatch

python scripts/p6_robust_gpt_full_package.py \
  --from-red-team llm_eval_paper_bundle_final_scratch/red_team_results.json \
  --out-dir datasets/runs/llm_eval_paper_bundle_final

python scripts/audit_llm_results.py --run-dir datasets/runs/llm_eval_paper_bundle_final \
  --red-team-results datasets/runs/llm_eval_paper_bundle_final/red_team_results.json --json

python scripts/verify_p6_robust_gpt_bundle.py --run-dir datasets/runs/llm_eval_paper_bundle_final \
  --schema full --require-paper-ready \
  --red-team-results datasets/runs/llm_eval_paper_bundle_final/red_team_results.json
```

Copy ``red_team_results.json`` into this directory if the exporter should audit in-place.

**PowerShell:** use ``Copy-Item -Force <sweep>/red_team_results.json <this_dir>/`` (do not use ``copy /Y``, which fails in PowerShell).
