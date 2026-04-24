# Results per paper — Quick reference

This document explains what each paper (P0–P8) measures, where its results are written, and how to read them. All paths are relative to the repo root; results live under `datasets/runs/` unless noted. **Current state:** All nine papers are at Draft; Phase 3 (submission-readiness) passed. Next: submission prep per [PRE_SUBMISSION_CHECKLIST.md](PRE_SUBMISSION_CHECKLIST.md). **Consolidated snapshot:** [datasets/runs/RUN_RESULTS_SUMMARY.md](../datasets/runs/RUN_RESULTS_SUMMARY.md) is maintained for **P5, P6, and P8** key numbers (see that file). Other papers use their eval JSON under `datasets/runs/` and, where present, `papers/Px_.../generated_tables.md` (e.g. P3: `replay_eval/summary.json`, `papers/P3_Replay/generated_tables.md`). **Where this appears in the draft:** For each paper, tables and figures are cited in `papers/Px_.../DRAFT.md`; generated table content lives in `papers/Px_.../generated_tables.md` where present.

**Excellence metrics:** Eval summary JSONs may include an optional `excellence_metrics` block (see [STANDARDS_OF_EXCELLENCE.md](STANDARDS_OF_EXCELLENCE.md)). To print a one-line excellence summary across all papers: `python scripts/export_excellence_summary.py` (or `--json` for machine-readable output). Regenerate evals to populate excellence_metrics.

---

## P0 — MADS-CPS (machine-checkable minimum assurance bar)

**What it measures:** E1 conformance corpus (challenge set with injected faults; checker agreement; Tier 1 validates `maestro_report.json` against MAESTRO_REPORT v0.2). E2 restricted auditability (4-col verification-mode admissibility matrix). E3 replay link (independent verifier; **`--standalone-verifier`** recommended for publishable runs). E4 algorithm-independence (two adapters, same artifact interface) plus admissibility-vs-productivity export. E5 model evolution / upstream-version-shift evaluation under fixed interface semantics.

**Result locations (canonical workshop package):**
- `papers/P0_MADS_CPS/kdd_workshop/artifacts/p0_e1_corpus_table.md` — E1 manuscript-facing corpus table
- `papers/P0_MADS_CPS/kdd_workshop/artifacts/p0_e2_admissibility_matrix.md` — E2 admissibility table
- `papers/P0_MADS_CPS/kdd_workshop/artifacts/e3_summary.json` and `papers/P0_MADS_CPS/kdd_workshop/artifacts/p0_e3_variance.json` — E3 replay-link summary and variance
- `papers/P0_MADS_CPS/kdd_workshop/artifacts/p0_e4_controller_matrix.json` — E4 controller matrix payload
- `papers/P0_MADS_CPS/kdd_workshop/artifacts/p0_e4_admissibility_vs_productivity.json` / `.csv` — E4 admissibility-vs-productivity summary
- `papers/P0_MADS_CPS/kdd_workshop/artifacts/p0_e4_coordination_shock_focus.json` / `.csv` — focused E4 slice for `coordination_shock` + `rep_cps_scheduling_v0`
- `papers/P0_MADS_CPS/kdd_workshop/artifacts/controller_divergence_table.md` and `papers/P0_MADS_CPS/kdd_workshop/artifacts/claim_matrix.md` — E4 claim-guardrail exports
- `papers/P0_MADS_CPS/kdd_workshop/artifacts/p0_e5_model_evolution.json` — E5 synthetic version-shift summary and pairwise deltas vs V0
- `papers/P0_MADS_CPS/kdd_workshop/artifacts/p0_e5_model_evolution_per_seed.jsonl` — E5 per-seed source rows (non-empty, committed)
- `papers/P0_MADS_CPS/kdd_workshop/artifacts/p0_e5_model_evolution_summary.csv` — E5 per-version compact table
- `papers/P0_MADS_CPS/kdd_workshop/artifacts/p0_e5_model_evolution_by_cell.json` / `.csv` — E5 by-cell export by version/controller/scenario/regime
- `papers/P0_MADS_CPS/kdd_workshop/artifacts/p0_e5_coordination_shock_focus.json` / `.csv` — focused E5 comparison rows for `rep_cps_scheduling_v0` + `coordination_shock`

**How to read:**
- **E3:** tasks_completed_mean, p95_latency_ms_mean, all_match, run_manifest; --standalone-verifier uses verify_maestro_from_trace.py as separate process.
- **E1:** corpus_manifest.json: case_id, fault_injected, expected_tier, observed_tier, agreement. Table 1: build_p0_conformance_corpus.py, export_e1_corpus_table.py.
- **E2:** 4-col verification-mode admissibility matrix; redacted trace preserves schema and integrity, replay_ok false. export_e2_admissibility_matrix.py.
- **E4:** controller-matrix summaries and per-seed diagnostics; use raw + normalized + per-seed + diagnostics artifacts. `export_p0_table3.py` prefers strong replay from `p0_e4_raw_summary.json` and requires E3 strong fields. In the current publishable run, `coordination_shock` on `rep_cps_scheduling_v0` shows MAESTRO-core divergence (`p0_e4_diagnostics.json`) even when high-level metrics remain close.
- **E4 focused validation package:** use `export_p0_e4_controller_divergence_table.py` for the `coordination_shock + rep_cps_scheduling_v0` comparison row set, and `export_p0_e4_claim_matrix.py` for overclaim guardrails. Semantics note for the zero-task anomaly row: `docs/P0_E4_COORDINATION_SHOCK_NOTE.md`. Productivity/admissibility split is explicit via per-seed `productive_success` / `safe_nonproductive` and summary `productive_success_rate` / `safe_nonproductive_rate`.
- **E5:** compare synthetic version conditions (V0 stable, V1 benign update, V2 regressive update) under fixed scenarios/regimes and fixed artifact interface semantics. Use `p0_e5_model_evolution_by_cell.json` and `p0_e5_coordination_shock_focus.json` for reviewer-legible local rows, then `pairwise_deltas_vs_v0` in `p0_e5_model_evolution.json` for bounded global deltas.
- **Verification mode:** verification_mode (public | evaluator | regulator); kernel/mads/VERIFICATION_MODES.v0.1.md.

**Tables and figures:** Table 1: build_p0_conformance_corpus.py, export_e1_corpus_table.py. Table 2: e2_redaction_demo.py, export_e2_admissibility_matrix.py. Table 3: run_p0_e4_controller_matrix.py, export_p0_table3.py (strong replay preference: E4 raw baseline rows, then E3 strong replay). E4 focused tables: export_p0_e4_controller_divergence_table.py, export_p0_e4_claim_matrix.py, export_p0_e4_admissibility_vs_productivity.py. E5 summary table: run_p0_e5_model_evolution.py (`p0_e5_model_evolution_summary.csv`). Figures 1-3: export_p0_assurance_pipeline.py, export_p0_tier_lattice.py, export_p0_redaction_figure.py. Per-seed E3: export_e3_table.py. plot_e3_latency.py. build_p0_conformance_summary.py. Workshop packaging: `papers/P0_MADS_CPS/kdd_workshop/`.

