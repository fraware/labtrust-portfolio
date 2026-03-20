# Standards of Excellence (Beyond the Peer-Review Bar)

This document defines **optional excellence metrics** that strengthen each paper and the portfolio beyond the minimum in [STATE_OF_THE_ART_CRITERIA.md](STATE_OF_THE_ART_CRITERIA.md) and [REPORTING_STANDARD.md](REPORTING_STANDARD.md). Adopting these improves reproducibility badges, reviewer confidence, and comparability with top-tier venues.

## Portfolio-wide excellence metrics

These apply to every paper; add to run manifests, summary JSONs, or docs as feasible.

| Metric | Description | Where to record |
|--------|-------------|-----------------|
| **Repro time (wall-clock)** | Actual time (minutes) to run minimal repro from clean clone to tables + Figure 1. Target: under 20 min. | DRAFT.md minimal run note; or `repro_wall_min` in a meta manifest. |
| **Effect size vs baseline** | When comparing to a baseline, report relative improvement or difference (e.g. "X% fewer violations", "Y ms lower p95"). | Draft text + summary JSON (e.g. `baseline_margin`, `improvement_pct`). |
| **Statistical test (optional)** | Where two conditions are compared, report a simple test (e.g. paired t-test, bootstrap CI for difference) and whether the difference is significant at a stated alpha. | Summary JSON: `excellence_metrics.difference_mean`, `difference_ci95`, `paired_t_p_value`, `alpha` (meta_eval, rep_cps_eval, scaling_heldout_eval via labtrust_portfolio.stats). See REPORTING_STANDARD.md section 5. |
| **Threats to validity** | One short subsection or bullet list: internal (e.g. single platform), external (e.g. scenario coverage), construct (e.g. proxy metrics). | Limitations in DRAFT.md. |
| **Artifact badge readiness** | Artifact available (repo/tag); artifact functional (scripts run); results reproducible (same commands, same env). Document for AE. | README or supplement; tag + PRE_SUBMISSION_CHECKLIST. |
| **Claim confidence** | Per claim: "high" (direct measure + 20 seeds + script), "medium" (fewer seeds or proxy), "low" (qualitative). | claims.yaml optional `evidence.confidence` or DRAFT backing sentence. |

## Per-paper excellence metrics

Add these to the relevant eval summary JSON and, where useful, to the draft. Scripts can populate `success_criteria_met` or a dedicated `excellence_metrics` block.

### P0 — MADS-CPS

| Metric | Description | Source / script |
|--------|-------------|-----------------|
| E1 corpus agreement (%) | Fraction of challenge cases where checker outcome matches expected tier/pass. | corpus_manifest.json; build_p0_conformance_corpus, export_e1_corpus_table. |
| Conformance coverage (%) | Fraction of required artifacts present and valid across runs. | conformance.json; build_p0_conformance_summary. |
| PONR coverage ratio | For lab_profile_v0: ratio of PONR tasks with at least one task_end in trace. | Tier 3; lab profile. |
| E3 variance (95% CI width) | Tighter CI = more precise estimate; report CI width for p95_latency_ms. | e3_summary / p0_e3_variance. |
| E4 conformance rate per adapter | Conformance rate (passed/total) per controller in multi-adapter run. | p0_e4_summary.json; run_p0_e4_multi_adapter, export_p0_table3. |
| Redaction completeness | E2: all payloads redacted; evidence_bundle_redacted has redaction_manifest. | e2_redaction_demo output. |

### P1 — Coordination Contracts

| Metric | Description | Source / script |
|--------|-------------|-----------------|
| Corpus detection rate (%) | Fraction of corpus sequences with detection_ok true (exact per-event verdict match; target 100%). | eval.json; export_contracts_corpus_table. |
| Overhead p99 (us) | Event-level 99th percentile time per write; latency_percentiles_us.p99 and p99_ci95 (bootstrap). | eval.json latency_percentiles_us. |
| Throughput (events/sec) | With --scale-test: events_per_sec; with --scale-sweep: sweep_results per size. Report mean and stdev over runs. | scale_test.json; scale_sweep.json. |
| Baseline margin | Violations denied with validator vs timestamp-only (count difference). Ablation by failure class in ablation_by_class. | eval.json (violations_denied_with_validator, baseline_timestamp_only_denials, ablation_by_class). |
| Resource and cost | wall_clock_sec, events_per_sec_overall, cost_proxy (events_per_dollar when LABTRUST_COST_PER_HOUR set). | eval.json resource_and_cost. |
| Transport parity | Same canonical sequence, event-log vs LADS-shaped; parity_ok when verdict vectors match. | transport_parity.json (contracts_transport_parity.py). |

