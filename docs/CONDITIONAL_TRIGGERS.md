# Conditional triggers

Papers P2, P5, P6, and P8 are **conditional**: proceed only when their trigger criteria are met. This document records the trigger condition, “proceed when” criterion, and dependency order.

## P2 REP-CPS

- **Trigger:** Sensitivity sharing materially influences scheduling or actuation decisions in the target architecture (lab/warehouse/traffic), and therefore becomes safety/security relevant.
- **Trigger proof required:** REP-CPS improves robustness under compromise/delay **without throughput regression** on at least one **non-toy** lab scenario. Evidence in release: scenario id, centralized vs REP-CPS metrics, statement that trigger is met or not (if not, paper is "conditional / optional" only). Full eval suite: Tables 1–7 (generated_tables.md via export_rep_cps_tables.py), Figures 1–2 (plot_rep_cps_summary.py, plot_rep_cps_latency.py); latency/cost (Table 5), profile ablation (Table 6), resilience envelope (Table 7), safety-gate campaign.
- **Current status (updated):** On **toy_lab_v0** and **lab_profile_v0**, scheduling does not read REP-CPS aggregate, so **tasks_completed** stays aligned across policies (scoped adapter parity). On **rep_cps_scheduling_v0**, **gated aggregate load** can **withhold scheduling** (zero `task_end` events when the gate denies); under duplicate-sender spoof stress, **naive in-loop mean** typically fails the gate while **trimmed REP-CPS** stays below threshold—see `summary.json` `scheduling_dependent_eval`. This is **harness-level** task influence, not a claim about all lab/warehouse/traffic deployments. The paper remains a **profile-and-harness** contribution for general CPS architecture; full operational trigger across real schedulers is still future work. See `papers/P2_REP-CPS/REVIEWER_ATTACK_SURFACE_LEDGER.md`.
- **Proceed when:** You can show that REP-like protocols are in scope for the lab (or other) profile and that naive forms break under CPS constraints; or submit as profile paper with honest scope (profile + harness, reduced observed bias under compromise).
- **Dependency order:** After Contracts (P1) typed state and Replay/MAESTRO harnesses exist; REP-CPS is a profile inside the MADS envelope.

## P5 Scaling laws

- **Trigger:** MAESTRO provides **multi-scenario** datasets sufficient for out-of-sample validation. Otherwise the paper reads as overclaim.
- **Trigger proof required (admissible, no leakage):** `heldout_results.json` must report `success_criteria_met.trigger_met` from **admissible** baselines only: `beat_global_mean_out_of_sample`, `beat_feature_baseline_out_of_sample`, and `beat_regime_baseline_out_of_sample` (train-only regime means). Oracle baselines (`oracle_baselines.per_scenario_mean_including_test_mae`, etc.) are for analysis only and **must not** drive the go/no-go trigger. If `trigger_met` is false, treat as negative / exploratory and say so in the draft.
- **Proceed when:** Runs span multiple scenario families, coordination regimes, agent counts, and fault mixtures, with frozen artifacts under `datasets/runs/scaling_eval/`, `scaling_eval_family/`, `scaling_eval_regime/`, `scaling_eval_agent_count/`, `scaling_eval_fault/`, `sensitivity_sweep/scaling_sensitivity.json`, and `scaling_recommend/recommendation_eval.json` produced by the paper runner.
- **Dependency order:** After P4 (MAESTRO) has multi-scenario coverage; consumes MAESTRO datasets and Replay traces.

## P6 LLM Planning

- **Trigger:** An LLM is in the control plane (planning/toolcalling), OR a typed-plan + validator firewall is needed as a general containment pattern.
- **Trigger proof required:** Firewall reduces unsafe attempts without collapsing task completion on at least one scenario family. Deliverable: evidence (unsafe blocked in released suites: red_team 15/15, confusable deputy 6/6, jailbreak-style 4/4); real-LLM Table 1b (publishable default 10 runs/case, full-suite mode, pass_rate with Wilson CI); adapter latency and 3-way baseline (tool-level, args_unsafe, optional benign); tasks_completed non-zero; document in release and P6.
- **Proceed when:** You are building or evaluating an LLM-in-the-loop control plane and need containment and measurable robustness (not “elimination” of prompt injection).
- **Dependency order:** LLM planning is a module inside the MADS envelope; evaluated on MAESTRO scenarios.

## P8 Meta-coordination

- **Trigger:** Multiple coordination regimes are actually deployed (e.g. centralized, market, swarm, fallback), and mode-thrashing or collapse occurs under compound faults.
- **Trigger proof required:** Meta is **non-inferior to the fixed regime on paired collapse counts** (meta_collapses <= fixed_collapses; field `meta_non_worse_collapse` / legacy `meta_reduces_collapse`) and **does not safety-regress** (`no_safety_regression` true). Publishable pipeline records **pre-specified** stress calibration when using `--non-vacuous` (`run_manifest.stress_selection_policy`). **Strict** count reduction (`meta_strictly_reduces_collapse`) and McNemar / Wilson fields in `collapse_paired_analysis` are reported separately; ties are not “wins.” Deliverable: comparison.json states `trigger_met` and interpretation fields; optional second scenario path `meta_eval/scenario_regime_stress_v1/` for external validity; if not met, paper remains conditional.
- **Proceed when:** You have at least two regimes and fault mixtures that cause regime stress; meta-controller can be compared to best fixed regime with explicit non-inferior vs strict semantics.
- **Dependency order:** After MAESTRO and Replay; safety constraints (PONRs from MADS) must remain invariant across regimes.

## Reference

See **PORTFOLIO_BOARD.md** section “Trigger criteria for conditional modules” for the canonical one-line triggers.