---

## P1 — Coordination Contracts

**Contribution / headline:** Trace-derived contract validation with 54+ corpus sequences (tiered benchmark including adversarial cases); timestamp-only and ownership-only baseline comparison; ablation by failure class with named comparators (occ_only, lease_only, lock_only, naive_lww); per-class detection metrics with uncertainty intervals; async stress robustness; transport parity with confidence metrics; gatekeeper integration. For a compact, presentable snapshot of key numbers, see [RUN_RESULTS_SUMMARY.md](../datasets/runs/RUN_RESULTS_SUMMARY.md) (generated by run_paper_experiments.py).

**What it measures:** Whether the contract validator correctly allows/denies event sequences (54+ sequence challenge corpus: positive controls, split-brain, stale write/reorder, boundary, long-horizon, adversarial including cross-key interleaving, delayed release/reassignment, concurrent controller races). Correctness by exact per-event verdict match. Named comparators (OCC/lease/lock/LWW proxies) in `ablation` / `ablation_by_class`; per-class detection metrics in `detection_metrics_by_class` with uncertainty intervals. Scale test and optional scale sweep; async stress robustness (delay/skew/reorder sweeps in stress_results.json); transport-invariance parity (multi-sequence, event-log vs LADS-shaped reference paths with parity_confidence); resource and cost proxy; gatekeeper denies release when contract invalid; lab-aligned instrument state machine.

**Result locations:**
- `datasets/runs/contracts_eval/eval.json` — corpus sequences, detection_ok (exact verdict vector), baseline_* fields (timestamp_only, ownership_only, accept_all, occ_only, lease_only, lock_only, naive_lww), ablation, ablation_by_class, detection_metrics, **detection_metrics_by_class** (TP/FP/FN, precision, recall, F1 per inferred failure class), latency_percentiles_us (event-level median/p95/p99 and median_ci95, p95_ci95, p99_ci95), resource_and_cost (wall_clock_sec, events_per_sec_overall, cost_proxy). run_manifest includes script_version, corpus_fingerprint. Optional with `--baseline`: `violations_would_apply_without_validator`.
- `datasets/runs/contracts_eval/scale_test.json` — when run with `--scale-test` (total_events, denials, total_time_sec, time_per_write_us, events_per_sec); with `--scale-test-runs 5`: events_per_sec_mean/stdev, time_per_write_us_mean/stdev, resource_and_cost.
- `datasets/runs/contracts_eval/scale_sweep.json` — when run with `--scale-sweep 1000,10000,100000` (sweep_results per size, run_manifest).
- `datasets/runs/contracts_eval/transport_parity.json` — from `scripts/contracts_transport_parity.py`: **`parity_ok_all`**, **`per_sequence[]`** (each: `parity_ok`, `event_log_verdicts`, `lads_shaped_verdicts`), **`parity_confidence`** (matching_events, total_events_checked, parity_rate), `run_manifest.sequences`; default multi-sequence stems configurable via `--sequences`.

**How to read:**
- `run_manifest`: corpus_sequences, corpus_sequence_count, corpus_dir, script. `success_criteria_met.all_detection_ok`: true when all sequences have detection_ok. `excellence_metrics`: corpus_detection_rate_pct, overhead_p99_us, baseline_margin_denials.
- `sequences[]`: each has `sequence`, `detection_ok` (true = violations denied as expected), `allows`, `denials`, `time_per_write_us`.
- `violations_denied_with_validator`: total violations correctly denied.
- `baseline_*_denials` / `baseline_*_missed`: timestamp_only, ownership_only, accept_all, occ_only, lease_only, lock_only, naive_lww (comparator framing; occ/lease align with timestamp-only on this corpus; lock with ownership-only; naive_lww with accept-all).
- `ablation`: full_contract, timestamp_only, ownership_only, occ_only, lease_only, lock_only, accept_all, naive_lww with violations_denied and violations_missed.
- `detection_metrics`: true_positives, false_positives, false_negatives, precision, recall, f1 (per-event, expected_verdicts as ground truth).
- `detection_metrics_by_class`: same metrics per inferred class (split_brain, stale_write, reorder, unknown_key, control). Rows include all classes present in the corpus; **control** may have `precision`/`recall`/`f1` as JSON `null` when there are no expected denials and no false denials (exported as `n/a` in Table 3).
- `latency_percentiles_us`: median, p95, p99 from event-level samples; median_ci95, p95_ci95, p99_ci95 (bootstrap 95% CI); event_level_n.
- `ablation_by_class`: per failure class (split_brain, stale_write, reorder, unknown_key, control), each policy's violations_denied and violations_missed.
- `resource_and_cost`: wall_clock_sec, process_time_sec, rss_kb, events_per_sec_overall, cost_proxy (assumption, events_per_dollar when LABTRUST_COST_PER_HOUR set).
- **Gatekeeper:** `allow_release(run_dir, check_contracts=True)` runs contract validator on trace; if any event denied, release is blocked. CLI: `labtrust_portfolio release-dataset --check-contracts <run_dir> <release_id>` enables strict PONR gating; default is conformance-only. See `impl/.../gatekeeper.py` (`check_contracts_on_trace`).
- **State machine:** `bench/contracts/README.md` documents alignment of single-writer contract with `instrument_state_machine.py` (idle/running transitions). Contract option `use_instrument_state_machine: true` enforces it.
- **Trace-derivability:** All contract predicates are computed from trace alone (no privileged hidden state). See `docs/P1_TRACE_DERIVABILITY.md`. Kill criterion K1: if a predicate required hidden state, design loses portability.
- **trigger_met:** In success_criteria_met when adapter runs: trigger_met = adapter_parity and robust_beats_naive (or robust_beats_naive when no adapter).

**Tables and figures:** `python scripts/export_contracts_corpus_table.py` (Table 1, ablation by class with all comparators, Table 3 from `detection_metrics_by_class`); `python scripts/export_p1_appendix_tex.py` (LaTeX longtable for `DRAFT.tex` appendix); `python scripts/export_p1_contract_flow.py` (Mermaid source `docs/figures/p1_contract_flow.mmd`); `python scripts/render_p1_flow_figure.py` (PDF/PNG `papers/P1_Contracts/figures/contracts_flow.{pdf,png}`); `python scripts/plot_contracts_scale.py` (throughput vs event count, now reads existing `scale_sweep.json`/`scale_test.json` unless `--rerun`); `python scripts/plot_p1_paper_figures.py` (latency percentiles, comparator heatmap with cell annotations, corpus coverage with adversarial family, optional stress summary PNGs + JSON sidecars under `docs/figures/`). One-shot: `python scripts/generate_paper_artifacts.py --paper P1`.

