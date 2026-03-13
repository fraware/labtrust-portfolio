# REP-CPS: A Real-Time, Authenticated Sensitivity-Sharing Profile

**Draft (v0.1). Paper ID: P2_REP-CPS. Conditional paper; trigger and scope: docs/CONDITIONAL_TRIGGERS.md (P2).**

**Reproducibility.** From repo root, with `PYTHONPATH=impl/src` and `LABTRUST_KERNEL_DIR=kernel`. See [REPORTING_STANDARD.md](../docs/REPORTING_STANDARD.md) and [RESULTS_PER_PAPER.md](../docs/RESULTS_PER_PAPER.md) for run_manifest and excellence_metrics.

**Minimal run (under 20 min):** `python scripts/rep_cps_eval.py --scenarios lab_profile_v0 --seeds 1,2,3` then `python scripts/export_p2_rep_profile_diagram.py` then `python scripts/plot_rep_cps_summary.py`.

**Publishable run:** Default 20 seeds; use `--scenarios lab_profile_v0` (optionally `--delay-sweep 0,0.05,0.1,0.2`). Run_manifest in `datasets/runs/rep_cps_eval/summary.json`. Conditional trigger: see Limitations and docs/CONDITIONAL_TRIGGERS.md (P2).

- **Figure 0:** `python scripts/export_p2_rep_profile_diagram.py` (output `docs/figures/p2_rep_profile_diagram.mmd`). Render Mermaid to PNG for camera-ready.
- **Table 1, Table 2, Table 3:** `python scripts/rep_cps_eval.py --scenarios lab_profile_v0` (writes summary.json with run_manifest); tables from summary. Single source: [generated_tables.md](generated_tables.md).
- **Figure 1:** `python scripts/plot_rep_cps_summary.py --summary datasets/runs/rep_cps_eval/summary.json` (output `docs/figures/p2_rep_cps_tasks.png`).
- **Trigger:** Summary reports `success_criteria_met.trigger_met`; see section 6.

## 1. Motivation

Sensitivity-sharing (REP-like) protocols are attractive for decentralized CPS coordination but break under naive deployment: unbounded influence, replay, Byzantine agents. This paper defines a CPS profile (typed variables, rate limits, provenance, robust aggregation) integrated with MADS safety gates.

## 2. Profile spec

Message schemas, windowing, rate limits, provenance: see `kernel/rep_cps/PROFILE_SPEC.v0.1.md`.

**Figure 0 — REP-CPS profile architecture.** Agents feed updates into robust aggregation; output passes through a MADS-compatible safety gate before actuation. Regenerate with `python scripts/export_p2_rep_profile_diagram.py` (output `docs/figures/p2_rep_profile_diagram.mmd`). Schema: `kernel/rep_cps/REP_CPS_PROFILE.v0.1.schema.json`; example: `kernel/rep_cps/example_profile.v0.1.json`. Variables are typed; updates carry value, ts, agent_id; windowing (max_age_sec) and rate limits (max_updates_per_sec) cap influence.

## 3. Threat model

Byzantine agents (arbitrary values); sybils (fake identities); spoofing (impersonation); replay (old messages). Mitigations: authenticated channels, rate limits per identity, timestamps/nonces, robust aggregation (trimmed mean, median) to bound influence of up to f faulty agents.

## 4. Robust aggregation and safety gate

Reference aggregator: `impl/src/labtrust_portfolio/rep_cps.py` (`aggregate()`, `auth_hook()`). Attack harness: `compromised_updates()` generates Byzantine-style updates for testing. Safety gate: protocol state does not actuate directly; MADS tier (e.g. Tier 2) required before actuation; profile property `safety_gate.gate_before_actuation`. Rate limiting and provenance (auth_hook, windowing) are exercised in eval (aggregate with rate_limit and max_age_sec; summary key `rate_limit_windowing.rate_limit_windowing_exercised`) and in tests (`tests/test_rep_cps_p2.py`); the adapter uses auth_hook to filter updates.

## 5. MAESTRO adapter and evaluation

**Headline:** Robust aggregation (trimmed mean + auth) bounds influence under compromise: bias_robust < bias_naive in both offline and in-loop evaluation; trigger_met when REP-CPS improves robustness without throughput regression (summary.json).

