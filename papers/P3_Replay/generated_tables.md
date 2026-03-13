# Generated tables for P3 (P3_Replay)

**How to read:** Table 1 lists corpus traces with expected and observed replay outcome and divergence_at_seq; Table 2 gives replay overhead (mean, stdev, p95 ms) over N replays. Source: `datasets/runs/replay_eval/summary.json`. Run manifest: corpus_dir, overhead_runs, script. Regenerate with `python scripts/replay_eval.py --out datasets/runs/replay_eval/summary.json --overhead-curve --overhead-runs 20`.

## From replay_eval.py (summary.json)

**Table 1 — Corpus and fidelity (source: replay_eval/summary.json).** Corpus includes all `*_trace.json`/`*_expected.json` pairs in bench/replay/corpus; table shows selected traces; full list in summary.json corpus_divergence_detected.

| Trace | expected_replay_ok | expected_divergence_at_seq | observed replay_ok | observed divergence_at_seq |
|-------|--------------------|----------------------------|--------------------|----------------------------|
| thin_slice | true | — | true | — |
| nondeterminism_trap | false | 0 | false | 0 |
| reorder_trap | false | 1 | false | 1 |
| timestamp_reorder_trap | false | 1 | false | 1 |

**Table 2 — Replay overhead (source: summary overhead_stats).** N replays of thin-slice trace; mean_ms, stdev_ms, p95_ms.

| n_replays | mean_ms | stdev_ms | p95_ms |
|-----------|---------|----------|--------|
| 20 | 0.21 | 0.08 | 0.40 |

See DRAFT.md repro block and RESULTS_PER_PAPER.md.
