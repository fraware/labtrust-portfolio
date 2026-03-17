# Coordination Contract Benchmark v0.1

This document defines the **Coordination Contract Benchmark v0.1**: a reusable benchmark for evaluating contract validators that enforce typed state, ownership, and valid transitions above messaging.

## Version

- **Version:** v0.1
- **Corpus location:** `bench/contracts/corpus/` (relative to repo root)

## Sequences (N = 25)

The challenge corpus includes sequences partitioned by failure class, with positive and negative controls:

- **Positive controls (good_*):** good_sequence, good_two_keys, good_three_events, good_four_events, good_single_allow, good_sequence_4events, multi_key_no_conflict, conflicting_writes_independent_keys, duplicate_delivery, same_ts_same_writer, edge_case_timestamps.
- **Split-brain:** split_brain_sequence, split_brain_same_epoch, split_brain_second_key, split_brain_three_writers, multi_writer_contention.
- **Stale write / reorder:** stale_write_sequence, stale_write_sequence_2, stale_write_margin, reorder_sequence, reorder_first_deny, reorder_three_events, reorder_multi_key, unsafe_lww_sequence.
- **Boundary:** stale_write_exact (ts equals last_ts; validator uses strict > so allow).

Discovery: all `*.json` files in the corpus directory; see corpus location above.

## Schema

Each corpus file is JSON with:

- **description** (string): Short scenario description.
- **initial_state** (object): At least `ownership` (key → owner) and `_last_ts` (key → last accepted write time).
- **events** (array): Event objects with `type`, `ts`, `actor`, `payload`. Types include `task_start`, `task_end`, `coordination_message`. Payload must include key (e.g. `task_id`) and writer when relevant.
- **expected_verdicts** (array): One of `"allow"` or `"deny"` per event; length must equal `events.length`.

## Discovery rule

The reference runner discovers all `*.json` files in the corpus directory via `sorted(corpus_dir.glob("*.json"))`. Generated sequences (e.g. from `scripts/generate_contract_corpus.py`) may be added with the same schema.

## Reference runner and table

- **Runner:** `python scripts/contracts_eval.py --out datasets/runs/contracts_eval` (with default corpus dir `bench/contracts/corpus/`).
- **Table:** `python scripts/export_contracts_corpus_table.py` (reads eval.json, prints corpus table for the draft).

## Success criterion

A validator satisfies the benchmark if for every sequence, the validator's verdict per event matches `expected_verdicts[i]` (detection_ok true for all sequences).
