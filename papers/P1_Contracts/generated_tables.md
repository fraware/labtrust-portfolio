# Generated tables for P1 (P1_Contracts)

**How to read:** Table 1 lists each corpus sequence with detection_ok (verdicts match expected) and denials; Table 2 compares policies (contract vs timestamp-only vs accept-all). Units: time_per_write in microseconds (eval.json). **Full corpus:** 7 sequences (good_sequence, reorder_sequence, split_brain_sequence, stale_write_sequence, unsafe_lww_sequence, multi_writer_contention, edge_case_timestamps). See [BENCHMARK_SPEC.v0.1.md](../../bench/contracts/BENCHMARK_SPEC.v0.1.md).

## From export_contracts_corpus_table.py

**Table 1 — Corpus evaluation.** Per-sequence verdict (detection_ok) and denials; run_manifest in eval.json (corpus_sequences, corpus_dir). Regenerate: `python scripts/export_contracts_corpus_table.py` (reads datasets/runs/contracts_eval/eval.json). Full list of 7 sequences in eval.json.

| Sequence | detection_ok | denials (contract) |
|----------|---------------|-------------------|
| good_sequence | yes | 0 |
| edge_case_timestamps | yes | 0 |
| multi_writer_contention | yes | 1 |
| reorder_sequence | yes | 1 |
| split_brain_sequence | yes | 1 |
| stale_write_sequence | yes | 1 |
| unsafe_lww_sequence | yes | 1 |

**Table 2 — Policy comparison.** Violations denied vs missed for contract, timestamp-only (monotonicity only), and accept-all. Run `contracts_eval.py --baseline` to populate. Source: eval.json (violations_denied_with_validator, baseline_timestamp_only_denials, baseline_timestamp_only_missed).

**Timestamp-only baseline:** denials with timestamp-only policy: 3. Violations the contract catches but timestamp-only would allow (missed): 1. Run contracts_eval.py with --baseline to populate.

