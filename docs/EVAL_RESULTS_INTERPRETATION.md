# Evaluation Results: Interpretation and Experiment Plan

This document interprets the current evaluation outputs across the portfolio and proposes follow-up tests and experiments. Use it to decide what to run next and how to read the results.

**Portfolio status:** All nine papers (P0–P8) are at Draft stage; Phase 3 (submission-readiness) passed 2025-03-11. Next: submission prep per [PRE_SUBMISSION_CHECKLIST.md](PRE_SUBMISSION_CHECKLIST.md). Summary JSONs may include optional **excellence_metrics**; run `python scripts/export_excellence_summary.py` to print a one-line summary per paper (see [STANDARDS_OF_EXCELLENCE.md](STANDARDS_OF_EXCELLENCE.md)). For a compact snapshot of key numbers per paper, see [RUN_RESULTS_SUMMARY.md](../datasets/runs/RUN_RESULTS_SUMMARY.md). For P5/P6/P8 key results as markdown, run `python scripts/export_key_results_p5_p6_p8.py` after the publishable pipeline.

## Executive summary

- **P2 REP-CPS:** Safety-gated profile; offline bias reduction; scoped adapter parity on non-scheduling scenarios; **rep_cps_scheduling_v0** links gate to scheduling (`scheduling_dependent_eval`); freshness_replay_evidence, sybil_vs_spoofing_evidence, messaging_sim, dynamic_aggregation_series in summary.json. Eval writes to `rep_cps_eval/`. See DRAFT §5.1 (two evaluation modes) and CONDITIONAL_TRIGGERS (P2).
- **P5 Scaling:** Publishable default is **30 seeds**, **`--profile real_world`**, coordination grid (**`--coordination-grid`**), narrow faults **`--fault-settings no_drop,drop_005`**, agent counts **1,2,4,8** → **7200** thin-slice rows; held-out eval modes **scenario, family, regime, agent_count, fault_setting**; `scaling_sensitivity_sweep.py` → `sensitivity_sweep/scaling_sensitivity.json`; `scaling_recommend_eval.py` → `scaling_recommend/recommendation_eval.json`; `export_scaling_regime_agent_summary.py` → `scaling_summary/regime_agent_summary.json`. **`trigger_met` is per protocol** (admissible baselines only); see `papers/P5_ScalingLaws/DRAFT.md` and [CONDITIONAL_TRIGGERS.md](CONDITIONAL_TRIGGERS.md). Spec: [P5_SCALING_SPEC.md](P5_SCALING_SPEC.md).
- **P6 LLM:** Expanded red-team, confusable deputy, jailbreak-style, `ponr_gate`; optional adaptive suite output (`p6_adaptive_results.json` when `p6_adaptive_suite_run.py` is executed). **Canonical committed bundle:** `llm_eval_camera_ready_20260424/` (Table 1b + adapter/baselines + `replay_denials.json` + `verify_p6_camera_ready_bundle.py` gate). Scratch regen defaults to `llm_eval/` (gitignored). Synthetic plans by default; optional `--real-llm` with `--real-llm-suite full|core` and `--real-llm-runs` (default 10). Prime / GPT-5.x supplementary runs must use separate `--out` dirs.
- **P8 Meta:** `meta_eval.py` with `--scenario regime_stress_v0|regime_stress_v1`, optional `--run-naive --fault-threshold 0`, `--non-vacuous` + documented `stress_selection_policy`, optional `--fallback-adapter retry_heavy`. Outputs `comparison.json` (`schema_version`, `collapse_paired_analysis`, non-inferior vs strict collapse fields), `collapse_sweep.json` (`schema_version`). Publishable runner: `run_paper_experiments.py --paper P8` (v0 + v1). Verify: `verify_p8_meta_artifacts.py`. Figure 1: `plot_meta_collapse.py` (t-CI + Wilson intervals).
- **Core (P0, P3, P4, P1, P5, P7):** Eval scripts run in CI; results under `datasets/runs/` (P0 E1: p0_conformance_corpus/, corpus_manifest.json; P0 E2: e2_redaction_demo/; P0 E3: e3_summary.json, p0_e3_variance.json; P0 E4: p0_e4_raw_summary.json, p0_e4_normalized_summary.json, p0_e4_per_seed.jsonl, p0_e4_diagnostics.json, p0_e4_controller_pairs.jsonl, p0_e4_raw_failure_reasons.json, p0_e4_controller_matrix.json; P0 conformance summary: build_p0_conformance_summary.py -> datasets/releases/portfolio_v0.1/p0_conformance_summary.json; **P3:** `replay_eval/summary.json` with `schema_version: p3_replay_eval_v0.2`, `baseline_overhead`, `multi_seed_overhead`, `corpus_outcome_wilson_ci95`, witness slices, optional `overhead_curve`; `verify_p3_replay_summary.py`; maestro_fault_sweep, maestro_antigaming/antigaming_results.json with scoring_proof; contracts_eval, P1_TRACE_DERIVABILITY.md; assurance_eval, audit_bundle --release; **AIES packaging path** `assurance_eval_aies/` with bounded packet + institutional baseline/portability exports; scaling_eval with trigger_met). **Conditional (P2, P5, P6, P8):** success_criteria_met includes trigger_met where applicable; see docs/CONDITIONAL_TRIGGERS.md for required evidence. **Real eval launches:** P1, P2, P3, P4, P5, P6, P7, and P8 each have an integration test; see tests/test_contracts_p1.py, test_rep_cps_p2.py, test_replay_p3.py, test_maestro_p4.py, test_scaling_p5.py, test_llm_p6.py, test_assurance_p7.py, test_meta_p8.py, and test_assurance_aies_exports.py. P5: test_scaling_p5.py runs generate_multiscenario_runs then scaling_heldout_eval and asserts on heldout_results.json. CI runs generate_multiscenario_runs --seeds 2 and scaling_heldout_eval.

