# REP-CPS: A Safety-Gated Profile for Authenticated Sensitivity Sharing in Cyber-Physical Coordination

**Draft (v0.2). Paper ID: P2_REP-CPS. Conditional scope: see docs/CONDITIONAL_TRIGGERS.md (P2) and [REVIEWER_ATTACK_SURFACE_LEDGER.md](REVIEWER_ATTACK_SURFACE_LEDGER.md).**

**Abstract.** Decentralized sensitivity sharing is attractive in cyber-physical systems because it can expose local congestion, uncertainty, or risk information that centralized controllers may not observe in time. However, naive deployment is unsafe: unauthenticated updates, stale messages, bursty senders, or compromised agents can distort downstream decisions. We introduce REP-CPS, a cyber-physical deployment profile for sensitivity sharing. REP-CPS specifies typed variables, freshness windows, rate limits, provenance and authentication hooks, and a permitted family of robust aggregation operators. A key design principle is that protocol state is informational rather than actuating: any downstream use of aggregated sensitivity must pass an explicit safety gate. We provide a reference implementation, a compromised-agent attack harness, and a MAESTRO-compatible evaluation workflow. In the evaluated scenarios, robust aggregation reduces compromise-induced bias relative to naive averaging in an offline aggregation harness, while explicit gate mediation prevents direct actuation from protocol state. **The present toy and lab scenarios validate profile discipline, bounded overhead, and parity with centralized throughput where scheduling does not depend on the gate; they do not by themselves establish task-level benefit everywhere.** On a dedicated scheduling-dependent scenario (`rep_cps_scheduling_v0`), duplicate-sender spoof stress causes naive in-loop averaging to exceed the gate threshold and withhold scheduling, while trimmed aggregation stays below threshold and preserves completions—demonstrating that gated informational state can materially affect task outcomes under the harness assumptions. We do not claim a new Byzantine-robust aggregation algorithm or a full distributed real-time deployment; we contribute a reproducible assurance profile and attack-evaluable harness for informational coordination in CPS.

**Reproducibility.** From repo root, with `PYTHONPATH=impl/src` and `LABTRUST_KERNEL_DIR=kernel`. See [REPORTING_STANDARD.md](../docs/REPORTING_STANDARD.md) and [RESULTS_PER_PAPER.md](../docs/RESULTS_PER_PAPER.md) for run_manifest and excellence_metrics. Profile framing (typed variables, rate limits, provenance, safety-gate mediation) aligns with NIST CPS framework (timing, data, communications, access control together). OPC UA LADS is a credible substrate for lab-facing interoperability.

**Minimal run (under 20 min):** `python scripts/rep_cps_eval.py --scenarios toy_lab_v0 --seeds 1,2,3` then `python scripts/export_p2_rep_profile_diagram.py` then `python scripts/plot_rep_cps_summary.py`.

**Publishable run:** `python scripts/rep_cps_eval.py --scenarios toy_lab_v0,lab_profile_v0,rep_cps_scheduling_v0 --delay-sweep 0,0.05,0.1,0.2 --drop-sweep 0.02 --gate-threshold-sweep 1.5,2.0,2.5` (default 20 seeds). Then `python scripts/export_rep_cps_tables.py`, `python scripts/export_p2_rep_profile_diagram.py`, `python scripts/plot_rep_cps_summary.py`, `python scripts/plot_rep_cps_gate_threshold.py`, `python scripts/plot_rep_cps_dynamics.py`, and `python scripts/plot_rep_cps_latency.py`. Run_manifest in `datasets/runs/rep_cps_eval/summary.json`. See Limitations for conditional trigger scope.

