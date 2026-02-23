# MADS-CPS: A Normative Minimum Assurance Bar for Agentic Cyber-Physical Workflows

**Paper ID:** P0_MADS-CPS  
**Stage target (board):** Spec → MVP → Eval → Draft  
**Kernel dependency:** must reference kernel schemas by version; breaking changes require version bump.

## 1) Thesis (one paragraph)
Define the minimum set of controls, telemetry, evidence, and conformance tiers required for third-party verification of system-level safety/security for agentic CPS workflows, including point-of-no-return (PONR) enforcement and admissible evidence bundles.

## 2) Claims (citable, falsifiable)
- Normative minimum bar is separable from any specific coordination algorithm: it constrains interfaces (telemetry/evidence/gating), not internal optimization.
- Conformance tiers can be tested by artifact presence + runtime checks + replayable evidence, enabling objective third-party verification.
- Evidence admissibility requires replayability + integrity + traceability; ‘logs’ are insufficient without deterministic replay constraints.
- PONR enforcement operationalizes safety in CPS by introducing explicit gate conditions before irreversible actuation.

## 3) Outline (high-level)
1. Problem framing and scope boundary (what this paper is / is not)
2. Core object (spec / protocol / trace / benchmark / model) and formal definitions
3. Implementation surface (schemas, validators, harness)
4. Evaluation plan (what evidence would convince a skeptic)
5. Limitations and explicit non-goals
6. Relationship to the portfolio (how it plugs into MADS-CPS / MAESTRO / Replay)

## 4) Experiment plan (minimum credible)
- Case study on 1 scenario (toy_lab_v0 initially; then a real micro-world) demonstrating tier checks: missing artifact → fails conformance; present + validated → passes.
- Replay-based verification: independent verifier reproduces MAESTRO metrics from TRACE; integrity checks via hashes.

## 5) Artifact checklist (must ship)
- kernel/mads/EVIDENCE_BUNDLE.v0.1.schema.json (stable schema + version discipline)
- kernel/policy/RELEASE_MANIFEST.v0.1.schema.json
- Assurance pack template (kernel/assurance_pack/ASSURANCE_PACK.v0.1.schema.json) for hazards→controls→evidence mapping
- Reference thin-slice pipeline producing evidence bundle and release manifest

## 6) Kill criteria (stop early if true)
- If tiers cannot be made objective (artifact-level + runtime-level checks) without devolving into subjective audits, the paper collapses into ‘best practices’.
- If replay/evidence requirements cannot be made implementable with credible overhead bounds, adoption path dies.
- If the scope overlaps too heavily with UL/IEC text without providing concrete executable artifacts, impact will be low.

## 7) Target venues (initial)
arXiv (cs.SE, cs.CR, cs.RO) + workshop track (safety/assurance for robotics/CPS); later journal venue oriented to safety cases (depending on positioning).

## 8) Integration contract (portfolio coherence)
- Output artifacts must validate against kernel schemas (or propose a versioned extension).
- All evaluations must be reproducible from `datasets/` with a release manifest and evidence bundle.
- Do not duplicate scope owned by other papers; cite and depend on them.
