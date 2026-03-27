# Replay Levels and Nondeterminism Detection for Agentic CPS

**Draft (v0.2). Paper ID: P3_Replay.**

## Abstract

We present contract-bounded **L0 control-plane replay** over a CPS trace format: per-event commitments (`state_hash_after`), sequence-level **divergence localization** (expected vs recomputed hash at a named `seq`), and structured diagnostics with witness slices for audit. The **primary empirical headline** is **localization accuracy on a trap corpus** together with **Wilson confidence intervals** on corpus-level outcomes (`divergence_localization_wilson_ci95`, `corpus_outcome_wilson_ci95` in the eval summary); timing reports the **bounded cost of admissible L0 verification** on evaluated workloads and explicit baselines, not a claim of universal fastest replay.

**Canonical publishable timing (primary thin-slice trace, `--overhead-runs 20`, from `overhead_stats` in `summary.json`):** mean full L0 **0.3495** ms, p95 **0.6911** ms, p99 **0.7821** ms; paired full-vs-apply-only mean difference **0.3251** ms (bootstrap 95% CI [0.2613, 0.3989] ms). Keep abstract, tables, and conclusion aligned to these values for the same run manifest. **L1** (twin stub and optional `--l1-twin`) is an **architectural extension**; primary results stay at L0 plus corpus statistics. We intentionally do **not** assert full-process record-replay determinism or plant/hardware behavioral equivalence under replay.

**Reproducibility.** From repo root, with `PYTHONPATH=impl/src` and `LABTRUST_KERNEL_DIR=kernel`. See [REPORTING_STANDARD.md](../../docs/REPORTING_STANDARD.md) and [RESULTS_PER_PAPER.md](../../docs/RESULTS_PER_PAPER.md). Use `--out` with the full file path (e.g. `datasets/runs/replay_eval/summary.json`), not a directory. Summary JSON includes `schema_version: p3_replay_eval_v0.2`, `run_manifest` (corpus_dir, overhead_runs, thin_slice_seeds, bootstrap_reps, platform, python_version), and `percentile_method: linear_hf7`. Replay levels L0/L1/L2; no claim to full determinism on hardware. Summary also includes **`corpus_space_summary`** (trace JSON sizes and `state_hash_after` field counts on the corpus) and **`process_peak_rss_bytes`** when the platform exposes peak RSS.

**Minimal run (under 20 min):** `python scripts/replay_eval.py --out datasets/runs/replay_eval/summary.json --overhead-curve --overhead-runs 5 --bootstrap-reps 100` then `python scripts/export_p3_paper_figures.py` then `python scripts/verify_p3_replay_summary.py --strict-curve`.

**Publishable run:** `--overhead-runs 20`, `--thin-slice-seeds 42,43,44,45,46` (multi-seed sensitivity), `--bootstrap-reps 500` or higher; run_manifest in summary.json. CI uses fewer replays and bootstrap reps; do not cite CI output as publishable tables.

- **Figure 0:** `python scripts/export_p3_paper_figures.py` writes `papers/P3_Replay/figures/p3_replay_levels_diagram.png` (and other paper figures). Alternatively: `python scripts/export_p3_replay_levels_diagram.py` (output `docs/figures/p3_replay_levels_diagram.mmd`) plus `python scripts/export_p3_replay_levels_figure.py` for the PNG.
- **Table 1 / Table 1b:** `python scripts/replay_eval.py` (as below), then `python scripts/export_replay_corpus_table.py --out-md papers/P3_Replay/generated_tables.md` (see [generated_tables.md](generated_tables.md)). Table 1b makes per-trace localization and corpus **space** metrics visible (on-disk trace bytes, per-event hash field counts, approximate diagnostic JSON size).
- **Table 2 / Table 3:** Same run; Table 2 from `overhead_stats` (full L0); Table 3 from `baseline_overhead` in summary.json (see [generated_tables.md](generated_tables.md)).
- **Figure 1:** `python scripts/plot_replay_overhead.py` (default output `docs/figures/p3_replay_overhead.png` and sidecar JSON; `export_p3_paper_figures.py` also copies these into `papers/P3_Replay/figures/`). Run replay_eval with `--overhead-curve` first.
- **Figure 2:** `python scripts/export_p3_first_divergence_timeline.py` (output `papers/P3_Replay/figures/p3_first_divergence_timeline.png` and sidecar JSON). Uses a representative trap row from `datasets/runs/replay_eval/summary.json` and the corresponding corpus trace to show committed vs replayed hashes, witness slice, and first-divergence localization.
- **Extra figures (TeX):** `python scripts/plot_p3_baseline_bars.py` and `python scripts/plot_p3_corpus_lanes.py` write baseline and corpus-lane bar charts under `papers/P3_Replay/figures/`.