- **Figure 0:** `python scripts/export_p2_rep_profile_diagram.py` (output `docs/figures/p2_rep_profile_diagram.mmd`); optional camera-ready renders via `--render-png|--render-svg|--render-pdf`.
- **Tables 1–7 + threat blocks:** `python scripts/rep_cps_eval.py` (writes `datasets/runs/rep_cps_eval/summary.json`); `python scripts/export_rep_cps_tables.py` (see [generated_tables.md](generated_tables.md)).
- **Figure 1:** `python scripts/plot_rep_cps_summary.py --summary datasets/runs/rep_cps_eval/summary.json` (outputs `docs/figures/p2_rep_cps_tasks.png` and `docs/figures/p2_rep_cps_tasks_per_scenario.png`).
- **Figure 2:** `python scripts/plot_rep_cps_gate_threshold.py --summary datasets/runs/rep_cps_eval/summary.json` (output `docs/figures/p2_rep_cps_gate_threshold.png`).
- **Figure 3:** `python scripts/plot_rep_cps_dynamics.py --summary datasets/runs/rep_cps_eval/summary.json` (output `docs/figures/p2_rep_cps_dynamics.png`).
- **Figure 4:** `python scripts/plot_rep_cps_latency.py --summary datasets/runs/rep_cps_eval/summary.json` (output `docs/figures/p2_rep_cps_latency.png`).

## 1. Motivation

Sensitivity-sharing (REP-like) protocols are attractive for decentralized CPS coordination but break under naive deployment: unbounded influence, replay, Byzantine agents, and bursty or spoofed senders. **Concrete vignette:** if a scheduler treats aggregated “load” or congestion signals as a soft input to admission or pacing, a compromised or spoofed stream can push the aggregate high—tripping a safety gate or causing denial/overload behavior—even when end-to-end task counts look unchanged in scenarios where scheduling ignores that signal.

**Why this paper now (even before full operational triggers everywhere):** CPS programs need a **named assurance surface** for informational coordination: schema-defined variables, admissibility rules, bounded influence, non-direct actuation, and reproducible fault injection. REP-CPS is reusable infrastructure for evaluating those properties under MAESTRO; it is not only a one-off robust estimator benchmark.

**Novelty is the profile, not the estimator.** The contribution is not “trimmed mean exists,” but the **composition**: typed sensitivity variables; an explicit **admissibility surface** (auth allow-list stub, freshness window, rate limit); **informational-only** protocol semantics; **gate-mediated** downstream effect; and a **MAESTRO-compatible** harness (adapter + summary.json contracts + safety-gate campaign). Without that bundle, robust aggregation alone does not specify CPS-relevant deployment discipline.

### 1.1 Related work (positioning)

We fence three adjacent areas:

- **Byzantine-robust aggregation:** classical trimmed mean, median, and variants; we use standard operators and report bias under compromise; we do **not** claim new f-resilience proofs.
- **Runtime assurance / safe control envelopes:** MADS-style gates and tiers; REP-CPS fits as an **informational subsystem** whose outputs are consumed only through policy.
- **Industrial / CPS messaging profiles:** typed fields, timing, access control (e.g. OPC UA); REP-CPS is a **lab-facing, evaluation-oriented** profile aligned with those concerns but not a substitute for a full field bus stack.

### 1.2 Research questions (journal framing)

- **RQ1:** Can a profiled sensitivity-sharing path bound compromised influence without material throughput regression on non-scheduling scenarios?
- **RQ2:** Which controls contribute most under attack: authentication, freshness, rate limits, robust aggregation, or safety gating?
- **RQ3:** Under what architecture conditions does sensitivity sharing become task-relevant rather than only informational?
- **RQ4:** How should REP-like protocols be evaluated so negative and conditional outcomes remain scientifically useful and reproducible?

These RQs are answered by a three-layer evidence structure in this draft: **offline robustness** (aggregation distortion under compromise), **in-loop bounded behavior** (parity, gate discipline, overhead), and **scheduling-dependent operational effect** (`rep_cps_scheduling_v0`).

## 2. Profile spec

Message schemas, windowing, rate limits, provenance: see `kernel/rep_cps/PROFILE_SPEC.v0.1.md`.

**Deployable (operational definition in this paper).** We call the profile **deployable within the evaluated assumptions** when it is: (1) **schema-defined** (REP_CPS_PROFILE JSON + PROFILE_SPEC); (2) **admissibility-controlled** (type, identity stub, freshness, rate limits); (3) **auditable** (trace metadata, MAESTRO report); (4) **bounded in overhead** (Table 5 / `latency_cost`); (5) **non-directly-actuating** (gate before actuation); (6) **attack-testable** (compromised and spoof harnesses in `rep_cps_eval.py`). We do **not** claim deployability on live WAN, ROS/OPC UA, or attested identity—those are out of scope.

