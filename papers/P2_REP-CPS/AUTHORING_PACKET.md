# REP-CPS: A Safety-Gated Profile for Authenticated Sensitivity Sharing in Cyber-Physical Coordination

**Paper ID:** P2_REP-CPS  
**Tag:** conditional  
**Board path:** Spec → MVP → Eval → Draft  
**Kernel ownership:** protocol profile kernel (schemas, rate limits, provenance, robust aggregation constraints)

## 1) Trigger condition (why this paper exists)
Proceed only if **sensitivity sharing materially influences scheduling/actuation decisions** in the target architecture (lab/warehouse/traffic) and therefore becomes safety/security relevant. **Current status:** In the evaluated scenario, sensitivity sharing does not materially change tasks_completed; the paper is framed as a profile-and-harness contribution until a scenario that meets the trigger is added.

## 2) Claims
- **C1:** A CPS-oriented sensitivity-sharing profile can make decentralized informational exchange deployable by specifying typed variables, freshness windows, rate limits, provenance, and authentication hooks.
- **C2:** In the evaluated attack harness, robust aggregation variants reduce compromise-induced bias relative to naive averaging.
- **C3:** Protocol output is not directly actuating; it influences downstream decisions only through explicit safety-gate mediation compatible with the broader assurance envelope.
- **C4:** The profile can be evaluated reproducibly through MAESTRO-compatible fault injection and compromised-agent suites.

## 3) Outline
1. Motivation: why REP-like protocols are attractive; why CPS constraints break naive forms
2. Profile spec: message schemas, windowing, rate limits, provenance; formal profile model (update, acceptance, aggregation, safety-gated influence)
3. Threat model: Byzantine agents, sybils, spoofing, replay
4. Robust aggregation + reduced observed bias: spec-level commitments + acceptance tests
5. Safety-gate integration contract (Gatekeeper/Monitor mediation)
6. Reference implementation + conformance tests
7. Evaluation in MAESTRO scenarios

## 4) Experiment plan
- Scenarios: one bottleneck coordination task where sensitivity-sharing provides a measurable benefit (future); current eval shows adapter parity and reduced bias under compromise.
- Metrics: robustness under compromise (bias_robust vs bias_naive), safety-gate compliance, aggregate_load; optional multi-step convergence when aggregation_steps > 1.
- Baselines: unsecured channels; naive averaging; no rate limiting; non-robust aggregators; centralized.
- Stressors: compromised fraction; delay sweep; optional: sparse connectivity, bursty updates, jitter.

## 5) Artifact checklist
- `kernel/rep_cps/REP_CPS_PROFILE.v0.1.schema.json`
- reference aggregator + authentication hooks
- attack harness: compromised-agent behaviors
- MAESTRO adapter module to run the protocol

## 6) Kill criteria
- **K1:** cannot define measurable robustness acceptance tests.
- **K2:** protocol does not outperform baselines in the one scenario where it should help (or paper is profile-only with honest scope).
- **K3:** becomes unnecessary in the lab architecture (no meaningful decentralized primitive).

## 7) Target venues
- arXiv first (cs.RO, cs.CR, cs.DC)
- security venues if the threat model + guarantees are strong

## 8) Integration contract
- REP-CPS is a **profile** inside MADS envelope, not the envelope.
- Must reuse Contracts typed state and Replay/MAESTRO harnesses.