REPCPSAdapter (`adapters/rep_cps_adapter.py`) runs scenario via thin-slice, injects REP-CPS protocol step (aggregation result in trace metadata), produces TRACE + MAESTRO_REPORT. Adapter accepts `aggregation_method` (trimmed_mean or mean) and `use_compromised` (honest+compromised updates); `allowed_agents` controls auth. Current adapter performs **one-shot aggregation** per run; convergence time and stability-over-time are not defined in this version (summary field `aggregation_steps`: 1). Evaluation: bottleneck scenario(s), delay sweep, robustness under compromise; baselines: centralized, naive-in-loop (aggregation_method=mean), unsecured (use_compromised=True, naive mean). Run `scripts/rep_cps_eval.py` (default 20 seeds); output: `datasets/runs/rep_cps_eval/summary.json`. **Real launches:** CI may use fewer seeds (e.g. 10) for speed; publishable default is 20. Integration tests in `.github/workflows/ci.yml`; integration tests in `tests/test_rep_cps_p2.py` run the eval script and real adapter runs, asserting summary structure and invariants (bias_robust < bias_naive, rate_limit exercised, adapter parity).

**Table 1 — Adapter comparison (source: summary.json).** REP-CPS vs Centralized vs naive-in-loop vs unsecured; 20 seeds (publishable default), scenario lab_profile_v0. Run manifest (seeds, scenario_ids, delay_fault_prob_sweep, script) in `datasets/runs/rep_cps_eval/summary.json`.

| Policy | tasks_completed_mean | tasks_stdev | aggregate_load (in-loop) |
|--------|----------------------|-------------|---------------------------|
| REP-CPS (trimmed, auth) | 4.9 | 0.32 | 0.32 |
| Naive-in-loop (mean, auth) | 4.9 | 0.32 | 0.32 |
| Unsecured (mean, no auth, compromised) | 4.9 | 0.32 | 5.16 |
| Centralized | 4.9 | 0.32 | — |

**Table 2 — Aggregation under compromise (offline; source: summary.json aggregation_under_compromise).** Headline metric: **max effect per compromised agent** (influence bound) in `aggregation_variants[].max_influence_per_compromised_agent`; robust aggregation bounds influence under Byzantine inputs.

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

Naive-in-loop baseline: adapter run with `aggregation_method=mean`; same scenario/seeds. Unsecured: `use_compromised=True`, `allowed_agents=None`, naive mean. Aggregation comparison is available both offline (aggregation_under_compromise) and in-loop (adapter comparison). Live sensitivity-sharing loop is future work.

**Convergence under compromise.** When `--aggregation-steps` > 1 (e.g. 5 or 10), the adapter runs multi-step aggregation until the aggregate value is stable within epsilon. Summary reports: `convergence_achieved` (whether the first run converged), `convergence_achieved_rate` (fraction of seeds that converged), `convergence_steps_to_convergence_mean` and `convergence_steps_to_convergence_stdev` (steps until |agg - prev| < epsilon). Table 4 (see generated_tables.md) and `scripts/export_rep_cps_convergence_table.py` produce the convergence table from summary.json. This moves the story from "we aggregate once" to "we show the protocol stabilizes under attack."

**Results summary (excellence metrics).** From summary.json: **influence bound** (max effect per compromised agent in aggregation_variants); **bias reduction** (bias_robust < bias_naive; when bias_naive > 0, (bias_naive - bias_robust)/bias_naive); **safety gate** (protocol output does not actuate without policy check); **trigger_met** (success_criteria_met.trigger_met: adapter_parity and robust_beats_naive without throughput regression). See [STANDARDS_OF_EXCELLENCE.md](../docs/STANDARDS_OF_EXCELLENCE.md) (P2).

**Figure 1 — tasks_completed by policy.** Mean tasks_completed (and stdev) by policy (REP-CPS, Centralized, Naive-in-loop, Unsecured) from summary.json (20 seeds (publishable default), lab_profile_v0). Regenerate with `python scripts/plot_rep_cps_summary.py --summary datasets/runs/rep_cps_eval/summary.json` (output `docs/figures/p2_rep_cps_tasks.png`). Run manifest in same summary.json.

## 6. Methodology and reproducibility

**Methodology:** Hypothesis—profile (typed variables, rate limits, robust aggregation) makes sensitivity-sharing deployable and bounds influence under compromise. Metrics: aggregation output under compromised_updates (trimmed mean vs naive mean); safety_gate_ok in trace; tasks_completed mean and stdev (20 seeds for publishable). Kill criteria (AUTHORING_PACKET): cannot define measurable influence bounds (K1); protocol does not outperform baselines in bottleneck scenario (K2); unnecessary in architecture (K3). Baselines: centralized, naive-in-loop, unsecured. Portfolio criteria: `docs/STATE_OF_THE_ART_CRITERIA.md`.

