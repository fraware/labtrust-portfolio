# REP-CPS: A Safety-Gated Profile for Authenticated Sensitivity Sharing in Cyber-Physical Coordination

**Draft (v0.1). Paper ID: P2_REP-CPS. Conditional paper; trigger and scope: docs/CONDITIONAL_TRIGGERS.md (P2).**

**Abstract.** Decentralized sensitivity sharing is attractive in cyber-physical systems because it can expose local congestion, uncertainty, or risk information that centralized controllers may not observe in time. However, naive deployment is unsafe: unauthenticated updates, stale messages, bursty senders, or compromised agents can distort downstream decisions. We introduce REP-CPS, a cyber-physical deployment profile for sensitivity sharing. REP-CPS specifies typed variables, freshness windows, rate limits, provenance and authentication hooks, and a permitted family of robust aggregation operators. A key design principle is that protocol state is informational rather than actuating: any downstream use of aggregated sensitivity must pass an explicit safety gate. We provide a reference implementation, a compromised-agent attack harness, and a MAESTRO-compatible evaluation workflow. In the evaluated scenarios, robust aggregation reduces compromise-induced bias relative to naive averaging, while explicit gate mediation prevents direct actuation from protocol state. We do not claim a new Byzantine-robust aggregation algorithm or a full real-time distributed deployment; rather, we contribute a reproducible profile that makes sensitivity sharing more disciplined, testable, and CPS-compatible.

**Reproducibility.** From repo root, with `PYTHONPATH=impl/src` and `LABTRUST_KERNEL_DIR=kernel`. See [REPORTING_STANDARD.md](../docs/REPORTING_STANDARD.md) and [RESULTS_PER_PAPER.md](../docs/RESULTS_PER_PAPER.md) for run_manifest and excellence_metrics. Profile framing (typed variables, rate limits, provenance, safety-gate mediation) aligns with NIST CPS framework (timing, data, communications, access control together). OPC UA LADS is a credible substrate for lab-facing interoperability.

**Minimal run (under 20 min):** `python scripts/rep_cps_eval.py --scenarios lab_profile_v0 --seeds 1,2,3` then `python scripts/export_p2_rep_profile_diagram.py` then `python scripts/plot_rep_cps_summary.py`.

**Publishable run:** Default 20 seeds; use `--scenarios lab_profile_v0` (optionally `--delay-sweep 0,0.05,0.1,0.2`). Run_manifest in `datasets/runs/rep_cps_eval/summary.json`. Conditional trigger: see Limitations and docs/CONDITIONAL_TRIGGERS.md (P2).

- **Figure 0:** `python scripts/export_p2_rep_profile_diagram.py` (output `docs/figures/p2_rep_profile_diagram.mmd`). Render Mermaid to PNG for camera-ready.
- **Table 1:** `python scripts/rep_cps_eval.py --scenarios lab_profile_v0` (writes `datasets/runs/rep_cps_eval/summary.json`); table from summary.json (see [generated_tables.md](generated_tables.md)).
- **Table 2:** Same run; Table 2 from summary.json aggregation_under_compromise (see [generated_tables.md](generated_tables.md)).
- **Table 3:** Same run; Table 3 from summary.json (see [generated_tables.md](generated_tables.md)).
- **Figure 1:** `python scripts/plot_rep_cps_summary.py --summary datasets/runs/rep_cps_eval/summary.json` (output `docs/figures/p2_rep_cps_tasks.png`).
- **Table 5 (latency/cost):** summary.json `latency_cost`; export via `python scripts/export_rep_cps_tables.py` (see [generated_tables.md](generated_tables.md)).
- **Figure 2:** `python scripts/plot_rep_cps_latency.py --summary datasets/runs/rep_cps_eval/summary.json` (output `docs/figures/p2_rep_cps_latency.png`).
- **Trigger:** See section 6 and Limitations. The evaluated scenario does not show material influence of sensitivity sharing on tasks_completed; paper is profile-and-harness contribution per CONDITIONAL_TRIGGERS.md (P2).

## 1. Motivation

Sensitivity-sharing (REP-like) protocols are attractive for decentralized CPS coordination but break under naive deployment: unbounded influence, replay, Byzantine agents. This paper defines a CPS profile (typed variables, rate limits, provenance, robust aggregation) integrated with MADS safety gates. The novelty of REP-CPS is not a new Byzantine-robust aggregation rule, but a CPS deployment profile that makes sensitivity sharing auditable, rate-bounded, authenticated, and explicitly non-actuating unless mediated by a safety gate.

