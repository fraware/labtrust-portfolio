# Generated tables for P1 (P1_Contracts)

**How to read:** Table 1 lists each corpus sequence with detection_ok (verdicts match expected) and denials; Table 2 compares policies (contract, timestamp-only, ownership-only, accept-all). Units: time_per_write in microseconds (eval.json). **Full corpus:** 25 sequences (positive controls, split-brain, stale write/reorder, boundary cases). See [BENCHMARK_SPEC.v0.1.md](../../bench/contracts/BENCHMARK_SPEC.v0.1.md).

## Source and regeneration

- **Table 1 — Corpus evaluation.** Per-sequence verdict (detection_ok) and denials; run_manifest in eval.json (corpus_sequences, corpus_dir, corpus_sequence_count). Regenerate: run `contracts_eval.py` then `export_contracts_corpus_table.py` (reads datasets/runs/contracts_eval/eval.json). Full list of 25 sequences is in eval.json.
- **Table 2 — Policy comparison.** Violations denied vs missed for full contract, timestamp-only (monotonicity only), ownership-only (no temporal), and accept-all. Run `contracts_eval.py --baseline` to populate. Source: eval.json (violations_denied_with_validator, baseline_timestamp_only_denials, baseline_timestamp_only_missed, baseline_ownership_only_denials, baseline_accept_all_denials).
- **Additional eval output:** detection_metrics (true_positives, false_positives, false_negatives, precision, recall), latency_percentiles_us (median, p95, p99), ablation (full_contract, timestamp_only, ownership_only, accept_all with violations_denied and violations_missed).

## Example Table 1 (subset)

| Sequence           | detection_ok | denials (contract) |
|--------------------|--------------|-------------------|
| good_sequence      | yes          | 0                 |
| split_brain_sequence | yes       | 1                 |
| stale_write_sequence | yes       | 1                 |
| reorder_sequence   | yes          | 1                 |
| unsafe_lww_sequence | yes        | 1                 |
| ... (25 total)     | ...          | ...               |

## Example Table 2

| Policy                            | Violations denied | Violations missed (would apply) |
|-----------------------------------|-------------------|----------------------------------|
| Contract (ownership + monotonicity) | 14                | 0                                |
| Timestamp-only (monotonicity only)  | 12                | 2 (split_brain)                  |
| Ownership-only (no temporal)       | 6                 | 8 (stale/reorder)                |
| Accept-all                        | 0                 | 14                               |

Run `contracts_eval.py --baseline` to regenerate; full tables are produced by the export script and the draft cites Appendix A for run manifest.
