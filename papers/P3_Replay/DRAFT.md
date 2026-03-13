# Replay Levels and Nondeterminism Detection for Agentic CPS

**Draft (v0.1). Paper ID: P3_Replay.**

**Reproducibility.** From repo root, with `PYTHONPATH=impl/src` and `LABTRUST_KERNEL_DIR=kernel`. See [REPORTING_STANDARD.md](../docs/REPORTING_STANDARD.md) and [RESULTS_PER_PAPER.md](../docs/RESULTS_PER_PAPER.md). Use `--out` with the full file path (e.g. `datasets/runs/replay_eval/summary.json`), not a directory. Run_manifest in summary.json (corpus_dir, overhead_runs, script). Replay levels L0/L1/L2; no claim to full determinism on hardware.

**Minimal run (under 20 min):** `python scripts/replay_eval.py --out datasets/runs/replay_eval/summary.json --overhead-curve --overhead-runs 5` then `python scripts/export_p3_replay_levels_diagram.py` then `python scripts/plot_replay_overhead.py`.

**Publishable run:** `--overhead-runs 20`; run_manifest in summary.json.

- **Figure 0:** `python scripts/export_p3_replay_levels_diagram.py` (output `docs/figures/p3_replay_levels_diagram.mmd`). Render Mermaid to PNG for camera-ready.
- **Table 1, Table 2:** `python scripts/replay_eval.py --out datasets/runs/replay_eval/summary.json --overhead-curve --overhead-runs 20`; table content from summary.
- **Figure 1:** `python scripts/plot_replay_overhead.py` (output `docs/figures/p3_replay_overhead.png`). Run replay_eval with `--overhead-curve` first.

## 1. Motivation

Replayability is the missing glue between robotics, distributed systems, and safety cases. Logs alone are insufficient for verification; we need replayable causal programs suitable for audit, forensics, and reproducible evaluation—without overclaiming full determinism on hardware.

## 2. Replay levels and nondeterminism budgets

Replay is defined in levels (L0 control-plane default, L1 twin, L2 hardware-assisted).

**Figure 0 — Replay levels and pipeline.** L0 (control-plane replay), L1 (+ recorded observations), L2 (aspirational); pipeline from trace to replay engine to state_hash check to diagnostics. Regenerate with `python scripts/export_p3_replay_levels_diagram.py` (output `docs/figures/p3_replay_levels_diagram.mmd`). The primary guarantee is **nondeterminism detection and localization** relative to a declared replay contract. See `kernel/trace/REPLAY_LEVELS.v0.1.md` and determinism contract there. For L0, the budget is tight: control-plane outputs must match exactly. **L2 (hardware-assisted replay)** is defined in REPLAY_LEVELS as aspirational; no L2 implementation or evaluation is included in this version.

## 3. Trace format

Trace format: event ontology, causal links, time model. Schema: `kernel/trace/TRACE.v0.1.schema.json`. Events carry seq, ts, type, actor, payload, state_hash_after so that replay can recompute state and detect divergence.

## 4. Replay engine and divergence detection

- **L0:** Deterministic scheduling: apply events in order, recompute state, compare state_hash_after and final_state_hash. On mismatch, emit structured diagnostics (seq, expected_hash, got_hash, event_type). CLI: `labtrust_portfolio replay --run-dir <dir>` or `replay <trace.json> --diagnostics`.
- **L1:** L1 = **control-plane replay with recorded observations**, not physics replay. All observations come from the trace; no live simulator is required for the minimal L1 contract. Design in `kernel/trace/L1_TWIN_DESIGN.v0.1.md`: twin configuration identity (build_hash, model_params, env_seed), mapping from trace to twin interface. Minimal stub: L0 replay + twin config validation. The eval runs the L1 stub on the thin-slice trace with `bench/replay/corpus/twin_config.json` and reports `l1_stub_ok` in the summary; full twin replay (simulator execution) remains future work.
- **Divergence detector:** Implemented in `replay_trace_with_diagnostics`; diagnostics integrated with evidence bundle (replay_diagnostics string).

**Comparison to other replay systems.** Full execution record-replay (e.g. RR, Scribe) targets full process determinism; we do not claim that. L0 focuses on **control-plane state** and **nondeterminism localization**: state-hash check per event and structured diagnostics (seq, expected/got hash). Log-only or best-effort replay has no divergence detection; we provide exact L0 contract and diagnostics.

| Approach | Scope | Divergence detection |
|----------|--------|----------------------|
| Full execution (RR, Scribe) | Whole process | Execution replay |
| Log-only / best-effort | Events only | None |
| **Our L0** | Control-plane, state_hash_after | Yes: seq, expected_hash, got_hash |

## 5. Evaluation

- **Trace corpus:** (1) MAESTRO scenario (thin-slice) with expected pass; (2) nondeterminism trap: divergence at seq 0; (3) reorder trap: divergence at seq 1; (4) timestamp_reorder_trap: wrong state_hash_after at seq 1; (5) hash_mismatch_trap: wrong state_hash_after at seq 1 (three events). Corpus is discovered from all `*_trace.json` / `*_expected.json` pairs in `bench/replay/corpus/`; `divergence_localization_confidence` is computed over the full set. See `bench/replay/README.md` and `kernel/trace/REPLAY_LEVELS.v0.1.md`.
- **Metrics:** Replay fidelity (pass/fail per trace), divergence detection (yes/no, divergence_at_seq), overhead (replay_time_ms per trace; distribution over N replays: mean, stdev, p95 in `overhead_stats`). The evaluation script `scripts/replay_eval.py` runs L0 replay on thin-slice and corpus traces, runs the L1 stub on the thin-slice trace, and outputs a JSON summary. Summary includes **replay_level** (L0|L1|L2), **nondeterminism_budget** (declared per level), **divergence_localization_confidence** (fraction of corpus traps localized at expected seq), plus fidelity_pass, l1_stub_ok, l1_stub_message, overhead_stats, corpus_divergence_detected, per_trace. Default `--overhead-runs 20` for overhead distribution.
- **Table 1 — Corpus and fidelity (source: replay_eval/summary.json).**