### P2 — REP-CPS

| Metric | Description | Source / script |
|--------|-------------|-----------------|
| Bias reduction (%) | (bias_naive - bias_robust) / bias_naive when bias_naive > 0; robust aggregation reduces observed compromise-induced bias. | summary.json aggregation_under_compromise. |
| Max influence per compromised (optional) | aggregation_variants[].max_influence_per_compromised_agent for trimmed_mean. | summary.json. |
| Safety gate integration | Boolean: protocol output does not actuate without policy check; safety_gate_campaign (pass/deny counts), denial_trace_recorded. | summary.json safety_gate_denial. |
| Adapter parity, robust_beats_naive | success_criteria_met; trigger not met in evaluated scenario (paper is profile-and-harness contribution). | summary.json. |
| Profile ablation | profile_ablation[]: no auth, no freshness, no rate limit, no robust agg, full profile; bias and failure per variant (Table 6). | summary.json profile_ablation; generated_tables.md Table 6. |
| Latency/cost | wall_sec per policy, aggregation_compute_ms, policy_overhead_vs_centralized (Table 5). Figure 2: plot_rep_cps_latency.py. | summary.json latency_cost. |
| Resilience envelope | safe_operating_region_n_compromised_max, failure_boundary_n_compromised (Table 7). | summary.json resilience_envelope. |

### P3 — Replay

| Metric | Description | Source / script |
|--------|-------------|-----------------|
| Corpus outcome accuracy | Fraction of corpus rows (pass + traps) matching expected outcome; `divergence_localization_accuracy_pct` in excellence_metrics. | summary.json; per_trace; corpus_outcome_wilson_ci95. |
| Divergence localization (seq traps) | Fraction of seq-expected traps where divergence_at_seq matches; divergence_localization_wilson_ci95. | summary.json; corpus_expected pairs. |
| Overhead p99 (ms) | Empirical p99 over N replays (linear percentile); not a normal approximation. | overhead_stats; overhead_p99_empirical in excellence_metrics. |
| Baseline margin | full_vs_apply_only (paired bootstrap CI) in baseline_overhead. | replay_eval summary.json. |
| Multi-seed variability | multi_seed_overhead.across_seeds_stdev_of_means_ms. | replay_eval summary.json. |
| L1 stub pass | l1_stub_ok true when twin config valid. | summary.json. |
| L1 twin pass | l1_twin_ok when --l1-twin. | summary.json (with --l1-twin). |
| Witness slices present | Top-level witness_slices length > 0 when divergence detected. | summary.json. |

### P4 — CPS-MAESTRO

| Metric | Description | Source / script |
|--------|-------------|-----------------|
| Anti-gaming margin | Legitimate strategy tasks_completed vs always_deny/always_wait (score gap). | antigaming_results.json scoring_proof. |
| Fault coverage | Number of distinct fault settings exercised (e.g. no_drop, drop_005, delay_01, etc.). | multi_sweep.json. |
| Scenario diversity | Number of scenario_ids in sweep (e.g. 2 = toy_lab_v0, lab_profile_v0). | multi_sweep run_manifest. |
| Variance reported | Every result row has stdev or CI; run_manifest has seeds. | multi_sweep.json; export_maestro_tables. |

### P5 — Scaling Laws

| Metric | Description | Source / script |
|--------|-------------|-----------------|
| Out-of-sample margin | Feature or regression MAE vs global mean baseline (absolute or %). | heldout_results.json overall_*_mae. |
| CI width (95%) | Upper − lower for baseline MAE; narrower = more precise. | heldout_results.json *_ci95_*. |
| Beat baseline (binary) | success_criteria_met.beat_per_scenario_baseline, beat_baseline_out_of_sample. | heldout_results.json. |
| Scenario coverage | Number of held-out scenarios (e.g. 5). | held_out_results length. |

