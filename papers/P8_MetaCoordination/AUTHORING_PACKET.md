# Meta-Coordination for Thousand-Agent CPS: Switching Coordination Regimes Under Stress

**Paper ID:** P8_MetaCoordination  
**Stage target (board):** Spec → MVP → Eval → Draft  
**Kernel dependency:** must reference kernel schemas by version; breaking changes require version bump.

## 1) Thesis (one paragraph)
Formalize and evaluate regime switching (centralized ↔ market ↔ swarm ↔ fallback) under compound faults with explicit safety and auditability constraints, using MADS gating + MAESTRO evaluation + replay evidence.

## 2) Claims (citable, falsifiable)
- Static coordination regimes fail under compound faults; meta-controllers can reduce collapse frequency.
- Safe switching requires explicit conditions and transition constraints, not ad hoc heuristics.
- Switching policies can be evaluated via MAESTRO under stress and audited via replayable traces.

## 3) Outline (high-level)
1. Problem framing and scope boundary (what this paper is / is not)
2. Core object (spec / protocol / trace / benchmark / model) and formal definitions
3. Implementation surface (schemas, validators, harness)
4. Evaluation plan (what evidence would convince a skeptic)
5. Limitations and explicit non-goals
6. Relationship to the portfolio (how it plugs into MADS-CPS / MAESTRO / Replay)

## 4) Experiment plan (minimum credible)
- Compare static regimes vs meta-controller across compound-fault suites; measure task completion, tail latency, MTTR, safety violations.
- Ablations: switching disabled, safety constraints removed, hysteresis removed.

## 5) Artifact checklist (must ship)
- Meta-controller spec (paper-local initially; kernel schema in v0.2 if stabilized)
- Switching criteria library + safety conditions
- MAESTRO scenarios designed to trigger regime stress (fault bursts, tool outages, latency spikes)
- Replay evidence showing safe transition attribution.

## 6) Kill criteria (stop early if true)
- If switching wins only in one toy scenario, contribution weak; must generalize across at least two stress profiles.
- If safety constraints are not enforceable (only post-hoc), paper fails.
- If meta-controller adds unacceptable complexity without measurable benefit, stop.

## 7) Target venues (initial)
arXiv (cs.RO, cs.AI, eess.SY); CPS/robotics control workshops.

## 8) Integration contract (portfolio coherence)
- Output artifacts must validate against kernel schemas (or propose a versioned extension).
- All evaluations must be reproducible from `datasets/` with a release manifest and evidence bundle.
- Do not duplicate scope owned by other papers; cite and depend on them.