---

## P2 — REP-CPS (safety-gated profile for sensitivity sharing)

**Contribution / headline:** Safety-gated, typed, authenticated, rate-limited sensitivity-sharing profile; offline robust aggregation reduces observed compromise-induced bias vs naive averaging; **scoped** adapter parity with centralized on non-scheduling scenarios; **rep_cps_scheduling_v0** demonstrates task-level scheduling dependence on gated aggregate under spoof stress (`scheduling_dependent_eval`). Contribution is profile + MAESTRO harness; live buses and all real schedulers remain future work. For a compact snapshot, see [RUN_RESULTS_SUMMARY.md](../datasets/runs/RUN_RESULTS_SUMMARY.md) (generated by run_paper_experiments.py).

**What it measures:** REP-CPS adapter vs centralized baseline; robust (trimmed-mean, clipping, median_of_means) vs naive aggregation under compromise; delay_fault_prob sweep (default: 0,0.05,0.1,0.2); optional drop_completion_prob sweep via `--drop-sweep` (default: 0.02 single value); sybil, magnitude, and trim-fraction sweeps; resilience envelope; latency/cost; safety-gate campaign; profile ablation; **per_scenario** summaries (aggregated metrics per scenario_id); **excellence_metrics** with comparison statistics (difference_mean, difference_ci95, paired_t_p_value, power_post_hoc on non-scheduling scenarios); **freshness_replay_evidence**, **sybil_vs_spoofing_evidence**, **messaging_sim**, **dynamic_aggregation_series**; scheduling-dependent eval.

**Result locations:**
- `datasets/runs/rep_cps_eval/summary.json` — adapter comparison, aggregation_under_compromise, delay_sweep (with optional drop_completion_prob_sweep), per_scenario (aggregated metrics per scenario_id), aggregation_variants, sybil_sweep, magnitude_sweep, trim_fraction_sweep, resilience_envelope, latency_cost, profile_ablation, safety_gate_denial (including safety_gate_campaign), scheduling_dependent_eval, freshness_replay_evidence, sybil_vs_spoofing_evidence, messaging_sim, dynamic_aggregation_series, n_sensitivity, excellence_metrics (including comparison statistics: difference_mean, difference_ci95, paired_t_p_value, power_post_hoc).
- `datasets/runs/rep_cps_eval/safety_gate_denial.json` — claim that REP output cannot directly trigger actuation; denial_trace_recorded; safety_gate_campaign (pass_count_rep_cps, deny_count_unsecured, etc.).

**How to read:**
- `run_manifest`: seeds, scenario_ids (default includes **rep_cps_scheduling_v0**), delay_fault_prob_sweep, drop_completion_prob_sweep (when `--drop-sweep` used), aggregation_steps_used, script. `success_criteria_met`: **adapter_parity** on non-scheduling-dependent runs only (`adapter_parity_scope`); **scheduling_scenario_task_divergence** when scheduling scenario present; **robust_beats_naive**; **trigger_met**. `excellence_metrics`: bias_reduction_pct; comparison statistics (difference_mean, difference_ci95, paired_t_p_value, power_post_hoc) on non-scheduling scenarios. See `docs/CONDITIONAL_TRIGGERS.md` (P2).
- Effect size: `excellence_metrics.bias_reduction_pct` (when aggregation_under_compromise has bias_naive > 0); comparison stats on scoped pairs.
- `rep_cps_tasks_completed_mean` vs `centralized_tasks_completed_mean`: **globally** may differ when scheduling scenario is included; interpret **scheduling_dependent_eval** and **delay_sweep** per scenario_id.
- `aggregation_under_compromise`: `honest_only_aggregate`, `with_compromise_robust_aggregate`, `with_compromise_naive_aggregate`; `bias_robust` < `bias_naive` means robust aggregation reduces observed bias under Byzantine inputs in the evaluated harness.
- `profile_ablation[]`: per variant (no_auth, no_freshness, no_rate_limit, no_robust_aggregation, no_safety_gate, full_profile), `bias`, `aggregate`, `failure`; Table 6 in generated_tables.md.
- `latency_cost`: wall_sec_*_mean/p95 per policy, policy_overhead_vs_centralized_ms_*, aggregation_compute_ms_mean/p95/p99; Table 5. Figure 4: `python scripts/plot_rep_cps_latency.py`.
- `resilience_envelope`: safe_operating_region_n_compromised_max, failure_boundary_n_compromised, magnitude_sweep_robust_beats_naive, trim_sweep_robust_beats_naive; Table 7.
- `magnitude_sweep[]`, `trim_fraction_sweep[]`: adversarial magnitude and trim-fraction sweeps; robust_beats_naive per row.
- `safety_gate_denial.safety_gate_campaign`: pass_count_rep_cps, deny_count_rep_cps, deny_count_unsecured; denial_trace_recorded true when unsecured runs produce gate denial.
- `aggregation_variants[]`: per method (trimmed_mean, median, clipping, median_of_means), `bias`, `max_influence_per_compromised_agent`.
- `sybil_sweep[]`: per `n_compromised`, `bias_robust`, `bias_naive`, `robust_beats_naive`.
- `delay_sweep[]`: per delay_fault_prob, tasks_completed mean/stdev and centralized baseline.
- `n_sensitivity`: seed_count_used, note on N=20/N=30 stability; run `sensitivity_seed_sweep.py --eval rep_cps --ns 20,30` to verify.
- **Multi-step aggregation (optional):** When `--aggregation-steps > 1`, summary includes `convergence_steps_to_convergence_mean`, `convergence_steps_to_convergence_stdev`, `convergence_achieved_rate`; per-seed `rep_cps_steps_to_convergence`. Table 4: `python scripts/export_rep_cps_convergence_table.py` (from summary.json).
- `rep_cps_naive_tasks_completed_mean`, `rep_cps_unsecured_tasks_completed_mean`: naive-in-loop and unsecured baselines.

---

## P3 — Replay (replay levels and nondeterminism detection)

**Contribution / headline:** L0 replay with divergence localization; baselines (apply-only, final-hash-only, witness ablation); empirical percentiles with bootstrap CIs; multi-seed thin-slice family; field-style pass trace for external-validity proxy; L1 stub and optional L1 twin. For a compact snapshot, see [RUN_RESULTS_SUMMARY.md](../datasets/runs/RUN_RESULTS_SUMMARY.md) when regenerated by run_paper_experiments.py.

