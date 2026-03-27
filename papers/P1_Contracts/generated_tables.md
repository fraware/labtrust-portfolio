# Generated tables for P1 (P1_Contracts)

## From export_contracts_corpus_table.py

# Generated tables for P1 (P1_Contracts)

## From export_contracts_corpus_table.py

# Table 1 — Corpus evaluation. Per-sequence detection_ok and denials; run_manifest in eval.json.

| Sequence | detection_ok | denials (contract) |
|----------|---------------|-------------------|
| actor_payload_writer_mismatch | yes | 1 |
| burst_duplicate_three | yes | 0 |
| concurrent_controller_race | yes | 2 |
| conflicting_writes_independent_keys | yes | 0 |
| coordination_message_passthrough | yes | 0 |
| cross_key_interleaved_race | yes | 0 |
| delayed_release_reassignment | yes | 1 |
| duplicate_delivery | yes | 0 |
| edge_case_timestamps | yes | 0 |
| good_eight_events | yes | 0 |
| good_five_events | yes | 0 |
| good_four_events | yes | 0 |
| good_interleaved_6 | yes | 0 |
| good_sequence | yes | 0 |
| good_sequence_4events | yes | 0 |
| good_seven_events | yes | 0 |
| good_single_allow | yes | 0 |
| good_six_keys | yes | 0 |
| good_ten_events | yes | 0 |
| good_then_unknown_key | yes | 1 |
| good_three_events | yes | 0 |
| good_three_keys_cycle | yes | 0 |
| good_two_keys | yes | 0 |
| long_horizon_10 | yes | 0 |
| mixed_key_contention_8 | yes | 0 |
| multi_key_no_conflict | yes | 0 |
| multi_writer_contention | yes | 1 |
| reorder_burst_four | yes | 1 |
| reorder_first_deny | yes | 1 |
| reorder_first_event_deny | yes | 1 |
| reorder_mid_chain | yes | 1 |
| reorder_multi_key | yes | 1 |
| reorder_sequence | yes | 1 |
| reorder_three_events | yes | 1 |
| same_ts_same_writer | yes | 0 |
| split_brain_delayed_conflict | yes | 1 |
| split_brain_five_writers | yes | 4 |
| split_brain_four_writers | yes | 3 |
| split_brain_same_epoch | yes | 1 |
| split_brain_second_key | yes | 1 |
| split_brain_sequence | yes | 1 |
| split_brain_then_allow | yes | 1 |
| split_brain_three_writers | yes | 2 |
| split_brain_two_keys | yes | 1 |
| stale_then_allow | yes | 1 |
| stale_write_delayed_delivery | yes | 1 |
| stale_write_exact | yes | 0 |
| stale_write_margin | yes | 1 |
| stale_write_sequence | yes | 1 |
| stale_write_sequence_2 | yes | 1 |
| stale_write_sequence_3 | yes | 1 |
| stale_write_sequence_4 | yes | 1 |
| unknown_key_deny | yes | 1 |
| unsafe_lww_sequence | yes | 1 |

**Timestamp-only baseline:** denials with timestamp-only policy: 24. Violations the contract catches but timestamp-only would allow (missed): 13. (Baselines and ablation are populated by every `contracts_eval.py` run; use `--baseline` only for the extra `violations_would_apply_without_validator` field.)

## Ablation by failure class

| Class | Policy | Violations denied | Violations missed |
|-------|--------|--------------------|--------------------|
| control | full_contract | 3 | 0 |
| control | timestamp_only | 8 | -5 |
| control | ownership_only | 3 | 0 |
| control | occ_only | 8 | -5 |
| control | lease_only | 8 | -5 |
| control | lock_only | 3 | 0 |
| control | accept_all | 0 | 3 |
| control | naive_lww | 0 | 3 |
| reorder | full_contract | 8 | 0 |
| reorder | timestamp_only | 8 | 0 |
| reorder | ownership_only | 0 | 8 |
| reorder | occ_only | 8 | 0 |
| reorder | lease_only | 8 | 0 |
| reorder | lock_only | 0 | 8 |
| reorder | accept_all | 0 | 8 |
| reorder | naive_lww | 0 | 8 |
| split_brain | full_contract | 17 | 0 |
| split_brain | timestamp_only | 0 | 17 |
| split_brain | ownership_only | 17 | 0 |
| split_brain | occ_only | 0 | 17 |
| split_brain | lease_only | 0 | 17 |
| split_brain | lock_only | 17 | 0 |
| split_brain | accept_all | 0 | 17 |
| split_brain | naive_lww | 0 | 17 |
| stale_write | full_contract | 7 | 0 |
| stale_write | timestamp_only | 8 | -1 |
| stale_write | ownership_only | 0 | 7 |
| stale_write | occ_only | 8 | -1 |
| stale_write | lease_only | 8 | -1 |
| stale_write | lock_only | 0 | 7 |
| stale_write | accept_all | 0 | 7 |
| stale_write | naive_lww | 0 | 7 |
| unknown_key | full_contract | 2 | 0 |
| unknown_key | timestamp_only | 0 | 2 |
| unknown_key | ownership_only | 0 | 2 |
| unknown_key | occ_only | 0 | 2 |
| unknown_key | lease_only | 0 | 2 |
| unknown_key | lock_only | 0 | 2 |
| unknown_key | accept_all | 0 | 2 |
| unknown_key | naive_lww | 0 | 2 |

