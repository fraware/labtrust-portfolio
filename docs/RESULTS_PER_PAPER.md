# Results per paper — Quick reference

This document explains what each paper (P0–P8) measures, where its results are written, and how to read them. All paths are relative to the repo root; results live under `datasets/runs/` unless noted. **Consolidated summary:** After running all paper experiments (`run_paper_experiments.py`), see [datasets/runs/RUN_RESULTS_SUMMARY.md](../datasets/runs/RUN_RESULTS_SUMMARY.md) for a single-file results summary per paper. **Where this appears in the draft:** For each paper, tables and figures are cited in `papers/Px_.../DRAFT.md` with captions and in-text interpretation; generated table content (with "How to read" and captions) lives in `papers/Px_.../generated_tables.md` where present.

**Excellence metrics:** Eval summary JSONs may include an optional `excellence_metrics` block (see [STANDARDS_OF_EXCELLENCE.md](STANDARDS_OF_EXCELLENCE.md)). To print a one-line excellence summary across all papers: `python scripts/export_excellence_summary.py` (or `--json` for machine-readable output). Regenerate evals to populate excellence_metrics.

---

## P0 — MADS-CPS (normative minimum bar)

**What it measures:** Conformance tiers (E1), redaction (E2), and replay-link variance (E3). Does an independent verifier get the same MAESTRO metrics from TRACE across seeds?

**Result locations:**
- `datasets/runs/e3_summary.json` — E3 replay-link summary over N seeds (default 20 for publishable)
- `datasets/runs/p0_e3_variance.json` — variance and 95% CIs
- `datasets/runs/e2_redaction_demo/trace_redacted.json` — one redacted trace (E2)
- `datasets/releases/p0_e3_release/` — released run (produced only when `produce_p0_e3_release.py` is run without `--no-release`; tables can be regenerated from `e3_summary.json` in `datasets/runs/` via export_e3_table.py when release is not produced)
- `datasets/releases/portfolio_v0.1/p0_conformance_summary.json` — conformance aggregated over P0 runs (from `scripts/build_p0_conformance_summary.py`)

**How to read:**
- **E3:** `tasks_completed_mean`, `tasks_completed_stdev`, `p95_latency_ms_mean`, `p99_latency_ms`, `all_match`, 95% CIs; `run_manifest` (seeds, scenario_ids, fault_settings, script; optional version from GIT_SHA); `success_criteria_met.e3_all_match`. Optional `excellence_metrics`: e3_ci_width_p95_ms, conformance_match_pct, n_scenarios, n_runs_per_scenario. With `--scenarios`: `per_scenario[]` (scenario_id, tasks_completed_mean/stdev, p95_latency_ms_mean/stdev, all_match, per_run). See `docs/REPORTING_STANDARD.md`.
- **E1:** Conformance is per-run via `labtrust_portfolio check-conformance <run_dir>`, which writes `<run_dir>/conformance.json` (tier, pass, reasons); schema: `kernel/conformance/CONFORMANCE.v0.1.schema.json`. no single “E1 result file.”
- **E2:** Redacted trace has payloads replaced by content-addressed refs; structure preserved for audit. The redacted trace is not replayed (L0 replay expects full payloads e.g. task_id); evidence_bundle_redacted has replay_ok false and replay_diagnostics noting audit-only.
- **Verification mode:** Evidence bundle schema requires `verification_mode` (public | evaluator | regulator). Public bundles are verifiable but not required replayable; restricted bundles are replayable at L0/L1 when full trace exists. See `kernel/mads/VERIFICATION_MODES.v0.1.md`.

**Tables and figures:** `python scripts/export_e3_table.py` (full table); `python scripts/export_e3_table.py --compact` (per-scenario variance + CI); `python scripts/export_e2_admissibility_matrix.py` (E2 redaction admissibility matrix); `python scripts/plot_e3_latency.py` (E3 p95 latency by scenario, output `docs/figures/p0_e3_latency.png`); `python scripts/build_p0_conformance_summary.py` (p0_conformance_summary.json). See `docs/P0_CONFORMANCE_SUMMARY_SPEC.md`.

---

## P1 — Coordination Contracts

**What it measures:** Whether the contract validator correctly allows/denies event sequences (seven corpus sequences: good_sequence, split_brain, stale_write, reorder, unsafe_lww, multi_writer_contention, edge_case_timestamps). Scale test (long trace); gatekeeper denies release when contract invalid; lab-aligned instrument state machine.

