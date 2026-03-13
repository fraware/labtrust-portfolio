# Safe LLM Planning for CPS: Typed Plans, Deterministic Toolcalling, and Runtime Safety Gates

**Paper ID:** P6_LLMPlanning  
**Tag:** conditional  
**Board path:** Spec → MVP → Eval → Draft  
**Kernel ownership:** LLM runtime kernel (typed plan schema + validator interface + toolcalling capture)

## 1) Trigger condition
Proceed only if:
- an LLM is in the control plane (planning/toolcalling), OR
- a typed-plan + validator firewall is needed as a general containment pattern.

## 2) Scope anchor (security realism)
Prompt injection is structurally different from SQL injection; treat LLMs as potentially “confusable deputies” and design for containment and residual risk, not perfect mitigation. citeturn0search1turn0search2

## 3) Claims
- **C1:** Typed plan outputs + validators produce a testable interface that blocks unsafe tool use and unsafe PONR proposals.
- **C2:** Deterministic toolcalling capture + bounded retries makes behavior replayable and auditable.
- **C3:** A CPS-specific red-team suite (prompt injection, malformed toolcalls, excessive agency) is required and sufficient to exercise key failure modes.
- **C4:** Under MAESTRO faults, the pattern reduces safety violations without unacceptable tail latency.

## 4) Outline
1. Why LLM-agent demos fail CPS constraints
2. Plan schema and type system
3. Validator stack: static checks, policy checks, gate integration
4. Deterministic toolcalling capture and replay integration
5. Red-team suite aligned with OWASP LLM Top 10 categories
6. Evaluation on MAESTRO scenarios
7. Deployment guidance: least privilege, safe refusal, residual risk posture

## 5) Experiment plan
- Scenarios: 1–2 MAESTRO scenarios with tool density + exceptions
- Metrics: unsafe proposals blocked, residual violations, latency tails, variance
- Baselines: untyped planner; typed without deterministic capture; rule-based
- Stressors: prompt injection via tool-fed content; partial tool results; time pressure

## 6) Artifact checklist
- `kernel/llm_runtime/TYPED_PLAN.v0.1.schema.json`
- validator library + policy hooks
- deterministic toolcalling wrapper
- red-team suite (cases + expected outcomes)
- MAESTRO adapter + baseline results

## 7) Kill criteria
- **K1:** validators fail to reliably block unsafe actions in red-team tests.
- **K2:** deterministic capture is too brittle across providers to support replay.
- **K3:** tail latency becomes operationally infeasible.

## 8) Target venues
- robotics systems + security workshops; arXiv first (cs.RO, cs.CR)

## 9) Integration contract
- Must treat LLM planning as a module inside MADS envelope.
- Must not claim elimination of prompt injection; claim containment + measurable robustness.

