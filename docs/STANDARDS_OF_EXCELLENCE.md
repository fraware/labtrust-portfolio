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
| **Claim confidence** | Per claim: "high" (direct measure + 10 seeds + script), "medium" (fewer seeds or proxy), "low" (qualitative). | claims.yaml optional `evidence.confidence` or DRAFT backing sentence. |

## Per-paper excellence metrics

Add these to the relevant eval summary JSON and, where useful, to the draft. Scripts can populate `success_criteria_met` or a dedicated `excellence_metrics` block.

### P0 — MADS-CPS

| Metric | Description | Source / script |
|--------|-------------|-----------------|
| Conformance coverage (%) | Fraction of required artifacts present and valid across runs. | conformance.json; build_p0_conformance_summary. |
| PONR coverage ratio | For lab_profile_v0: ratio of PONR tasks with at least one task_end in trace. | review_assurance_run; Tier 3. |
| E3 variance (95% CI width) | Tighter CI = more precise estimate; report CI width for p95_latency_ms. | e3_summary / p0_e3_variance. |
| Redaction completeness | E2: all payloads redacted; evidence_bundle_redacted has redaction_manifest. | e2_redaction_demo output. |

### P1 — Coordination Contracts

| Metric | Description | Source / script |
|--------|-------------|-----------------|
| Corpus detection rate (%) | Fraction of corpus sequences with detection_ok true (target 100%). | eval.json; export_contracts_corpus_table. |
| Overhead p99 (us) | 99th percentile time per write (validator + state update). | eval.json per-sequence; report max or p99. |
| Throughput (events/sec) | With --scale-test: events_per_sec; report mean and stdev over runs. | scale_test.json. |
| Baseline margin | Violations denied with validator vs timestamp-only (count difference). | eval.json (violations_denied_with_validator, baseline_timestamp_only_denials). |

### P2 — REP-CPS

| Metric | Description | Source / script |
|--------|-------------|-----------------|
| Influence bound (max per compromised) | aggregation_variants[].max_influence_per_compromised_agent for trimmed_mean. | summary.json. |
| Bias reduction (%) | (bias_naive - bias_robust) / bias_naive when bias_naive > 0. | summary.json aggregation_under_compromise. |
| Safety gate integration | Boolean: protocol output does not actuate without policy check. | summary.json safety_gate_denial. |
| Trigger met | success_criteria_met.trigger_met; adapter_parity, robust_beats_naive. | summary.json. |

### P3 — Replay

| Metric | Description | Source / script |
|--------|-------------|-----------------|
| Divergence localization accuracy | Fraction of corpus traps where observed divergence_at_seq == expected. | summary.json; corpus_divergences_detected, per_trace. |
| Overhead p99 (ms) | p99 replay time over N replays (in addition to mean, stdev, p95). | overhead_stats or derived. |
| L1 stub pass | l1_stub_ok true when twin config valid. | summary.json. |
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
| Denial latency p95 (ms) | Adapter run: task_latency_ms_p95 or wall_sec; tail latency for firewall. | adapter_latency.json. |
| Confusable deputy pass | success_criteria_met.confusable_deputy_all_pass. | confusable_deputy_results.json. |
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
| Collapse reduction | meta_controller collapse_count vs fixed (or naive); or collapse rate difference. | comparison.json. |
| No safety regression | success_criteria_met.no_safety_regression (meta >= 90% of fixed or similar). | comparison.json. |
| Switch audit trail | regime_switch_count_total present; every switch justifiable from trace. | comparison.json; trace regime_switch events. |
| Trigger met | meta_reduces_collapse true; non-vacuous comparison. | comparison.json. |

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
