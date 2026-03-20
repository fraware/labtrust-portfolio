# Replay Levels and Nondeterminism Detection for Agentic CPS

**Draft (v0.2). Paper ID: P3_Replay.**

**Reproducibility.** From repo root, with `PYTHONPATH=impl/src` and `LABTRUST_KERNEL_DIR=kernel`. See [REPORTING_STANDARD.md](../docs/REPORTING_STANDARD.md) and [RESULTS_PER_PAPER.md](../docs/RESULTS_PER_PAPER.md). Use `--out` with the full file path (e.g. `datasets/runs/replay_eval/summary.json`), not a directory. Summary JSON includes `schema_version: p3_replay_eval_v0.2`, `run_manifest` (corpus_dir, overhead_runs, thin_slice_seeds, bootstrap_reps, platform, python_version), and `percentile_method: linear_hf7`. Replay levels L0/L1/L2; no claim to full determinism on hardware.

**Minimal run (under 20 min):** `python scripts/replay_eval.py --out datasets/runs/replay_eval/summary.json --overhead-curve --overhead-runs 5 --bootstrap-reps 100` then `python scripts/export_p3_replay_levels_diagram.py` then `python scripts/plot_replay_overhead.py` then `python scripts/verify_p3_replay_summary.py --strict-curve`.

**Publishable run:** `--overhead-runs 20`, `--thin-slice-seeds 42,43,44,45,46` (multi-seed sensitivity), `--bootstrap-reps 500` or higher; run_manifest in summary.json. CI uses fewer replays and bootstrap reps; do not cite CI output as publishable tables.

- **Figure 0:** `python scripts/export_p3_replay_levels_diagram.py` (output `docs/figures/p3_replay_levels_diagram.mmd`). Render Mermaid to PNG for camera-ready.
- **Table 1:** `python scripts/replay_eval.py` (as below), then `python scripts/export_replay_corpus_table.py` (see [generated_tables.md](generated_tables.md)).
- **Table 2 / Table 3:** Same run; Table 2 from `overhead_stats` (full L0); Table 3 from `baseline_overhead` in summary.json (see [generated_tables.md](generated_tables.md)).
- **Figure 1:** `python scripts/plot_replay_overhead.py` (output `docs/figures/p3_replay_overhead.png` and sidecar JSON). Run replay_eval with `--overhead-curve` first.

**Single command for paper tables and Figure 1:**

`PYTHONPATH=impl/src python scripts/replay_eval.py --out datasets/runs/replay_eval/summary.json --overhead-curve --overhead-runs 20 --thin-slice-seeds 42,43,44,45,46 --bootstrap-reps 500`

## 1. Motivation

Replayability is the missing glue between robotics, distributed systems, and safety cases. Logs alone are insufficient for verification; we need replayable causal programs suitable for audit, forensics, and reproducible evaluation, without overclaiming full determinism on hardware. The **primary** contribution is a contract-bounded replay story: detect and **localize** control-plane divergence with structured diagnostics, and quantify overhead against explicit baselines.

## 2. Replay levels and nondeterminism budgets

Replay is defined in levels (L0 control-plane default, L1 twin, L2 hardware-assisted).

**Figure 0 — Replay levels and pipeline.** L0 (control-plane replay), L1 (+ recorded observations), L2 (aspirational); pipeline from trace to replay engine to state_hash check to diagnostics. Regenerate with `python scripts/export_p3_replay_levels_diagram.py` (output `docs/figures/p3_replay_levels_diagram.mmd`). The primary guarantee is **nondeterminism detection and localization** relative to a declared replay contract. See `kernel/trace/REPLAY_LEVELS.v0.1.md` and determinism contract there. For L0, the budget is tight: control-plane outputs must match exactly. **L2 (hardware-assisted replay)** is aspirational; no L2 implementation or evaluation is included in this version (see REPLAY_LEVELS).

## 3. Trace format

Trace format: event ontology, causal links, time model. Schema: `kernel/trace/TRACE.v0.1.schema.json`. Events carry seq, ts, type, actor, payload, state_hash_after so that replay can recompute state and detect divergence.

## 4. Replay engine and divergence detection