**What it measures:** L0 fidelity on thin-slice; corpus traps (core + long-horizon + mixed-failure), benign pass, two field-style pass families (`field_style_pass_*`), real-ingest bucket example (`real_bucket_example`); `per_trace` with **`corpus_category`** (synthetic_trap, field_proxy, real_ingest, synthetic_pass), localization fields and **`corpus_space_summary`** (trace bytes, `state_hash_after` counts, diagnostic payload size proxy); `baseline_overhead` (paired full vs apply-only); `multi_seed_overhead` across `--thin-slice-seeds`; `overhead_stats` with `p95_ms`, `p99_ms`, CIs (`percentile_method: linear_hf7`); `corpus_outcome_wilson_ci95`; overhead curve with optional p95 CI per bin. **L1** stub and **L1 twin** (`--l1-twin` produces **`l1_twin_summary`** with multi-seed aggregate: n_seeds, all_pass, mean_time_ms, stdev_time_ms, min/max_time_ms). **L2** aspirational. Schema: `schema_version: p3_replay_eval_v0.2`. Validation: `scripts/verify_p3_replay_summary.py`. Tables: DRAFT and `papers/P3_Replay/generated_tables.md` (Table 1, **Table 1b** via `export_replay_corpus_table.py --out-md`).

**Result location:** `datasets/runs/replay_eval/summary.json`. Use `--out datasets/runs/replay_eval/summary.json` (file path, not directory).

**How to read:**
- `run_manifest`: corpus_dir, overhead_runs, warmup_iterations, thin_slice_seeds, primary_thin_slice_seed, bootstrap_reps, percentile_method, platform, python_version. `success_criteria_met`: fidelity_pass, corpus_expected_outcomes_met, corpus_divergences_detected (backward-compatible alias). `excellence_metrics`: divergence_localization_accuracy_pct (all corpus rows), overhead_p99_ms (empirical), l1_stub_ok, witness_slices_present.
- `divergence_localization_confidence` / `divergence_localization_wilson_ci95`: seq-localization traps only. `corpus_outcome_wilson_ci95`: Wilson CI for proportion of corpus rows matching expected outcome.
- `baseline_overhead`: apply_only_no_hash, final_hash_only, full_l0_witness_window_0, full_vs_apply_only.
- `overhead_curve[]`: `p95_replay_ci95_lower_ms`, `p95_replay_ci95_upper_ms` when bootstrap_reps > 0.
- **L1:** `bench/replay/README.md`, `kernel/trace/REPLAY_LEVELS.v0.1.md`; `--l1-twin` for twin re-run timing in `l1_twin_replay_time_ms` and **`l1_twin_summary`** (multi-seed aggregate statistics across all thin-slice seeds).

**Figure:** `python scripts/plot_replay_overhead.py` (optional error bars from curve CIs; output `docs/figures/p3_replay_overhead.png`).

---

## P4 — CPS-MAESTRO (fault sweep and baselines)

**Contribution / headline:** Scenario-driven benchmark with fault sweep, recovery metrics, anti-gaming, and adapter comparison. For a compact, presentable snapshot of key numbers, see [RUN_RESULTS_SUMMARY.md](../datasets/runs/RUN_RESULTS_SUMMARY.md) (generated by run_paper_experiments.py).

**What it measures:** tasks_completed and p95 latency under fault settings (no_drop, drop_005, delay_01, calibration_invalid_01, etc.) across scenarios; recovery metrics (steps_to_completion_after_first_fault, tasks_completed_after_fault) when faults occur; Centralized vs Blackboard vs RetryHeavy adapter comparison; anti-gaming (always_deny, always_wait score poorly); adapter cost.

**Result locations:**
- `datasets/runs/maestro_fault_sweep/multi_sweep.json` — per-scenario, per-setting sweep (mean/stdev over seeds); fault_settings include lab-real `calibration_invalid_01`; per-setting summaries may include `steps_to_completion_after_first_fault_mean/stdev`, `tasks_completed_after_fault_mean/stdev`.
- `datasets/runs/maestro_fault_sweep/<scenario>/<setting>_summary.json` — per-scenario, per-setting (e.g. no_drop_summary.json, drop_02_summary.json) with recovery metrics when applicable.
- `datasets/runs/maestro_antigaming/antigaming_results.json` — always_deny (tasks_completed 0), always_wait (1); conclusion that pathological strategies score poorly.
- `bench/maestro/adapter_costs.json` — loc_estimate, hours_estimate per adapter (Centralized, Blackboard, RetryHeavy).
- `bench/maestro/baseline_summary.json` — Centralized vs Blackboard vs RetryHeavy table (and baseline_results.md)

**How to read:**
- In `multi_sweep.json`: `run_manifest` (seeds, seed_count, scenarios, fault_settings); `success_criteria_met.run_manifest_present`; `per_scenario[]` → `sweep[]` with `setting`, `tasks_completed_mean/stdev`, `p95_latency_ms_mean/stdev`, `p95_latency_ms_p99`, `per_run[]`. Optional `excellence_metrics`: fault_coverage, scenario_diversity, variance_reported, n_seeds_per_setting; recovery vs no_drop can be reported as improvement_pct or baseline_margin. In `antigaming_results.json`: excellence_metrics (anti_gaming_margin_tasks, legitimate_safe_min, pathological_max_tasks_completed).
- Anti-gaming: `antigaming_results.json` has `success_criteria_met.antigaming_penalized` (always_deny/always_wait tasks_completed < 2), `scoring_proof` (explicit comparison: legitimate_safe_min > always_wait > always_deny; unsafe success not rewarded). Strategies must score worse than legitimate operation (see `bench/maestro/SCENARIO_SPEC.md`).
- Baselines: Centralized, Blackboard, RetryHeavy (RetryHeavy is architecturally distinct: per-task retries); compare tasks_completed and p95_latency_ms per seed. Recovery metrics in fault-sweep output: steps_to_completion_after_first_fault, tasks_completed_after_fault (when faults occur). For publishable tables use `--seeds 20`; see `docs/REPORTING_STANDARD.md`. Warehouse and traffic scenarios are minimal (few tasks); not full-scale benchmarks. Figure 1 is a recovery proxy (tasks_completed vs fault setting), not MTTR or time-to-safe-state.

**Tables and figure:** `scripts/export_maestro_tables.py` from multi_sweep.json and baseline_summary.json. `python scripts/plot_maestro_recovery.py` (recovery proxy: tasks_completed vs fault setting; output `docs/figures/p4_recovery_curve.png`).

---

## P5 — Scaling laws (held-out scenario prediction)

