# L1 twin cross-family evidence (P3 freeze)

L1 in this repo is a **control-plane twin contract** (L0 + twin config + deterministic re-run of the same state machine from the trace), not physics or plant replay. See `replay_l1_twin` in `impl/src/labtrust_portfolio/replay.py`.

## What the frozen summary must show

From `datasets/runs/replay_eval/summary.json` (run with **`--l1-twin`**):

| Key | Role |
|-----|------|
| `l1_twin_multi_seed` | Per thin-slice seed: `l1_twin_ok`, `l1_twin_time_ms` |
| `l1_twin_summary.n_seeds`, `seeds`, `all_pass`, `per_seed` | Aggregate over the publishable seed set |
| `l1_twin_summary.real_ingest_traces` | **Second evaluation family:** each passing `real_ingest` corpus trace |
| `l1_twin_summary.real_ingest_all_pass` | All real-ingest L1 twins passed |
| `run_manifest.l1_twin_real_ingest_n` | Count of real-ingest L1 runs |

`all_pass` in `l1_twin_summary` is true only if every thin-slice seed **and** every real-ingest row passes.

## Paper-facing export

`papers/P3_Replay/generated_tables.md` includes the L1 multi-seed block and the **L1 twin on real_ingest traces** table (from `export_replay_corpus_table.py`).

## Consistency with L0

On passing traces, `l1_twin_ok` implies L0 replay succeeded first (`replay_l1_twin` calls `replay_trace_with_diagnostics` before the twin re-run). Mismatches surface as `l1_twin_ok: false` with a non-empty `l1_twin_message`.
