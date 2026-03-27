# Coordination Contracts: Typed State, Ownership, and Valid Transitions Above Messaging

**Paper ID:** P1_Contracts  
**Tag:** core-kernel  
**Board path:** Spec → MVP → Eval → Draft  
**Kernel ownership:** coordination semantics kernel (authority, valid writes, time model)

## 1) One-line question
What does “coordination” mean in CPS when messaging is not authority—i.e., what are the **contracts** for shared state ownership, valid transitions, time semantics, and conflict resolution?

## 2) Scope anchors (lab reality)
- Primary anchor is **resource graphs + device heterogeneity + recovery**, not only “large N.”
- Must map cleanly to lab instrument substrates; explicitly include an interoperability hook to **OPC UA LADS** state machines.

## 3) Claims
- **C1:** Within a declared contract model, a trace-derived validator can detect and deny invalid writes corresponding to specified coordination failure classes (ownership conflicts, stale writes, reorder-sensitive violations). The contribution is an explicit coordination-admission layer (keyed authority, temporal admissibility, reason-coded denial, trace-derivability), positioned against OCC/locking/transport-only idioms; see draft Section 3 “Why Coordination Contracts are not just OCC, locking, or transport policy.”
- **C2:** Contract validation can be executed from event traces plus declared configuration alone, without privileged hidden state, enabling auditability and replay-based diagnosis.
- **C3:** The contract model is transport-agnostic by construction (defined over event/state semantics above the messaging layer); the paper demonstrates **boundary semantics** via reference store, LADS-shaped mapping, and multi-sequence **verdict-vector parity** between reference ingestion paths—not empirical equivalence of live transports.
- **C4:** A reference implementation can enforce the contract with bounded per-write overhead on the evaluated workload.

## 4) Outline
1. Motivation: “communication ≠ coordination” with concrete failure classes
2. Contract model: types, ownership/leases, authority scope
3. Valid transitions: invariants, preconditions, conflict rules
4. Time model above messaging: event vs processing vs actuation time
5. Concurrency semantics: lease/OCC/CRDT options + when each is admissible
6. Security invariants: provenance, writer authentication hooks
7. Interop mapping: OPC UA LADS → contract semantics
8. Reference implementation + evaluation

## 5) Experiment plan (tight and decisive)
- Micro-scenarios that isolate failures:
  - split-brain ownership,
  - stale write acceptance,
  - orphan lease/liveness hazard,
  - unsafe last-write-wins under delay/reorder.
- Metrics:
  - detection/denial rate,
  - false positives,
  - overhead (latency added per write validation),
  - convergence success.
- Baselines / comparators (eval.json `ablation` and `ablation_by_class`):
  - full contract vs timestamp-only vs ownership-only vs **occ_only** (version/timestamp proxy) vs **lease_only** (temporal proxy without lease fields in corpus) vs **lock_only** (ownership mutex proxy) vs accept-all vs **naive_lww**.
- Stressors:
  - clock skew, delay, reorder, partial partitions.

## 6) Artifact checklist
- `kernel/contracts/COORD_CONTRACT.v0.1.schema.json` (schema + stable IDs)
- validator library (pure function): `validate(state, event) -> verdict + reason_codes`
- reference implementation of a contract-enforcing store
- trace corpus of good/bad sequences + expected verdicts
- LADS mapping note: `kernel/interop/OPC_UA_LADS_MAPPING.v0.1.md`

## 7) Kill criteria
- **K1:** If a contract predicate requires **privileged hidden state** not derivable from trace + declared config, the design loses portability/auditability; document and either remove or make optional. See docs/P1_TRACE_DERIVABILITY.md.
- **K2:** semantics cannot be made transport-agnostic.
- **K3:** overhead makes even L0 control-plane enforcement infeasible.

## 8) Target venues
- NSDI / OSDI (coordination substrate framing)
- DSN / ICSE (dependability/spec+tooling)
- arXiv first (cs.DC, cs.RO, cs.SE)

## 9) Integration contract
- Contracts defines **what is a valid write** and **who may write**.
- MADS defines **what must be gated** and **what evidence is admissible**.
- Replay defines **how traces are replayed** and how nondeterminism is surfaced.