**Formal profile model.**

- **Update model.** An update is a tuple \(u = (x, v, a, t, n, \pi)\), where \(x\) is a typed sensitivity variable, \(v\) its value, \(a\) the claimed sender identity, \(t\) the timestamp, \(n\) a nonce or sequence token, and \(\pi\) the provenance/authentication material.
- **Acceptance.** An update is admissible only if it passes type validation, identity validation, freshness checks, and rate-limit checks under the declared profile.
- **Aggregation.** For each variable \(x\), the profile instantiates an aggregation operator \(A_x\) from a permitted family (e.g., mean, trimmed mean, median, clipped variants). The output of \(A_x\) is informational only.
- **Safety-gated influence.** Aggregated protocol state cannot directly actuate. Any downstream action that depends on protocol state must pass an explicit safety gate defined outside the profile.

**Worked example (harness semantics).** Honest updates `(agent_1, 0.3)` and `(agent_2, 0.35)` are joined by a **duplicate-sender spoof** `(agent_1, 10.0)` (same claimed id, poison value—accepted only by the stub allow-list, modeling mis-attribution risk). **Naive mean** over the three admitted scalars exceeds the gate threshold (2.0); **trimmed mean** discards extremes and stays below threshold. On `rep_cps_scheduling_v0`, when the gate denies, thin-slice emits `scheduling_denied_rep_cps_gate` and **no task_end** events; when the gate passes, the usual lab task sequence completes (subject to stochastic drop/delay faults).

**Figure 0 — REP-CPS profile architecture.** Agents feed updates into robust aggregation; output passes through a MADS-compatible safety gate before actuation. Regenerate with `python scripts/export_p2_rep_profile_diagram.py` (output `docs/figures/p2_rep_profile_diagram.mmd`). Schema: `kernel/rep_cps/REP_CPS_PROFILE.v0.1.schema.json`; example: `kernel/rep_cps/example_profile.v0.1.json`.

## 3. Threat model

**Stated threats (full list).** Byzantine agents (arbitrary values); sybils (many fake identities); spoofing (impersonation / duplicate sender id); replay (stale or repeated messages).

**Exercised directly in eval.**

| Threat | Mechanism in eval | Evidence (summary.json / tables) |
|--------|-------------------|----------------------------------|
| Byzantine value distortion | `compromised_updates`, offline aggregation | Table 2, `aggregation_under_compromise`, `sybil_sweep`, Table 7 |
| Sybil pressure (many fake ids) | Distinct `compromised_*` agents | `sybil_sweep`, `sybil_vs_spoofing_evidence` |
| Spoofing (duplicate honest id) | `sensitivity_spoof_duplicate_sender_update` | `sybil_vs_spoofing_evidence`, `rep_cps_scheduling_v0` adapter path |
| Stale / replay-style flooding | `max_age_sec`, `rate_limit` in `aggregate()` | `freshness_replay_evidence`, `rate_limit_windowing`, Table 6 `no_freshness` / `no_rate_limit` |

**Threat-control-evidence matrix (main-paper view).**

| Threat | Profile control | Evidence block | Residual limitation |
|--------|-----------------|----------------|---------------------|
| Byzantine value distortion | Robust aggregation family + gate mediation | Table 2, Table 7, `aggregation_variants`, `safety_gate_campaign` | No formal f-resilience theorem |
| Sybil multiplicity | Auth allow-list stub + robust aggregation + rate limits | `sybil_sweep`, `sybil_vs_spoofing_evidence`, Table 6 | No Sybil-resistant enrollment |
| Spoofing / duplicate sender | Auth hooks + robust estimator + gate | `sybil_vs_spoofing_evidence`, `scheduling_dependent_eval` | No cryptographic sender attestation |
| Replay / staleness | Freshness window (`max_age_sec`) | `freshness_replay_evidence`, Table 6 `no_freshness` | Not a full replay engine (see P3) |
| Bursty influence | Per-sender rate limiting | `rate_limit_windowing`, Table 6 `no_rate_limit` | No adaptive rate policy in this version |