**Result locations:**
- `datasets/runs/contracts_eval/eval.json` — corpus sequences, detection_ok, baseline_timestamp_only.
- `datasets/runs/contracts_eval/scale_test.json` — when run with `--scale-test` (total_events, denials, total_time_sec, time_per_write_us, events_per_sec).

**How to read:**
- `run_manifest`: corpus_sequences, corpus_dir, script. `success_criteria_met.all_detection_ok`: true when all sequences have detection_ok. Optional `excellence_metrics`: corpus_detection_rate_pct, overhead_p99_us, baseline_margin_denials.
- `sequences[]`: each has `sequence`, `detection_ok` (true = violations denied as expected), `allows`, `denials`, `time_per_write_us`.
- `violations_denied_with_validator`: total violations correctly denied.
- `baseline_timestamp_only_denials` / `baseline_timestamp_only_missed`: comparison to a timestamp-only (monotonicity) baseline.
- **Gatekeeper:** `allow_release(run_dir, check_contracts=True)` runs contract validator on trace; if any event denied, release is blocked. CLI: `labtrust_portfolio release-dataset --check-contracts <run_dir> <release_id>` enables strict PONR gating; default is conformance-only. See `impl/.../gatekeeper.py` (`check_contracts_on_trace`).
- **State machine:** `bench/contracts/README.md` documents alignment of single-writer contract with `instrument_state_machine.py` (idle/running transitions). Contract option `use_instrument_state_machine: true` enforces it.
- **Trace-derivability:** All contract predicates are computed from trace alone (no privileged hidden state). See `docs/P1_TRACE_DERIVABILITY.md`. Kill criterion K1: if a predicate required hidden state, design loses portability.
- **trigger_met:** In success_criteria_met when adapter runs: trigger_met = adapter_parity and robust_beats_naive (or robust_beats_naive when no adapter).

**Tables and figures:** `python scripts/export_contracts_corpus_table.py` (corpus detection_ok + timestamp-only baseline); `python scripts/plot_contracts_scale.py` (throughput vs event count, output `docs/figures/p1_scale_throughput.png`).

---

## P2 — REP-CPS (robust aggregation)

**What it measures:** REP-CPS adapter vs centralized baseline; robust (trimmed-mean, clipping, median_of_means) vs naive aggregation under compromise; delay sweep; sybil stress test; safety-gate integration.

**Result locations:**
- `datasets/runs/rep_cps_eval/summary.json` — adapter comparison, aggregation_under_compromise, delay_sweep, aggregation_variants, sybil_sweep.
- `datasets/runs/rep_cps_eval/safety_gate_denial.json` — claim that REP output cannot directly trigger actuation; denial trace recorded when policy rejects.

**How to read:**
- `run_manifest`: seeds, scenario_ids, delay_fault_prob_sweep, aggregation_steps_used, script. `aggregation_steps`, `convergence_achieved` (when --aggregation-steps > 1). `success_criteria_met`: adapter_parity (REP == centralized), robust_beats_naive. Optional `excellence_metrics`: influence_bound_max_per_compromised, bias_reduction_pct, safety_gate_integration, trigger_met. When n >= 2: `rep_cps_tasks_completed_ci95`, `centralized_tasks_completed_ci95`.
- Effect size: `excellence_metrics.bias_reduction_pct` (when aggregation_under_compromise has bias_naive > 0); comparison stats `difference_mean`, `difference_ci95`, `paired_t_p_value` when n >= 2 (adapter comparison).
- `rep_cps_tasks_completed_mean` vs `centralized_tasks_completed_mean`: should be equal (no throughput regression).
- `aggregation_under_compromise`: `honest_only_aggregate`, `with_compromise_robust_aggregate`, `with_compromise_naive_aggregate`; `bias_robust` < `bias_naive` means robust aggregation reduces bias under Byzantine inputs.
- `aggregation_variants[]`: per method (trimmed_mean, median, clipping, median_of_means), `bias`, `max_influence_per_compromised_agent`. `success_criteria_met.trigger_met`: REP-CPS improves robustness without throughput regression on evaluated scenario (conditional; see `docs/CONDITIONAL_TRIGGERS.md`).
- `sybil_sweep[]`: per `n_compromised`, `bias_robust`, `bias_naive` (robust should degrade gracefully).
- `delay_sweep[]`: per delay_fault_prob, tasks_completed mean/stdev and centralized baseline.
- **Convergence (multi-step aggregation):** When `--aggregation-steps > 1`, summary includes `convergence_steps_to_convergence_mean`, `convergence_steps_to_convergence_stdev`, `convergence_achieved_rate`; per-seed `rep_cps_steps_to_convergence`. Table 4: `python scripts/export_rep_cps_convergence_table.py` (from summary.json).
- `rep_cps_naive_tasks_completed_mean`, `rep_cps_unsecured_tasks_completed_mean`: naive-in-loop and unsecured baselines.

