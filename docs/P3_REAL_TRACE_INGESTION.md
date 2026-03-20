# P3 Real trace ingestion

This note describes how to run the replay pipeline on **traces from a real platform** (e.g. one robot, one ROS node, one lab device). When such traces exist, you can report L0 pass/fail, divergence localization, and overhead.

## TRACE schema

Traces must conform to the portfolio TRACE schema (`kernel/trace/TRACE.v0.1.schema.json`): events array with `seq`, `ts`, `type`, `actor`, `payload`, and optionally `state_hash_after`. Each event should have a type (e.g. `task_start`, `task_end`, `coordination_message`).

## Mapping external logs to TRACE

- **ROS bag / node logs:** Map each relevant topic or action to an event: `type` (e.g. task_start), `ts` (header stamp or wall time), `actor` (node id), `payload` (task_id, name, etc.). If the platform does not emit `state_hash_after`, you can omit it; L0 replay will recompute state from the event sequence and compare final state hash only if the trace includes it for a subset of events.
- **OPC UA events:** Map state transitions (e.g. Idle→Running) to `task_start`/`task_end` with `ts`, `actor`, `payload` (task_id, writer). See `kernel/interop/OPC_UA_LADS_MAPPING.v0.1.md`.

## Running L0 without state hashes

If the external trace has no `state_hash_after` fields, the replay engine can still run: it will apply events in order and compute a final state hash. Divergence detection then requires a **reference trace** (e.g. from a golden run) with the same event sequence to compare final_state_hash. For corpus-style evaluation, provide pairs (trace.json, expected.json) where expected holds the expected pass/fail and divergence_at_seq.

## When real traces exist

1. Place trace files (and optional expected outcomes) in a directory under `bench/replay/corpus/` (or pass `--corpus-dir` to `replay_eval.py`). Discovery uses `*_trace.json` / `*_expected.json` pairs in that directory.
2. For a redacted production log, map to TRACE first; include `expected_replay_ok` and `expected_divergence_at_seq` when ground truth is known.
3. The checked-in `field_style_pass_trace.json` is a **synthetic** TRACE-conformant trace (alternate thin-slice seed) used as an external-validity proxy until a real trace is released.

## Portfolio note

P3 `replay_eval` summary (`datasets/runs/replay_eval/summary.json`) lists `field_style_pass` in `per_trace` when present in the corpus. Regenerate tables with `export_replay_corpus_table.py` after adding real traces.
