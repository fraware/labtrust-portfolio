# REP-CPS: Safety-Gated Sensitivity Sharing as a Profiled Informational Control Surface in Cyber-Physical Coordination

**Paper ID:** P2_REP-CPS  
**Tag:** conditional (scoped)  
**Board path:** Spec → MVP → Eval → Draft  
**Kernel ownership:** protocol profile kernel (schemas, rate limits, provenance, robust aggregation constraints)

## 1) Trigger condition (why this paper exists)
Proceed when **sensitivity sharing materially influences scheduling or actuation** in the target architecture (lab/warehouse/traffic) and therefore becomes safety/security relevant.

**Current status:** **Partial:** On **rep_cps_scheduling_v0**, gated aggregate load **withholds thin-slice scheduling** when the safety gate denies; under duplicate-sender spoof stress, **REP-CPS (trimmed)** preserves completions vs **naive-in-loop mean** in the harness (`scheduling_dependent_eval` in summary.json). On **toy_lab_v0** / **lab_profile_v0**, scheduling does not consume REP aggregate, so **tasks_completed** stays parity with centralized (no task-level sensitivity there). Real schedulers and live buses remain future work. See `docs/CONDITIONAL_TRIGGERS.md` (P2) and `papers/P2_REP-CPS/REVIEWER_ATTACK_SURFACE_LEDGER.md`.

## 2) Claims
- **C1:** Deployable (within evaluated assumptions) profile: typed variables, freshness, rate limits, provenance, auth hooks; bounded overhead.
- **C2:** Robust aggregation reduces observed compromise-induced bias vs naive; ablation shows rate/freshness/auth surface matters.
- **C3:** Informational-only protocol state; gate-mediated downstream effect; MADS-compatible.
- **C4:** Reproducible MAESTRO eval: compromise + spoof + freshness/replay micro-evidence + messaging-order slice + scheduling-dependent scenario.

## 3) Outline
1. Motivation + necessity vignette + novelty-as-profile
2. Related work (Byzantine agg, runtime assurance, industrial messaging)
3. Profile spec + formal model + worked example + deployable definition
4. Threat model: exercised / partial / out of scope + threat-to-evidence table
5. Robust aggregation + safety gate + “not just trimmed mean / not just auth”
6. Evaluation: **two modes** (offline vs in-loop); adapter parity (scoped); scheduling scenario; ablation; sweeps; latency; threat evidence blocks
7. Discussion: profiled informational subsystem; reusable harness
8. Limitations + conditional trigger scope

## 3.1) Research questions (journal framing)
- **RQ1:** Can the profile bound compromised informational influence without non-scheduling throughput regression?
- **RQ2:** Which controls matter most (auth, freshness, rate-limit, robust aggregation, gate)?
- **RQ3:** When does sensitivity sharing become task-relevant rather than only informational?
- **RQ4:** How should conditional/negative outcomes be reported reproducibly for reviewer scrutiny?

## 4) Experiment plan
- Scenarios: **toy_lab_v0**, **lab_profile_v0**, **rep_cps_scheduling_v0** (gate-linked scheduling); default in `rep_cps_eval.py`.
- Metrics: offline bias; in-loop tasks_completed (global + scheduling_dependent_eval); gate campaign; latency_cost; profile_ablation; resilience_envelope; freshness_replay_evidence; sybil_vs_spoofing_evidence; messaging_sim; dynamic_aggregation_series.
- Baselines: centralized; naive-in-loop; unsecured.
- Stressors: delay sweep; compromise; spoof; optional `--aggregation-steps` for convergence table; optional `--drop-sweep`; optional `--gate-threshold-sweep` for scheduling-scenario gate sensitivity.

## 5) Artifact checklist
- `kernel/rep_cps/REP_CPS_PROFILE.v0.1.schema.json`, PROFILE_SPEC, example_profile
- `bench/maestro/scenarios/rep_cps_scheduling_v0.yaml`
- reference aggregator + `sensitivity_spoof_duplicate_sender_update`
- attack harness: `compromised_updates`
- REPCPSAdapter + thinslice `rep_cps_safety_gate_ok` scheduling path
- `scripts/rep_cps_eval.py`, `export_rep_cps_tables.py`, plot scripts

## 6) Kill criteria
- **K1:** cannot define measurable robustness acceptance tests.
- **K2:** no scenario where profile semantics matter for eval outcomes (addressed by scheduling scenario + offline bias).
- **K3:** becomes unnecessary in the lab architecture (no meaningful decentralized primitive).

## 7) Target venues
- journal-first packaging with explicit scoped-trigger framing and script-backed visuals/tables
- arXiv companion release (cs.RO, cs.CR, cs.DC)

## 8) Integration contract
- REP-CPS is a **profile** inside MADS envelope, not the envelope.
- Must reuse Contracts typed state and Replay/MAESTRO harnesses.