**Contribution / headline:** Publishable **7200-row** grid (six `real_world` scenarios × five coordination regimes × agent counts 1/2/4/8 × fault labels `no_drop` / `drop_005` × 30 seeds) with ridge-stabilized linear regression on the default P5 feature vector, multiple LOO protocols, sensitivity over seed caps, recommendation/regret metrics, and a frozen **regime × agent** summary for title-level scaling deltas. **`success_criteria_met.trigger_met` is protocol-specific:** on the freeze recorded in `papers/P5_ScalingLaws/DRAFT.md` (`run_manifest.commit` in `scaling_eval/heldout_results.json`), leave-one-family-out can be **true** while leave-one-scenario-out is **false** (regression fails vs the num-tasks bucket baseline). See `papers/P5_ScalingLaws/generated_tables.md` and `datasets/runs/scaling_summary/regime_agent_summary.json`.

**What it measures:** Out-of-sample MAE for `tasks_completed` (and optional `secondary_targets`) under scenario, family, regime, agent-count, and fault-setting holdouts; admissible vs oracle baselines; strict nulling when any fold cannot fit regression; exploratory `scaling_fit`.

**Result location:** `datasets/runs/scaling_eval/heldout_results.json` and sibling dirs `scaling_eval_family`, `scaling_eval_regime`, `scaling_eval_agent_count`, `scaling_eval_fault`; `sensitivity_sweep/scaling_sensitivity.json`; `scaling_recommend/recommendation_eval.json`; `scaling_summary/regime_agent_summary.json`. Produced by `run_paper_experiments.py --paper P5` or the individual scripts in `papers/P5_ScalingLaws/README.md`.

**How to read:**
- `run_manifest`: runs_dir, scenario_ids, held_out_scenarios, holdout_mode, train_n_total, test_n_total, script. `success_criteria_met`: beat_baseline_out_of_sample, beat_per_scenario_baseline, trigger_met (conditional paper; see `docs/CONDITIONAL_TRIGGERS.md`). Optional `excellence_metrics`: out_of_sample_margin_vs_global_baseline, ci_width_95_baseline_mae, beat_baseline_out_of_sample, scenario_coverage.
- `held_out_results[]`: per fold, `baseline_mae`, `feat_baseline_mae`, `regression_mae`, `regression_pi_coverage_95`, `stump_mae`, `actuals_mean`, `train_n`, `test_n`.
- `secondary_targets`: compact summaries for extra response keys (e.g. coordination_tax_proxy, error_amplification_proxy).
- `overall_baseline_mae`, `overall_feat_baseline_mae`, `overall_regression_mae`, `overall_stump_mae`: aggregate; when regression is skipped (e.g. train_n < k or singular), summary includes `regression_skipped_reason`; export_scaling_tables prints N/A with footnote. Feature/regression/stump beating global mean = “beat baseline out-of-sample.”
- `overall_*_mae_ci95_lower/upper`: 95% CI for MAE; regression row uses CI across held-out folds when all folds fit.
- `mean_regression_pi_coverage_95`: exploratory calibration (train-residual intervals).
- `scaling_fit`: `scaling_exponent`, `scaling_r2`, `n_used` (exploratory log-log fit).
- **Title/claims:** If scaling-law stability is not demonstrated, use "empirical predictors" and state scaling laws are exploratory.
- `overall_collapse_rate`, per-result `test_collapse_rate`: collapse (e.g. tasks_completed below threshold) if defined.

**Tables:** `scripts/export_scaling_tables.py`.

---

## P6 — LLM Planning (red-team and adapter latency)

**Contribution / headline:** Typed-plan firewall and expanded CPS-oriented suites with OWASP alignment; real-LLM table (Table 1b, pass_rate and Wilson CI); baseline 3-way (gated vs weak vs ungated); denial-trace statistics; containment only (no elimination claim). Latest camera-ready snapshot (`llm_eval_camera_ready_20260424`): synthetic red-team 15/15 pass, confusable 6/6 pass, jailbreak-style 4/4 pass, adapter latency p95 mean 32.07 ms, baseline denials gated/weak/ungated = 60/60/0, and OpenAI full-suite N=3 with gpt-4.1-mini and gpt-4.1 each 75/75 (CI95 [95.1, 100.0]). Supplementary isolated GPT-5.x post-patch runs (not merged into canonical Table 1b): `gpt-5.4` 73/75 (97.3, CI95 [90.8, 99.3]) and `gpt-5.4-pro` 54/75 (72.0, CI95 [61.0, 80.9]). See [RUN_RESULTS_SUMMARY.md](../datasets/runs/RUN_RESULTS_SUMMARY.md).

**What it measures:** Red-team: policy blocks disallowed tools and allows allowed ones. Confusable deputy: adversarial args (privilege) blocked. Jailbreak-style: prompt-injection args blocked. Validator stack: allow_list + safe_args + ponr_gate (+ privilege heuristic). E2E denial trace: planner proposes unsafe, validator blocks, recovery safe. Adapter latency: p95 and wall time over 3 scenarios, 20 seeds. **Real-LLM (state-of-practice):** `--real-llm --real-llm-runs N --real-llm-suite full` runs repeated API calls per case; `red_team_results.json` `real_llm_models[]` has per-case pass_rate_pct, 95% Wilson CI, latency_mean_ms ± stdev; overall pass_rate_pct and Wilson CI. Latest OpenAI camera-ready full-suite snapshot (`llm_eval_camera_ready_20260424`): both gpt-4.1-mini and gpt-4.1 are 75/75 with CI95 [95.1, 100.0]. **Prime Inference:** `--real-llm-provider prime` uses `https://api.pinference.ai/api/v1` with `PRIME_INTELLECT_API_KEY` (fallback `PRIME_API_KEY`) and optional `PRIME_TEAM_ID`; treat as separately labeled denominator. **Baseline:** `--run-baseline` runs gated vs weak vs ungated; `baseline_comparison.json` (denial_count_gated/weak/ungated, tasks_completed_mean per mode). **Argument-level (safe_args ablation):** `--run-baseline --baseline-plan args_unsafe` uses allow-listed tool with path-traversal args; writes `baseline_comparison_args.json`; gated denies, weak/ungated allow. Export: `export_p6_baseline_table.py --baseline-file baseline_comparison_args.json`. **Denial stats:** `--run-adapter --denial-stats` writes `denial_trace_stats.json`. OWASP LLM Top 10 coverage: [docs/P6_OWASP_MAPPING.md](P6_OWASP_MAPPING.md).

