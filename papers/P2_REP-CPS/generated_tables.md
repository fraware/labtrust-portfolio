# Generated tables for P2 (P2_REP-CPS)

**How to read:** Table 1 compares adapter policies; Table 2 aggregation under compromise; Table 3 baselines; Table 4 convergence (optional); Table 5 latency/cost; Table 6 profile ablation; Table 7 resilience envelope; scheduling-dependent eval and threat-evidence blocks (when present) summarize `rep_cps_scheduling_v0` and micro-harness rows from summary.json. Source: `datasets/runs/rep_cps_eval/summary.json`. Run manifest (seeds, scenario_ids, delay_fault_prob_sweep, script) in that file. Publishable default: 20 seeds; scenarios include `rep_cps_scheduling_v0`.

## From rep_cps_eval.py and summary.json

**Table 1 — Adapter comparison (source: summary.json).** REP-CPS vs Centralized vs naive-in-loop vs unsecured; 20 seeds (publishable default), scenarios toy_lab_v0, lab_profile_v0, rep_cps_scheduling_v0.

| Policy | tasks_completed_mean | tasks_stdev | aggregate_load (in-loop) |
|--------|----------------------|-------------|---------------------------|
| REP-CPS (trimmed, auth) | 4.24 | 0.55 | 1.4 |
| Naive-in-loop (mean, auth) | 2.93 | 2.13 | 1.4 |
| Unsecured (mean, no auth, compromised) | 2.93 | 2.13 | 5.48 |
| Centralized | 4.24 | 0.55 | — |


**Table 2 — Aggregation under compromise (offline; source: summary.json aggregation_under_compromise).** Robust aggregation reduces observed compromise-induced bias relative to naive averaging.

| Metric | Value |
|--------|--------|
| honest_only_aggregate | 0.32 |
| with_compromise_robust_aggregate | 3.56 (trimmed mean) |
| with_compromise_naive_aggregate | 4.19 (plain mean) |
| unsecured_aggregate | same as naive (all updates) |
| bias_robust | 3.24 |
| bias_naive | 3.87 |


**Table 3 — Baselines.**

| Policy | Auth | Aggregation | Aggregate bias (under compromise) |
|--------|------|-------------|------------------------------------|
| REP-CPS (robust) | yes | trimmed_mean | bias_robust (3.24) |
| Naive-in-loop | yes | mean | bias_naive (3.87) |
| Unsecured | no (all agents) | mean | same as naive |


**Table 4 — Convergence under multi-step aggregation (when aggregation_steps > 1).** Source: summary.json after `rep_cps_eval.py --aggregation-steps 5`. Export: `python scripts/export_rep_cps_convergence_table.py`.

| Metric | Value |
|--------|-------|
| aggregation_steps | 1 (default); use --aggregation-steps 5 for convergence table |
| convergence_achieved_rate | from summary.json |
| steps_to_convergence_mean | from summary.json |
| steps_to_convergence_stdev | from summary.json |


**Table 5 — Latency and cost (source: summary.json latency_cost).** Wall time per run (sec) and aggregation compute time (ms); overhead vs centralized baseline.

| Policy / metric | Mean (s) | p95 (s) | Overhead vs centralized (ms) |
|------------------|----------|---------|-------------------------------|
| REP-CPS | 0.1173 | 0.1882 | -0.08 |
| Naive-in-loop | 0.1178 | 0.1959 | 0.41 |
| Unsecured | 0.1201 | 0.1995 | 2.7 |
| Centralized | 0.1174 | 0.1769 | 0 |

| Aggregation compute | Mean (ms) | p95 (ms) | p99 (ms) |
|----------------------|-----------|----------|----------|
| aggregate() (trimmed_mean) | 0.0016 | 0.0018 | 0.0116 |


**Table 6 — Profile ablation (source: summary.json profile_ablation).** Each row disables one profile component; bias and aggregate vs honest-only.

