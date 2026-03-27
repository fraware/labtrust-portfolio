# Table 1 — Corpus and fidelity

All corpus traces (from summary.json); N = 11. Regenerate with export_replay_corpus_table.py.

| Trace | expected_replay_ok | expected_divergence_at_seq | observed_replay_ok | observed_divergence_at_seq |
|-------|--------------------|----------------------------|---------------------|----------------------------|
| thin_slice | — | — | true | — |
| benign_perturbation_pass | true | — | true | — |
| field_style_pass | true | — | true | — |
| field_style_pass_variant_b | true | — | true | — |
| hash_mismatch_trap | false | 1 | false | 1 |
| long_horizon_trap | false | 20 | false | 20 |
| mixed_failure_trap | false | 2 | false | 2 |
| nondeterminism_trap | false | 0 | false | 0 |
| real_bucket_example | true | — | true | — |
| reorder_trap | false | 1 | false | 1 |
| timestamp_reorder_trap | false | 1 | false | 1 |

# Table 1b — Localization and corpus space (per trace)

Per-trace divergence detection, localization vs expected (when declared), ambiguous multi-diagnostic flag (reserved), root-cause category, and on-disk trace size / hash-field count / approximate diagnostic JSON size.

| Trace | corpus_category | divergence_detected | localization_matches_expected | localization_ambiguous | root_cause_category | trace_json_bytes | state_hash_after_count | diagnostic_payload_bytes_approx |
|-------|-----------------|---------------------|-------------------------------|-------------------------|----------------------|------------------|-------------------------|--------------------------------|
| thin_slice | synthetic_pass | false | true | false | — | 3388 | 12 | — |
| benign_perturbation_pass | synthetic_pass | false | true | false | — | 1901 | 5 | — |
| field_style_pass | field_proxy | false | true | false | — | 4932 | 12 | — |
| field_style_pass_variant_b | field_proxy | false | true | false | — | 2408 | 6 | — |
| hash_mismatch_trap | synthetic_trap | true | true | false | tool_io | 1061 | 3 | 850 |
| long_horizon_trap | synthetic_trap | true | true | false | tool_io | 7233 | 21 | 869 |
| mixed_failure_trap | synthetic_trap | true | true | false | tool_io | 2263 | 6 | 1285 |
| nondeterminism_trap | synthetic_trap | true | true | false | tool_io | 519 | 1 | 452 |
| real_bucket_example | real_ingest | false | true | false | — | 1319 | 3 | — |
| reorder_trap | synthetic_trap | true | true | false | tool_io | 784 | 2 | 651 |
| timestamp_reorder_trap | synthetic_trap | true | true | false | tool_io | 804 | 2 | 651 |

## Corpus space summary (aggregate, corpus rows only)

- corpus_traces_n: 10
- trace_json_bytes_sum: 23224
- trace_json_bytes_mean: 2322.4
- state_hash_after_count_sum: 61
- state_hash_after_count_mean: 6.1
- diagnostic_payload_bytes_approx_sum: 4758
- diagnostic_payload_bytes_approx_mean: 793

## L1 twin summary (multi-seed aggregate)

- n_seeds: 5
- all_pass: true
- n_pass: 5
- mean_time_ms: 1.7425
- stdev_time_ms: 0.8187
- min_time_ms: 1.0233
- max_time_ms: 3.0904
