# Safe LLM Planning for CPS: Typed Plans, Deterministic Toolcalling, and Runtime Safety Gates

**Paper ID:** P6_LLMPlanning  
**Stage target (board):** Spec → MVP → Eval → Draft  
**Kernel dependency:** must reference kernel schemas by version; breaking changes require version bump.

## 1) Thesis (one paragraph)
Provide a CPS-grade pattern for using LLMs inside coordination spines: typed plan interface, validators, deterministic toolcalling, bounded retries, and red-team suites, all measurable in MAESTRO and replayable via TRACE.

## 2) Claims (citable, falsifiable)
- Typed plans + validators reduce tool misuse and unsafe action proposals without requiring perfect LLM alignment.
- Deterministic toolcalling plus replay controls are necessary for credible evaluation and post-incident analysis.
- Red-team suites (prompt injection, malformed tool calls, boundary violations) can be standardized and scored.

## 3) Outline (high-level)
1. Problem framing and scope boundary (what this paper is / is not)
2. Core object (spec / protocol / trace / benchmark / model) and formal definitions
3. Implementation surface (schemas, validators, harness)
4. Evaluation plan (what evidence would convince a skeptic)
5. Limitations and explicit non-goals
6. Relationship to the portfolio (how it plugs into MADS-CPS / MAESTRO / Replay)

## 4) Experiment plan (minimum credible)
- Compare baseline agent vs typed+validated pipeline on safety violations, recovery, and latency budgets.
- Repeated trials to characterize variance; replay to confirm determinism envelope.

## 5) Artifact checklist (must ship)
- kernel/llm_runtime/TYPED_PLAN.v0.1.schema.json expanded into an actual plan DSL
- Validator library + refusal/bounded retry semantics
- Red-team suite: injection prompts, tool boundary tests, malformed JSON cases
- MAESTRO adapter enabling optional LLM planner to be benchmarked consistently.

## 6) Kill criteria (stop early if true)
- If typed+validated planning does not measurably reduce unsafe actions, paper fails.
- If determinism constraints make LLM integration unrealistic, reframe to ‘best-effort replay’ or drop.
- If red-team suite cannot be standardized, contribution becomes anecdotal.

## 7) Target venues (initial)
arXiv (cs.RO, cs.AI, cs.CR); agent safety workshops; potentially security-adjacent venues.

## 8) Integration contract (portfolio coherence)
- Output artifacts must validate against kernel schemas (or propose a versioned extension).
- All evaluations must be reproducible from `datasets/` with a release manifest and evidence bundle.
- Do not duplicate scope owned by other papers; cite and depend on them.