**Partially represented.** Freshness/replay are exercised at the **aggregator** micro-harness, not with a full protocol replay engine (see P3 separately). Identity is an **allow-list stub**, not cryptography or Sybil-resistant enrollment.

**Out of scope (explicit non-claims).** Live distributed agents; real network timing pathologies; WAN security; formal f-resilience proofs; full sybil-resistant identity architecture.

## 4. Robust aggregation and safety gate

Reference aggregator: `impl/src/labtrust_portfolio/rep_cps.py` (`aggregate()`, `auth_hook()`, `sensitivity_spoof_duplicate_sender_update()`). Attack harness: `compromised_updates()`. Safety gate: aggregate load must be at or below `SAFETY_GATE_MAX_LOAD` (2.0 in the adapter) for `rep_cps_safety_gate_ok`; protocol state does not actuate directly; MADS tier (e.g. Tier 2) remains the broader envelope.

**Why robust aggregation alone is not the whole story.** Profile ablation (Table 6) shows that **removing rate limits or freshness** can dominate failure modes: robust trimming does not replace admission control. **Why message authentication alone is not enough:** even with an allow-list, **duplicate-sender** updates (spoof stress) can poison **mean** while **trimmed** estimators reduce impact in the evaluated multiset—motivating both robust aggregation and gate mediation.

## 5. MAESTRO adapter and evaluation

### 5.1 Two evaluation modes (reviewer-facing)

**Offline compromise evaluation** answers: *If compromised (and honest) updates are fed to the aggregator, how far does the aggregate deviate from the honest-only reference?* This is `aggregation_under_compromise` and related sweeps (Table 2, Table 7, `sybil_sweep`). It isolates **estimator behavior** under a fixed multiset.

**In-loop secured evaluation** answers: *When the adapter runs the profile (filtering, aggregation method, gate) against thin-slice scheduling, what are `tasks_completed`, `aggregate_load`, and gate outcomes?* This is Table 1, Figure 1, and the safety-gate campaign. **Important:** Table 1 **global means** blend scenarios. On `toy_lab_v0` and `lab_profile_v0`, scheduling does not consult REP-CPS aggregate, so **tasks_completed** stays aligned across policies (parity with centralized on those runs). On **`rep_cps_scheduling_v0`**, the gate outcome **does** affect whether tasks complete, so **naive-in-loop can diverge from REP-CPS** under spoof stress. **Do not compare “mean looks fine in Table 1” to “mean is bad in Table 2” without this distinction—they answer different questions.**

**Headline.** Offline: robust reduces observed bias vs naive under compromise. In-loop: parity on non-scheduling scenarios; on `rep_cps_scheduling_v0`, REP-CPS preserves scheduling under duplicate-sender spoof stress where naive mean trips the gate. Unsecured paths show high aggregate load and gate denial counts.

### 5.2 When sensitivity sharing changes outcomes

| Architecture condition | Scheduler consumes aggregate? | Expected task-level effect | What REP-CPS improves |
|------------------------|-------------------------------|----------------------------|-----------------------|
| Informational-only monitoring path | No | Throughput parity expected | Bounded informational distortion; auditable gate discipline |
| Gate-mediated path, but scheduler independent of aggregate | No (for completion logic) | Task parity, but gate traces still meaningful | Prevents direct actuation; preserves auditability under attack |
| Scheduling-dependent path (`rep_cps_scheduling_v0`) | Yes | Divergence possible under spoof/compromise stress | Preserves completions where naive in-loop mean exceeds gate threshold |

This table is why the paper is conditional but positive: the protocol is not claimed to improve every scenario, but it does change operational outcomes where informational state is wired into scheduling decisions.

