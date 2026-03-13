# REP-CPS: A Real-Time, Authenticated Sensitivity-Sharing Profile for Cyber-Physical Coordination

**Paper ID:** P2_REP-CPS  
**Tag:** conditional  
**Board path:** Spec → MVP → Eval → Draft  
**Kernel ownership:** protocol profile kernel (schemas, rate limits, provenance, robust aggregation constraints)

## 1) Trigger condition (why this paper exists)
Proceed only if **sensitivity sharing materially influences scheduling/actuation decisions** in the target architecture (lab/warehouse/traffic) and therefore becomes safety/security relevant.

## 2) Claims
- **C1:** A CPS profile makes sensitivity-sharing deployable: typed variables, bounded update rates, authenticated channels, robust aggregation under compromise.
- **C2:** Under compromised agents, aggregation maintains bounded influence and stable convergence behavior.
- **C3:** Protocol state does not directly actuate; it influences decisions only through explicit safety gates (MADS-compatible).
- **C4:** The profile is testable via fault injection and compromised-agent suites in MAESTRO.

## 3) Outline
1. Motivation: why REP-like protocols are attractive; why CPS constraints break naive forms
2. Profile spec: message schemas, windowing, rate limits, provenance
3. Threat model: Byzantine agents, sybils, spoofing, replay
4. Robust aggregation + influence bounds: spec-level commitments + acceptance tests
5. Safety-gate integration contract (Gatekeeper/Monitor mediation)
6. Reference implementation + conformance tests
7. Evaluation in MAESTRO scenarios

## 4) Experiment plan
- Scenarios: one bottleneck coordination task where sensitivity-sharing provides a measurable benefit.
- Metrics: convergence time, stability under delay, robustness under compromise, safety-gate compliance.
- Baselines: unsecured channels; naive averaging; no rate limiting; non-robust aggregators.
- Stressors: compromised fraction sweep; sparse connectivity; bursty updates; jitter.

## 5) Artifact checklist
- `kernel/rep_cps/REP_CPS_PROFILE.v0.1.schema.json`
- reference aggregator + authentication hooks
- attack harness: compromised-agent behaviors
- MAESTRO adapter module to run the protocol

## 6) Kill criteria
- **K1:** cannot define measurable influence bounds / robustness acceptance tests.
- **K2:** protocol does not outperform baselines in the one scenario where it should help.
- **K3:** becomes unnecessary in the lab architecture (no meaningful decentralized primitive).

## 7) Target venues
- arXiv first (cs.RO, cs.CR, cs.DC)
- security venues if the threat model + guarantees are strong

## 8) Integration contract
- REP-CPS is a **profile** inside MADS envelope, not the envelope.
- Must reuse Contracts typed state and Replay/MAESTRO harnesses.

