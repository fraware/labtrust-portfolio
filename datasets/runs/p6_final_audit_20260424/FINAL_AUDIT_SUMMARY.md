# P6 final engineering audit (2026-04-24)

## 1. Executive verdict

Canonical camera-ready JSON recomputation and integrity checks are recorded in `reproducibility_check.json`.

## 2. Reproducibility status

- all required files present: `True`
- summary matches raw recompute: `True`

## 3. GPT-5.x failure audit

See `gpt5_failure_audit.json` / `.csv`. If run directories are missing, each model audit includes a `status` explaining the gap.

## 4. Parser/harness stress-test findings

- summary: `{"parser_handles_markdown_fences": true, "parser_handles_leading_trailing_prose": true, "parser_handles_json_arrays": true, "parser_handles_stringified_args": true, "parser_failure_likely_affects_gpt5_results": false}`

## 5. Baseline and task-critical consistency

See `baseline_consistency_check.json` and `task_critical_consistency_check.json`.

## 6. Replay and trace/audit findings

See `validator_replay_full.json` and `trace_audit_field_inventory.json`.

## 7. Paper claim checklist

See `paper_claims_checklist.md`.

## 8. Recommended final wording changes

- primary axis for interpreting supplementary GPT-5.x scoring drift: `harness_aggregate_pass_labeling_and_or_api_transport`

## 9. Remaining limitations

- `gpt-5.4-pro` run JSON often omits per-run `run_details` except for a small subset of cases; where absent, this audit expands aggregate `pass_count` using an explicit deterministic convention (`synthetic_pass_bit_ordering` in `gpt5_failure_audit.*`).
- `replay_denials.json` is a frozen summary (60/60 in the camera-ready bundle); the repo checkout also contains additional traces such that a full `trace.json` scan replays more denied steps (see `reproducibility_check.json`).
- Structured-output rerun was not executed here (see `structured_comparison`).

## 10. Sign-off

ENGINEERING SIGN-OFF: READY FOR PAPER SUBMISSION
