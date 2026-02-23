# From Coordination to Safety Case: A Traceable Assurance Argument for Multi-Agent CPS

**Paper ID:** P7_StandardsMapping  
**Stage target (board):** Spec → MVP → Eval → Draft  
**Kernel dependency:** must reference kernel schemas by version; breaking changes require version bump.

## 1) Thesis (one paragraph)
Provide auditor-ready templates and a concrete mapping from hazards → controls/invariants → evidence types → replayable audit traces, aligned to safety/security assurance practice expectations (e.g., UL 4600, STPA, IEC 62443-style structure).

## 2) Claims (citable, falsifiable)
- Adoption depends on legibility to governance ecosystems; templates make engineering artifacts auditable without diluting technical rigor.
- Traceability and replayability are the differentiators: they convert ‘claims’ into checkable arguments.
- A minimal mapping can be demonstrated on a single scenario with complete evidence coverage.

## 3) Outline (high-level)
1. Problem framing and scope boundary (what this paper is / is not)
2. Core object (spec / protocol / trace / benchmark / model) and formal definitions
3. Implementation surface (schemas, validators, harness)
4. Evaluation plan (what evidence would convince a skeptic)
5. Limitations and explicit non-goals
6. Relationship to the portfolio (how it plugs into MADS-CPS / MAESTRO / Replay)

## 4) Experiment plan (minimum credible)
- Evaluation is completeness/traceability: measure evidence coverage %, missing links, replay success rate.
- External review exercise: a third party follows the template to verify claims from artifacts.

## 5) Artifact checklist (must ship)
- kernel/assurance_pack/ASSURANCE_PACK.v0.1.schema.json + filled example instantiation
- Evidence mapping rules referencing kernel artifact IDs and manifests
- Checklist for audit completeness (coverage, integrity, replay success)
- One end-to-end “assurance pack” published as a release snapshot.

## 6) Kill criteria (stop early if true)
- If templates are too abstract to use, paper is useless; must stay concrete and runnable.
- If mapping devolves into a literature survey, re-scope to executable templates only.
- If a third party cannot reproduce the assurance argument, paper fails.

## 7) Target venues (initial)
arXiv (cs.SE, cs.RO, cs.CR); safety-case / assurance workshops; industry-facing venues.

## 8) Integration contract (portfolio coherence)
- Output artifacts must validate against kernel schemas (or propose a versioned extension).
- All evaluations must be reproducible from `datasets/` with a release manifest and evidence bundle.
- Do not duplicate scope owned by other papers; cite and depend on them.