**Reproducibility:** Run `python scripts/rep_cps_eval.py` (PYTHONPATH=impl/src, LABTRUST_KERNEL_DIR=kernel); default 20 seeds (use --seeds 1,2,...,10 for quick local runs). For non-toy scenario: `--scenarios lab_profile_v0` (and optionally `--delay-sweep 0,0.05,0.1,0.2`). REPCPSAdapter: `run(scenario_id, out_dir, seed, aggregation_method="trimmed_mean"|"mean", use_compromised=False|True)`. Trace metadata: rep_cps_aggregate_load, rep_cps_safety_gate_ok. Attack harness: `compromised_updates()` in rep_cps.py. Profile example: `kernel/rep_cps/example_profile.v0.1.json`.

**Trigger proof (conditional paper).** Summary reports `success_criteria_met.trigger_met`: true when REP-CPS improves robustness (adapter_parity and robust_beats_naive) without throughput regression on the evaluated scenario(s). To demonstrate on a non-toy scenario, run with `--scenarios lab_profile_v0`. If trigger_met is false, this paper is "conditional / optional" until evidence on a non-toy scenario is provided; see `docs/CONDITIONAL_TRIGGERS.md`.

## 7. Limitations

Scope and conditional triggers: [EXPERIMENTS_AND_LIMITATIONS.md](../docs/EXPERIMENTS_AND_LIMITATIONS.md). Per-paper:

- **Conditional paper:** If success_criteria_met.trigger_met is false (e.g. eval only on toy_lab_v0), this paper is "conditional / optional" until evidence on a non-toy scenario (e.g. lab_profile_v0) is provided; see docs/CONDITIONAL_TRIGGERS.md.
- **Multi-step aggregation (optional):** With `--aggregation-steps 5` (or 10), the adapter runs multiple aggregation steps and reports steps_to_convergence and convergence_achieved_rate; see "Convergence under compromise" and Table 4 in generated_tables.md. Default remains one step for speed.
- **Synthetic updates:** Adapter uses fixed synthetic updates (two agents, 0.3 and 0.35) or eval-defined honest/compromised sets; no real sensors or live sensitivity-sharing loop.
- **No real deployment:** Evaluation is trace-driven and thin-slice; no real distributed agents, no real network, no real REP protocol deployment.
- **Aggregation comparison:** Robust vs naive under compromise is run offline (honest+compromised in eval script) and in-loop via adapter variants (naive, unsecured); not integrated into a live sensitivity-sharing loop with real messaging.

**Threats to validity.** *Internal:* One-shot aggregation per run; no multi-step convergence or stability-over-time. *External:* Evaluation on lab_profile_v0 (and optionally toy_lab_v0); real deployment and live sensitivity-sharing not tested. *Construct:* aggregate_load and bias_robust/bias_naive are proxies for influence; no formal Byzantine bound (e.g. f-resilience) proved.

**Comparison to prior REP/Byzantine work.** We position the profile relative to known Byzantine-resistant aggregation: same threat model (Byzantine agents, arbitrary values), same or derived metrics (influence bound, bias under compromise). summary.json `aggregation_variants` reports bias and max_influence_per_compromised_agent for trimmed_mean, median, clipping, median_of_means on the same honest+compromised inputs. Conceptual comparison:

| Scheme | Threat model | Metric (our eval) | Notes |
|--------|--------------|-------------------|-------|
| REP-CPS (trimmed mean) | Byzantine agents, sybils | bias_robust, max_influence_per_compromised | Trim fraction 0.25; auth + rate limits. |
| Median-only | Same | aggregation_variants[method=median] | Classical f-resilient; we include in variants. |
| Mean (naive) | Same | bias_naive | No resilience; baseline. |

Literature: trimmed mean and median are standard in Byzantine fault tolerance (e.g. distributed sensing, multi-agent consensus). Our profile adds CPS-specifics: typed variables, rate limits, provenance (auth_hook), and integration with MADS safety gates; we do not claim a new aggregation algorithm but a deployable profile with bounded influence under the same threat model.

---

**Claims and backing.**

| Claim | Evidence |
|-------|----------|
| C1 (Deployable) | PROFILE_SPEC, example_profile, aggregate(), auth_hook(). |
| C2 (Bounded influence) | Table 2, compromised_updates harness; bias_robust < bias_naive. |
| C3 (Safety gate) | Trace metadata safety_gate_ok, MADS tier. |
| C4 (Testable) | Table 1, REPCPSAdapter, rep_cps_eval.py, summary.json. |
