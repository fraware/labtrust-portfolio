# Corpus Expansion Protocol

This document describes how to add and discover corpus cases for P1 (contracts), P3 (replay), and P6 (red-team / confusable deputy). Run manifests record corpus size for reproducibility.

## P1 — Contracts

- **Location:** `bench/contracts/corpus/`
- **Schema:** Each file is JSON: `description` (string), `initial_state` (object, e.g. ownership, _last_ts), `events` (array of events: type, ts, actor, payload), `expected_verdicts` (array of "allow"|"deny", length = events.length).
- **Discovery:** `scripts/contracts_eval.py` uses `sorted(args.corpus.glob("*.json"))`; add any `.json` with the same schema.
- **Checklist:** One failure class per sequence; `expected_verdicts.length == events.length`; document scenario in `description`.
- **Parameterized generator:** `scripts/generate_contract_corpus.py --writers W --tasks T [--out path]` generates one JSON (N-writer contention: first writer allow, rest deny per task). Add `--out bench/contracts/corpus/gen_Wwriter_Ttask.json` to extend the corpus without hand-writing.
- **Run manifest:** `run_manifest.corpus_sequence_count`, `run_manifest.corpus_sequences`, `run_manifest.corpus_dir`. See `bench/contracts/README.md`.

## P3 — Replay

- **Location:** `bench/replay/corpus/`
- **Schema:** Pairs of files: `NAME_trace.json` (trace format per kernel/trace) and `NAME_expected.json` with at least `expected_replay_ok` (bool), optionally `expected_divergence_at_seq`, `expected_diagnostic`.
- **Discovery:** `scripts/replay_eval.py` globs `*_trace.json` in `--corpus-dir` and pairs with `NAME_expected.json` by base name (e.g. `foo_trap_trace.json` → base `foo_trap`).
- **Checklist:** Add both `NAME_trace.json` and `NAME_expected.json`; naming convention: shared base name.
- **Run manifest:** `run_manifest.replay_trap_count`, `run_manifest.corpus_dir`. See `bench/replay/README.md`.

## P6 — Red-team and confusable deputy

- **Location:** Cases are defined in code: `impl/src/labtrust_portfolio/llm_planning.py` (`RED_TEAM_CASES`, `CONFUSABLE_DEPUTY_CASES`). Current counts: 8 red-team, 4 confusable deputy. Validator v0.2 applies allow_list + safe_args (path traversal, dangerous patterns).
- **Schema (per case):** `id`, `description`, `step` (tool/args), `expected_block` (bool).
- **How to add:** Add a new entry to the appropriate list in `llm_planning.py`; re-run `scripts/llm_redteam_eval.py`. Full table: `scripts/export_llm_redteam_table.py`. No file discovery; counts are fixed per run.
- **Run manifest:** `run_manifest.red_team_case_count`, `run_manifest.red_team_cases` (in red_team_results.json); `run_manifest.confusable_deputy_case_count` (in confusable_deputy_results.json). When `--real-llm --real-llm-runs N`: `real_llm.n_runs_per_case`, `real_llm.pass_rate_pct`, `real_llm.pass_rate_ci95_*` (Wilson), per-case pass_rate_pct and latency stats.

## Summary

| Corpus    | Discovery              | run_manifest fields              |
|-----------|------------------------|----------------------------------|
| Contracts | All `*.json` in corpus | corpus_sequence_count, corpus_sequences |
| Replay    | All `*_trace.json`     | replay_trap_count                |
| Red-team  | Code (llm_planning.py) | red_team_case_count              |
| Confusable| Code (llm_planning.py) | confusable_deputy_case_count     |

See also: `docs/EXPERIMENTS_AND_LIMITATIONS.md` (corpus scope), `docs/REPORTING_STANDARD.md` (run_manifest requirements).