---

## 1. P2 REP-CPS — Interpretation

### Results (from `datasets/runs/rep_cps_eval/summary.json`)

| Metric | Value | Meaning |
|--------|--------|--------|
| Scenario | toy_lab_v0, lab_profile_v0, rep_cps_scheduling_v0 | Three scenarios; publishable default (scheduling scenario demonstrates gate-linked task effect) |
| Seeds | 20 (publishable default) | CI may use fewer; mean and stdev reported |
| rep_cps_tasks_completed_mean | from summary | Same as centralized |
| centralized_tasks_completed_mean | from summary | Baseline |
| rep_cps_naive_tasks_completed_mean | from summary | Naive-in-loop baseline |
| rep_cps_unsecured_aggregate_load_mean | from summary | Unsecured (compromised in loop) |
| rep_cps_tasks_completed_stdev | from summary | Variance across seeds |
| honest_only_aggregate | 0.32 | True load (3 honest agents) |
| with_compromise_robust_aggregate | ~3.56 | Trimmed mean with 2 Byzantine (value=10) |
| with_compromise_naive_aggregate | ~4.19 | Plain mean with same inputs |
| bias_robust | ~3.24 | |robust − honest| |
| bias_naive | ~3.87 | |naive − honest| |
| profile_ablation[] | from summary | No auth, no freshness, no rate limit, no robust agg, full profile; bias and failure per variant (Table 6). |
| latency_cost | from summary | Wall time per policy, aggregation compute ms, overhead vs centralized; Table 5. Figure 2: plot_rep_cps_latency.py. |
| resilience_envelope | from summary | safe_operating_region_n_compromised_max, failure_boundary_n_compromised; Table 7. |
| safety_gate_campaign | from summary | pass_count_rep_cps, deny_count_unsecured, denial_trace_recorded. |

### Interpretation

- **Adapter parity:** REP-CPS and Centralized complete the same number of tasks on average; no throughput regression from the protocol in this setup.
- **Robust vs naive aggregation:** Under 2 Byzantine agents (extreme value 10), robust (trimmed mean) stays closer to the honest aggregate (0.32) than naive mean (4.19). So **robust aggregation reduces bias under compromise**.
- **Real tests and launches:** CI runs rep_cps_eval with reduced seeds for speed. Publishable default is 20 seeds, three scenarios (toy_lab_v0, lab_profile_v0, rep_cps_scheduling_v0), delay sweep. Integration tests in tests/test_rep_cps_p2.py run the eval script and real adapter runs, asserting summary structure and invariants (bias_robust < bias_naive, rate_limit exercised, adapter parity, latency_cost, resilience_envelope, scheduling_dependent_eval). Naive-in-loop and unsecured baselines are in the adapter and eval.
- **Validity and robustness:** Summary includes run_manifest (seeds, scenario_ids including rep_cps_scheduling_v0, delay_fault_prob_sweep, drop_completion_prob_sweep, aggregation_steps_used, script), per_scenario (aggregated metrics per scenario_id across all delay/drop combinations), profile_ablation (Table 6), latency_cost (Table 5), resilience_envelope (Table 7), safety_gate_campaign, scheduling_dependent_eval, freshness_replay_evidence, sybil_vs_spoofing_evidence, messaging_sim, dynamic_aggregation_series, excellence_metrics (including comparison statistics: difference_mean, difference_ci95, paired_t_p_value, power_post_hoc on non-scheduling scenarios), and 95% CI for tasks_completed when n >= 2. success_criteria_met (adapter_parity on non-scheduling scenarios, scheduling_scenario_task_divergence, robust_beats_naive, trigger_met) is machine-checked in CI. Conditional paper: on toy_lab_v0 and lab_profile_v0, adapter parity holds (scheduler does not consume REP aggregate); on rep_cps_scheduling_v0, gated aggregate can materially affect tasks_completed under spoof stress. Contribution is profile + MAESTRO-compatible harness. See docs/CONDITIONAL_TRIGGERS.md (P2). Use default (20 seeds, three scenarios) for publishable tables. Regenerate tables with `python scripts/export_rep_cps_tables.py`; figures with plot_rep_cps_summary.py and plot_rep_cps_latency.py.

### Follow-up experiments (P2)

1. **Stability under delay:** Sweep delay_fault_prob (e.g. 0, 0.05, 0.1, 0.2); record tasks_completed and aggregate stability per scenario.
2. **Scheduling scenario analysis:** Analyze scheduling_dependent_eval results to quantify gate effect on task completion under spoof stress; compare naive vs robust aggregation outcomes.
3. **Convergence (optional):** When --aggregation-steps > 1, summary reports convergence_achieved_rate, steps_to_convergence; Table 4 via export_rep_cps_convergence_table.py.
4. **Threat-specific evidence:** Review freshness_replay_evidence, sybil_vs_spoofing_evidence, messaging_sim, and dynamic_aggregation_series to validate threat model coverage.


---

## 2. P5 Scaling — Interpretation

Integration test: `tests/test_scaling_p5.py` runs `generate_multiscenario_runs` (2 seeds) then `scaling_heldout_eval` and asserts `heldout_results.json` structure (including CI keys, `scaling_fit`, `success_criteria_met`). CI uses reduced seeds for speed.

### Results (publishable freeze; refresh JSON after every regen)

Orchestrated run: `PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/run_paper_experiments.py --paper P5`. One checked-in freeze (see `papers/P5_ScalingLaws/DRAFT.md`) used **7200** rows, **six** `real_world` scenario ids, **five** regimes, **`run_manifest.commit` 5b280e800ff309c215bbe52f7854805176a632bc**. Headline **`tasks_completed`** values (scenario LOO): `overall_baseline_mae` **0.7367**, `overall_feat_baseline_mae` **0.3899**, `overall_regression_mae` **0.5105**, `mean_regression_pi_coverage_95` **0.7707**, **`trigger_met` false** (does not beat num-tasks bucket). Family LOO: **`trigger_met` true** on the same freeze. Do not quote older lite-grid or seven-scenario fault-mix numbers here.

