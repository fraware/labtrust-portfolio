# Deterministic Replay as a First-Class Primitive for Large-Scale Agentic CPS Coordination

**Paper ID:** P3_Replay  
**Stage target (board):** Spec → MVP → Eval → Draft  
**Kernel dependency:** must reference kernel schemas by version; breaking changes require version bump.

## 1) Thesis (one paragraph)
Turn audit logs into replayable causal programs: specify determinism requirements, a trace format, a replay engine, and nondeterminism detection for CPS coordination under faults and tail latency.

## 2) Claims (citable, falsifiable)
- Replayability is the missing glue between evaluation, incident response, and safety cases in agentic CPS.
- Determinism requirements can be made explicit and testable (same trace must imply same state evolution, or divergence is flagged).
- Nondeterminism detection is actionable: it identifies missing logging fields, hidden randomness, or time-source ambiguity.

## 3) Outline (high-level)
1. Problem framing and scope boundary (what this paper is / is not)
2. Core object (spec / protocol / trace / benchmark / model) and formal definitions
3. Implementation surface (schemas, validators, harness)
4. Evaluation plan (what evidence would convince a skeptic)
5. Limitations and explicit non-goals
6. Relationship to the portfolio (how it plugs into MADS-CPS / MAESTRO / Replay)

## 4) Experiment plan (minimum credible)
- Inject hidden randomness and show replay divergence is detected and localized.
- Replay MAESTRO metrics from TRACE; independent verification: metrics consistency + fault-event consistency.

## 5) Artifact checklist (must ship)
- kernel/trace/TRACE.v0.1.schema.json (expand with time model fields as needed)
- Replay engine (impl/src/labtrust_portfolio/replay.py) + test vectors
- Nondeterminism classifier: mismatch localization + missing-field suggestions (v0.2 target)
- Replay report format (may be folded into Evidence Bundle in v0.1; separate schema later).

## 6) Kill criteria (stop early if true)
- If determinism requirements become too strict to be practical, replay is dead-on-arrival.
- If replay cannot detect meaningful nondeterminism (high false negatives), value proposition collapses.
- If replay adds unacceptable overhead for CPS, must be reframed or dropped.

## 7) Target venues (initial)
arXiv (cs.RO, cs.DC, cs.SE); systems/robotics reproducibility workshops; later systems venue if robust.

## 8) Integration contract (portfolio coherence)
- Output artifacts must validate against kernel schemas (or propose a versioned extension).
- All evaluations must be reproducible from `datasets/` with a release manifest and evidence bundle.
- Do not duplicate scope owned by other papers; cite and depend on them.
