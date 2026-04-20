# L1 twin cross-family evidence (P3 freeze)

Supplement to the manuscript: L1 is exercised on (1) the full publishable thin-slice seed set and (2) every `real_ingest` corpus lane that passes L0 replay, using the same `replay_l1_twin` contract as in `impl/src/labtrust_portfolio/replay.py`.

## Source of truth

- `datasets/runs/replay_eval/summary.json` keys: `l1_twin_multi_seed`, `l1_twin_summary` (including `real_ingest_traces`, `real_ingest_all_pass`, `all_pass`).
- Paper-facing tables: `papers/P3_Replay/generated_tables.md` (L1 section).

## Consistency claim

On the frozen artifact set, every reported L1 twin run agrees with its paired L0 outcome on passing traces (`l1_twin_ok` true where `replay_ok` is true for the same trace). Mismatch cases would appear as `l1_twin_ok: false` with a non-empty `l1_twin_message` in the summary JSON.