**Key results.** (1) **Adapter parity (scoped):** REP-CPS vs Centralized **mean tasks_completed** match on **non-scheduling-dependent** scenarios; see `success_criteria_met.adapter_parity_scope` and per-scenario summary in generated_tables.md. (2) **Aggregation under compromise:** `bias_robust < bias_naive`. (3) **Scheduling scenario:** `scheduling_dependent_eval.rep_beats_naive_tasks` when publishable scenarios include `rep_cps_scheduling_v0`. (4) **Safety gate:** campaign pass/deny counts; denial traces under attack. (5) **Excellence metrics:** bias_reduction_pct, paired comparison statistics (difference_mean, difference_ci95, paired_t_p_value) on parity subset (non-scheduling rows); see comparison statistics block in generated_tables.md. (6) **Threat micro-evidence:** freshness/replay, sybil vs spoofing, messaging simulation, and dynamic aggregation series documented in generated_tables.md. *Regenerate with `python scripts/rep_cps_eval.py`; see [RUN_RESULTS_SUMMARY.md](../../datasets/runs/RUN_RESULTS_SUMMARY.md).*

REPCPSAdapter runs thin-slice (or aggregation-first for scheduling-dependent scenarios), writes trace metadata `rep_cps_aggregate_load`, `rep_cps_safety_gate_ok`. Baselines: centralized, naive-in-loop (`aggregation_method=mean`), unsecured (`use_compromised=True`, `allowed_agents=None`). **Dynamic / messaging slice (synthetic):** `dynamic_aggregation_series` (tick-wise offline series) and `messaging_sim` (duplicate delivery / reorder into `aggregate`) document bounded construct validity—they are **not** live buses.

**Table 1 — Adapter comparison.** Global means blend scenarios; interpret alongside `scheduling_dependent_eval` and per-scenario summary in generated_tables.md. Regenerate with `python scripts/export_rep_cps_tables.py`. See [generated_tables.md](generated_tables.md) for concrete values from the latest `summary.json`.

| Policy | tasks_completed_mean | tasks_stdev | aggregate_load (in-loop) |
|--------|----------------------|-------------|---------------------------|
| REP-CPS (trimmed, auth) | See generated_tables.md | See generated_tables.md | See generated_tables.md |
| Naive-in-loop (mean, auth) | See generated_tables.md | See generated_tables.md | See generated_tables.md |
| Unsecured (mean, no auth, compromised) | See generated_tables.md | See generated_tables.md | See generated_tables.md |
| Centralized | See generated_tables.md | See generated_tables.md | — |

**Table 2 — Aggregation under compromise (offline).** See `aggregation_under_compromise` in summary.json and [generated_tables.md](generated_tables.md) for values.

| Metric | Value |
|--------|--------|
| honest_only_aggregate | See generated_tables.md |
| with_compromise_robust_aggregate | See generated_tables.md |
| with_compromise_naive_aggregate | See generated_tables.md |
| bias_robust / bias_naive | See generated_tables.md |

**Table 3 — Baselines.** Policy comparison; see generated_tables.md.

**Profile ablation (Table 6), resilience (Table 7), latency (Table 5), safety-gate campaign, threat-evidence blocks (freshness/replay, sybil vs spoofing, messaging simulation, dynamic aggregation series), per-scenario summary, and comparison statistics** — see [generated_tables.md](generated_tables.md).

**Gate-threshold sensitivity (new).** We report a scheduling-scenario sweep over `safety_gate_max_load` (`gate_threshold_sweep_results` in summary.json). This identifies the regime where naive-in-loop crosses the gate while REP-CPS remains admissible, making the gate an explicit systems design knob instead of only an architectural statement.

**Safety-gate value when throughput looks flat.** On toy/lab scenarios, **tasks_completed** may be unchanged while **aggregate_load** and **gate_ok** still separate secured from unsecured paths. On the scheduling scenario, **unchanged throughput is not the right metric for gate value:** the gate **withholds work** when informational state is unsafe, which is a deliberate safety outcome (zero completions under denial).

**Latency and cost.** Table 5 and Figure 4; `latency_cost` in summary.json.

**Figure 1 — tasks_completed by policy.** `plot_rep_cps_summary.py`.