## 2. Profile spec

Message schemas, windowing, rate limits, provenance: see `kernel/rep_cps/PROFILE_SPEC.v0.1.md`.

**Formal profile model.**

- **Update model.** An update is a tuple \(u = (x, v, a, t, n, \pi)\), where \(x\) is a typed sensitivity variable, \(v\) its value, \(a\) the claimed sender identity, \(t\) the timestamp, \(n\) a nonce or sequence token, and \(\pi\) the provenance/authentication material.
- **Acceptance.** An update is admissible only if it passes type validation, identity validation, freshness checks, and rate-limit checks under the declared profile.
- **Aggregation.** For each variable \(x\), the profile instantiates an aggregation operator \(A_x\) from a permitted family (e.g., mean, trimmed mean, median, clipped variants). The output of \(A_x\) is informational only.
- **Safety-gated influence.** Aggregated protocol state cannot directly actuate. Any downstream action that depends on protocol state must pass an explicit safety gate defined outside the profile.

**Figure 0 — REP-CPS profile architecture.** Agents feed updates into robust aggregation; output passes through a MADS-compatible safety gate before actuation. Regenerate with `python scripts/export_p2_rep_profile_diagram.py` (output `docs/figures/p2_rep_profile_diagram.mmd`). Schema: `kernel/rep_cps/REP_CPS_PROFILE.v0.1.schema.json`; example: `kernel/rep_cps/example_profile.v0.1.json`. Variables are typed; updates carry value, ts, agent_id; windowing (max_age_sec) and rate limits (max_updates_per_sec) cap influence.

## 3. Threat model

Byzantine agents (arbitrary values); sybils (fake identities); spoofing (impersonation); replay (old messages). Mitigations: authenticated channels, rate limits per identity, timestamps/nonces, robust aggregation (trimmed mean, median) to limit the influence of up to f faulty agents.

## 4. Robust aggregation and safety gate

Reference aggregator: `impl/src/labtrust_portfolio/rep_cps.py` (`aggregate()`, `auth_hook()`). Attack harness: `compromised_updates()` generates Byzantine-style updates for testing. Safety gate: protocol state does not actuate directly; MADS tier (e.g. Tier 2) required before actuation; profile property `safety_gate.gate_before_actuation`. Rate limiting and provenance (auth_hook, windowing) are exercised in eval (aggregate with rate_limit and max_age_sec; summary key `rate_limit_windowing.rate_limit_windowing_exercised`) and in tests (`tests/test_rep_cps_p2.py`); the adapter uses auth_hook to filter updates.

## 5. MAESTRO adapter and evaluation

**Headline:** In the evaluated attack harness, robust aggregation (trimmed mean + auth) reduces compromise-induced bias relative to naive averaging (bias_robust < bias_naive) in offline and in-loop evaluation. Adapter parity: REP-CPS vs Centralized tasks_completed equal (no throughput regression). The contribution is the profile and its evaluation harness; in the evaluated scenario, sensitivity sharing does not materially change tasks_completed (see Limitations).

**Key results.** (1) Adapter parity: REP-CPS vs Centralized tasks_completed equal (no throughput regression); success_criteria_met.adapter_parity true. (2) Aggregation under compromise: robust aggregation reduces observed bias (bias_robust < bias_naive); excellence_metrics.bias_reduction_pct when bias_naive > 0. (3) success_criteria_met.trigger_met when robust_beats_naive and adapter_parity; use run with --scenarios toy_lab_v0,lab_profile_v0 and 20 seeds. (4) Safety gate: protocol output does not actuate without policy check. (5) Excellence metrics (n>=2 seeds): difference_mean, difference_ci95, paired_t_p_value, power_post_hoc in summary.json. *Numbers from summary.json. Regenerate with `python scripts/rep_cps_eval.py`. See [RUN_RESULTS_SUMMARY.md](../../datasets/runs/RUN_RESULTS_SUMMARY.md).*

REPCPSAdapter (`adapters/rep_cps_adapter.py`) runs scenario via thin-slice, injects REP-CPS protocol step (aggregation result in trace metadata), produces TRACE + MAESTRO_REPORT. Adapter accepts `aggregation_method` (trimmed_mean or mean) and `use_compromised` (honest+compromised updates); `allowed_agents` controls auth. Current adapter performs **one-shot aggregation** per run; convergence time and stability-over-time are not defined in this version (summary field `aggregation_steps`: 1). Evaluation: bottleneck scenario(s), delay sweep, robustness under compromise; baselines: centralized, naive-in-loop (aggregation_method=mean), unsecured (use_compromised=True, naive mean). Run `python scripts/rep_cps_eval.py` (default 20 seeds); output: `datasets/runs/rep_cps_eval/summary.json`. **Real launches:** CI may use fewer seeds (e.g. 10) for speed; publishable default is 20. Integration tests in `.github/workflows/ci.yml`; integration tests in `tests/test_rep_cps_p2.py` run the eval script and real adapter runs, asserting summary structure and invariants (bias_robust < bias_naive, rate_limit exercised, adapter parity).