- **L0:** Deterministic scheduling: apply events in order, recompute state, compare state_hash_after and final_state_hash. On mismatch, emit structured diagnostics (seq, expected_hash, got_hash, event_type). CLI: `labtrust_portfolio replay --run-dir <dir>` or `replay <trace.json> --diagnostics`.
- **Baselines (for overhead and scope):** `replay_trace_apply_only` applies events with **no** hash checks (lower bound; no audit). `replay_trace_final_hash_only` checks only **final** state hash (verification without per-event localization). Both are timed in `replay_eval.py` alongside full L0.
- **L1:** L1 = L0 + twin config + deterministic twin replay (same state machine from trace); full simulator/physics twin is future work. The eval runs the L1 stub by default; use `--l1-twin` for full L1 (one re-execution of the control-plane state machine so the twin consumes the same trace and reproduces state_hash). L1 = **control-plane replay with recorded observations**, not physics replay. All observations come from the trace; no live simulator is required for the minimal L1 contract. Design in `kernel/trace/L1_TWIN_DESIGN.v0.1.md`: twin configuration identity (build_hash, model_params, env_seed), mapping from trace to twin interface. The eval runs the L1 stub on the thin-slice trace with `bench/replay/corpus/twin_config.json` and reports `l1_stub_ok` in the summary.
- **Divergence detector:** Implemented in `replay_trace_with_diagnostics`; diagnostics integrated with evidence bundle (replay_diagnostics string).

**Comparison to record-replay systems.** We clarify the niche relative to full execution record-replay and log-only tools.

| System | Guarantee | Scope | Divergence detection | When our approach is preferable |
|--------|-----------|--------|----------------------|----------------------------------|
| RR (record-replay) | Full process determinism | Whole process, syscalls | Re-execution match | Control-plane audit without full-process determinism; no kernel/syscall capture. |
| Scribe / similar | Deterministic replay from log | Process + I/O | Replay from log | We need state_hash and localization (which event diverged), not only replay. |
| Log-only / best-effort | Events only | Events | None | Audit and forensics require *detection* of divergence and seq-level diagnostics. |
| **Our L0** | Control-plane state + state_hash | Events, state_hash_after | Yes: seq, expected_hash, got_hash | Control-plane audit, evidence for safety cases, no full-process determinism. |

RR and Scribe aim at full-process or I/O determinism for debugging; we do not. L0 targets **control-plane state** and **nondeterminism localization** with structured diagnostics (seq, expected_hash, got_hash) for audit and evidence bundles. Our approach is preferable when: (1) only control-plane behaviour must be verified (e.g. MADS evidence); (2) full-process determinism is infeasible or unnecessary; (3) divergence must be localized to a specific event for forensics.

## 5. Evaluation

- **Trace corpus:** (1) MAESTRO thin-slice (generated; primary seed 42 for main overhead tables). (2) Trap traces: nondeterminism (divergence at seq 0), reorder and timestamp_reorder (seq 1), hash_mismatch (seq 1). (3) **Field-style pass trace** (`field_style_pass_*`): TRACE-conformant synthetic trace from an alternate thin-slice seed, standing in for an externally mapped log (see [P3_REAL_TRACE_INGESTION.md](../docs/P3_REAL_TRACE_INGESTION.md)); expected pass. Corpus is discovered from all `*_trace.json` / `*_expected.json` pairs under `bench/replay/corpus/`. **divergence_localization_confidence** is the fraction of **seq-expected** traps where `divergence_at_seq` matches; **corpus outcome accuracy** (excellence metric) requires every row to match expected pass/fail and, for traps, expected seq. **corpus_outcome_wilson_ci95** is a Wilson interval for the proportion of correct corpus outcomes. See `bench/replay/README.md` and `kernel/trace/REPLAY_LEVELS.v0.1.md`.

- **Multi-seed thin-slice family:** `--thin-slice-seeds` runs the overhead distribution on each seed; `multi_seed_overhead.across_seeds_mean_of_means_ms` and `across_seeds_stdev_of_means_ms` summarize variability of the **mean** replay time across seeds (mitigates overfitting overhead to one event mix).

- **Statistics:** Overhead uses empirical **linear** percentiles (Hyndman-Fan type 7, recorded as `percentile_method`). **p95** and **p99** are empirical; bootstrap 95% CIs for percentiles and paired **full vs apply-only** difference when `bootstrap_reps` > 0. **overhead_p99_ms** in excellence_metrics is empirical (not a normal approximation).

- **Table 1 — Corpus and fidelity.** Source: replay_eval `per_trace[]`. Regenerate with `python scripts/export_replay_corpus_table.py`.

- **Table 2 — Full L0 replay overhead.** Source: `overhead_stats` on primary thin-slice trace; N=`overhead_runs` (default 20). Includes mean, stdev, p95, p99, and CIs as in summary.json.

- **Table 3 — Baselines.** Source: `baseline_overhead` in summary: `apply_only_no_hash`, `final_hash_only`, `full_l0_witness_window_0`, and `full_vs_apply_only` (paired bootstrap CI for mean difference). See [generated_tables.md](generated_tables.md).