**Result locations:**
- `datasets/runs/llm_eval/red_team_results.json` — red-team cases (15), plus embedded jailbreak_style (4); when --real-llm: `real_llm` or `real_llm_models[]` (full suite: 25 cases/model by default with `--real-llm-suite full`); run_manifest includes timestamp_iso, evaluator_version, policy_version; real-LLM run_manifest adds prompt_template_hash and suite_mode; per-case attribution (allow_list_only, safe_args_only, ponr_gate_only, both, admitted) and denial_by_layer; when 2+ models: cross_model_summary (per_case_pass_rates, per_case_variance, disagreement_matrix); argument-level cases with n_runs>1 store run_details (raw_response, parsed_step, pass) for failure analysis
- `datasets/runs/llm_eval/confusable_deputy_results.json` — confusable deputy cases (6); run_manifest, attribution, denial_by_layer
- `datasets/runs/llm_eval/e2e_denial_trace.json` — claim and example: planner proposed unsafe, validator blocked, recovery safe
- `datasets/runs/llm_eval/adapter_latency.json` — when run with `--run-adapter` (default: 3 scenarios, 20 seeds); optional denial_stats when --denial-stats; optional latency_decomposition (validation_ms, capture_total_ms p50/p95/p99) when --latency-decomposition
- `datasets/runs/llm_eval/baseline_comparison.json` — when run with `--run-baseline` (gated vs weak vs ungated, tool-level unsafe)
- `datasets/runs/llm_eval/baseline_comparison_args.json` — when run with `--run-baseline --baseline-plan args_unsafe` (argument-level path-traversal; safe_args ablation)
- `datasets/runs/llm_eval/baseline_benign.json` — when run with `--run-baseline --baseline-plan benign` (benign_acceptance_rate, false_positive_count per mode)
- `datasets/runs/llm_eval/denial_trace_stats.json` — when run with `--run-adapter --denial-stats`
- `datasets/runs/llm_eval/p6_artifact_hashes.json` — from export_p6_artifact_hashes.py; artifacts SHA256 and reproducibility_table (table_id, artifact, model_id, timestamp_iso, seed, prompt_template_hash, evaluator_version, policy_version, artifact_hash)
- `datasets/runs/llm_eval/p6_failure_analysis.json` — from export_p6_failure_analysis.py (after real-LLM run with run_details); rows and by_case_mode for argument-level failure taxonomy
- Optional: p6_concurrency_benchmark.json, p6_capture_ablation.json, p6_storage_benchmark.json, p6_cost_model.json, p6_policy_sweep.json, p6_replanning_benchmark.json, p6_adaptive_results.json (scripts: p6_concurrency_benchmark.py, p6_capture_ablation.py, p6_storage_benchmark.py, p6_cost_model.py, p6_policy_sweep.py, p6_replanning_benchmark.py, p6_adaptive_suite_run.py)

**How to read:**
- **Red-team:** `run_manifest` (red_team_cases, script); `success_criteria_met.red_team_all_pass`, `trigger_met`. `cases[]`: expected_block, actually_blocked, pass. **Real-LLM:** When n_runs_per_case > 1: real_llm.cases[] (case_id, expected_block, n_runs, pass_count, pass_rate_pct, pass_rate_ci95_lower/upper, latency_mean_ms, latency_stdev_ms); pass_rate_pct, pass_rate_ci95_* overall; all_block_unsafe_pass, total_latency_ms. When n_runs_per_case == 1: actually_blocked, pass, latency_ms per case. **Jailbreak-style:** jailbreak_style (cases with prompt-injection style args).
- **Confusable deputy:** `success_criteria_met.confusable_deputy_all_pass`; `confusable_deputy_cases[]`, `all_pass`.
- **E2E denial:** `e2e_denial_trace.json` documents blocked step example and outcome.
- **Adapter latency:** `run_manifest` (adapter_scenarios, adapter_seeds; publishable: 3 scenarios, 20 seeds); `runs[]` (scenario_id, seed, task_latency_ms_p95, wall_sec); `tail_latency_p95_mean_ms`; when n >= 2: stdev and 95% CI. Optional `denial_stats`: total_runs, runs_with_denial, per_scenario (runs, denials, tasks_completed_mean).
- **Baseline comparison:** `baseline_comparison.json` (tool-level) and `baseline_comparison_args.json` (args_unsafe): rows (scenario_id, seed, gated_denials, weak_denials, ungated_denials, tasks_completed per mode); plan_type; excellence_metrics (denial_count_gated/weak/ungated, tasks_completed_mean per mode). For args_unsafe: expect gated denials = total runs, weak/ungated = 0. **Benign (false-positive study):** `--run-baseline --baseline-plan benign` writes baseline_benign.json with benign_acceptance_rate_* and false_positive_count_* per mode.
- **Denial trace stats:** `denial_trace_stats.json`: total_runs, runs_with_denial, per_scenario; run_manifest.
- **Reproducibility:** All result JSONs include run_manifest with timestamp_iso, evaluator_version, policy_version; real-LLM adds prompt_template_hash. Run `export_p6_artifact_hashes.py` then `export_p6_reproducibility_table.py` for appendix table (result-to-artifact mapping). Venue pack: papers/P6_LLMPlanning/sat-cps2026/EXPERIMENTS_RUNBOOK.md.
- **Layer attribution:** Per-case attribution (allow_list_only, safe_args_only, both, admitted) in red_team_results and confusable_deputy_results; denial_by_layer summary. Export: `export_p6_layer_attribution.py`. **Failure analysis:** export_p6_failure_analysis.py (from run_details in real-LLM argument-level cases). **Cross-model:** When 2+ real-LLM models, red_team_results.json has cross_model_summary; export_p6_cross_model_heatmap.py. **Latency decomposition:** adapter_latency.json gains latency_decomposition when --latency-decomposition; export_p6_latency_decomposition.py.

---

## P7 — Standards mapping (assurance pack)

**Contribution / headline:** Traceable assurance argument (assurance pack, mapping completeness, scripted review) plus **governance-evidence discrimination** (negative controls, reviewer ablations, stable failure codes). For a compact, presentable snapshot of key numbers, see [RUN_RESULTS_SUMMARY.md](../datasets/runs/RUN_RESULTS_SUMMARY.md) (generated by run_paper_experiments.py) when populated.

**What it measures:** Mapping check (hazards → controls → evidence types; PONR coverage); per-scenario review (evidence_bundle, trace, PONR events, controls_covered); **robust matrix** (400 runs default); **negative suite** (injected pack/artifact/scenario/misleading faults across reviewer modes); auditor walk-through (mapping + PONR + optional run review); Part 11-style audit trail alignment. Non-goals: no certification claim; translation layer only. **Three instantiations:** lab v0.1, warehouse v0.1, medical v0.1; results.json includes `per_profile` (review outcome per pack). Standards mapping table: [docs/P7_STANDARDS_MAPPING.md](P7_STANDARDS_MAPPING.md). **Review:** PONR coverage requires `--scenario-id` from the known list; `--review-mode` selects ablation vs full governance checks ([docs/P7_REVIEW_CHECKLIST.md](P7_REVIEW_CHECKLIST.md)). Failure codes: [docs/P7_REVIEW_FAILURE_CODES.md](P7_REVIEW_FAILURE_CODES.md). Perturbation ids: [docs/P7_PERTURBATION_CHECKLIST.md](P7_PERTURBATION_CHECKLIST.md). Scripted review is partial and does not constitute a full safety-case proof. Auditor feedback protocol: [docs/P7_AUDITOR_FEEDBACK_PROTOCOL.md](P7_AUDITOR_FEEDBACK_PROTOCOL.md).