**Table 1 — Adapter comparison (source: summary.json).** REP-CPS vs Centralized vs naive-in-loop vs unsecured; 20 seeds (publishable default), scenarios toy_lab_v0, lab_profile_v0. Tasks_completed_mean is identical across policies (adapter parity; no throughput regression). Aggregate_load reflects protocol output: only unsecured shows high load under compromise; REP-CPS and naive-in-loop show lower load. In this scenario, sensitivity sharing does not materially change tasks_completed; the table demonstrates parity and that aggregate_load distinguishes secured from unsecured. Regenerate with `python scripts/export_rep_cps_tables.py`. Run_manifest in `datasets/runs/rep_cps_eval/summary.json`.

| Policy | tasks_completed_mean | tasks_stdev | aggregate_load (in-loop) |
|--------|----------------------|-------------|---------------------------|
| REP-CPS (trimmed, auth) | 4.4 | 0.57 | 0.32 |
| Naive-in-loop (mean, auth) | 4.4 | 0.57 | 0.32 |
| Unsecured (mean, no auth, compromised) | 4.4 | 0.57 | 5.16 |
| Centralized | 4.4 | 0.57 | — |

**Table 2 — Aggregation under compromise (offline; source: summary.json aggregation_under_compromise).** Robust aggregation reduces observed compromise-induced bias relative to naive averaging in the evaluated scenarios (bias_robust 3.24 vs bias_naive 3.87). Run_manifest in summary.json.

| Metric | Value |
|--------|--------|
| honest_only_aggregate | 0.32 |
| with_compromise_robust_aggregate | 3.56 (trimmed mean) |
| with_compromise_naive_aggregate | 4.19 (plain mean) |
| unsecured_aggregate | same as naive (all updates) |
| bias_robust | 3.24 |
| bias_naive | 3.87 |

**Table 3 — Baselines.** Policy comparison (auth, aggregation method, aggregate bias under compromise). Run_manifest in summary.json.

| Policy | Auth | Aggregation | Aggregate bias (under compromise) |
|--------|------|-------------|------------------------------------|
| REP-CPS (robust) | yes | trimmed_mean | bias_robust (3.24) |
| Naive-in-loop | yes | mean | bias_naive (3.87) |
| Unsecured | no (all agents) | mean | same as naive (3.87) |

Naive-in-loop baseline: adapter run with `aggregation_method=mean`; same scenario/seeds. Unsecured: `use_compromised=True`, `allowed_agents=None`, naive mean. Aggregation comparison is available both offline (aggregation_under_compromise) and in-loop (adapter comparison). **Profile ablation:** summary.json `profile_ablation` reports bias and failure for variants (no auth, no freshness, no rate limit, no robust aggregation, full profile); see generated_tables.md Table 6. **Robustness sweeps:** summary.json includes `sybil_sweep` (compromised count 0..8), `magnitude_sweep` (adversarial extreme values 2, 5, 10, 20, 50), and `trim_fraction_sweep` (0.1–0.4). **Resilience envelope:** `resilience_envelope` reports safe operating region (max n_compromised with bias below threshold where robust beats naive), failure boundary (n_compromised where robust no longer beats naive), and that conclusions are explicitly bounded by the tested envelope; see generated_tables.md Table 7. Live sensitivity-sharing loop is future work.

**Safety-gate campaign.** Adapter runs with unsecured (compromised) updates produce aggregate load above the safety threshold; the gate sets `rep_cps_safety_gate_ok` to false and denial is recorded in the trace. summary.json `safety_gate_denial` includes `denial_trace_recorded` and `safety_gate_campaign` (pass/deny counts). See generated_tables.md.

**Multi-step aggregation (optional).** When `--aggregation-steps` > 1 (e.g. 5 or 10), the adapter runs multi-step aggregation until the aggregate value is stable within epsilon. Summary reports convergence_achieved, convergence_achieved_rate, steps_to_convergence. Table 4 (see generated_tables.md) and `scripts/export_rep_cps_convergence_table.py` produce the convergence table. Default evaluation uses one-shot aggregation; we do not claim stability or convergence in the main results.