- **Figure 1 — Replay overhead vs trace size.** p95 replay time (ms) vs event count from `overhead_curve` (prefixes of the **primary** thin-slice trace). Points may include bootstrap CIs; plotted as error bars when present. Thin traces may yield a single curve point if `event_count` bins exceed trace length.

**Key results.** (1) `fidelity_pass` true on thin-slice. (2) Corpus: `success_criteria_met.corpus_expected_outcomes_met` true when all expected outcomes hold (pass traces replay ok; traps diverge at expected seq). (3) L1 stub: `l1_stub_ok` when twin config present. (4) L1 twin: optional `--l1-twin`; supplement or appendix. (5) Overhead: publishable defaults `--overhead-runs 20`, `--bootstrap-reps` 500+.

**Results summary (excellence metrics).** From summary.json: **divergence_localization_accuracy_pct** (corpus rows correct); **overhead_p99_ms** (empirical); **l1_stub_ok**; **witness_slices_present**. See [STANDARDS_OF_EXCELLENCE.md](../docs/STANDARDS_OF_EXCELLENCE.md) (P3).

## 6. Evidence integration

Replay outcomes are admissible evidence (MADS): evidence bundle includes replay_ok and replay_diagnostics. Conformance Tier 2 requires replay ok. **Formal + empirical:** The evidence-bundle verifier (required artifact presence, schema validity) is specified in the W3 wedge (`formal/lean/`); replay_ok and verification flags in the bundle align with that spec. L0 replay (state_hash check and diagnostics) provides the empirical replay outcome that the evidence bundle records.

## 7. Methodology and reproducibility

**Methodology:** Hypothesis: L0 replay detects and localizes divergence when state hashes mismatch. Metrics: replay fidelity per trace, divergence at seq, overhead distributions, baselines, multi-seed summary. **Threats to validity:** Internal: microbenchmark noise (mitigate with N=20, optional `--warmup`). External: synthetic and field-style proxy traces only; not a production fleet. Construct: overhead measures in-process replay cost, not distributed log ingest.

**Reproducibility:** Run `replay_eval.py` with `--out` as a **file** path. Then `python scripts/plot_replay_overhead.py`. Validate with `python scripts/verify_p3_replay_summary.py [--strict-curve]`. Integration tests run the eval and assert schema, corpus traps (including hash_mismatch and field_style_pass), overhead_curve when requested, and baselines. Optional release: copy to `datasets/releases/p3_replay_eval`. See `datasets/README.md`.

**Submission note.** Publishable tables use `--overhead-runs 20` and documented `run_manifest`. Before submit, Phase 3 checklist in [STATE_OF_THE_ART_CRITERIA.md](../docs/STATE_OF_THE_ART_CRITERIA.md#3-submission-readiness-phase-3--hostile-reviewer-checklist). Consolidated multi-paper summary: [RUN_RESULTS_SUMMARY.md](../../datasets/runs/RUN_RESULTS_SUMMARY.md) when regenerated via `run_paper_experiments.py`.

## 8. Limitations

Scope and determinism levels: [EXPERIMENTS_AND_LIMITATIONS.md](../docs/EXPERIMENTS_AND_LIMITATIONS.md). Per-paper:

- **Replay levels and scope:** L0 is implemented; L1 stub and L1 twin (`--l1-twin`) are available; L2 is design-only. We do not claim full hardware determinism.
- **K3 (fidelity bound):** If replay fidelity cannot be bounded clearly, claims narrow to **detection and localization only**. The design provides L0 pass/fail and structured diagnostics (seq, expected_hash, got_hash, witness_slice).
- **Synthetic and proxy traces:** MAESTRO thin-slice, hand-crafted traps, and field-style pass trace are not a live nondeterministic fleet; `field_style_pass` is a TRACE-conformant external-validity proxy, not a redacted production log.
- **L1:** Full simulator/physics twin is not implemented; L1 = control-plane replay with recorded observations.
- **L2 (design):** Not implemented; see `kernel/trace/REPLAY_LEVELS.v0.1.md`.
- **Overhead:** In-process, small traces; multi-seed summary does not substitute for large-trace or distributed deployment benchmarks.
- **Corpus size:** Bounded trap set; long-horizon real traces are future work.

---

**Claims and backing.** See [claims.yaml](claims.yaml).

| Claim | Evidence |
|-------|----------|
| C1 (L0 verifiable + localization) | replay_eval summary, corpus, `replay_trace_with_diagnostics`, Table 1–3, verify script. |
| C2 (Nondeterminism detectable; baselines) | Trap traces, `baseline_overhead`, paired comparison. |
| C3 (Audit / reconstruction) | Diagnostics, witness slices; user-study not claimed. |
| C4 (Evidence integration) | Evidence bundle replay_ok, replay_diagnostics. |