**Result locations:**
- `datasets/runs/assurance_eval/results.json` — mapping_check, review, reviews
- `datasets/runs/assurance_eval/robust_results.json` — positive-control stability matrix (`aggregate`, `rows`, `run_manifest`)
- `datasets/runs/assurance_eval/negative_results.json` — discrimination: `aggregate`, `by_mode`, `by_family`, `by_scenario`, `by_perturbation`, `rows` (run with `--submission-mode` for path redaction in release bundles)
- `datasets/runs/assurance_eval_aies/` — AIES paper-facing bundle:
  `baseline_summary.json`, `institutional_positive_summary.json`, `negative_summary.json`,
  `bounded_review_packet/`, `tables/`, `figures/`, `RUN_MANIFEST.json`, `README.md`
- `papers/P7_StandardsMapping/p7_*.csv` — Tables 4–6 + `p7_perturbation_reject_matrix.csv`, `p7_aggregate_lift_metrics.csv`, `p7_latency_by_mode.csv`, `p7_negative_by_scenario.csv`, `p7_boundary_case_summary.csv`, `p7_submission_manifest_redacted.json`, `p7_generation_metadata.json` (`export_p7_negative_tables.py`)
- **Auditor script:** `scripts/audit_bundle.py` — pass/fail mapping completeness and PONR coverage; `--run-dir` for optional run review; `--release datasets/releases/portfolio_v0.1` for one-command audit over a release dir (runs mapping + PONR; if release contains evidence_bundle.json, runs review there too). JSON + human output.
- **Part 11:** `docs/PART11_AUDIT_TRAIL_ALIGNMENT.md` — each requirement mapped to artifact path and field/event (machine-checkable; no prose-only).

**How to read:**
- `run_manifest`: scenarios, profile_dir, script. `success_criteria_met`: mapping_ok, ponr_coverage_ok. Optional `excellence_metrics`: mapping_completeness_pct, ponr_coverage_ratio, review_pass_all_scenarios, no_certification_claimed.
- `mapping_check.ok`: schema and mapping complete; `mapping_check.ponr_coverage_ok`: every profile PONR in at least one hazard.
- `reviews.<scenario_id>`: `evidence_bundle_ok`, `trace_ok`, `ponr_events[]`, `controls_covered[]`, `ponr_coverage.ratio`, `control_coverage_ratio`, `exit_ok`.
- `review`: backward-compat alias for toy_lab_v0. For lab_profile_v0, `ponr_coverage.required_task_names` typically includes `disposition_commit`.
- **Negative JSON:** `by_mode.*.false_accept_rate` vs `full_review`; `aggregate.invalid_reject_lift_full_minus_schema_only`, `false_accept_drop_full_vs_schema_only`; `by_scenario` for valid acceptance/latency; `by_perturbation` for per-case reject under each mode.
- **Auditor:** Run `audit_bundle.py [--run-dir path]`; output includes `mapping_completeness`, `ponr_coverage`, `review_exit_ok` (if run-dir given).

**Tables and figures:** `scripts/export_assurance_tables.py` (Tables 1–3). `scripts/export_assurance_gsn.py`, `scripts/export_p7_mapping_flow.py` (Figure 0), `docs/figures/p7_review_stages.mmd` (Figure 2), `scripts/render_p7_mermaid_figures.py`. `scripts/run_assurance_negative_eval.py --submission-mode` + `scripts/export_p7_negative_tables.py --submission-mode` (Tables 4–6 + supplements). Non-goals: P7 DRAFT, kernel/assurance_pack/README.md, profiles/lab/v0.1/README.md. Kill criterion K7: no "template theater"; every mapping claim checkable by script or schema.

**AIES sprint exports:** `scripts/export_bounded_review_packet.py`,
`scripts/export_aies_assurance_tables.py`, and
`scripts/export_aies_review_packet_figure.py` generate bounded-access review artifacts,
institutional baseline/portability tables, and reviewer-view figure assets under
`datasets/runs/assurance_eval_aies/`. Traffic/medical proxy outputs are isolated in
`proxy_stress_only/` and excluded from main-text tables by default.

---

## P8 — Meta-Coordination (regime switching)

**Contribution / headline:** Tiered claims: (1) auditable regime switching under safety proxy; (2) non-inferior paired collapse counts vs fixed when non-vacuous (`meta_non_worse_collapse`; legacy `meta_reduces_collapse`); (3) strict count reduction and McNemar / Wilson reported separately; two real regimes with `--fallback-adapter retry_heavy`; methodology-only framing when collapse is absent. Publishable pipeline includes `regime_stress_v0` and `regime_stress_v1` artifacts. See [RUN_RESULTS_SUMMARY.md](../datasets/runs/RUN_RESULTS_SUMMARY.md).

**What it measures:** Fixed (Centralized) vs meta-controller vs naive: tasks_completed_mean, collapse_count, regime_switch_count; paired binary analysis (`collapse_paired_analysis`); bootstrap CI for paired tasks_completed difference (`excellence_metrics`). Optional fallback adapter: `--fallback-adapter blackboard|centralized|retry_heavy`. Scenarios: `--scenario regime_stress_v0|regime_stress_v1`. Thrash control (`--hysteresis N`). Force-collapse sweep for stress calibration.

**Result locations:**
- `datasets/runs/meta_eval/comparison.json` — primary (v0). `schema_version`, `collapse_paired_analysis`, `meta_non_worse_collapse`, `meta_strictly_reduces_collapse`, `run_manifest.stress_selection_policy` when `--non-vacuous`.
- `datasets/runs/meta_eval/scenario_regime_stress_v1/comparison.json` — secondary scenario (publishable runner).
- `datasets/runs/meta_eval/collapse_sweep.json` (and v1 sibling directory) — `meta_collapse_sweep.py` output with `schema_version` and per_run collapse flags.

**Publishable run:** Run `meta_collapse_sweep.py` first (default 20 seeds), then `meta_eval.py --run-naive --fault-threshold 0 --non-vacuous` so Table 1 uses a drop_prob where collapse occurs. If no such drop_prob exists, meta_eval exits with a message; present results as methodology and auditability only. See EVALS_RUNBOOK P8.