**Results summary (excellence metrics).** From summary.json: **bias reduction** (bias_robust < bias_naive; when bias_naive > 0, (bias_naive - bias_robust)/bias_naive); **safety gate** (protocol output does not actuate without policy check); **adapter_parity** and **robust_beats_naive** (success_criteria_met). See [STANDARDS_OF_EXCELLENCE.md](../docs/STANDARDS_OF_EXCELLENCE.md) (P2).

**Latency and cost.** summary.json `latency_cost` records per-run wall time (mean, p95) per policy and aggregation compute time (mean, p95, p99 in ms). Policy overhead vs centralized baseline is reported in ms. Table 5 in generated_tables.md; Figure 2: `python scripts/plot_rep_cps_latency.py` (output `docs/figures/p2_rep_cps_latency.png`). Deployability claims are tied to measured overhead (typically on the order of a few ms vs centralized).

**Figure 1 — tasks_completed by policy.** Mean tasks_completed (count) and stdev by policy (REP-CPS, Centralized, Naive-in-loop, Unsecured) from summary.json; 20 seeds (publishable default), scenarios toy_lab_v0, lab_profile_v0. Regenerate with `python scripts/plot_rep_cps_summary.py --summary datasets/runs/rep_cps_eval/summary.json` (output `docs/figures/p2_rep_cps_tasks.png`). Run_manifest in summary.json.

## 6. Methodology and reproducibility

**Methodology:** Hypothesis—profile (typed variables, rate limits, robust aggregation) makes sensitivity-sharing deployable within the evaluated profile assumptions and reduces observed bias under compromise. Metrics: aggregation output under compromised_updates (trimmed mean vs naive mean); safety_gate_ok in trace; tasks_completed mean and stdev (20 seeds for publishable). Kill criteria (AUTHORING_PACKET): cannot define measurable robustness acceptance tests (K1); protocol does not outperform baselines in the scenario where it should help (K2); unnecessary in architecture (K3). Baselines: centralized, naive-in-loop, unsecured. Portfolio criteria: `docs/STATE_OF_THE_ART_CRITERIA.md`.

**Reproducibility:** Run `python scripts/rep_cps_eval.py` (PYTHONPATH=impl/src, LABTRUST_KERNEL_DIR=kernel); default 20 seeds (use --seeds 1,2,...,10 for quick local runs). For non-toy scenario: `--scenarios lab_profile_v0` (and optionally `--delay-sweep 0,0.05,0.1,0.2`). REPCPSAdapter: `run(scenario_id, out_dir, seed, aggregation_method="trimmed_mean"|"mean", use_compromised=False|True)`. Trace metadata: rep_cps_aggregate_load, rep_cps_safety_gate_ok. Attack harness: `compromised_updates()` in rep_cps.py. Profile example: `kernel/rep_cps/example_profile.v0.1.json`. **Statistical sensitivity:** summary.json excellence_metrics include difference_mean, difference_ci95, paired_t_p_value, power_post_hoc; publishable run uses 20 seeds. Run `python scripts/sensitivity_seed_sweep.py --eval rep_cps --ns 20,30` to verify CI/effect-size stability across N; no key claim relies on low-power comparisons (adapter parity is zero difference).

**Trigger proof (conditional paper).** The paper's trigger condition (sensitivity sharing materially influences scheduling or actuation) is not yet met in the evaluated scenario: tasks_completed is identical across policies. The contribution is the profile (typed, authenticated, rate-limited, safety-gated) and its MAESTRO-compatible evaluation harness. success_criteria_met.trigger_met (adapter_parity and robust_beats_naive) is reported for the run; see `docs/CONDITIONAL_TRIGGERS.md` (P2) for conditional/optional framing until a scenario where sensitivity sharing materially affects outcomes is added.

**Submission note (P2 trigger).** Use a run with --scenarios toy_lab_v0,lab_profile_v0 and 20 seeds (e.g. run_paper_experiments.py --paper P2) so summary.json has excellence_metrics (bias_reduction_pct, adapter_parity) populated. State in the draft that the paper is a profile-and-harness contribution; operational benefit in the evaluated scenario is not claimed. See [CONDITIONAL_TRIGGERS.md](../docs/CONDITIONAL_TRIGGERS.md) (P2).

## 7. Limitations

Scope and conditional triggers: [EXPERIMENTS_AND_LIMITATIONS.md](../docs/EXPERIMENTS_AND_LIMITATIONS.md). Per-paper:

- **Trigger not met in evaluated scenario:** In the evaluated scenario, sensitivity sharing did not materially change tasks_completed; Table 1 shows identical tasks_completed_mean across REP-CPS, naive-in-loop, unsecured, and centralized. The contribution is the profile (typed, authenticated, rate-limited, safety-gated) and its evaluation harness, not demonstrated operational benefit in this scenario. The paper is conditional/optional until a scenario where sensitivity sharing materially influences scheduling or actuation is evaluated. See [CONDITIONAL_TRIGGERS.md](../docs/CONDITIONAL_TRIGGERS.md) (P2) and [STANDARDS_OF_EXCELLENCE.md](../docs/STANDARDS_OF_EXCELLENCE.md).
- **Scenario where sensitivity would matter (future work):** A scenario that would meet the trigger would be one in which task admission, resource allocation, or actuation decisions depend on the aggregated sensitivity (e.g. a threshold on aggregate load or congestion). In such a setting, naive or unsecured sharing could lead to worse tasks_completed or safety-gate denials under compromise, while robust sharing would preserve performance. The current evaluation does not include such a sensitivity-dependent scenario; adding one (e.g. a scenario variant where scheduling uses the protocol output) would allow the trigger to be re-evaluated.
- **Multi-step aggregation (optional):** With `--aggregation-steps 5` (or 10), the adapter runs multiple aggregation steps and reports steps_to_convergence and convergence_achieved_rate; see "Multi-step aggregation (optional)" and Table 4 in generated_tables.md. Default remains one step; we do not claim stability or convergence in the main evaluation.
- **Synthetic updates:** Adapter uses fixed synthetic updates (two agents, 0.3 and 0.35) or eval-defined honest/compromised sets; no real sensors or live sensitivity-sharing loop.
- **No real deployment:** Evaluation is trace-driven and thin-slice; no real distributed agents, no real network, no real REP protocol deployment. The profile is timing-aware and rate-limited but not demonstrated under live or bounded-latency distributed deployment.
- **Aggregation comparison:** Robust vs naive under compromise is run offline (honest+compromised in eval script) and in-loop via adapter variants (naive, unsecured); not integrated into a live sensitivity-sharing loop with real messaging.

**Threats to validity.** *Internal:* One-shot aggregation per run in main eval; no multi-step convergence or stability-over-time. *External:* Evaluation on lab_profile_v0 (and optionally toy_lab_v0); real deployment and live sensitivity-sharing not tested. *Construct:* aggregate_load and bias_robust/bias_naive are proxies for reduced observed bias; no formal Byzantine bound (e.g. f-resilience) proved.

**Comparison to prior REP/Byzantine work.** We position the profile relative to known Byzantine-resistant aggregation: same threat model (Byzantine agents, arbitrary values), same or derived metrics (bias under compromise). summary.json `aggregation_variants` reports bias and max_influence_per_compromised_agent for trimmed_mean, median, clipping, median_of_means on the same honest+compromised inputs. Conceptual comparison:

| Scheme | Threat model | Metric (our eval) | Notes |
|--------|--------------|-------------------|-------|
| REP-CPS (trimmed mean) | Byzantine agents, sybils | bias_robust, max_influence_per_compromised | Trim fraction 0.25; auth + rate limits. |
| Median-only | Same | aggregation_variants[method=median] | Classical f-resilient; we include in variants. |
| Mean (naive) | Same | bias_naive | No resilience; baseline. |

Literature: trimmed mean and median are standard in Byzantine fault tolerance (e.g. distributed sensing, multi-agent consensus). Our profile adds CPS-specifics: typed variables, rate limits, provenance (auth_hook), and integration with MADS safety gates; we do not claim a new aggregation algorithm but a deployable profile (within the evaluated profile assumptions) that reduces observed bias under compromise in the evaluated scenarios.

---

**Claims and backing.**

| Claim | Evidence |
|-------|----------|
| C1 (Profile deployable) | PROFILE_SPEC, example_profile, typed schema, auth/rate/freshness; aggregate(), auth_hook(). |
| C2 (Reduced bias under compromise) | Table 2, Table 3, compromised_updates harness; bias_robust < bias_naive in evaluated scenarios. |
| C3 (Safety gate) | Trace metadata safety_gate_ok, MADS tier; protocol state does not directly actuate. |
| C4 (Testable) | Table 1, REPCPSAdapter, rep_cps_eval.py, summary.json, MAESTRO fault injection. |