| Metric | Where to read it |
|--------|------------------|
| Per-protocol triggers and MAEs | `scaling_eval/heldout_results.json`, `scaling_eval_family/heldout_results.json`, etc. |
| Seed-cap sensitivity | `sensitivity_sweep/scaling_sensitivity.json` |
| Recommendation / regret | `scaling_recommend/recommendation_eval.json` |
| Title grounding (1→8 deltas) | `scaling_summary/regime_agent_summary.json` + Table 8 in `generated_tables.md` |

**Family artifact:** `scaling_eval_family/heldout_results.json` (leave-one-taxonomy-family-out: lab / traffic / warehouse). Strict rule: if any fold has `regression_mae: null`, protocol-level regression MAE is null and `trigger_met` is false unless you implement an explicit comparable-fold block (see `scaling_heldout_eval.py`).

### Interpretation

- **Baselines:** Global mean, num-tasks bucket, regime and agent-count train means (admissible); oracle per-scenario mean is **not** part of `trigger_met`. **trigger_met** requires beating global mean, num-tasks bucket, and regime train mean on the primary target (see `success_criteria_met` in JSON).
- **Secondary targets:** `secondary_targets` in `heldout_results.json` summarizes MAE for `coordination_tax_proxy` and `error_amplification_proxy` (see [P5_SCALING_SPEC.md](P5_SCALING_SPEC.md)).
- **Calibration (exploratory):** `mean_regression_pi_coverage_95` — fraction of test points inside train-residual 95% intervals, averaged over folds; near 0.95 supports narrative for calibration (not a formal guarantee).

### Follow-up experiments (P5)

1. **Larger N / narrower CIs:** default publishable already uses **30** seeds; increase only if runtime allows.
2. **Fault breadth:** optional `--fault-mix` adds settings beyond `no_drop` / `drop_005`; keep publishable tables on the narrow grid unless the paper explicitly widens scope.
3. **Sensitivity:** `scaling_sensitivity_sweep.py` (invoked from `--paper P5`) reproduces `scaling_sensitivity.json` caps 10 / 20 / 30.
4. **Collapse / richer responses:** report-derived `collapse_rate` fields in scaling rows; optional future: MTTR if the trace schema gains it.

**P5 verification (implementation, tests):** `scripts/export_scaling_tables.py`, `scripts/plot_scaling_paper.py`, `papers/P5_ScalingLaws/DRAFT.md`, `claims.yaml`. Spec: [P5_SCALING_SPEC.md](P5_SCALING_SPEC.md).

- **Validity and robustness:** `run_manifest` includes `commit`, `scenario_ids`, `coordination_regimes`, `agent_counts`, `fault_setting_labels`, `seeds`, and paths; top-level `total_rows` is the scaling row count. `success_criteria_met` uses admissible baselines only. Conditional paper: see [CONDITIONAL_TRIGGERS.md](CONDITIONAL_TRIGGERS.md). Publishable default: `run_paper_experiments.py --paper P5` (real_world six scenarios, 7200 rows, narrow fault pair).

---

## 3. P6 LLM Planning — Interpretation

Integration test: tests/test_llm_p6.py runs llm_redteam_eval with --run-adapter (toy_lab_v0, seed 7) and asserts red_team_results.json and adapter_latency.json.

### Results (from `datasets/runs/llm_eval_camera_ready_20260424/red_team_results.json`)

Synthetic red-team rows are listed in Table 1 from `export_llm_redteam_table.py` (case count is versioned in `llm_planning.py`). `jailbreak_style` is embedded in the same JSON. Adapter latency (`--run-adapter`): `adapter_latency.json` includes runs, `tail_latency_p95_mean_ms`, scenarios, seeds, and optional `latency_decomposition`.

### Interpretation

- **Validators block unsafe:** allow-list for tools; `safe_args` for path traversal, deny-list keys, and jailbreak-style substrings in args; `ponr_gate` for unsafe PONR or gate-bypass *proposals* in args; privilege heuristic on args keys. `all_block_unsafe_pass` = true when every synthetic case matches `expected_block`.
- **Limitations:** Evidence from synthetic plans by default; real-LLM mode (`--real-llm`) optional and costs API calls. Containment heuristics, not elimination. Latency is thin-slice adapter time. Optional `--latency-threshold-ms` for SLA.
- **Validity and robustness:** red_team_results and confusable_deputy include run_manifest and success_criteria_met; jailbreak-style must also pass for exit code 0. adapter_latency.json has run_manifest; when n >= 2, tail_latency_p95_ci95_lower/upper and stdev reported.

### Follow-up experiments (P6)

1. **Tail latency SLA:** Use `--run-adapter --latency-threshold-ms 5000` to add latency_acceptable to adapter_latency.json.
2. **Draft:** Red-team table, adapter latency table, comparison to benchmarks, Limitations.
3. **Validator stack:** allow_list + safe_args + ponr_gate + privilege heuristic; `validate_plan_step` / `validate_plan_step_with_attribution`. Real-LLM Table 1b: `scripts/llm_redteam_eval.py --real-llm` (see EXPERIMENTS_RUNBOOK). Full table: `scripts/export_llm_redteam_table.py`. One-shot bundle: `scripts/p6_publish_bundle.py`.

**P6 verification:** `python scripts/verify_p6_camera_ready_bundle.py` (CI) plus `tests/test_llm_p6.py` (scratch `--out` integration smoke).

---

## 4. P8 Meta-Coordination — Interpretation