## Table 3 — Detection metrics by inferred failure class

| Class | TP | FP | FN | Precision | Recall | F1 |
|-------|----|----|----|-----------|--------|-----|
| control | 3 | 0 | 0 | 1.0 | 1.0 | 1.0 |
| reorder | 8 | 0 | 0 | 1.0 | 1.0 | 1.0 |
| split_brain | 17 | 0 | 0 | 1.0 | 1.0 | 1.0 |
| stale_write | 7 | 0 | 0 | 1.0 | 1.0 | 1.0 |
| unknown_key | 2 | 0 | 0 | 1.0 | 1.0 | 1.0 |

**Comparator notes:** `occ_only` and `lease_only` use temporal monotonicity only in the reference benchmark (OCC/version proxy; lease proxy without explicit lease fields). `lock_only` is ownership-only (mutex-style). `naive_lww` accepts all writes. These are reference proxies for conceptual comparison; full OCC/lease/lock implementations would include additional semantics (read sets, lease windows, lock acquisition) not captured in the corpus event model.

## Stress robustness (async delay/skew/reorder)

| Stress profile | Sequences tested | Detection OK rate | Notes |
|----------------|------------------|-------------------|-------|
| delay=0.0, skew=0.0, reorder=0.0 | 54 | 100.0% | Async stress test |
| delay=0.0, skew=0.0, reorder=0.1 | 54 | 85.2% | Async stress test |
| delay=0.0, skew=0.0, reorder=0.2 | 54 | 87.0% | Async stress test |
| delay=0.0, skew=0.1, reorder=0.0 | 54 | 98.1% | Async stress test |
| delay=0.0, skew=0.1, reorder=0.1 | 54 | 87.0% | Async stress test |
| delay=0.0, skew=0.1, reorder=0.2 | 54 | 83.3% | Async stress test |
| delay=0.0, skew=0.5, reorder=0.0 | 54 | 98.1% | Async stress test |
| delay=0.0, skew=0.5, reorder=0.1 | 54 | 87.0% | Async stress test |
| delay=0.0, skew=0.5, reorder=0.2 | 54 | 83.3% | Async stress test |
| delay=0.001, skew=0.0, reorder=0.0 | 54 | 64.8% | Async stress test |
| delay=0.001, skew=0.0, reorder=0.1 | 54 | 63.0% | Async stress test |
| delay=0.001, skew=0.0, reorder=0.2 | 54 | 61.1% | Async stress test |
| delay=0.001, skew=0.1, reorder=0.0 | 54 | 61.1% | Async stress test |
| delay=0.001, skew=0.1, reorder=0.1 | 54 | 64.8% | Async stress test |
| delay=0.001, skew=0.1, reorder=0.2 | 54 | 61.1% | Async stress test |
| delay=0.001, skew=0.5, reorder=0.0 | 54 | 66.7% | Async stress test |
| delay=0.001, skew=0.5, reorder=0.1 | 54 | 64.8% | Async stress test |
| delay=0.001, skew=0.5, reorder=0.2 | 54 | 59.3% | Async stress test |
| delay=0.01, skew=0.0, reorder=0.0 | 54 | 63.0% | Async stress test |
| delay=0.01, skew=0.0, reorder=0.1 | 54 | 63.0% | Async stress test |
| delay=0.01, skew=0.0, reorder=0.2 | 54 | 64.8% | Async stress test |
| delay=0.01, skew=0.1, reorder=0.0 | 54 | 64.8% | Async stress test |
| delay=0.01, skew=0.1, reorder=0.1 | 54 | 61.1% | Async stress test |
| delay=0.01, skew=0.1, reorder=0.2 | 54 | 66.7% | Async stress test |
| delay=0.01, skew=0.5, reorder=0.0 | 54 | 59.3% | Async stress test |
| delay=0.01, skew=0.5, reorder=0.1 | 54 | 64.8% | Async stress test |
| delay=0.01, skew=0.5, reorder=0.2 | 54 | 64.8% | Async stress test |

## Transport parity (boundary semantics)

**Parity rate:** 100.0% (6/6 events match between event-log and LADS-shaped paths).
**All sequences parity:** OK.

**Detection metrics:** TP=37, FP=0, FN=0, precision=1.0, recall=1.0, F1=1.0.

## From export_p1_appendix_tex.py

Wrote C:\Users\mateo\labtrust-portfolio\papers\P1_Contracts\generated_appendix_corpus.tex

