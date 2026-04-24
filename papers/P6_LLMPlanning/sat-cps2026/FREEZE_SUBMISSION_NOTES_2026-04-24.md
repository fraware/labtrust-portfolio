# P6 Freeze Submission Notes (2026-04-24)

Use this note as the final integrity snapshot for camera-ready text and
artifact citation.

## Canonical run for Table 1b

- Canonical directory: `datasets/runs/llm_eval_camera_ready_20260424`
- Canonical models: `gpt-4.1-mini`, `gpt-4.1`
- Suite mode: `full` (15 red-team + 6 confusable deputy + 4 jailbreak-style)
- Runs per case: `3`
- Denominator per model: `75`
- Canonical aggregate:
  - `gpt-4.1-mini`: 75/75, 100.0%, Wilson [95.1, 100.0]
  - `gpt-4.1`: 75/75, 100.0%, Wilson [95.1, 100.0]

## Canonical evidence files

- `datasets/runs/llm_eval_camera_ready_20260424/red_team_results.json`
- `datasets/runs/llm_eval_camera_ready_20260424/confusable_deputy_results.json`
- `datasets/runs/llm_eval_camera_ready_20260424/MANIFEST.json`

## Baseline/adapter evidence files

Camera-ready baseline/adapter artifacts are now committed in the canonical run:

- `datasets/runs/llm_eval_camera_ready_20260424/adapter_latency.json`
- `datasets/runs/llm_eval_camera_ready_20260424/denial_trace_stats.json`
- `datasets/runs/llm_eval_camera_ready_20260424/baseline_comparison.json`
- `datasets/runs/llm_eval_camera_ready_20260424/baseline_comparison_args.json`
- `datasets/runs/llm_eval_camera_ready_20260424/baseline_benign.json`
- `datasets/runs/llm_eval_camera_ready_20260424/e2e_denial_trace.json`
- `datasets/runs/llm_eval_camera_ready_20260424/replay_denials.json`
- `datasets/runs/llm_eval_camera_ready_20260424/p6_artifact_hashes.json`

## Supplementary isolated GPT-5.x runs (do not merge denominators)

- `datasets/runs/llm_eval_openai_gpt54_postpatch_20260424`
  - model: `gpt-5.4`
  - full suite, n=3/case
  - 73/75, 97.3%, Wilson [90.8, 99.3]
- `datasets/runs/llm_eval_openai_gpt54pro_postpatch2_n3_20260424`
  - model: `gpt-5.4-pro`
  - full suite, n=3/case
  - 54/75, 72.0%, Wilson [61.0, 80.9]

## Non-merge rule (required wording discipline)

- Do not mix canonical Table 1b rows with Prime or GPT-5.x supplementary rows
  unless the table explicitly relabels run directory, models, suite mode, and
  denominator.

## Final consistency status

- Claims and checklist wording are aligned with canonical camera-ready paths.
- Baseline/adapter references in claim YAMLs now point to camera-ready artifacts.
- Machine gate: `python scripts/verify_p6_camera_ready_bundle.py` (also runs in CI on every push/PR).
- Claim gate: `python scripts/verify_p6_claims_consistency.py` (also runs in CI on every push/PR).