**Integration tests:** `tests/test_meta_p8.py` runs `meta_eval` in a temp directory (`--run-naive`, `--fault-threshold` 0), checks `comparison.json` schema fields (including `collapse_paired_analysis`, `meta_non_worse_collapse`, `meta_strictly_reduces_collapse`), runs `export_meta_tables.py` and `verify_p8_meta_artifacts.py`, and includes a `regime_stress_v1` smoke run. `tests/test_stats_p8_tools.py` covers Student t critical values and McNemar helpers.

### Results (from `datasets/runs/meta_eval/comparison.json`)

Example snapshot (regime_stress_v0, 20 seeds, non-vacuous publishable-style run; see [RUN_RESULTS_SUMMARY.md](../datasets/runs/RUN_RESULTS_SUMMARY.md)):

| Metric | Fixed (Centralized) | Meta-controller |
|--------|----------------------|-----------------|
| tasks_completed_mean | 3.40 | 3.40 |
| collapse_count (per run_manifest definition) | 1 | 1 |
| regime_switch_count_total (meta, sum per_seed) | — | 8 |
| naive_switch_baseline | tasks_completed_mean 3.40; collapse_count exported in Table 1 | regime_switch_count_total 8 |

**Secondary scenario:** After `run_paper_experiments.py --paper P8`, also read `datasets/runs/meta_eval/scenario_regime_stress_v1/comparison.json` for external-validity rows (same schema).

### Interpretation

- **Non-inferiority vs strict improvement:** `meta_reduces_collapse` means **non-inferiority** on collapse counts (meta <= fixed), not necessarily strict reduction. Use `meta_strictly_reduces_collapse`, `collapse_paired_analysis`, and `excellence_metrics.mcnemar_exact_p_value_two_sided` for paired binary readouts; Wilson CIs marginalize collapse **rates** (not a paired test).
- **Vacuous case:** If fixed and meta both have collapse_count 0, non-inferiority holds vacuously; the draft should not imply a meaningful “win” unless non-vacuous stress was used.
- **Regime switches:** With `--fault-threshold` 0 and `--run-naive`, the naive baseline typically shows many switches; compare to meta `regime_switch_count_total` for thrash discussion.
- **No safety regression:** meta mean >= 90% of fixed mean (`no_safety_regression`).
- **Validity:** Prefer publishable defaults (20 seeds), `meta_eval --non-vacuous` with `stress_selection_policy`, and dual-scenario artifacts from `run_paper_experiments.py --paper P8`. CI uses fewer seeds; do not cite CI outputs as table sources.

### Follow-up experiments (P8)

1. **Stress calibration:** Run `meta_collapse_sweep.py` with `--scenario` matching the eval; widen `--drop-probs` if a scenario never collapses.
2. **Fixed RetryHeavy baseline (optional):** If claims need “best fixed” beyond Centralized, add an explicit fixed-adapter baseline run and document it in the draft (narrow claims if only Centralized is evaluated).
3. **Hysteresis sweep:** Compare `excellence_metrics.switch_audit_trail_total` and collapse counts for `--hysteresis 1,2,3`.
4. **Separate calibration seeds (optional):** Run sweep on a held-out seed list and fix `drop_prob` before the evaluation seeds (document in `run_manifest`).

**P8 verification (current repo):**

| Check | Status |
|-------|--------|
| meta_eval --out hermetic | `test_meta_p8` temp dir |
| comparison.json core fields | `schema_version`, arms, `collapse_paired_analysis`, success_criteria_met |
| no_safety_regression; non-inferior collapse | asserted (`meta_non_worse_collapse` / `meta_reduces_collapse`) |
| naive regime_switch_count_total >= 1 | asserted when `--run-naive` |
| export_meta_tables.py | exit 0 asserted |
| verify_p8_meta_artifacts.py | exit 0 asserted |
| regime_stress_v1 smoke | dedicated test |
| Unit tests: decide_switch, regime_switch_event | `TestMetaController` |
| Draft / claims | tiered claims; see `papers/P8_MetaCoordination/DRAFT.md`, `claims.yaml` |

---

## 5. Cross-cutting and core papers

### P0 (MADS-CPS)

- **Existing:** E1 conformance corpus (build_p0_conformance_corpus, export_e1_corpus_table; Table 1). E2 redaction and 4-col verification-mode admissibility matrix (Table 2). E3 replay-link with optional --standalone-verifier (verify_maestro_from_trace.py). E4 algorithm-independence (`run_p0_e4_controller_matrix`, export_p0_table3; Table 3 with strong replay preference from E4 raw rows and E3 strong replay when present). Evidence bundle schema requires verification_mode (public | evaluator | regulator); Tier 2 replay conditional on verification_mode. Portfolio conformance: build_p0_conformance_summary.py -> datasets/releases/portfolio_v0.1/p0_conformance_summary.json. Figures: export_p0_assurance_pipeline (Fig 1), export_p0_tier_lattice (Fig 2), export_p0_redaction_figure (Fig 3); plot_e3_latency. Repro: papers/P0_MADS-CPS/DRAFT.md Appendix.
- **E3 (20 seeds publishable):** tasks_completed mean, stdev; p95_latency_ms mean, stdev; all_match; 95% CI. export_e3_table.py (per-seed table in appendix). run_manifest; success_criteria_met.e3_all_match. Use --standalone-verifier for independent verifier process.
- **Validity and robustness:** E3 summary self-describing via run_manifest; independent verifier recomputes from trace. E1 corpus: expected vs observed tier and agreement per case.
- **E4 controller-separating evidence:** `coordination_shock` is the stress regime used to expose controller differences in scheduling-sensitive rows. Read `p0_e4_diagnostics.json` and `p0_e4_controller_pairs.jsonl` for MAESTRO-core/hash and event-level divergence rates. For raw-failure causal accounting, read `p0_e4_raw_failure_reasons.json` (currently dominated by Tier-3 PONR-miss reasons, not hidden schema patching).
- **E2 redaction:** Redacted trace has payloads replaced by content-addressed refs; it is not replayed (L0 replay expects full payloads). evidence_bundle_redacted has replay_ok false and a note that the redacted trace is audit-only.
- **Follow-up (CI):** E1 build_p0_conformance_corpus; E3 produce_p0_e3_release.py --runs 10 --no-release; E2 e2_redaction_demo.py. Run all: `python scripts/run_paper_experiments.py` (or --quick, --paper P0 … P8).