**Canonical command path (publishable):**

1) `PYTHONPATH=impl/src python scripts/replay_eval.py --out datasets/runs/replay_eval/summary.json --overhead-curve --overhead-runs 20 --thin-slice-seeds 42,43,44,45,46 --bootstrap-reps 500`
2) `python scripts/export_replay_corpus_table.py --out-md papers/P3_Replay/generated_tables.md`
3) `PYTHONPATH=impl/src python scripts/export_p3_paper_figures.py`
4) `python scripts/verify_p3_replay_summary.py --strict-curve`

## 1. Motivation

**Vignette.** Two auditors replay the **same** ordered event list from an agentic lab workflow. Until `seq = 7`, recomputed control-plane state matches every recorded `state_hash_after`. At `seq = 7`, a hidden control-plane update (e.g. scheduler bookkeeping) differs from what the trace asserts; recomputation yields `got_hash` while the trace records `expected_hash`. Downstream enforcement may **deny** an action or fail a bundle check at a later `seq`, but the **first contract violation** is localized to `seq = 7`. That is the object of L0: not “we hashed a log line,” but **which sequence step** first breaks the declared control-plane contract.

Replayability is the missing glue between robotics, distributed systems, and safety cases. Logs alone are insufficient for verification; we need replayable causal programs suitable for audit, forensics, and reproducible evaluation, without overclaiming full determinism on hardware. The **primary** contribution is a contract-bounded replay story: detect and **localize** control-plane divergence with structured diagnostics, and quantify overhead against explicit baselines.

## 2. Replay levels and nondeterminism budgets

Replay is defined in levels (L0 control-plane default, L1 twin, L2 hardware-assisted).

**Figure 0 — Replay levels and pipeline.** L0 (control-plane replay), L1 (+ recorded observations), L2 (aspirational); pipeline from trace to replay engine to state_hash check to diagnostics. Regenerate with `python scripts/export_p3_replay_levels_diagram.py` (output `docs/figures/p3_replay_levels_diagram.mmd`). The primary guarantee is **nondeterminism detection and localization** relative to a declared replay contract. See `kernel/trace/REPLAY_LEVELS.v0.1.md` and determinism contract there. For L0, the budget is tight: control-plane outputs must match exactly. **L2 (hardware-assisted replay)** is aspirational; no L2 implementation or evaluation is included in this version (see REPLAY_LEVELS).

## 3. Trace format

Trace format: event ontology, causal links, time model. Schema: `kernel/trace/TRACE.v0.1.schema.json`. Events carry seq, ts, type, actor, payload, state_hash_after so that replay can recompute state and detect divergence.

## 4. Replay engine and divergence detection

**Definition (replay success / fidelity).** Under the declared **L0 contract** and hash semantics in `kernel/trace/REPLAY_LEVELS.v0.1.md`, **replay success** means the recomputed control-plane state matches **every** recorded `state_hash_after` and the trace `final_state_hash`. This is **not** behavioral equivalence of the physical plant, actuators, or hardware; it is **same abstract control-plane state** under the trace’s event ontology and transition rules. Failure is **replay_fail** at the first mismatching `seq` (or final hash), with diagnostics.

- **L0:** Deterministic scheduling: apply events in order, recompute state, compare state_hash_after and final_state_hash. On mismatch, emit structured diagnostics (seq, expected_hash, got_hash, event_type). CLI: `labtrust_portfolio replay --run-dir <dir>` or `replay <trace.json> --diagnostics`.
- **Baselines (for overhead and scope):** `replay_trace_apply_only` applies events with **no** hash checks (lower bound; no audit). `replay_trace_final_hash_only` checks only **final** state hash (verification without per-event localization). Both are timed in `replay_eval.py` alongside full L0.
- **L1 (architectural path, secondary to L0 corpus results in this paper):** L1 = L0 + twin config + deterministic twin replay (same state machine from trace); full simulator/physics twin is future work. The eval runs the **L1 stub** by default on the thin-slice trace (`l1_stub_ok`); **`--l1-twin`** runs an optional full L1 twin path across all thin-slice seeds, producing `l1_twin_summary` with multi-seed aggregate statistics (n_seeds, all_pass, mean_time_ms, stdev_time_ms, min/max) for supplementary material, not the primary empirical claim. L1 = **control-plane replay with recorded observations**, not physics replay. All observations come from the trace; no live simulator is required for the minimal L1 contract. Design in `kernel/trace/L1_TWIN_DESIGN.v0.1.md`: twin configuration identity (build_hash, model_params, env_seed), mapping from trace to twin interface. Corpus outcomes and localization statistics are **L0-first**; cite L1 stub/twin only as extension hooks.
- **Divergence detector:** Implemented in `replay_trace_with_diagnostics`; diagnostics integrated with evidence bundle (replay_diagnostics string).

