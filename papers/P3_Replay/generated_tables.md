# Generated tables for P3 (P3_Replay)

**How to read:** Table 1 lists all corpus traces (including field-style pass and traps). Table 2 is full L0 replay overhead on the primary thin-slice trace (seed 42). Table 3 compares baselines on the same trace (paired bootstrap CI for full vs apply-only). Source: `datasets/runs/replay_eval/summary.json` (schema `p3_replay_eval_v0.2`). Regenerate:

`PYTHONPATH=impl/src python scripts/replay_eval.py --out datasets/runs/replay_eval/summary.json --overhead-curve --overhead-runs 20 --thin-slice-seeds 42,43,44,45,46 --bootstrap-reps 500`

Then `python scripts/export_replay_corpus_table.py` and `python scripts/plot_replay_overhead.py`. Verify: `python scripts/verify_p3_replay_summary.py --strict-curve`.

## From replay_eval.py (summary.json)

**Table 1 — Corpus and fidelity.** Full list: run `python scripts/export_replay_corpus_table.py` (N = thin_slice + all `*_trace.json` in corpus with expected files).

**Table 2 — Full L0 replay overhead (primary thin-slice, seed 42).** Empirical percentiles (linear interpolation, Hyndman-Fan type 7); bootstrap 95% CIs for p95/p99 when `bootstrap_reps` > 0.

| n_replays | mean_ms | stdev_ms | p95_ms | p99_ms |
|-----------|---------|----------|--------|--------|
| 20 | 0.3246 | 0.1767 | 0.5665 | 0.8624 |

**Table 3 — Baselines and ablation (same N replays, paired).** `apply_only_no_hash`: apply events, no verification. `final_hash_only`: final hash only (no per-event localization). `full_l0_witness_window_0`: full L0 with witness_window=0 (same pass path as full L0 on non-diverging traces). `full_vs_apply_only`: bootstrap CI on paired difference (ms).

| Variant | mean_ms (approx.) | Note |
|---------|-------------------|------|
| apply_only_no_hash | 0.041 | Lower bound; no audit |
| final_hash_only | 0.052 | No localization |
| full L0 (Table 2) | 0.325 | Per-event checks + diagnostics |

**Multi-seed family:** `multi_seed_overhead.across_seeds_mean_of_means_ms` and `across_seeds_stdev_of_means_ms` report variability across thin-slice seeds (external validity for synthetic event mix).

See DRAFT.md repro block and RESULTS_PER_PAPER.md.