### P3 (Replay)

- **Existing:** `replay_eval.py` produces `datasets/runs/replay_eval/summary.json` with `schema_version: p3_replay_eval_v0.2`. **Corpus:** traps (nondeterminism, reorder, timestamp_reorder, hash_mismatch, long_horizon, mixed_failure), pass traces (benign_perturbation_pass, field_style_pass, field_style_pass_variant_b), real-ingest example (`real_bucket_example`); `twin_config.json` for L1 stub. Summary includes `replay_level`, `nondeterminism_budget`, `divergence_localization_confidence`, `corpus_outcome_wilson_ci95`, `l1_stub_ok`, `overhead_stats` (empirical p95/p99, bootstrap CIs, `percentile_method`), `baseline_overhead` (apply-only, final-hash-only, witness_window ablation, paired full_vs_apply_only), `multi_seed_overhead`, `excellence_metrics` (`overhead_p99_empirical`, corpus accuracy). **Corpus categorization:** `per_trace[]` includes **`corpus_category`** (synthetic_trap, field_proxy, real_ingest, synthetic_pass). **Root cause:** `root_cause_category` and `witness_slice` per divergence. **Overhead curve:** `--overhead-curve` populates `overhead_curve[]` (optional p95 CI per bin); figure: `plot_replay_overhead.py`; verify: `verify_p3_replay_summary.py`. **L1:** control-plane replay with recorded observations (not physics); `--l1-twin` produces **`l1_twin_summary`** with multi-seed aggregate statistics. See `bench/replay/README.md`, `kernel/trace/REPLAY_LEVELS.v0.1.md`, `papers/P3_Replay/DRAFT.md`, `generated_tables.md`.
- **Validity and robustness:** `run_manifest` (corpus_dir, overhead_runs, thin_slice_seeds, bootstrap_reps, platform, python_version); `success_criteria_met` (fidelity_pass, corpus_expected_outcomes_met). Publishable defaults: `--overhead-runs 20`, multi-seed thin-slice list, `--bootstrap-reps` 500+ as in DRAFT.
- **Follow-up:** Run `replay_eval.py` per [EVALS_RUNBOOK.md](EVALS_RUNBOOK.md) P3 section; `plot_replay_overhead.py`; `verify_p3_replay_summary.py --strict-curve` when using the curve figure.

### P4 (MAESTRO)

- **Existing:** maestro_fault_sweep.py (no_drop, drop_005, delay_01, drop_005_delay_01, calibration_invalid_01); baseline_results.md and baseline_summary.json (Centralized vs Blackboard); bench/maestro/adapter_costs.json (loc_estimate, hours_estimate per adapter); maestro_antigaming_eval.py writes antigaming_results.json (always_deny, always_wait score poorly; scoring_proof documents legitimate_safe_min > always_wait > always_deny). Scenarios with scenario taxonomy (family). Benchmark release v0.1: BENCHMARK_RELEASE.v0.1.md and benchmark_scenarios.v0.1.json. Draft: Table 1 (fault sweep), Table 2 (baseline) via export_maestro_tables.py; recovery proxy figure: scripts/plot_maestro_recovery.py. Integration tests: tests/test_maestro_p4.py runs fault sweep and baselines and asserts on multi_sweep.json, baseline_results.md, and baseline_summary.json structure; TestScenarioFamily unit tests for get_scenario_family and load_scenario family.
- **Validity and robustness:** multi_sweep has run_manifest and success_criteria_met.run_manifest_present; antigaming_results has success_criteria_met.antigaming_penalized. Use default (20 seeds) for publishable; CI overrides with fewer.
- **Follow-up:** Run fault sweep for two or more scenarios with 20 seeds (incl. calibration_invalid_01); run maestro_antigaming_eval.py; save multi_sweep.json to datasets/runs/maestro_fault_sweep/; cite adapter_costs and anti-gaming in draft.

**P4 verification (implementation, tests, deployment, SOTA):**

| Check | Status |
|-------|--------|
| Scenario family/taxonomy in SCENARIO_SPEC and all scenario YAMLs | Done; optional `family` field; get_scenario_family() in scenario.py |
| Adapter limitation and no human judge stated in draft | Done; Section 4 and Section 8 (Limitations) |
| Comparison to other benchmarks + benchmark release doc/JSON | Done; subsection and table in draft; BENCHMARK_RELEASE.v0.1.md, benchmark_scenarios.v0.1.json |
| Integration tests (fault sweep + baselines + baseline_summary.json) | Done; test_maestro_p4.py; 5 tests (2 integration, 3 scenario family) |
| Draft Table 1 and Table 2 as markdown; export_maestro_tables.py | Done; script reads multi_sweep.json and baseline_summary.json |
| REPRODUCIBILITY.md Benchmark release subsection | Done |
| CI runs P4 fault sweep and P4 baselines | Done; test job runs unit+integration tests; conditional-evals runs maestro_fault_sweep.py and maestro_baselines.py |
| STATE_OF_THE_ART_CRITERIA: real eval launches, methodology, baselines, claims backing | Done; draft has hypothesis, kill criterion, metrics, Table 1/2, claims table; integration test asserts artifacts |

### P1 (Contracts)