| Trace | expected_replay_ok | expected_divergence_at_seq | observed replay_ok | observed divergence_at_seq |
|-------|--------------------|----------------------------|--------------------|----------------------------|
| thin_slice | true | — | true | — |
| nondeterminism_trap | false | 0 | false | 0 |
| reorder_trap | false | 1 | false | 1 |
| timestamp_reorder_trap | false | 1 | false | 1 |

- **Table 2 — Replay overhead (source: summary overhead_stats).** N replays of thin-slice trace; mean_ms, stdev_ms, p95_ms.

| n_replays | mean_ms | stdev_ms | p95_ms |
|-----------|---------|----------|--------|
| 20 | 0.21 | 0.08 | 0.40 |

- **Representative results:** Thin-slice: replay_ok true; nondeterminism trap: divergence at seq 0; reorder trap and timestamp_reorder_trap: divergence at seq 1. L1 stub: l1_stub_ok true when twin_config.json is present. Overhead distribution: in `datasets/runs/replay_eval/summary.json` under `overhead_stats` (n_replays, mean_ms, stdev_ms, p95_ms). Publishable tables/figures: regenerate with `--overhead-runs 20` and `--out datasets/runs/replay_eval/summary.json` (file path).

**Figure 1 — Replay overhead vs trace size.** p95 replay time (ms) vs event count from `overhead_curve`. Regenerate: (1) `python scripts/replay_eval.py --out datasets/runs/replay_eval/summary.json --overhead-curve --overhead-runs 20`; (2) `python scripts/plot_replay_overhead.py` (input: `datasets/runs/replay_eval/summary.json`, output: `docs/figures/p3_replay_overhead.png`).

## 6. Evidence integration

Replay outcomes are admissible evidence (MADS): evidence bundle includes replay_ok and replay_diagnostics. Conformance Tier 2 requires replay ok.

## 7. Methodology and reproducibility

**Methodology:** Hypothesis—L0 replay detects and localizes divergence when state hashes mismatch. Metrics: replay fidelity (pass/fail per trace), divergence detection (yes/no, divergence_at_seq), overhead (replay_time_ms; distribution: mean, stdev, p95 over N replays). Baseline: expected outcomes from corpus (nondeterminism trap diverge at seq 0; reorder and timestamp_reorder traps at seq 1; thin-slice pass). Kill criterion: if divergence is not localized to the correct event seq, the engine fails. Portfolio criteria: `docs/STATE_OF_THE_ART_CRITERIA.md`.

**Reproducibility:** Run evaluation with **`--out` as the full file path** (not a directory): `python scripts/replay_eval.py --out datasets/runs/replay_eval/summary.json --overhead-curve --overhead-runs 20` (PYTHONPATH=impl/src, LABTRUST_KERNEL_DIR=kernel). Then `python scripts/plot_replay_overhead.py` to refresh Figure 1 (default reads `datasets/runs/replay_eval/summary.json`). Run manifest in summary.json: corpus_dir, overhead_runs, overhead_curve_runs, script. Corpus: `bench/replay/corpus/*.json` (including twin_config.json for L1 stub). Optional release: copy to `datasets/releases/p3_replay_eval`. See `datasets/README.md`. Integration test runs the eval and asserts on summary (fidelity_pass, l1_stub_ok, overhead_stats, corpus divergence at expected seq).

## 8. Limitations

Scope and determinism levels: [EXPERIMENTS_AND_LIMITATIONS.md](../docs/EXPERIMENTS_AND_LIMITATIONS.md). Per-paper:

- **K3 (fidelity bound):** If replay fidelity cannot be bounded clearly (e.g. no clear pass/fail, or dependency on simulator internals), claims are narrowed to **detection and localization only** (no strong fidelity guarantee). The current design provides a clear L0 pass/fail and structured diagnostics (seq, expected_hash, got_hash, witness_slice).
- **Synthetic traces:** Corpus and thin-slice traces are synthetic (MAESTRO thin-slice and hand-crafted trap traces); no real nondeterministic platform or hardware.
- **L1:** Twin design is documented in `kernel/trace/L1_TWIN_DESIGN.v0.1.md`; only the stub (L0 + twin config validation) is implemented. Full twin replay (simulator execution) is not implemented; future work.
- **L2:** Not implemented; hardware-assisted replay is aspirational (see REPLAY_LEVELS). L2 is out of scope for this version.
- **Overhead:** Measured on small traces and a single process; not representative of large-scale or distributed deployment.
- **L1 stub only:** Full L1 twin replay (simulator execution) is not implemented; only L0 + twin config validation. L1 = control-plane replay with recorded observations, not physics replay.
- **Small corpus:** A few trap traces; no long real-world traces.

---

**Claims and backing.**

| Claim | Evidence |
|-------|----------|
| C1 (L0 replay verifiable) | replay_trace_with_diagnostics, conformance Tier 2. |
| C2 (Nondeterminism detectable) | Table 1, corpus tests, replay_eval (divergence at seq 0/1). |
| C3 (Time-travel debugging) | Event-order replay, diagnostics (seq, expected/got hash). |
| C4 (Evidence integration) | Evidence bundle replay_ok, replay_diagnostics. |
| C5 (L1 contract) | L1 stub in eval, l1_stub_ok; twin config validation. |