### P6 — LLM Planning

| Metric | Description | Source / script |
|--------|-------------|-----------------|
| Red-team pass rate (%) | Fraction of red-team cases with pass true (target 100% for expected_block alignment). | red_team_results.json. |
| Real-LLM pass rate (%) | When --real-llm-runs N: overall pass_rate_pct and 95% Wilson CI (pass_rate_ci95_lower/upper). | red_team_results.json real_llm. |
| Denial latency p95 (ms) | Adapter run: task_latency_ms_p95 or wall_sec; tail latency for firewall. | adapter_latency.json. |
| Confusable deputy pass | success_criteria_met.confusable_deputy_all_pass. | confusable_deputy_results.json. |
| Baseline 3-way | Gated vs weak vs ungated denial counts and tasks_completed_mean. | baseline_comparison.json. |
| E2E denial trace | One run where unsafe proposal blocked and system still completes; documented. | e2e_denial_trace.json. |

### P7 — Standards Mapping

| Metric | Description | Source / script |
|--------|-------------|-----------------|
| Mapping completeness (%) | All hazards have control_ids; all controls have evidence_artifact_types. | check_assurance_mapping; results.json mapping_ok. |
| PONR coverage ratio | review output: ponr_coverage.ratio or equivalent (target 1.0 for lab profile). | results.json; review_assurance_run. |
| Review pass (binary) | review exit_ok; evidence_bundle_ok, trace_ok. | results.json reviews. |
| No certification claim | Documented in draft; no compliance/certification language. | Limitations / Non-goals. |

### P8 — Meta-Coordination

| Metric | Description | Source / script |
|--------|-------------|-----------------|
| Collapse (non-inferior vs strict) | Non-inferior: `meta_non_worse_collapse` (meta_collapses <= fixed). Strict: `meta_strictly_reduces_collapse` (meta_collapses < fixed). | comparison.json. |
| Paired binary collapse | McNemar exact two-sided on discordant pairs; Wilson CIs on marginal rates. | comparison.json `collapse_paired_analysis`. |
| No safety regression | success_criteria_met.no_safety_regression (meta >= 90% of fixed or similar). | comparison.json. |
| Switch audit trail | regime_switch_count_total present; every switch justifiable from trace. | comparison.json; trace regime_switch events. |
| Trigger met | no_safety_regression and meta_non_worse_collapse; stress policy in manifest when non-vacuous. | comparison.json. |
| Stress calibration | Pre-specified rule for drop_prob when `--non-vacuous`. | comparison.json `run_manifest.stress_selection_policy`. |

## Implementation notes

- **Optional fields:** Excellence metrics are added to existing summary JSONs under the key `excellence_metrics`. Eval scripts (replay_link_e3, contracts_eval, rep_cps_eval, replay_eval, maestro_fault_sweep, maestro_antigaming_eval, scaling_heldout_eval, llm_redteam_eval, run_assurance_eval, meta_eval) populate this block when run. Do not break existing consumers.
- **Export summary:** Run `python scripts/export_excellence_summary.py` to print a one-line excellence summary per paper from `datasets/runs/`. Use `--json` for machine-readable output.
- **Draft:** In the draft, report 1–3 of these per paper in a "Results summary" or "Metrics" subsection so reviewers see the bar.
- **CI:** Optionally add a non-blocking "excellence" job that asserts on a subset of these (e.g. repro time < 25 min, pass rate 100% for red-team).

## References

- [STATE_OF_THE_ART_CRITERIA.md](STATE_OF_THE_ART_CRITERIA.md) — minimum bar (Phase 3, draft conversion).
- [REPORTING_STANDARD.md](REPORTING_STANDARD.md) — seeds, statistics, run manifest.
- [VISUALS_PER_PAPER.md](VISUALS_PER_PAPER.md) — tables and figures per paper.
- [PRE_SUBMISSION_CHECKLIST.md](PRE_SUBMISSION_CHECKLIST.md) — final pass before submit.