- **Existing:** `contracts_eval.py` on the full tiered corpus (54+ sequences: positive controls, split-brain, stale write/reorder, boundary, long-horizon, adversarial including cross-key interleaving, delayed release/reassignment, concurrent controller races); pure validator and reference store. Every run writes **named comparators** in `ablation` / `ablation_by_class`: full contract, timestamp_only, ownership_only, occ_only, lease_only, lock_only, accept_all, naive_lww (OCC/lease/lock/LWW are **reference proxies** on this corpus; see draft and export script footnotes). Baseline counters: `baseline_*_denials` / `baseline_*_missed` for each. **`detection_metrics_by_class`:** per inferred class (including `control`), TP/FP/FN and precision/recall/F1; JSON `null` / exported `n/a` when metrics are undefined (e.g. no expected denials and no FPs on controls). **`excellence_metrics`:** per_class_ci95 (uncertainty intervals), split_brain_detection_advantage. **Async stress:** `contracts_async_stress.py` → `stress_results.json` (delay/skew/reorder sweeps). **Transport parity:** `contracts_transport_parity.py` → `transport_parity.json` with `parity_ok_all`, `per_sequence[]`, and `parity_confidence` (default multi-sequence stems; `--sequences` override). **Scale test:** `--scale-test [--scale-events 100000]` writes `scale_test.json`. **Gatekeeper:** `allow_release(run_dir, check_contracts=True)`; release CLI defaults to conformance-only. **State machine:** `instrument_state_machine.py`; optional `use_instrument_state_machine`. **Trace-derivability:** `docs/P1_TRACE_DERIVABILITY.md`. **Labeling:** `bench/contracts/BENCHMARK_SPEC.v0.1.md` (ground-truth / anti-circularity). Tables/figures: `export_contracts_corpus_table.py` (Tables 1–3), `export_p1_contract_flow.py`, `plot_contracts_scale.py`. Throughput: `--throughput --scale 1000 --throughput-runs 5` on eval.json.
- **Validity and robustness:** `eval.json` includes `run_manifest` (script_version, corpus_fingerprint, corpus_sequences), `success_criteria_met.all_detection_ok`, exact per-event verdict vectors. Integration test: `tests/test_contracts_p1.py` (corpus driver + eval + scale-test smoke).
- **Follow-up:** Run `contracts_eval.py` and `contracts_transport_parity.py`; keep `eval.json` / `transport_parity.json` under `datasets/runs/contracts_eval/` for publishable cites; regenerate `papers/P1_Contracts/generated_tables.md` via export or `generate_paper_artifacts.py --paper P1`.

### P7 (Standards mapping)

- **Existing:** `run_assurance_eval.py` runs `check_assurance_mapping` and scripted review on toy_lab_v0 and lab_profile_v0; writes `results.json` (`mapping_check`, `reviews`, scenario-matched `per_profile`, `run_manifest`, `success_criteria_met`). **`run_assurance_robust_eval.py`** writes `robust_results.json` (default 20 seeds, 400 runs). **`run_assurance_negative_eval.py`** writes `negative_results.json` (ablations `schema_only` / `schema_plus_presence` / `full_review`, `generation`, `by_scenario`, `by_perturbation`, lift metrics); use `--submission-mode` for blind-review-safe manifests. **`export_p7_negative_tables.py`** emits `papers/P7_StandardsMapping/p7_*.csv` (Tables 4–6 + reject matrix + lift + latency + by-scenario + boundary summary + redacted manifest + generation metadata). **Auditor:** `audit_bundle.py` (optional `--release datasets/releases/portfolio_v0.1`). **Part 11:** `docs/PART11_AUDIT_TRAIL_ALIGNMENT.md`. **GSN / figures:** `export_assurance_gsn.py`, `export_p7_mapping_flow.py`, `p7_review_stages.mmd`, `render_p7_mermaid_figures.py`. Docs: `P7_STANDARDS_MAPPING.md`, `P7_ROBUST_EXPERIMENT_PLAN.md`, `P7_REVIEW_CHECKLIST.md`, `P7_REVIEW_FAILURE_CODES.md`, `P7_PERTURBATION_CHECKLIST.md`. Non-goals and K7 as in DRAFT.
- **Existing:** `run_assurance_eval.py` runs `check_assurance_mapping` and scripted review on toy_lab_v0 and lab_profile_v0; writes `results.json` (`mapping_check`, `reviews`, scenario-matched `per_profile`, `run_manifest`, `success_criteria_met`). **`run_assurance_robust_eval.py`** writes `robust_results.json` (default 20 seeds, 400 runs). **`run_assurance_negative_eval.py`** writes `negative_results.json` (ablations `schema_only` / `schema_plus_presence` / `full_review`, `generation`, `by_scenario`, `by_perturbation`, lift metrics); use `--submission-mode` for blind-review-safe manifests. **`export_p7_negative_tables.py`** emits `papers/P7_StandardsMapping/p7_*.csv` (Tables 4–6 + reject matrix + lift + latency + by-scenario + boundary summary + redacted manifest + generation metadata). **AIES path:** `assurance_eval_aies/` is generated with `export_bounded_review_packet.py`, `export_aies_assurance_tables.py`, and `export_aies_review_packet_figure.py` to produce institutional main-text exports (`lab_profile_v0`, `warehouse_v0`) plus bounded-access reviewer artifacts and `RUN_MANIFEST.json`; proxy-domain outputs are demoted to `proxy_stress_only/`. **Auditor:** `audit_bundle.py` (optional `--release datasets/releases/portfolio_v0.1`). **Part 11:** `docs/PART11_AUDIT_TRAIL_ALIGNMENT.md`. **GSN / figures:** `export_assurance_gsn.py`, `export_p7_mapping_flow.py`, `p7_review_stages.mmd`, `render_p7_mermaid_figures.py`. Docs: `P7_STANDARDS_MAPPING.md`, `P7_ROBUST_EXPERIMENT_PLAN.md`, `P7_REVIEW_CHECKLIST.md`, `P7_REVIEW_FAILURE_CODES.md`, `P7_PERTURBATION_CHECKLIST.md`, `AIES_2026_ASSURANCE_SPRINT.md`. Non-goals and K7 as in DRAFT.
- **Validity and robustness:** Deterministic mapping checks; robust matrix for positive-control stability; negative suite for **discrimination** (false-accept gap under baselines vs `full_review`).
- **Integration tests:** `tests/test_assurance_p7.py` (baseline eval + export_assurance_tables); **`tests/test_assurance_negative_eval.py`** (quick negative eval + export_p7_negative_tables + CSV↔JSON consistency checks for `by_mode`, `by_family`, and aggregate lift fields).
- **Unit test:** `TestAssuranceMappingCheck` asserts `check_assurance_mapping` JSON has `mapping_ok` and `ponr_coverage_ok`.
- **Export:** `export_assurance_tables.py` (Tables 1–3); `export_p7_negative_tables.py` (Tables 4–6 + supplements).
- **P7 verification (SOTA):**