---

## P3 — Replay (replay levels and nondeterminism detection)

**What it measures:** L0 replay fidelity (thin-slice trace replays bit-identical); corpus of “trap” traces that are expected to diverge (discovery from all *_trace.json/*_expected.json pairs in bench/replay/corpus, e.g. nondeterminism, reorder, timestamp_reorder, hash_mismatch_trap); replay overhead; root cause category for divergences; overhead curve (p95 vs trace size). **L1** stub (L0 + twin config validation) and **L1 twin** (--l1-twin: deterministic re-run of control-plane state machine; l1_twin_ok, l1_twin_final_hash_match). **L2** aspirational with design subsection in REPLAY_LEVELS. Full corpus table: `scripts/export_replay_corpus_table.py`. Tables: DRAFT and `papers/P3_Replay/generated_tables.md`.

**Result location:** `datasets/runs/replay_eval/summary.json`. Use `--out datasets/runs/replay_eval/summary.json` (file path, not directory).

**How to read:**
- `run_manifest`: corpus_dir, overhead_runs, overhead_curve_runs, script. `success_criteria_met`: fidelity_pass, corpus_divergences_detected. Optional `excellence_metrics`: divergence_localization_accuracy_pct, overhead_p99_ms, l1_stub_ok, witness_slices_present.
- `replay_level` (L0|L1|L2), `nondeterminism_budget`, `divergence_localization_confidence`.
- `fidelity_pass`, `corpus_divergence_detected[]` (each can include `root_cause_category`: scheduler, tool_io, timestamp, unknown; and `witness_slice`: events around divergence_at_seq), **witness_slices** (top-level list of all divergence witness slices from corpus/run), `overhead_stats`, `l1_stub_ok`. Overhead curve bins may include `p95_replay_stdev_ms` when n > 1.
- `overhead_curve[]`: with `--overhead-curve`, `event_count` and `p95_replay_ms` per trace size.
- **L1:** See `bench/replay/README.md` and `kernel/trace/REPLAY_LEVELS.v0.1.md`: L1 = control-plane replay with recorded observations, not physics replay; use `--l1-twin` for full L1 (deterministic twin re-run). `l1_twin_ok`, `l1_twin_final_hash_match` in summary when `--l1-twin`. Table: `python scripts/export_replay_corpus_table.py` (all corpus traces).

**Figure:** `python scripts/plot_replay_overhead.py` (p95 replay ms vs event count from overhead_curve; output `docs/figures/p3_replay_overhead.png`).

---

## P4 — CPS-MAESTRO (fault sweep and baselines)

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

**What it measures:** Can we predict tasks_completed for a held-out scenario from other scenarios? Global-mean vs feature-based vs regression baseline; MAE and 95% CI; scaling_fit (exploratory exponent).

**Result location:** `datasets/runs/scaling_heldout_eval/results.json` (or `scaling_eval/heldout_results.json` depending on script)

**How to read:**
- `run_manifest`: runs_dir, scenario_ids, held_out_scenarios, train_n_total, test_n_total, script. `success_criteria_met`: beat_baseline_out_of_sample, beat_per_scenario_baseline, trigger_met (conditional paper; see `docs/CONDITIONAL_TRIGGERS.md`). Optional `excellence_metrics`: out_of_sample_margin_vs_global_baseline, ci_width_95_baseline_mae, beat_baseline_out_of_sample, scenario_coverage.
- `held_out_results[]`: per held-out scenario, `baseline_mae`, `feat_baseline_mae`, `regression_mae`, `stump_mae`, `actuals_mean`, `train_n`, `test_n`.
- `overall_baseline_mae`, `overall_feat_baseline_mae`, `overall_regression_mae`, `overall_stump_mae`: aggregate; when regression is skipped (e.g. train_n < k or singular), summary includes `regression_skipped_reason`; export_scaling_tables prints N/A with footnote. Feature/regression/stump beating global mean = “beat baseline out-of-sample.”
- `overall_*_mae_ci95_lower/upper`: 95% CI for MAE.
- `scaling_fit`: `scaling_exponent`, `scaling_r2`, `n_used` (exploratory log-log fit).
- **Title/claims:** If scaling-law stability is not demonstrated, use "empirical predictors" and state scaling laws are exploratory.
- `overall_collapse_rate`, per-result `test_collapse_rate`: collapse (e.g. tasks_completed below threshold) if defined.

**Tables:** `scripts/export_scaling_tables.py`.

---

## P6 — LLM Planning (red-team and adapter latency)

**What it measures:** Red-team: does the policy block disallowed tools and allow allowed ones? Confusable deputy: adversarial tool output (args requesting privilege) blocked. Jailbreak-style: prompt-injection style args (e.g. "ignore previous instructions") blocked by safe_args. Validator v0.2: allow_list + safe_args (path traversal, dangerous patterns, jailbreak-style phrases). E2E denial trace: planner proposes unsafe, validator blocks, system recovers. Adapter latency: p95 and wall time for synthetic adapter runs. **Evidence is from synthetic plans by default;** real-LLM mode (`--real-llm`) is optional; optional smoke: `scripts/llm_real_llm_smoke.py` when .env has keys (writes real_llm_smoke.json). Full table: `python scripts/export_llm_redteam_table.py` (8 red-team + 4 confusable deputy + jailbreak_style; optional Table 1b for real-LLM). OWASP LLM Top 10 coverage: [docs/P6_OWASP_MAPPING.md](P6_OWASP_MAPPING.md).

**Result locations:**
- `datasets/runs/llm_eval/red_team_results.json` — red-team cases (8)
- `datasets/runs/llm_eval/confusable_deputy_results.json` — confusable deputy cases (4; args induce privilege; validate_plan_step blocks)
- `datasets/runs/llm_eval/e2e_denial_trace.json` — claim and example: planner proposed unsafe, validator blocked, recovery safe
- `datasets/runs/llm_eval/adapter_latency.json` — only when run with `--run-adapter`

**How to read:**
- **Red-team:** `run_manifest` (red_team_cases, script); `success_criteria_met.red_team_all_pass`, `success_criteria_met.trigger_met` (conditional: firewall reduces unsafe without collapsing completion). `cases[]` each has `expected_block`, `actually_blocked`, `pass`. Optional `excellence_metrics`: red_team_pass_rate_pct, n_cases, n_pass. Eight cases (e.g. rt_unsafe_tool, rt_safe_tool, rt_unsafe_write, rt_safe_submit, rt_unsafe_shell, rt_allowed_tool_disallowed_args, rt_boundary_tool_name, rt_safe_read_only). **Jailbreak-style:** `red_team_results.json` may include `jailbreak_style` (cases with prompt-injection style args; all_pass). Real-LLM: optional `--real-llm` when `.env` has API keys; results merged into red_team_results.json; export_llm_redteam_table can emit Table 1b for real-LLM.
- **Confusable deputy:** `success_criteria_met.confusable_deputy_all_pass`; `confusable_deputy_cases[]`, `all_pass`; excellence_metrics: confusable_deputy_pass_rate_pct. Validator blocks steps whose args request elevation/privilege.
- **E2E denial:** `e2e_denial_trace.json` documents blocked step example and outcome (blocked, recovery safe).
- **Adapter latency:** `run_manifest` (adapter_scenarios, adapter_seeds, script); `runs[]` (scenario_id, seed, task_latency_ms_p95, wall_sec); `tail_latency_p95_mean_ms`; excellence_metrics: denial_latency_p95_mean_ms, e2e_denial_trace_present. When n >= 2: `tail_latency_p95_stdev_ms`, `tail_latency_p95_ci95_lower/upper`.

---

## P7 — Standards mapping (assurance pack)

**What it measures:** Mapping check (hazards → controls → evidence types; PONR coverage); per-scenario review (evidence_bundle, trace, PONR events, controls_covered); auditor walk-through (mapping + PONR + optional run review); Part 11-style audit trail alignment. Non-goals: no certification claim; translation layer only. **Three instantiations:** lab v0.1, warehouse v0.1, medical v0.1; results.json includes `per_profile` (review outcome per pack). Standards mapping table (assurance-pack elements to ISO 62304 / ISO 26262-6 clauses): [docs/P7_STANDARDS_MAPPING.md](P7_STANDARDS_MAPPING.md). **Review:** PONR coverage requires `--scenario-id` from the known list; no heuristic when scenario unknown. Scripted review is partial and does not constitute a full safety-case proof. Auditor feedback protocol: [docs/P7_AUDITOR_FEEDBACK_PROTOCOL.md](P7_AUDITOR_FEEDBACK_PROTOCOL.md).

**Result locations:**
- `datasets/runs/assurance_eval/results.json` — mapping_check, review, reviews
- **Auditor script:** `scripts/audit_bundle.py` — pass/fail mapping completeness and PONR coverage; `--run-dir` for optional run review; `--release datasets/releases/portfolio_v0.1` for one-command audit over a release dir (runs mapping + PONR; if release contains evidence_bundle.json, runs review there too). JSON + human output.
- **Part 11:** `docs/PART11_AUDIT_TRAIL_ALIGNMENT.md` — each requirement mapped to artifact path and field/event (machine-checkable; no prose-only).

**How to read:**
- `run_manifest`: scenarios, profile_dir, script. `success_criteria_met`: mapping_ok, ponr_coverage_ok. Optional `excellence_metrics`: mapping_completeness_pct, ponr_coverage_ratio, review_pass_all_scenarios, no_certification_claimed.
- `mapping_check.ok`: schema and mapping complete; `mapping_check.ponr_coverage_ok`: every profile PONR in at least one hazard.
- `reviews.<scenario_id>`: `evidence_bundle_ok`, `trace_ok`, `ponr_events[]`, `controls_covered[]`, `ponr_coverage.ratio`, `control_coverage_ratio`, `exit_ok`.
- `review`: backward-compat alias for toy_lab_v0. For lab_profile_v0, `ponr_coverage.required_task_names` typically includes `disposition_commit`.
- **Auditor:** Run `audit_bundle.py [--run-dir path]`; output includes `mapping_completeness`, `ponr_coverage`, `review_exit_ok` (if run-dir given).

**Tables and figure:** `scripts/export_assurance_tables.py`. `python scripts/export_assurance_gsn.py` (GSN-lite Mermaid graph from assurance_pack_instantiation.json). Non-goals: P7 DRAFT, kernel/assurance_pack/README.md, profiles/lab/v0.1/README.md. Kill criterion K7: no "template theater"; every mapping claim checkable by script or schema.

---

## P8 — Meta-Coordination (regime switching)

**What it measures:** Fixed (Centralized) vs meta-controller vs naive (switch-on-any-fault) baseline: tasks_completed_mean, collapse_count, regime_switch_count. Optional fallback adapter when meta switches: `--fallback-adapter blackboard|centralized|retry_heavy` (two real coordination algorithms; fallback_tasks_completed in per_seed when set). Second stress scenario: `--stress-preset very_high` or scenario `regime_stress_v1.yaml`. Thrash control (hysteresis: require N consecutive fault observations before switch). Force-collapse sweep: which drop_prob yields collapse in some seeds. Effect size: `excellence_metrics.collapse_reduction_vs_fixed`, `difference_mean`, `difference_ci95`, `paired_t_p_value` (meta vs fixed comparison).

**Result locations:**
- `datasets/runs/meta_eval/comparison.json` — fixed, meta_controller, naive_switch_baseline; no_safety_regression, meta_reduces_collapse, collapse_definition, per_seed. When publishable run uses non-vacuous procedure, run_manifest includes `non_vacuous: true` and drop_completion_prob was chosen from collapse_sweep (smallest drop_prob where collapse_count > 0).
- `datasets/runs/meta_eval/collapse_sweep.json` — from `scripts/meta_collapse_sweep.py`: per (drop_prob, seed) tasks_completed and collapsed; collapse_count; documents point at which collapse appears.

**Publishable run:** Run `meta_collapse_sweep.py` first (default 20 seeds), then `meta_eval.py --run-naive --fault-threshold 0 --non-vacuous` so Table 1 uses a drop_prob where collapse occurs. If no such drop_prob exists, meta_eval exits with a message; present results as methodology and auditability only. See EVALS_RUNBOOK P8.

**How to read:**
- `run_manifest`: seeds, scenario_id, drop_completion_prob, collapse_threshold, fault_threshold, script, optional non_vacuous. `success_criteria_met`: no_safety_regression, meta_reduces_collapse, trigger_met (conditional: meta beats best fixed in at least one stress regime, no safety regression; see `docs/CONDITIONAL_TRIGGERS.md`). Optional `excellence_metrics`: collapse_reduction_vs_fixed, no_safety_regression, switch_audit_trail_total, trigger_met. When n >= 2: `fixed.tasks_completed_ci95`, `meta_controller.tasks_completed_ci95` (and optional naive_switch_baseline.tasks_completed_ci95).
- `fixed`: `tasks_completed_mean`, `tasks_completed_stdev`, `tasks_completed_ci95`, `collapse_count`, `per_seed[]` (tasks_completed, collapse).
- `meta_controller`: same plus `per_seed[].regime_switch_count`; sum = regime_switch_count_total. Use `--hysteresis N` for thrash control.
- `naive_switch_baseline`: `tasks_completed_mean`, `regime_switch_count_total`, `per_seed[]`.
- `no_safety_regression`: true if meta mean ≥ 90% of fixed mean.
- `meta_reduces_collapse`: true if meta collapse_count ≤ naive (vacuously true when both 0).
- `collapse_definition`: "tasks_completed < {threshold} or recovery_ok false"; per-seed entries include `recovery_ok` when present in report.faults.
- **Collapse sweep:** Run `meta_collapse_sweep.py --drop-probs 0.15,0.2,0.25,0.3`; `per_run[]` gives (drop_prob, seed, tasks_completed, recovery_ok, collapsed); `collapse_count` shows how many runs collapsed.

**Tables and figure:** `python scripts/export_meta_tables.py --comparison datasets/runs/meta_eval/comparison.json` (add `--table2` for per-seed). Figure 1: run `meta_collapse_sweep.py` to produce collapse_sweep.json, then `python scripts/plot_meta_collapse.py --sweep datasets/runs/meta_eval/collapse_sweep.json` (output `docs/figures/p8_meta_collapse.png`).

---

## One-line summary

| Paper | One-line result |
|-------|------------------|
| P0 | E3: multi-scenario, per_scenario[]; E2 redacted + admissibility matrix; E1 conformance.json per run; verification_mode required; p0_conformance_summary.json; export_e3_table (--compact), plot_e3_latency, build_p0_conformance_summary. |
| P1 | Contract validator: corpus detection_ok; scale_test; gatekeeper check_contracts; instrument state machine; P1_TRACE_DERIVABILITY.md; export_contracts_corpus_table, plot_contracts_scale. |
| P2 | REP-CPS = centralized on tasks; aggregation_variants, sybil_sweep, safety_gate_denial; convergence (steps_to_convergence, Table 4) when --aggregation-steps > 1; robust lowers bias. |
| P3 | Fidelity pass; root_cause_category; witness_slice per divergence; overhead_curve; plot_replay_overhead; L1 stub + L1 twin (--l1-twin); export_replay_corpus_table; L2 design subsection. |
| P4 | Fault sweep (incl. calibration_invalid_01); recovery metrics (steps_after_fault, tasks_after_fault); Centralized/Blackboard/RetryHeavy baselines; anti-gaming + scoring_proof; adapter_costs.json; plot_maestro_recovery. |
| P5 | Held-out MAE; per_scenario_baseline_mae; feature/regression; 95% CI; scaling_fit; success_criteria_met.trigger_met; --seeds 20, --fault-mix. |
| P6 | Red-team (8) + confusable_deputy (4) + jailbreak_style; validator v0.2 (allow_list + safe_args); e2e_denial_trace; adapter_latency with --run-adapter; export_llm_redteam_table (Table 1b real-LLM when present); P6_OWASP_MAPPING; optional --real-llm. |
| P7 | mapping_check + ponr_coverage_ok; three profiles (lab, warehouse, medical); per_profile; P7_STANDARDS_MAPPING; audit_bundle.py (--release); PONR requires --scenario-id; export_assurance_gsn; P7_AUDITOR_FEEDBACK_PROTOCOL; non-goals; K7. |
| P8 | fixed/meta/naive; --non-vacuous (collapse_sweep-driven drop_prob); optional --fallback-adapter blackboard|centralized|retry_heavy; --stress-preset very_high / regime_stress_v1; comparison.json + collapse_sweep.json; trigger_met; export_meta_tables; plot_meta_collapse. |

For full interpretation, follow-up experiments, and verification checklists, see [EVAL_RESULTS_INTERPRETATION.md](EVAL_RESULTS_INTERPRETATION.md). For how to run each pipeline, see [EVALS_RUNBOOK.md](EVALS_RUNBOOK.md).
