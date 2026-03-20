# Generated tables for P2 (P2_REP-CPS)

**How to read:** Table 1 compares adapter policies; Table 2 aggregation under compromise; Table 3 baselines; Table 4 convergence (optional); Table 5 latency/cost; Table 6 profile ablation; Table 7 resilience envelope. Source: `datasets/runs/rep_cps_eval/summary.json`. Run manifest (seeds, scenario_ids, delay_fault_prob_sweep, script) in that file. Publishable default: 20 seeds.

## From rep_cps_eval.py and summary.json

**Table 1 — Adapter comparison (source: summary.json).** REP-CPS vs Centralized vs naive-in-loop vs unsecured; 20 seeds (publishable default), scenarios toy_lab_v0, lab_profile_v0.

| Policy | tasks_completed_mean | tasks_stdev | aggregate_load (in-loop) |
|--------|----------------------|-------------|---------------------------|
| REP-CPS (trimmed, auth) | 4.4 | 0.57 | 0.32 |
| Naive-in-loop (mean, auth) | 4.4 | 0.57 | 0.32 |
| Unsecured (mean, no auth, compromised) | 4.4 | 0.57 | 5.16 |
| Centralized | 4.4 | 0.57 | — |


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
| REP-CPS | 0.1336 | 0.2214 | 2.62 |
| Naive-in-loop | 0.1289 | 0.1836 | -2.12 |
| Unsecured | 0.1312 | 0.1969 | 0.14 |
| Centralized | 0.131 | 0.1996 | 0 |

| Aggregation compute | Mean (ms) | p95 (ms) | p99 (ms) |
|----------------------|-----------+----------|----------|
| aggregate() (trimmed_mean) | 0.0027 | 0.0034 | 0.0127 |


**Table 6 — Profile ablation (source: summary.json profile_ablation).** Each row disables one profile component; bias and aggregate vs honest-only.

| Variant | Description | Bias | Aggregate | Failure |
|---------|-------------|------|-----------+---------|
| no_auth | All agents accepted (no auth filter), trimmed | 3.2367 | 3.5567 | yes |
| no_freshness | No freshness window (stale compromised accept | 3.2367 | 3.5567 | yes |
| no_rate_limit | No rate limit (burst from one agent), auth, t | 7.2675 | 7.5875 | yes |
| no_robust_aggregation | Mean (no robust agg), all agents | 3.874 | 4.194 | yes |
| no_safety_gate | Safety gate bypass (N/A in current eval) | — | — | — |
| full_profile | Auth, trimmed_mean, rate_limit, freshness | 0.0 | 0.32 | no |


**Safety-gate campaign (source: summary.json safety_gate_denial).** Pass/deny counts from adapter runs; denial when aggregate exceeds threshold.

| Metric | Value |
|--------|-------|
| denial_trace_recorded | True |
| pass_count_rep_cps | 160 |
| deny_count_rep_cps | 0 |
| deny_count_unsecured | 160 |
| total_runs | 160 |


**Table 7 — Resilience envelope (source: summary.json resilience_envelope).** Safe operating region and failure boundary from compromise/magnitude/trim sweeps.

| Metric | Value |
|--------|-------|
| bias_threshold | 1.0 |
| safe_operating_region_n_compromised_max | 1 |
| failure_boundary_n_compromised | 3 |
| magnitude_sweep robust beats naive | True |
| trim_sweep robust beats naive | True |


Regenerate: `python scripts/rep_cps_eval.py --scenarios lab_profile_v0` (writes summary.json). Tables: `python scripts/export_rep_cps_tables.py`. Latency/cost: in summary.json latency_cost; Table 5. Resilience: summary.json resilience_envelope, magnitude_sweep, trim_fraction_sweep. For convergence: `python scripts/rep_cps_eval.py --aggregation-steps 5` then `python scripts/export_rep_cps_convergence_table.py`. See DRAFT.md repro block and RESULTS_PER_PAPER.md.