| Check | Status |
|-------|--------|
| Hermetic integration test (--out temp dir) | Done; test_assurance_p7.py |
| Multi-scenario review (toy_lab_v0 + lab_profile_v0) | Done; kernel PONR exercised |
| Robust matrix + negative suite + CSV exports | Done; runbooks + test_assurance_negative_eval.py |
| Assert ponr_coverage_ok, ponr_coverage, control_coverage_ratio | Done |
| Assert export_assurance_tables.py succeeds | Done |
| Unit test for check_assurance_mapping | Done |
| Draft: standard link, tables 1–6 (+ boundary/by-scenario supplements), comparison, limitations, threat model | Done (DRAFT v0.4+) |

---

## 6. Suggested order for next runs

**One-command option:** Run `python scripts/run_paper_experiments.py` (or `--quick` for fewer seeds, `--paper P0` … `P8` for one paper) to execute a tailored set of experiments per paper; outputs go to `datasets/runs/` as below. See [EVALS_RUNBOOK.md](EVALS_RUNBOOK.md).

1. **Quick wins (all papers):**  
   - P3: Run `replay_eval.py` → save to `datasets/runs/replay_eval/`.  
   - P4: Run `maestro_fault_sweep.py` for toy_lab_v0 and lab_profile_v0 → save to `datasets/runs/maestro_fault_sweep/`.  
   - P1: Run `contracts_eval.py` and `contracts_transport_parity.py` → `datasets/runs/contracts_eval/` (`eval.json`, `transport_parity.json`).  
   - P7: Run assurance check/review on one run → write to `datasets/runs/assurance_eval/`.

2. **Conditional papers — deeper evals:**  
   - P2: More seeds (10), delay sweep, optional naive-mean baseline.  
   - P5: More seeds (12--30), `--fault-mix`, optional family holdout, refresh `RUN_RESULTS_SUMMARY.md`.  
   - P6: More red-team cases, `--run-adapter` for latency.  
   - P8: Higher fault and/or lower thresholds to trigger switches; naive-switching baseline.

3. **Unify reporting:**  
   - Ensure every eval script writes a summary JSON under `datasets/runs/<eval_name>/` and that the runbook and STATE_OF_THE_ART_CRITERIA point to “results in datasets” for each paper.

---

## 7. Summary table (current state)

| Paper | Primary result location | Main finding | Next step |
|-------|-------------------------|-------------|-----------|
| P2 | rep_cps_eval/summary.json | Robust aggregation reduces bias; delay sweep + scenarios in place | Draft; optional naive-in-loop adapter |
| P5 | scaling_eval/heldout_results.json (+ optional scaling_eval_family/) | Seven scenarios, fault-mix, secondary_targets, PI coverage, family OOS; trigger_met | Draft; refresh seeds as needed |
| P6 | llm_eval_camera_ready_20260424/red_team_results.json (+ sibling bundle JSONs) | Red-team + confusable + jailbreak-style suites; adapter latency; real-LLM Table 1b; baselines; replay + mock harness artifacts | Draft |
| P8 | meta_eval/comparison.json (+ optional scenario_regime_stress_v1/) | Non-inferior collapse vs fixed, paired stats, auditable switches; publishable dual-scenario + non-vacuous stress policy | Draft; verify_p8_meta_artifacts |
| P0 | p0_conformance_corpus/, e3_summary.json, p0_e4_raw_summary.json, p0_e4_normalized_summary.json, p0_e4_per_seed.jsonl, p0_e4_diagnostics.json, p0_e4_controller_pairs.jsonl, p0_e4_raw_failure_reasons.json, p0_e4_controller_matrix.json, e2_redaction_demo/, p0_conformance_summary.json | E1 corpus; E2 4-col matrix; E3 replay link (optional standalone verifier); E4 controller matrix + controller-separating evidence + raw-failure causal accounting; Table 1/2/3, Figures 1-3; repro in DRAFT Appendix | Claim table + Appendix |
| P3 | replay_eval/summary.json | L0 + corpus + baselines + multi-seed; schema v0.2; verify script | Draft |
| P4 | maestro_fault_sweep/ (multi_sweep.json) | Multi-scenario; drop + delay_fault_prob sweep | Draft |
| P1 | contracts_eval/eval.json (+ transport_parity.json) | Exact corpus verdicts; comparators + per-class metrics; boundary parity artifact; P1_TRACE_DERIVABILITY; export_contracts_corpus_table, export_p1_contract_flow, plot_contracts_scale | Claim table + repro block |
| P7 | assurance_eval/results.json, robust_results.json, negative_results.json, papers/P7_StandardsMapping/p7_*.csv, assurance_eval_aies/ | Mapping + PONR + robust matrix + negative suite / ablations + boundary cases; institutional AIES bundle (lab baseline + warehouse portability + bounded-review packet + proxy_stress_only split); audit_bundle; Part 11; export_assurance_gsn; export_p7_negative_tables; export_aies_assurance_tables | Claim table + repro block |