**Comparison to record-replay systems.** We clarify the niche relative to full execution record-replay and log-only tools.

| System | Guarantee | Scope | Divergence detection | When our approach is preferable |
|--------|-----------|--------|----------------------|----------------------------------|
| RR (record-replay) | Full process determinism | Whole process, syscalls | Re-execution match | Control-plane audit without full-process determinism; no kernel/syscall capture. |
| Scribe / similar | Deterministic replay from log | Process + I/O | Replay from log | We need state_hash and localization (which event diverged), not only replay. |
| Log-only / best-effort | Events only | Events | None | Audit and forensics require *detection* of divergence and seq-level diagnostics. |
| **Our L0** | Control-plane state + state_hash | Events, state_hash_after | Yes: seq, expected_hash, got_hash | Control-plane audit, evidence for safety cases, no full-process determinism. |

RR and Scribe aim at full-process or I/O determinism for debugging; we do not. L0 targets **control-plane state** and **nondeterminism localization** with structured diagnostics (seq, expected_hash, got_hash) for audit and evidence bundles. Our approach is preferable when: (1) only control-plane behaviour must be verified (e.g. MADS evidence); (2) full-process determinism is infeasible or unnecessary; (3) divergence must be localized to a specific event for forensics.

**What we intentionally do not do (novelty packaging).** The contribution is **not** “hashing logs”: it is **replay levels** + a CPS **trace contract** + **per-event commitments** + **sequence-level localization** + **witness diagnostics** + **evidence-bundle fields** aligned to MADS admissibility. **Full record-replay (RR)** of the whole process or syscall stream is the wrong abstraction for **control-plane evidence** under our contract: we neither capture nor replay the full execution environment. **Log-only** pipelines without the trace contract cannot, under the declared semantics, provide **contract-level** localization of *which* event first violated `state_hash_after`. PeerReview-style RR and log-only tools remain complementary for debugging; they do not subsume L0’s audit story.

### 4.1 Worked example (four events, one divergence)

| seq | type | Note | Recorded `state_hash_after` (abbrev.) | Recomputed after apply |
|-----|------|------|----------------------------------------|-------------------------|
| 0 | task_start | Consistent | `5693228d…` | matches |
| 1 | task_end | Consistent | `a1b2c3d4…` | matches |
| 2 | task_start | **Divergence** | `00000000…` (wrong) | `deadbeef…` (example) |
| 3 | task_end | Not reached for pass/fail | — | — |

Replay stops at **seq = 2** and emits a diagnostic: `expected_hash` from the trace, `got_hash` from recomputation, plus `root_cause_category` and a **witness_slice** (events around seq 2). This is the localization semantics evaluated on the trap corpus.

## 5. Evaluation

- **Trace corpus:** Corpus traces are categorized as **synthetic_trap**, **synthetic_pass**, **field_proxy**, or **real_ingest** (see `corpus_category` in `per_trace` entries). (1) MAESTRO thin-slice (generated; primary seed 42 for main overhead tables; category `synthetic_pass`). (2) **Core synthetic trap traces:** nondeterminism (seq 0), reorder and timestamp_reorder (seq 1), hash_mismatch (seq 1). (3) **Expanded synthetic traps / passes:** `long_horizon_trap` (late mismatch, seq 20), `mixed_failure_trap` (first mismatch at seq 2; documents **first-failure** witness policy when a trace also contains latent inconsistencies later in the file), `benign_perturbation_pass` (irrelevant coordination noise; expected pass). (4) **Field-style pass traces** (`field_style_pass_*`, category `field_proxy`): TRACE-conformant synthetic traces from alternate thin-slice seeds, standing in for externally mapped logs (see [P3_REAL_TRACE_INGESTION.md](../../docs/P3_REAL_TRACE_INGESTION.md)); expected pass. (5) **Real-ingest bucket** (`real_bucket_*`, category `real_ingest`): Example template demonstrating structure for redacted production or partner-export traces mapped to TRACE schema; when ground-truth `expected_divergence_at_seq` is known, real-ingest rows can contribute to localization statistics; otherwise they are reported separately. Corpus is discovered from all `*_trace.json` / `*_expected.json` pairs under `bench/replay/corpus/`. Regenerate auxiliary traces with `PYTHONPATH=impl/src python scripts/generate_p3_replay_corpus_traces.py` or `python scripts/generate_real_bucket_example.py` if needed. **divergence_localization_confidence** is the fraction of **seq-expected** traps (rows with `expected_divergence_at_seq` set) where `divergence_at_seq` matches; **corpus outcome accuracy** (excellence metric) requires every corpus row to match expected pass/fail and, for traps, expected seq. **corpus_outcome_wilson_ci95** is a Wilson interval for the proportion of correct corpus outcomes. **Space / shape:** `corpus_space_summary` aggregates on-disk trace sizes and counts of `state_hash_after` fields; timing on the evaluated corpus should be read with **Figure 1** (`overhead_curve`, methodology `percentile_method`) as **control-plane evidence path cost**, not a universal scalability proof.

