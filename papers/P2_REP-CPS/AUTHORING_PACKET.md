# REP-CPS: A Real-Time, Authenticated Sensitivity-Sharing Profile for Cyber-Physical Coordination

**Paper ID:** P2_REP-CPS  
**Stage target (board):** Spec → MVP → Eval → Draft  
**Kernel dependency:** must reference kernel schemas by version; breaking changes require version bump.

## 1) Thesis (one paragraph)
Define a CPS-grade protocol profile for real-time sensitivity/coordination-variable sharing: typed variables, bounded rates, authenticated provenance, robust aggregation under compromise, and explicit safety gates before actuation.

## 2) Claims (citable, falsifiable)
- Naive sensitivity sharing is unsafe in CPS under compromise; a tight profile is required for authenticated, rate-bounded, influence-bounded aggregation.
- Robust aggregation + safety gating can make sensitivity signals usable without giving any agent unilateral control of actuation.
- A profile can be evaluated via fault injection (compromised agents, spoofing, delay) and measured via MAESTRO.

## 3) Outline (high-level)
1. Problem framing and scope boundary (what this paper is / is not)
2. Core object (spec / protocol / trace / benchmark / model) and formal definitions
3. Implementation surface (schemas, validators, harness)
4. Evaluation plan (what evidence would convince a skeptic)
5. Limitations and explicit non-goals
6. Relationship to the portfolio (how it plugs into MADS-CPS / MAESTRO / Replay)

## 4) Experiment plan (minimum credible)
- Convergence under sparsity + bounded update rates; robustness under compromised agents; safety-gate prevents unsafe actuation.
- Tail latency + throughput evaluation under rate limits; measure effect on coordination tax.

## 5) Artifact checklist (must ship)
- kernel/rep_cps/REP_CPS_PROFILE.v0.1.schema.json expanded into a concrete profile
- Threat model spec + test harness: compromised-agent injection, spoofed provenance, rate-limit violation
- Reference aggregator implementations (median/trimmed mean + influence bounds as baseline)
- Safety-gate interface linking profile outputs to Gatekeeper/Monitor logic (MADS).

## 6) Kill criteria (stop early if true)
- If the profile cannot be specified without re-deriving the entire REP framework, scope is wrong.
- If robustness cannot be demonstrated with clear threat-model tests, the profile is cosmetic.
- If runtime costs make it infeasible under CPS constraints, adoption fails.

## 7) Target venues (initial)
arXiv (cs.CR, cs.RO, cs.DC); security/robotics workshops; depending on maturity, security-focused venue.

## 8) Integration contract (portfolio coherence)
- Output artifacts must validate against kernel schemas (or propose a versioned extension).
- All evaluations must be reproducible from `datasets/` with a release manifest and evidence bundle.
- Do not duplicate scope owned by other papers; cite and depend on them.
