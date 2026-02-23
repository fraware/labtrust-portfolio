# Coordination Contracts: Typed State, Ownership, and Valid Transitions Above Messaging for Large-Scale CPS

**Paper ID:** P1_Contracts  
**Stage target (board):** Spec → MVP → Eval → Draft  
**Kernel dependency:** must reference kernel schemas by version; breaking changes require version bump.

## 1) Thesis (one paragraph)
Make ‘communication isn’t coordination’ executable: specify a portable contract layer for shared state authority (ownership, admissible writes, temporal semantics, conflict resolution) that is auditable across ROS2/DDS, event logs, and hybrids.

## 2) Claims (citable, falsifiable)
- A contract layer reduces whole classes of failure (split brain, stale writes, orphan leases, unsafe last-write-wins) without prescribing a single messaging substrate.
- Authority + temporal semantics are necessary preconditions for auditability and replayability in agentic CPS.
- Minimal contract surfaces can be standardized as schemas + validation rules and adopted incrementally.

## 3) Outline (high-level)
1. Problem framing and scope boundary (what this paper is / is not)
2. Core object (spec / protocol / trace / benchmark / model) and formal definitions
3. Implementation surface (schemas, validators, harness)
4. Evaluation plan (what evidence would convince a skeptic)
5. Limitations and explicit non-goals
6. Relationship to the portfolio (how it plugs into MADS-CPS / MAESTRO / Replay)

## 4) Experiment plan (minimum credible)
- Construct 3–5 minimal failure scenarios; show contract flags violations early; quantify false positives/negatives.
- Integrate into MAESTRO: contract violations become scored failures (not just logs).

## 5) Artifact checklist (must ship)
- kernel/contracts/COORD_CONTRACT.v0.1.schema.json (placeholder now; expand to enumerated invariants)
- Reference validator: checks write admissibility, ownership/lease rules, and time ordering assumptions against TRACE.
- Two example ‘contract profiles’: blackboard/event-sourced and ROS2-style.
- Negative examples: traces that violate contract invariants (for tests).

## 6) Kill criteria (stop early if true)
- If the contract cannot remain substrate-agnostic (i.e., collapses into “ROS2 best practices”), thesis fails.
- If invariants become too many / too vague to validate, the contract cannot be enforced.
- If benefits cannot be demonstrated with small, concrete failure classes, paper won’t be citable.

## 7) Target venues (initial)
arXiv (cs.DC, cs.RO, cs.SE); distributed systems or robotics systems workshops; later systems venue if implementation matures.

## 8) Integration contract (portfolio coherence)
- Output artifacts must validate against kernel schemas (or propose a versioned extension).
- All evaluations must be reproducible from `datasets/` with a release manifest and evidence bundle.
- Do not duplicate scope owned by other papers; cite and depend on them.