- **Multi-seed thin-slice family:** `--thin-slice-seeds` runs the overhead distribution on each seed; `multi_seed_overhead.across_seeds_mean_of_means_ms` and `across_seeds_stdev_of_means_ms` summarize variability of the **mean** replay time across seeds (mitigates overfitting overhead to one event mix).

- **Statistics:** Overhead uses empirical **linear** percentiles (Hyndman-Fan type 7, recorded as `percentile_method`). **p95** and **p99** are empirical; bootstrap 95% CIs for percentiles and paired **full vs apply-only** difference when `bootstrap_reps` > 0. **overhead_p99_ms** in excellence_metrics is empirical (not a normal approximation).

- **Table 1 — Corpus and fidelity.** Source: replay_eval `per_trace[]`. Regenerate with `python scripts/export_replay_corpus_table.py`.
- **Table 1b — Localization and corpus space.** Same script; columns include `divergence_detected`, `localization_matches_expected`, `localization_ambiguous` (reserved for multi-diagnostic cases), `trace_json_bytes`, `state_hash_after_count`, `diagnostic_payload_bytes_approx`, plus aggregate `corpus_space_summary` in the eval JSON.

- **Table 2 — Full L0 replay overhead.** Source: `overhead_stats` on primary thin-slice trace; N=`overhead_runs` (default 20). Includes mean, stdev, p95, p99, and CIs as in summary.json.

- **Table 3 — Baselines.** Source: `baseline_overhead` in summary: `apply_only_no_hash`, `final_hash_only`, `full_l0_witness_window_0`, and `full_vs_apply_only` (paired bootstrap CI for mean difference). See [generated_tables.md](generated_tables.md).

- **Figure 1 — Replay overhead vs trace size.** p95 replay time (ms) vs event count from `overhead_curve` (prefixes of the **primary** thin-slice trace). Points may include bootstrap CIs; plotted as error bars when present. Thin traces may yield a single curve point if `event_count` bins exceed trace length.

**Key results.** (1) `fidelity_pass` true on thin-slice. (2) Corpus: `success_criteria_met.corpus_expected_outcomes_met` true when all expected outcomes hold (pass traces replay ok; traps diverge at expected seq); corpus categories (synthetic_trap, field_proxy, real_ingest, synthetic_pass) are reported per trace in Table 1b. (3) L1 stub: `l1_stub_ok` when twin config present. (4) L1 twin: optional `--l1-twin` produces `l1_twin_summary` with multi-seed aggregate (all_pass, mean_time_ms across seeds); supplement or appendix. (5) Overhead: publishable defaults `--overhead-runs 20`, `--thin-slice-seeds 42,43,44,45,46` (multi-seed sensitivity), `--bootstrap-reps` 500+.

**Results summary (excellence metrics).** From summary.json: **divergence_localization_accuracy_pct** (corpus rows correct); **overhead_p99_ms** (empirical); **l1_stub_ok**; **witness_slices_present**. See [STANDARDS_OF_EXCELLENCE.md](../../docs/STANDARDS_OF_EXCELLENCE.md) (P3).

## 6. Evidence integration

Replay outcomes are admissible evidence (MADS): the evidence bundle records **`replay_ok`** and **`replay_diagnostics`** (and related verification flags) as structured fields, not merely a pointer to raw logs. Schema: `kernel/mads/EVIDENCE_BUNDLE.v0.1.schema.json`; builder API: `impl/src/labtrust_portfolio/evidence.py` (`build_evidence_bundle`, `verification.replay_ok`, `verification.replay_diagnostics`, `verification_mode`, optional `redaction_manifest`).

