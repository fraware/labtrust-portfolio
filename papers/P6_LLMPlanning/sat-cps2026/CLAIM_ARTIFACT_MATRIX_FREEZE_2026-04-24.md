# P6 Pre-Submit Integrity Matrix (2026-04-24)

This matrix consolidates the active P6 claim sources and verifies referenced
artifact paths against the current repository state.

## Sources audited

- `papers/P6_LLMPlanning/claims.yaml`
- `papers/P6_LLMPlanning/sat-cps2026/claims_satcps.yaml`
- `papers/P6_LLMPlanning/sat-cps2026/FINAL_CHECKLIST.md`
- `papers/P6_LLMPlanning/sat-cps2026/ENGINEERING_TRUTH_PACKAGE_2026-04-24.md`

## Consolidated claim-to-artifact matrix

| Claim set | Claim ID | Artifact path | Exists | Notes |
|---|---|---|---|---|
| `claims.yaml` | C1 | `datasets/runs/llm_eval_camera_ready_20260424/red_team_results.json` | yes | Canonical camera-ready Table 1b companion path. |
| `claims.yaml` | C1 | `kernel/llm_runtime/TYPED_PLAN.v0.1.schema.json` | yes | Schema artifact present. |
| `claims.yaml` | C1/C2 | `impl/src/labtrust_portfolio/llm_planning.py` | yes | Validator implementation present. |
| `claims.yaml` | C2 | `datasets/runs/llm_eval_camera_ready_20260424/adapter_latency.json` | yes | Adapter latency artifact present. |
| `claims.yaml` | C2/C4 | `datasets/runs/llm_eval/denial_trace_stats.json` | yes | Denial stats artifact present. |
| `claims.yaml` | C3 | `datasets/runs/llm_eval_camera_ready_20260424/confusable_deputy_results.json` | yes | Canonical camera-ready suite artifact present. |
| `claims.yaml` | C3 | `datasets/runs/llm_eval/p6_adaptive_results.json` | yes | Adaptive suite artifact present. |
| `claims.yaml` | C3 | `docs/P6_OWASP_MAPPING.md` | yes | OWASP mapping doc present. |
| `claims.yaml` | C3 | `datasets/p6_benign_suite.json` | yes | Benign corpus present. |
| `claims.yaml` | C3 | `datasets/p6_adaptive_suite.json` | yes | Adaptive corpus present. |
| `claims.yaml` | C4 | `datasets/runs/llm_eval/e2e_denial_trace.json` | yes | E2E denial artifact present. |
| `claims.yaml` | C4 | `datasets/runs/llm_eval_camera_ready_20260424/baseline_comparison.json` | yes | Tool-level baseline artifact present. |
| `claims.yaml` | C4 | `datasets/runs/llm_eval_camera_ready_20260424/baseline_comparison_args.json` | yes | Arg-level baseline artifact present. |
| `claims.yaml` | C4 | `datasets/runs/llm_eval/baseline_benign.json` | yes | Benign baseline artifact present. |
| `claims_satcps.yaml` | C1 | `datasets/runs/llm_eval_camera_ready_20260424/red_team_results.json` | yes | Canonical venue claim source path exists. |
| `claims_satcps.yaml` | C1 | `datasets/runs/llm_eval_camera_ready_20260424/confusable_deputy_results.json` | yes | Canonical venue claim source path exists. |
| `claims_satcps.yaml` | C3 | `docs/P6_OWASP_MAPPING.md` | yes | Mapping source exists. |
| `claims_satcps.yaml` | C4 | `scripts/export_p6_denial_trace_case_study.py` | yes | Export script exists. |
| `claims_satcps.yaml` | C4 | `datasets/runs/llm_eval/p6_artifact_hashes.json` | yes | Hash mapping artifact exists. |

## Camera-ready run checks

| Camera-ready artifact | Exists | Notes |
|---|---|---|
| `datasets/runs/llm_eval_camera_ready_20260424/red_team_results.json` | yes | Canonical Table 1b run in venue docs. |
| `datasets/runs/llm_eval_camera_ready_20260424/confusable_deputy_results.json` | yes | Canonical suite companion artifact. |
| `datasets/runs/llm_eval_camera_ready_20260424/MANIFEST.json` | yes | Canonical manifest present. |

## Mismatches flagged before freeze

No blocking path mismatches remain after harmonization:

- Claim YAMLs now point camera-ready Table 1b evidence to
  `datasets/runs/llm_eval_camera_ready_20260424` where appropriate.
- `FINAL_CHECKLIST.md` now references the cited canonical run directory wording
  (with explicit allowance for clearly labeled alternate dirs).

## Freeze recommendation

- Keep `llm_eval_camera_ready_20260424` as canonical for Table 1b in paper text.
- Keep all canonical citation rows mapped to `llm_eval_camera_ready_20260424`
  unless explicitly labeled as supplementary or historical.
- Keep GPT-5.x post-patch runs (`llm_eval_openai_gpt54_postpatch_20260424`,
  `llm_eval_openai_gpt54pro_postpatch2_n3_20260424`) clearly labeled as
  supplementary and denominator-separated.
