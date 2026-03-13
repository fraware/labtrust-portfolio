# Generated tables for P1 (P1_Contracts)

**How to read:** Table 1 lists each corpus sequence with detection_ok (verdicts match expected) and denials; Table 2 compares policies (contract vs timestamp-only vs accept-all). Units: time_per_write in microseconds (eval.json).

## From export_contracts_corpus_table.py

**Table 1 — Corpus evaluation.** Per-sequence verdict (detection_ok) and denials; run_manifest in eval.json (corpus_sequences, corpus_dir).

| Sequence | detection_ok | denials (contract) |
|----------|---------------|-------------------|
| good_sequence | yes | 0 |
| reorder_sequence | yes | 1 |
| split_brain_sequence | yes | 1 |
| stale_write_sequence | yes | 1 |
| unsafe_lww_sequence | yes | 1 |

**Table 2 — Policy comparison.** Violations denied vs missed for contract, timestamp-only (monotonicity only), and accept-all. Run `contracts_eval.py --baseline` to populate. Source: eval.json (violations_denied_with_validator, baseline_timestamp_only_denials, baseline_timestamp_only_missed).

**Timestamp-only baseline:** denials with timestamp-only policy: 3. Violations the contract catches but timestamp-only would allow (missed): 1. Run contracts_eval.py with --baseline to populate.