Using this document you can interpret existing results, plug in new result files as they appear, and launch the suggested follow-up tests and experiments for all papers in a consistent way.

---

## 8. Experiments run (from interpretation plan)

The following were run and written under `datasets/runs/`:

| Paper | Script / action | Output |
|-------|-----------------|--------|
| P0 | `build_p0_conformance_corpus.py` (CI) | `p0_conformance_corpus/`, `corpus_manifest.json` |
| P0 | `produce_p0_e3_release.py --runs 10 --no-release` (CI) | `e3_summary.json`, `p0_e3_variance.json` |
| P0 | `e2_redaction_demo.py` (CI) | `e2_redaction_demo/trace_redacted.json` |
| P0 | `run_p0_e4_controller_matrix.py` | `p0_e4_raw_summary.json`, `p0_e4_normalized_summary.json`, `p0_e4_per_seed.jsonl`, `p0_e4_diagnostics.json`, `p0_e4_controller_pairs.jsonl`, `p0_e4_raw_failure_reasons.json`, `p0_e4_controller_matrix.json` |
| P3 | `replay_eval.py` (default out) | `replay_eval/summary.json` |
| P4 | `maestro_fault_sweep.py --seeds 5` (multi-scenario) | `maestro_fault_sweep/{toy_lab_v0,lab_profile_v0}/sweep.json`, `multi_sweep.json` |
| P1 | `contracts_eval.py`; `contracts_transport_parity.py` | `contracts_eval/eval.json`; `transport_parity.json` |
| P7 | `run_assurance_eval.py`, `run_assurance_robust_eval.py`, `run_assurance_negative_eval.py` | `assurance_eval/results.json`, `robust_results.json`, `negative_results.json` |
| P2 | `rep_cps_eval.py --delay-sweep 0,0.05,0.1` (CI) | `rep_cps_eval/summary.json` |
| P5 | `generate_multiscenario_runs.py`, `scaling_heldout_eval.py` (optional `--holdout-mode family`) | `scaling_eval/heldout_results.json`, optional `scaling_eval_family/`; tables: `export_scaling_tables.py` |
| P6 | `llm_redteam_eval.py --run-adapter` (CI smoke) | temp `llm_eval/` scratch outputs; canonical bundle: `llm_eval_camera_ready_20260424/` |
| P8 | `meta_eval.py` (CI: `--run-naive --fault-threshold 0`, `--seeds` 1,2,3; v1 smoke; `verify_p8_meta_artifacts`) | `meta_eval/comparison.json` |

P5: feature and regression baselines beat global mean on held-out folds when `trigger_met` is true; see `overall_feat_baseline_mae` vs `overall_baseline_mae` and `secondary_targets` in `heldout_results.json`. P6: synthetic red-team suite is versioned in `llm_planning.py` (15 cases in the released suite); camera-ready bundle includes real-LLM Table 1b and adapter/baseline artifacts; `verify_p6_camera_ready_bundle.py` enforces headline invariants in CI. P8: use `--fault-threshold 0 --run-naive` to exercise naive switches; publishable pipeline uses `run_paper_experiments.py --paper P8` (non-vacuous, dual scenario, optional `retry_heavy`).

---

## 9. Remaining experiments (implemented and run)

| Paper | What was added | How to run |
|-------|----------------|------------|
| **P2** | Delay sweep + three scenarios (including scheduling) | `rep_cps_eval.py --delay-sweep 0,0.05,0.1 --scenarios toy_lab_v0,lab_profile_v0,rep_cps_scheduling_v0 --seeds 1,2,3`; output includes `delay_sweep`, `scheduling_dependent_eval`, `freshness_replay_evidence`, `sybil_vs_spoofing_evidence`, `messaging_sim`, `dynamic_aggregation_series`, and per-scenario stability. |
| **P4** | delay_fault_prob sweep | `maestro_fault_sweep.py` now has 4 settings: no_drop, drop_005, delay_01, drop_005_delay_01; each setting has `delay_fault_prob` in summary. |
| **P8** | Non-vacuous stress + dual scenario + paired stats | `run_paper_experiments.py --paper P8`; `meta_eval.py --scenario`, `--non-vacuous`, `stress_selection_policy`, `collapse_paired_analysis`, `verify_p8_meta_artifacts.py`; `meta_collapse_sweep.py` writes `schema_version` on sweep JSON. |
| **P0** | Table 1 (E1 corpus) | `build_p0_conformance_corpus.py`, `export_e1_corpus_table.py`. |
| **P0** | Table 2 (E2 admissibility) | `e2_redaction_demo.py`, `export_e2_admissibility_matrix.py` (4-col verification-mode matrix). |
| **P0** | Table 3 (E3+E4) | `run_p0_e4_controller_matrix.py`, `export_p0_table3.py` (strong replay preference: `p0_e4_raw_summary.json` baseline rows first, E3 strong replay if present); optionally refresh E3 via produce_p0_e3_release + export_p0_table3 --e3. |
| **P0** | E3 variance / per-seed table | `produce_p0_e3_release.py` (--runs 20); `export_e3_table.py` (per-seed table for appendix). |
| **P0** | E2 redaction demo | `e2_redaction_demo.py` -> `datasets/runs/e2_redaction_demo/trace_redacted.json`. |

**P5 (more N / stronger OOS):** Run `generate_multiscenario_runs.py --seeds 12` (or higher) with `--fault-mix`, then `scaling_heldout_eval.py`. Optional: `--holdout-mode family --no-secondary --out datasets/runs/scaling_eval_family`. **P5 implemented:** regression on compact features, derived proxies in `response`, scenario `family`, `secondary_targets`, PI coverage summary, regression MAE CI across folds, collapse (report-derived), `scaling_fit`, `export_scaling_tables.py`, integration test `test_scaling_p5.py`, unit tests for `scaling` module.