| Variant | Description | Bias | Aggregate | Failure |
|---------|-------------|------|-----------|---------|
| no_auth | All agents accepted (no auth filter), trimmed | 3.2367 | 3.5567 | yes |
| no_freshness | No freshness window (stale compromised accept | 3.2367 | 3.5567 | yes |
| no_rate_limit | No rate limit (burst from one agent), auth, t | 7.2675 | 7.5875 | yes |
| no_robust_aggregation | Mean (no robust agg), all agents | 3.874 | 4.194 | yes |
| no_safety_gate | Safety gate bypass (N/A in current eval) | — | — | — |
| full_profile | Auth, trimmed_mean, rate_limit, freshness | 0.0 | 0.32 | no |


**Scheduling-dependent scenario (source: summary.json scheduling_dependent_eval).** Task-level outcome when the safety gate blocks scheduling under duplicate-sender spoof stress (`rep_cps_scheduling_v0`).

| Metric | Value |
|--------|-------|
| scenario_id | rep_cps_scheduling_v0 |
| rep_cps_tasks_mean | 3.91 |
| naive_in_loop_tasks_mean | 0.0 |
| centralized_tasks_mean | 3.91 |
| rep_beats_naive_tasks | True |


**Threat evidence — freshness and replay burst (summary.json freshness_replay_evidence).** Micro-harness for max_age_sec and rate_limit (not a live replay engine).

| Check | Value |
|-------|-------|
| stale_value_dropped_by_max_age | True |
| mean_with_freshness_window | 0.3 |
| rate_limit_reduces_replay_influence | True |


**Threat evidence — sybil vs spoofing (summary.json sybil_vs_spoofing_evidence).** Sybil: many distinct fake agent ids; spoofing: duplicate sender id with poison value.

| Metric | Value |
|--------|-------|
| sybil_robust_beats_naive | True |
| spoof_robust_beats_naive | True |
| spoof_naive_aggregate_exceeds_gate_2 | True |


**Threat evidence — messaging simulation (summary.json messaging_sim).** Ordered delivery simulation: duplicate and reorder handling (synthetic message ordering only; not a deployed bus or ROS/OPC UA path).

| Metric | Value |
|--------|-------|
| duplicate_delivery_mean | 0.3167 |
| duplicate_delivery_trimmed_mean | 0.3 |
| reordered_same_multiset_mean | 0.3167 |


**Threat evidence — dynamic aggregation series (summary.json dynamic_aggregation_series).** Multi-tick synthetic series: growing sybil count per tick (offline).

| Metric | Value |
|--------|-------|
| honest_only_trimmed_baseline | 0.32 |
| max_trim_bias_drift_across_ticks | 2.57 |
| trim_bias_drift_area | 7.725 |
| trim_bias_persistence_ticks_gt_1 | 3.0 |
| temporal_series_kind | offline_synthetic_harness |


| Tick | n_compromised | trimmed_mean | naive_mean | bias_trim_vs_honest_only |
|------|---------------|--------------|------------|--------------------------|
| 0 | 0 | 0.32 | 0.3233 | 0.0 |
| 1 | 1 | 0.335 | 2.2425 | 0.015 |
| 2 | 2 | 2.89 | 3.394 | 2.57 |
| 3 | 2 | 2.89 | 3.394 | 2.57 |
| 4 | 2 | 2.89 | 3.394 | 2.57 |


**Per-scenario summary (source: summary.json per_scenario).** Aggregated metrics per scenario across all delay/drop combinations.

| Scenario | REP-CPS mean | REP stdev | Naive mean | Naive stdev | Unsecured mean | Centralized mean |
|----------|-------------|-----------|------------|-------------|----------------|------------------|
| toy_lab_v0 | 3.91 | 0.28 | 3.91 | 0.28 | 3.91 | 3.91 |
| lab_profile_v0 | 4.89 | 0.32 | 4.89 | 0.32 | 4.89 | 4.89 |
| rep_cps_scheduling_v0 | 3.91 | 0.28 | 0.0 | 0.0 | 0.0 | 3.91 |


**Offline aggregation comparators (source: summary.json aggregation_variants).** Same honest+compromised multiset as Table 2; robust operators vs plain mean.

| method | bias vs honest trimmed | beats_naive_mean |
|--------|-------------------------|------------------|
| trimmed_mean | 3.2367 | True |
| median | 0.03 | True |
| clipping | 3.874 | False |
| median_of_means | 0.03 | True |


**Offline comparator baselines (source: summary.json offline_comparator_baselines).** Includes honest-range clamp heuristic (oracle bounds strawman).

| Metric | Value |
|--------|-------|
| bias_naive_mean | 3.874 |
| honest_range_clamped_bias_vs_honest_trimmed | 0.014 |
| honest_range_clamped_beats_naive_mean | True |
| robust_statistical_comparators | trimmed_mean, median, clipping, median_of_means |
| practical_heuristic_comparators | honest_range_clamped_mean |
| selection_rationale | Comparators chosen to distinguish robust statistics from lightweight operational heuristics used in constrained CPS settings. |


**Comparison statistics (source: summary.json excellence_metrics).** Paired comparison metrics for REP-CPS vs Centralized (non-scheduling scenarios only).

| Metric | Value |
|--------|-------|
| difference_mean (REP-CPS - Centralized) | 0.0 |
| difference_ci95_lower | 0.0 |
| difference_ci95_upper | 0.0 |
| difference_ci_width | 0.0 |
| paired_t_p_value | 1.0 |
| power_post_hoc | 0.0 |
| alpha | 0.05 |


**Safety-gate campaign (source: summary.json safety_gate_denial).** Pass/deny counts from adapter runs; denial when aggregate exceeds threshold.

| Metric | Value |
|--------|-------|
| denial_trace_recorded | True |
| pass_count_rep_cps | 240 |
| deny_count_rep_cps | 0 |
| deny_count_unsecured | 240 |
| total_runs | 240 |


**Table 7 — Resilience envelope (source: summary.json resilience_envelope).** Safe operating region and failure boundary from compromise/magnitude/trim sweeps.

| Metric | Value |
|--------|-------|
| bias_threshold | 1.0 |
| safe_operating_region_n_compromised_max | 1 |
| failure_boundary_n_compromised | 3 |
| magnitude_sweep robust beats naive | True |
| trim_sweep robust beats naive | True |


Regenerate: `python scripts/rep_cps_eval.py` (default scenarios: toy_lab_v0, lab_profile_v0, rep_cps_scheduling_v0). Tables: `python scripts/export_rep_cps_tables.py`. Latency/cost: summary.json latency_cost; Table 5. Resilience: resilience_envelope, magnitude_sweep, trim_fraction_sweep. Threat micro-evidence: freshness_replay_evidence, sybil_vs_spoofing_evidence, messaging_sim, dynamic_aggregation_series. Convergence: `python scripts/rep_cps_eval.py --aggregation-steps 5` then `python scripts/export_rep_cps_convergence_table.py`. See DRAFT.md repro block and RESULTS_PER_PAPER.md.