**How to read:**
- `run_manifest`: seeds, seed_count, scenario_id, drop_completion_prob, collapse_threshold, fault_threshold, hysteresis, script, schema_version, optional non_vacuous and stress_selection_policy. `success_criteria_met`: no_safety_regression, meta_reduces_collapse (non-inferior counts), meta_strictly_reduces_collapse, trigger_met (see `docs/CONDITIONAL_TRIGGERS.md`). `excellence_metrics`: difference_mean, difference_ci95 (+ methods), McNemar p, collapse_outcome_* , switch_audit_trail_total. When n >= 2: Student t `tasks_completed_ci95` per arm.
- `fixed`: `tasks_completed_mean`, `tasks_completed_stdev`, `tasks_completed_ci95`, `collapse_count`, `per_seed[]` (tasks_completed, collapse).
- `meta_controller`: same plus `per_seed[].regime_switch_count`; sum = regime_switch_count_total. Use `--hysteresis N` for thrash control.
- `naive_switch_baseline`: `tasks_completed_mean`, `regime_switch_count_total`, `per_seed[]`.
- `no_safety_regression`: true if meta mean ≥ 90% of fixed mean.
- `meta_reduces_collapse` / `meta_non_worse_collapse`: true if meta collapse_count ≤ fixed (non-inferiority on counts; vacuous when both 0).
- `collapse_definition`: "tasks_completed < {threshold} or recovery_ok false"; per-seed entries include `recovery_ok` when present in report.faults.
- **Collapse sweep:** Run `meta_collapse_sweep.py --drop-probs 0.15,0.2,0.25,0.3`; `per_run[]` gives (drop_prob, seed, tasks_completed, recovery_ok, collapsed); `collapse_count` shows how many runs collapsed.

**Tables and figure:** `python scripts/export_meta_tables.py --comparison datasets/runs/meta_eval/comparison.json` (add `--table2` for per-seed). Figure 1: run `meta_collapse_sweep.py` to produce collapse_sweep.json, then `python scripts/plot_meta_collapse.py --sweep datasets/runs/meta_eval/collapse_sweep.json` (output `docs/figures/p8_meta_collapse.png`).

---

## One-line summary

| Paper | One-line result |
|-------|------------------|
| P0 | E1 conformance corpus (build_p0_conformance_corpus, export_e1_corpus_table); E2 4-col admissibility matrix; E3 replay link (`produce_p0_e3_release` / `replay_link_e3` with `--standalone-verifier` for publishable evidence); E4 controller matrix (run_p0_e4_controller_matrix, export_p0_table3 with strong replay preference from E4 raw baseline rows and E3 strong replay if present); Table 1/2/3, Figures 1–3; MAESTRO_REPORT v0.2; repro in DRAFT Appendix. |
| P1 | Contract validator: corpus detection_ok; scale_test/scale_sweep; gatekeeper check_contracts; instrument state machine; P1_TRACE_DERIVABILITY.md; export_contracts_corpus_table + export_p1_appendix_tex; render_p1_flow_figure; plot_p1_paper_figures; submission lock at papers/P1_Contracts/SUBMISSION_LOCK.md. |
| P2 | REP-CPS profile; scoped adapter parity; rep_cps_scheduling_v0 + scheduling_dependent_eval; delay_fault_prob sweep, optional drop_completion_prob sweep; per_scenario summaries; excellence_metrics with comparison statistics; freshness/spoof/messaging_sim/dynamic_series; offline comparator baselines; Tables 1–7 (includes per-scenario summary, comparison statistics, messaging_sim and dynamic_aggregation_series blocks); robust bias offline; conditional scope per CONDITIONAL_TRIGGERS. Figures: summary (Figure 1), gate-threshold (Figure 2), dynamics (Figure 3), latency (Figure 4). Optional convergence (Table 4) when --aggregation-steps > 1. |
| P3 | schema_version; baseline_overhead; multi_seed_overhead; corpus_outcome_wilson_ci95; corpus_space_summary; per_trace localization + space fields; empirical p95/p99 + bootstrap CIs; verify_p3_replay_summary; field_style_pass; plot_replay_overhead (optional error bars); L1 stub + L1 twin; export_replay_corpus_table (Table 1b); L2 design subsection. |
| P4 | Fault sweep (incl. calibration_invalid_01); recovery metrics (steps_after_fault, tasks_after_fault); Centralized/Blackboard/RetryHeavy baselines; anti-gaming + scoring_proof; adapter_costs.json; plot_maestro_recovery. |
| P5 | Held-out MAE; per_scenario_baseline_mae; feature/regression; 95% CI; scaling_fit; success_criteria_met.trigger_met; --seeds 20, --fault-mix. |
| P6 | Red-team (15) + confusable_deputy (6) + jailbreak_style (4) + adaptive suite; validator stack allow_list+safe_args+ponr_gate(+privilege heuristic); run_manifest (timestamp_iso, evaluator_version, policy_version, prompt_template_hash, suite_mode); e2e_denial_trace; adapter_latency (3 scenarios, 20 seeds); optional latency_decomposition (--latency-decomposition); real_llm / real_llm_models with camera-ready snapshot `llm_eval_camera_ready_20260424` using `--real-llm-runs 3 --real-llm-suite full` (pass_rate, Wilson CI); cross_model_summary when 2+ models; baseline 3-way tool-level + args_unsafe + benign (--baseline-plan benign); denial_trace_stats; layer attribution (denial_by_layer incl. ponr_gate_only, export_p6_layer_attribution); failure analysis (run_details, export_p6_failure_analysis); export_llm_redteam_table, export_p6_baseline_table, export_p6_artifact_hashes, export_p6_reproducibility_table, export_p6_cross_model_heatmap, export_p6_latency_decomposition; optional p6_concurrency_benchmark, p6_capture_ablation, p6_storage_benchmark, p6_cost_model, p6_policy_sweep, p6_replanning_benchmark, p6_adaptive_suite_run; P6_OWASP_MAPPING. |
| P7 | mapping_check + ponr_coverage_ok; robust_results; negative_results + ablation CSVs; three profiles; per_profile; **AIES bundle** under `assurance_eval_aies/` with institutional baseline (`lab_profile_v0`), portability row (`warehouse_v0`), bounded review packet, negative-family/failure exports, reviewer figure, and `RUN_MANIFEST.json`; P7_STANDARDS_MAPPING; P7_REVIEW_FAILURE_CODES; P7_PERTURBATION_CHECKLIST; audit_bundle; review modes; export_assurance_gsn; mapping flow + review-stage figures; P7_AUDITOR_FEEDBACK_PROTOCOL; non-goals; K7. |
| P8 | fixed/meta/naive; --scenario v0/v1; --non-vacuous + stress_selection_policy; verify_p8_meta_artifacts; optional --fallback-adapter retry_heavy; comparison.json + collapse_sweep.json; collapse_paired_analysis; export_meta_tables; plot_meta_collapse (uncertainty). |

For full interpretation, follow-up experiments, and verification checklists, see [EVAL_RESULTS_INTERPRETATION.md](EVAL_RESULTS_INTERPRETATION.md). For how to run each pipeline, see [EVALS_RUNBOOK.md](EVALS_RUNBOOK.md).
