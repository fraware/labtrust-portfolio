# Generated tables for P2 (P2_REP-CPS)

**How to read:** Table 1 compares adapter policies (REP-CPS, Centralized, Naive-in-loop, Unsecured) on tasks_completed and aggregate_load; Table 2 reports aggregation under compromise (bias_robust, bias_naive); Table 3 summarizes baselines by auth and aggregation. Source: `datasets/runs/rep_cps_eval/summary.json`. Run manifest (seeds, scenario_ids, delay_fault_prob_sweep, script) in that file. Publishable default: 20 seeds.

## From rep_cps_eval.py and summary.json

**Table 1 — Adapter comparison (source: summary.json).** REP-CPS vs Centralized vs naive-in-loop vs unsecured; 20 seeds (publishable default), scenario lab_profile_v0.

| Policy | tasks_completed_mean | tasks_stdev | aggregate_load (in-loop) |
|--------|----------------------|-------------|---------------------------|
| REP-CPS (trimmed, auth) | 4.9 | 0.32 | 0.32 |
| Naive-in-loop (mean, auth) | 4.9 | 0.32 | 0.32 |
| Unsecured (mean, no auth, compromised) | 4.9 | 0.32 | 5.16 |
| Centralized | 4.9 | 0.32 | — |

**Table 2 — Aggregation under compromise (offline; source: summary.json aggregation_under_compromise).** Robust aggregation reduces observed compromise-induced bias relative to naive averaging in the evaluated scenarios (bias_robust vs bias_naive).

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
| Unsecured | no (all agents) | mean | same as naive (3.87) |

**Table 4 — Convergence under multi-step aggregation (when aggregation_steps > 1).** Source: summary.json after `rep_cps_eval.py --aggregation-steps 5`. Export: `python scripts/export_rep_cps_convergence_table.py`.

| Metric | Value |
|--------|-------|
| aggregation_steps | 5 |
| convergence_achieved_rate | from summary.json |
| steps_to_convergence_mean | from summary.json |
| steps_to_convergence_stdev | from summary.json |

**Table 5 — Profile ablation (source: summary.json profile_ablation).** Each row disables one profile component; bias and aggregate are vs honest-only. Failures reappear when a component is missing (e.g. no auth or no robust aggregation yields high bias). No safety gate row: N/A in current eval (gate bypass not simulated).

| Variant | Description | Bias | Aggregate | Failure |
|---------|-------------|------|-----------+---------|
| no_auth | All agents accepted, trimmed_mean | from summary | from summary | from summary |
| no_freshness | No freshness window, trimmed_mean | from summary | from summary | from summary |
| no_rate_limit | No rate limit, auth, trimmed_mean | from summary | from summary | from summary |
| no_robust_aggregation | Mean, all agents | from summary | from summary | from summary |
| no_safety_gate | N/A in current eval | — | — | — |
| full_profile | Auth, trimmed_mean, rate_limit, freshness | from summary | from summary | from summary |

Regenerate: `python scripts/rep_cps_eval.py --scenarios lab_profile_v0` (writes summary.json). For convergence table: `python scripts/rep_cps_eval.py --aggregation-steps 5` then `python scripts/export_rep_cps_convergence_table.py`. See DRAFT.md repro block and RESULTS_PER_PAPER.md.