**Mini walkthrough (C4).** Given a TRACE file, L0 replay yields either success or `replay_fail` with diagnostics (seq, hashes, witness). The bundle sets `verification.replay_ok` from that outcome and `verification.replay_diagnostics` to a concise string (e.g. first diagnostic message). If schema validation passes, `verification.schema_validation_ok` is true; **`verification_mode`** (e.g. `evaluator` vs stricter modes) records how the bundle was checked. Conformance Tier 2 requires replay ok in the assurance story. **Formal + empirical:** The evidence-bundle verifier (required artifact presence, schema validity) is specified in the W3 wedge (`formal/lean/`); replay_ok and verification flags in the bundle align with that spec. L0 replay provides the empirical outcome the bundle records.

**Admissible evidence vs re-executable data.** L0 + diagnostics + bundle fields are aimed at **MADS admissibility** and third-party checking of **control-plane claims**, not at shipping a full re-executable dataset of the world. RR-style “re-run the universe” is out of scope; the contract states what must hold for **replay_ok**, and violations are **localized** for audit response.

## 7. Methodology and reproducibility

**Methodology:** Hypothesis: L0 replay detects and localizes divergence when state hashes mismatch. Metrics: replay fidelity per trace, divergence at seq, overhead distributions, baselines, multi-seed summary. **Threats to validity:** Internal: microbenchmark noise (mitigate with N=20, optional `--warmup`). External: synthetic and field-style proxy traces only; not a production fleet. Construct: overhead measures in-process replay cost, not distributed log ingest.

**Reproducibility:** Run `replay_eval.py` with `--out` as a **file** path. Then `python scripts/plot_replay_overhead.py`. Validate with `python scripts/verify_p3_replay_summary.py [--strict-curve]`. Integration tests run the eval and assert schema, corpus traps (including hash_mismatch and field_style_pass), overhead_curve when requested, and baselines. Optional release: copy to `datasets/releases/p3_replay_eval`. See `datasets/README.md`.

**Submission note.** Publishable tables use `--overhead-runs 20` and documented `run_manifest`. Before submit, Phase 3 checklist in [STATE_OF_THE_ART_CRITERIA.md](../../docs/STATE_OF_THE_ART_CRITERIA.md#3-submission-readiness-phase-3--hostile-reviewer-checklist). Consolidated multi-paper summary: [RUN_RESULTS_SUMMARY.md](../../datasets/runs/RUN_RESULTS_SUMMARY.md) when regenerated via `run_paper_experiments.py`.

## 8. Limitations

Scope and determinism levels: [EXPERIMENTS_AND_LIMITATIONS.md](../../docs/EXPERIMENTS_AND_LIMITATIONS.md). Per-paper:

- **Replay levels and scope:** L0 is implemented; L1 stub and L1 twin (`--l1-twin`) are available; L2 is design-only. We do not claim full hardware determinism.
- **K3 (fidelity bound):** If replay fidelity cannot be bounded clearly, claims narrow to **detection and localization only**. The design provides L0 pass/fail and structured diagnostics (seq, expected_hash, got_hash, witness_slice).
- **Synthetic and proxy traces:** MAESTRO thin-slice, hand-crafted traps, and field-style pass traces are not a live nondeterministic fleet. **`field_style_pass` / `field_style_pass_variant_b`:** TRACE-conformant **external-validity proxies** only; **not** redacted production logs and **not** claims of fleet representativeness (aligns with [P3_REAL_TRACE_INGESTION.md](../../docs/P3_REAL_TRACE_INGESTION.md)).
- **L1:** Full simulator/physics twin is not implemented; L1 = control-plane replay with recorded observations.
- **L2 (design):** Not implemented; see `kernel/trace/REPLAY_LEVELS.v0.1.md`.
- **Overhead:** In-process, small traces; multi-seed summary does not substitute for large-trace or distributed deployment benchmarks.
- **Corpus size:** Bounded trap set; **real-trace bucket** and long-horizon **production** traces are optional Tier-C extensions (ingestion note). **Tier C (optional):** ingest redacted real traces as a **separately labeled** `per_trace` category in eval summaries; expand `--l1-twin` multi-seed / second trace family before elevating L1 in the abstract; optional scripted incident workflow using bundle + conformance (not a user study unless explicitly scoped).

---

**Claims and backing.** See [claims.yaml](claims.yaml).

| Claim | Evidence |
|-------|----------|
| C1 (L0 verifiable + localization) | replay_eval summary, corpus, `replay_trace_with_diagnostics`, Table 1–3, verify script. |
| C2 (Nondeterminism detectable; baselines) | Trap traces, `baseline_overhead`, paired comparison. |
| C3 (Audit / reconstruction) | Diagnostics, witness slices; user-study not claimed. |
| C4 (Evidence integration) | Evidence bundle replay_ok, replay_diagnostics. |
