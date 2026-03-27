# P2 REP-CPS — Reviewer rebuttal matrix

| Reviewer question | Evidence | Explicit non-claim |
|-------------------|----------|-------------------|
| Why is this a paper now? | Named assurance profile + MAESTRO harness + summary.json contracts; **rep_cps_scheduling_v0** shows task-level gate effect (`scheduling_dependent_eval`). | Not a production protocol standard; not field-trial results on hardware. |
| What is the real novelty? | **Composition + semantics**: typed variables, admissibility surface, informational-only state, gate-mediated effect, reproducible eval (DRAFT §1, §2). | Not a new trimmed-mean theorem. |
| Why identical tasks on some runs? | **Two eval modes** (DRAFT §5.1): toy/lab scenarios do not wire aggregate to scheduler; parity is **scoped** (`adapter_parity_scope` in summary.json). | Global Table 1 mean blends scenarios; read with `scheduling_dependent_eval`. |
| Why care if tasks match on toy/lab? | Offline bias + ablation + latency + gate campaign still bound profile discipline; scheduling scenario shows **when** task counts move. | Does not prove benefit on every deployment. |
| Is robust bias reduction compelling alone? | Report with **resilience envelope**, **Table 6**, **sybil_vs_spoofing_evidence**; frame as directional + bounded. | Not worst-case Byzantine proof. |
| Is this only a hand-crafted harness? | Aligns with MAESTRO thin-slice + trace schema; threat rows map to metrics (DRAFT §3 table). | Not external validity for all CPS. |
| Sybil vs spoofing? | **sybil_sweep** / many `compromised_*` ids vs **spoof** duplicate sender (`sensitivity_spoof_duplicate_sender_update`). | No PKI / Sybil enrollment. |
| Replay / freshness? | **freshness_replay_evidence**, `max_age_sec` / `rate_limit` in `aggregate()`. | Not full P3 replay corpus integration. |
| Live messaging? | **messaging_sim** (reorder/duplicate into aggregate) and **dynamic_aggregation_series** (multi-tick synthetic series); see threat-evidence blocks in generated_tables.md. | Not ROS/OPC UA deployment. |
| Per-scenario breakdown? | **per_scenario** summary in summary.json and generated_tables.md separates metrics by scenario_id; scheduling-dependent eval isolates `rep_cps_scheduling_v0` outcomes. | Global means still blend for overall comparison. |
| Statistical comparison rigor? | **excellence_metrics** includes difference_mean, difference_ci95, paired_t_p_value, power_post_hoc; see comparison statistics block in generated_tables.md. | Bootstrap CIs and paired tests on non-scheduling subset only. |
| Is the safety gate just a fixed threshold anecdote? | `gate_threshold_sweep_results` reports denial-rate and tasks outcomes vs `safety_gate_max_load` on `rep_cps_scheduling_v0`, making gate sensitivity explicit. | Threshold policy remains scenario-specific, not universally tuned. |
| How can reviewers audit claim-to-number traceability quickly? | Use the manuscript repro route: `rep_cps_eval.py` -> `summary.json` + `safety_gate_denial.json` -> `export_rep_cps_tables.py` -> figure scripts -> claim mapping in `claims.yaml` and DRAFT claim table. | Not a third-party certified artifact badge package yet. |
| Is this deployable guidance or only benchmark evidence? | DRAFT adds a deployment-readiness checklist (identity assumptions, freshness/rate policy, gate calibration, traceability, negative-case testing) and a repeated-denial playbook. | Not an operational runbook for a specific production plant. |
| What controls are non-negotiable vs context-dependent? | Non-negotiable: admissibility (identity/freshness/rate), explicit gate mediation, and traceability; context-dependent: threshold tuning and comparator choice under mission constraints. | Does not claim one universal threshold or one universal comparator across CPS domains. |

See also [REVIEWER_ATTACK_SURFACE_LEDGER.md](REVIEWER_ATTACK_SURFACE_LEDGER.md).
