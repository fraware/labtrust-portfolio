# Coordination Contract Benchmark v0.1

This document defines the **Coordination Contract Benchmark v0.1**: a reusable benchmark for evaluating contract validators that enforce typed state, ownership, and valid transitions above messaging.

## Version

- **Version:** v0.1
- **Corpus location:** `bench/contracts/corpus/` (relative to repo root)

## Sequences (N = 51+)

The challenge corpus is stratified by failure class and by tier. Discovery: all `*.json` files in the corpus directory via `sorted(corpus_dir.glob("*.json"))`.

### Tier 1 — Micro (correctness)

Short sequences (1–10 events) covering:

- **Positive controls (good_*):** good_sequence, good_two_keys, good_three_events, good_four_events, good_five_events, good_six_keys, good_seven_events, good_eight_events, good_ten_events, good_single_allow, good_sequence_4events, good_interleaved_6, good_three_keys_cycle, multi_key_no_conflict, conflicting_writes_independent_keys, duplicate_delivery, same_ts_same_writer, edge_case_timestamps, coordination_message_passthrough.
- **Split-brain:** split_brain_sequence, split_brain_same_epoch, split_brain_second_key, split_brain_three_writers, split_brain_four_writers, split_brain_five_writers, split_brain_delayed_conflict, split_brain_two_keys, split_brain_then_allow, multi_writer_contention.
- **Stale write / reorder:** stale_write_sequence, stale_write_sequence_2, stale_write_sequence_3, stale_write_sequence_4, stale_write_margin, stale_write_delayed_delivery, stale_then_allow, reorder_sequence, reorder_first_deny, reorder_three_events, reorder_multi_key, reorder_burst_four, reorder_mid_chain, reorder_first_event_deny, unsafe_lww_sequence.
- **Boundary:** stale_write_exact (ts equals last_ts; validator uses strict > so allow).

### Tier 2 — Meso (long-horizon and mixed-key)

- **Long-horizon:** long_horizon_10 (10 events, one key).
- **Mixed-key contention:** mixed_key_contention_8 (8 events across multiple keys).

### Tier 3 — Stress and adversarial

- **Adversarial / robustness:** actor_payload_writer_mismatch (actor id vs payload writer; split_brain), burst_duplicate_three (same-ts burst), unknown_key_deny, good_then_unknown_key (empty task_id).

### Required reporting per tier

- **Tier 1:** Per-sequence detection_ok (exact per-event verdict match), corpus_detection_rate_pct, detection_metrics (TP/FP/FN, precision, recall, F1).
- **Tier 2:** Same as Tier 1; report latency and throughput for long-horizon runs.
- **Tier 3:** Same as Tier 1; document expected behavior for malformed/adversarial cases.

### Acceptance criteria

- A validator satisfies the benchmark if for every sequence, the validator's verdict per event matches `expected_verdicts[i]` (detection_ok true for all sequences).
- Run manifest must include corpus_sequence_count, corpus_fingerprint, and script_version.

## Schema

Each corpus file is JSON with:

- **description** (string): Short scenario description.
- **initial_state** (object): At least `ownership` (key → owner) and `_last_ts` (key → last accepted write time).
- **events** (array): Event objects with `type`, `ts`, `actor`, `payload`. Types include `task_start`, `task_end`, `coordination_message`. Payload must include key (e.g. `task_id`) and writer when relevant.
- **expected_verdicts** (array): One of `"allow"` or `"deny"` per event; length must equal `events.length`.

## Ground-truth labeling and anti-circularity

**Definition of labels.** For each sequence, `expected_verdicts[i]` is the **intended** allow/deny outcome for `events[i]` under the **declared** contract configuration in that file (`initial_state`, event shapes, and the reference validator semantics in `impl/.../contracts.py`). Labels are **not** outputs of an automated labeler trained on the validator.

**Provenance.** Corpus authors should record how each file was authored:

- **Manual:** scenario + verdicts written by hand from the contract rules.
- **Script-generated:** produced by `scripts/generate_contract_corpus.py` or similar; the run should record a **reproducible seed** and generator version in the sequence `description` or in corpus governance metadata (see [CORPUS_EXPANSION.md](../../docs/CORPUS_EXPANSION.md)).

**Anti-circularity.** The reference runner compares the validator’s per-event verdicts to `expected_verdicts`; it does **not** copy labels from `validate()` into the JSON at eval time. CI and `tests/test_contracts_p1.py` load each corpus file independently and assert agreement, catching accidental label drift.

**Independent check.** Maintainers may run a **label–validator audit**: for every corpus file, recompute verdicts with the frozen validator and assert equality with `expected_verdicts` (the eval script and tests already enforce this on every run).

**Ambiguity and exclusions.** If a scenario is underspecified under the current schema, either refine the contract declaration in the file or **exclude** the sequence from the benchmark until the expected verdict is unambiguous. Do not commit sequences with “best guess” labels without documenting the decision.

## Discovery rule

The reference runner discovers all `*.json` files in the corpus directory via `sorted(corpus_dir.glob("*.json"))`. Generated sequences (e.g. from `scripts/generate_contract_corpus.py`) may be added with the same schema.

## Reference runner and table

- **Runner:** `python scripts/contracts_eval.py --out datasets/runs/contracts_eval` (with default corpus dir `bench/contracts/corpus/`).
- **Table:** `python scripts/export_contracts_corpus_table.py` (reads eval.json, prints corpus table for the draft).

## Success criterion

A validator satisfies the benchmark if for every sequence, the validator's verdict per event matches `expected_verdicts[i]` (detection_ok true for all sequences).