## 6. Methodology and reproducibility

**Methodology.** Evaluate profile discipline (admissibility, aggregation family, gate), offline bias under compromise, scoped adapter parity, scheduling-dependent outcomes, ablation, sweeps, latency. Kill criteria: see AUTHORING_PACKET.

**Reproducibility.** `python scripts/rep_cps_eval.py` (default 20 seeds, three scenarios including `rep_cps_scheduling_v0`). Trace metadata: `rep_cps_aggregate_load`, `rep_cps_safety_gate_ok`. **Statistical sensitivity:** `sensitivity_seed_sweep.py --eval rep_cps --ns 20,30`.

**Conditional trigger (updated).** On **toy_lab_v0** and **lab_profile_v0**, sensitivity aggregate does not change **tasks_completed** (scheduling is independent). On **rep_cps_scheduling_v0**, **gated aggregate does affect scheduling** under the harness, and **REP-CPS can preserve completions where naive-in-loop mean fails the gate** (see `scheduling_dependent_eval`). We still do **not** claim full operational benefit across all lab profiles or real deployments. See `docs/CONDITIONAL_TRIGGERS.md` (P2).

## 7. Limitations

- **Scope:** Thin-slice simulation; synthetic updates; no live sensors or production messaging (OPC UA / ROS 2 slice is future work).
- **Identity:** `auth_hook` is allow-list stub; no Sybil-resistant enrollment or cryptographic provenance in eval.
- **Construct validity:** Results are **profile + harness-specific**; they bound behavior under documented attacks, not all possible CPS deployments.
- **Robust aggregation magnitude:** Bias reduction is **directional** in the harness; interpretation should use **resilience envelope**, **ablation**, and **spoof/sybil** rows together—not a single scalar in isolation. At **large sybil counts** in the fixed multiset, `sybil_sweep` can show **robust not beating naive** (`failure_boundary_n_compromised` in Table 7); we do not claim uniform dominance of trimmed mean for all n.
- **Trigger wording:** Material task-level influence is **demonstrated on `rep_cps_scheduling_v0`**, not on every scenario in the suite. Generalizing to real schedulers remains future work.

**Threats to validity.** *Internal:* synthetic message generation; scheduling linkage is explicit only on scheduling-dependent YAML. *External:* scenario set small; no WAN. *Construct:* proxies for “safety” are gate threshold + task counts.

**Comparison to prior work.** See §1.1; `aggregation_variants` in summary.json for median/clipping/median-of-means on the same multiset.

---

**Discussion (contribution summary).** Sensitivity sharing should be treated as a **profiled informational subsystem** inside a larger assurance envelope: typed, admissible, rate-bounded, robustly aggregated, and **never** silently equivalent to actuation without a gate. This paper establishes **reusable profile semantics** and an **attack-evaluable harness** for that subsystem in MAESTRO.

**Design principles.**

- **P1:** Decision-relevant informational state is not harmless telemetry when it can shape scheduling or admission.
- **P2:** Admission controls (auth/freshness/rate) are part of semantics, not preprocessing.
- **P3:** Robust aggregation alone is insufficient without provenance and rate controls.
- **P4:** Operational effect must be explicitly gate-mediated.
- **P5:** Evaluation must separate offline robustness, in-loop bounded behavior, and task-level operational effect.

**Claims and backing.**

| Claim | Evidence |
|-------|----------|
| C1 (Profile deployable within assumptions) | PROFILE_SPEC, example_profile, Table 1 (scoped parity), Table 5–6, `latency_cost`, `profile_ablation`. |
| C2 (Reduced bias under compromise) | Table 2, Table 3, Table 6, Table 7, `sybil_vs_spoofing_evidence`, compromised harness. |
| C3 (Safety gate; gated influence) | Trace metadata, `safety_gate_denial`, scheduling-dependent eval, `rep_cps_scheduling_v0`. |
| C4 (Reproducible eval) | `rep_cps_eval.py`, summary.json, Tables 1–7, Figures 1–2, `freshness_replay_evidence`, `messaging_sim`, `dynamic_aggregation_series`. |
