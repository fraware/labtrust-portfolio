# Coordination Contract Benchmark v0.1

This document defines the **Coordination Contract Benchmark v0.1**: a reusable benchmark for evaluating contract validators that enforce typed state, ownership, and valid transitions above messaging.

## Version

- **Version:** v0.1
- **Corpus location:** `bench/contracts/corpus/` (relative to repo root)

## Sequences (N = 7)

| Sequence file | Failure class | Description |
|---------------|---------------|-------------|
| good_sequence | — | Single writer, monotonic timestamps; all events allowed. |
| split_brain_sequence | split_brain | Second writer for same key denied (ownership). |
| stale_write_sequence | stale_write | Event timestamp before last_ts for key; deny. |
| reorder_sequence | reorder_violation | Second event has lower ts than first; allow then deny. |
| unsafe_lww_sequence | reorder_violation | Unsafe last-write-wins under delay/reorder; deny. |
| multi_writer_contention | split_brain | Two writers same task_id; second denied after first owns. |
| edge_case_timestamps | (ordering) | Same-ts events; ordering by seq. |

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
