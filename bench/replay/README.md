# Replay Levels and Nondeterminism Detection

Replay is treated as a first-class primitive with explicit levels (L0/L1/L2). Hardware cannot be bit-identical; the guarantee is **detection and localization** of divergence.

**Corpus:** `corpus/` contains `*_trace.json` and `*_expected.json` pairs (nondeterminism_trap, reorder_trap, timestamp_reorder_trap, hash_mismatch_trap). Add new pairs with the same naming; `replay_eval.py` discovers all `*_trace.json` and reports `divergence_localization_confidence` over the full set.

**Corpus expansion:** To add a new trap: (1) Add `NAME_trace.json` (trace with events and optional state_hash_after; format per kernel/trace). (2) Add `NAME_expected.json` with at least `expected_replay_ok` (bool) and optionally `expected_divergence_at_seq`, `expected_diagnostic`. Naming: base name shared (e.g. `foo_trap_trace.json` and `foo_trap_expected.json` yield base `foo_trap`). Discovery: `replay_eval.py` globs `*_trace.json` in `--corpus-dir` and pairs with `*_expected.json` by base name.

- **L0:** Control-plane replay; TRACE format allows reconstruction of state transitions; replay engine validates state hashes and flags divergence with structured diagnostics.
- **L1:** Control-plane replay with recorded observations. L1 = replay using the trace as the sole source of observations (no live simulator required). L1 stub: L0 + twin config validation. L1 twin: use `replay_eval.py --l1-twin` for deterministic re-run of the control-plane state machine (l1_twin_ok, l1_twin_final_hash_match in summary). See `kernel/trace/REPLAY_LEVELS.v0.1.md` and `kernel/trace/L1_TWIN_DESIGN.v0.1.md`.
- **L2:** Hardware-assisted (aspirational; design subsection in REPLAY_LEVELS).

Nondeterminism is flagged when replay diverges; summary includes `replay_level`, `nondeterminism_budget`, and `divergence_localization_confidence`. For each divergence, the engine outputs a **witness_slice** (events around divergence_at_seq) in `per_trace` entries and a top-level **witness_slices** list aggregating all divergence slices. Run the eval with **`--out datasets/runs/replay_eval/summary.json`** (file path, not directory) so the summary is written correctly. Overhead curve (p95 vs event count) is produced with `replay_eval.py --overhead-curve`; figure: `scripts/plot_replay_overhead.py`. See `kernel/trace/REPLAY_LEVELS.v0.1.md`.

Thin-slice replay lives in `impl/src/labtrust_portfolio/replay.py`.
