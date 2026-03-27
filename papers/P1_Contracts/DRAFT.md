# Coordination Contracts: Typed State, Ownership, and Valid Transitions Above Messaging for Cyber-Physical Systems

**Draft (v0.2).**

## Abstract

In cyber-physical systems, message delivery is not the same as coordination. Middleware and logs provide delivery, ordering hints, and stored values, but they do not by themselves define **whether a write to shared keyed state was coordination-valid** under explicit authority and temporal rules. We propose Coordination Contracts, a contract layer above the messaging substrate that defines typed state, writer authority, valid transitions, and temporal admissibility, with **trace-derivability**: validation is executable from event traces plus declared configuration alone, without privileged hidden state. We present a pure-function validator, a contract-enforcing reference store, and a stratified challenge corpus; the validator detects and denies targeted invalid-write classes with bounded per-write overhead on the evaluated workload. We map the surface to OPC UA LADS-shaped events to illustrate boundary portability; we do not claim full cross-transport deployment or live distributed evaluation.

---

## 1. Introduction

In CPS, "communication is not coordination." Messaging does not imply authority. A minimal contract layer makes coordination pathologies explicit as invalid state transitions and allows a validator to detect and deny them before application. For a declared contract model and trace-derived validator, invalid writes belonging to a specified failure class are detected and denied before state application. We need contracts for shared state ownership, valid transitions, time semantics, and conflict resolution so that coordination is auditable and replayable.

**Motivating vignette.** Two lab controllers both believe they may drive the same functional unit after a delayed handover message: Controller A releases the unit in the orchestration UI, but Controller B’s stale assignment still issues a `task_start` for the same key. Messages arrive in an order that preserves transport QoS yet violates coordination intent. Without a portable, trace-checkable rule for **who may write which key when**, the system can accept an invalid transition path even when every packet was delivered. Coordination Contracts make that situation a **deny** with explicit reason codes (e.g. split-brain, stale write) before application state moves.

---

## 2. Problem setting and failure model

**Failure classes.** We target coordination pathologies that arise when multiple writers or delayed delivery affect shared keyed state:

- **Split-brain ownership:** Two writers believe they own the same key; both attempt to write. Detected when an event claims to write a key that is owned by another writer in state and no handover is defined.
- **Stale write:** A write is accepted that is based on an outdated view of state. Detected when event timestamp or sequence is before the last update for that key and the contract requires monotonicity.
- **Unsafe last-write-wins under delay/reorder:** Messages are reordered; a later write (by wall clock) is applied after an earlier one, violating intended ordering. Detected when conflict semantics require ordering and event order is violated.

**Assumptions.** We state explicitly: (i) writer identity is as given in the trace (no Byzantine or spoofed writers in the evaluated model); (ii) lease and ordering semantics are defined in the declared configuration; (iii) validation is applied before state application; (iv) we do not claim prevention in live distributed deployment, under partitions, or with Byzantine writers—only that the validator detects and denies the specified failure classes on the event stream and state as defined.

**Ground truth for invalidity (benchmark).** For the challenge corpus, each event’s expected allow/deny label is **authored against the declared contract configuration and the scenario description**, independently of the implementation output: for each sequence, the label is justified by a short textual invariant argument (e.g. "writer ≠ owner at this key," or "event time strictly before last accepted time for key"). Labels are **not** produced by running the reference validator and copying its output; the reference runner is used only for **regression checking** (`detection_ok`). Ambiguous scenarios are resolved by fixing the declared configuration (e.g. strict vs. non-strict timestamp rule) and documenting it in the sequence `description` and benchmark spec.

---

## 3. Related work and positioning

**Distributed coordination and concurrency specification.** Contract Net [1] and TLA+ [2] address protocol-level task allocation and rigorous specification of concurrent systems. They do not provide a drop-in, trace-replayable admission layer for **keyed shared state** in CPS orchestration traces with reason-coded denials at the write boundary.

**Distributed consistency, OCC, and transactional stores.** Optimistic concurrency control, version checks, and transactional isolation prevent conflicting updates when versions or transactions are available. These mechanisms typically assume a **store-defined** conflict domain (tuple version, row lock epoch) rather than a **portable coordination contract** over heterogeneous event shapes with explicit **writer authority** and CPS-oriented reason codes on a trace.

**Locks, leases, reservations.** Mutual exclusion, leases, and workflow reservations regulate *who may proceed* at a point in time. They do not by themselves yield **trace-derived** explanations of *why a particular write was invalid* after the fact, nor a uniform verdict interface across event-log vs. RPC-style ingestion without shared lock state in the trace.

**Runtime verification, shields, and monitors.** Runtime enforcement layers (e.g. monitors, shields) can block unsafe actions. Our emphasis differs: a **pure validator** over replay state with **trace-derivability** and a **benchmarked** coordination failure taxonomy for CPS-style keyed tasks.

**Transport and middleware (ROS 2/DDS, logs).** ROS 2/DDS provide transport, discovery, and QoS; Kafka-style logs preserve records and compaction per key. Neither defines **coordination validity** of a write to shared orchestration state under declared authority and temporal rules.

**Industrial interoperability (OPC UA LADS).** LADS gives rich device and FunctionalUnit state machines for interoperation. It does not subsume a **generic** contract for cross-controller write authority and conflict handling at the shared coordination boundary.

**Positioning.** This paper sits above transport, transactional/OCC idioms, and single-component state machines: we define a **contract boundary** where invalid coordination becomes an explicit, replay-checkable **deny** with reasons, before application.

### Why Coordination Contracts are not just OCC, locking, or transport policy

A skeptical reader may collapse our contribution to "schema + timestamp + ownership map." The distinction is **what is being specified and what evidence is produced**:

- **OCC / version checks** resolve conflicts on a stored version or transaction read set; they do not, without further semantics, define **portable authority** over **orchestration keys** across heterogeneous writers with **reason-coded denials** aligned to CPS coordination failures (split-brain, stale write, reorder-sensitive violations).
- **Locks and leases** enforce mutual exclusion or time-bounded access; they do not automatically provide **audit-grade, trace-replayable verdicts** on each write event using only trace fields and declared configuration (trace-derivability).
- **Transport QoS** governs delivery and ordering *statistics*; it does not define **write validity** under explicit ownership and monotonicity rules.
- **Local state-machine guards** constrain one component; they do not replace a **shared-state coordination contract** across controllers unless every participant shares identical hidden state (which we avoid by construction).

**Novelty synthesis.** Coordination Contracts combine **explicit keyed ownership**, **temporal admissibility**, **reason-coded denial**, **trace-derivability**, and **semantic portability at the event/state boundary**—a package adjacent layers address piecemeal but do not substitute as a whole.

---

## 4. Coordination contract model

We give explicit definitions so the semantics are extractable from the manuscript.

**Contract state.** Let \(S\) denote the contract state for a keyed resource graph. For each key \(k\), the state includes (i) a typed value \(v_k\), (ii) an ownership record \(o_k\), (iii) a version or logical time summary \(\tau_k\) (e.g. last accepted write time), and (iv) optional lease metadata \(\ell_k\). The implementation maintains at least `ownership` (key to writer) and `_last_ts` (key to last accepted timestamp).

**Events.** An event \(e\) is a tuple \((k, a, w, t_e, t_p, \sigma, \Delta)\): target key \(k\), action type \(a\), claimed writer identity \(w\), event time \(t_e\), processing time \(t_p\), ordering token or sequence number \(\sigma\), and proposed state update payload \(\Delta\). In the reference implementation these appear as `type`, `ts`, `actor`/`payload.writer`, and `payload` with `task_id` (key).

**Declared configuration.** \(C\) is the contract configuration (e.g. conflict semantics, use of instrument state machine). The validator is parameterized by \(C\); no hidden state is required beyond what is in the trace and \(C\).

**Ownership and authority scope.** The owner of key \(k\) in state \(S\) is \(o_k\). Writer \(w\) is authorized for key \(k\) iff \(w = o_k\) or the contract defines an admissible handover. Lease validity, when present, is evaluated from \(\ell_k\) and the current time or sequence.

**Valid transition predicate.** A transition \((S, e) \rightarrow S'\) is valid iff: type validity holds for the payload, the writer has authority for the affected key(s), lease validity holds when required, temporal admissibility holds (e.g. \(t_e \geq \tau_k\) for monotonicity), and the transition is admissible under the contract (e.g. allowed state-machine edge).

**Temporal order relation.** For monotonicity we require event time not to go backward per key: \(t_e \geq \tau_k\) where \(\tau_k\) is the last accepted write time for key \(k\). Violations yield reason codes such as `stale_write` and `reorder_violation`.

**Worked example.** Let \(S\) have `ownership["t1"] = "agent_1"` and `_last_ts["t1"] = 3.0`. Event \(e\) is `task_end` with `payload.task_id = "t1"`, `payload.writer = "agent_2"`, `ts = 4.0`. Then \(V_C(S,e)\) returns **deny** with reason `split_brain` (writer differs from owner). If instead `payload.writer = "agent_1"` but `ts = 2.0`, the verdict is **deny** with reasons `stale_write` and `reorder_violation` (strict backward move relative to \(\tau_{t1}\)). If `ts = 4.0` and writer matches, the verdict is **allow** and the admitted transition updates \(\tau_{t1}\) and ownership per the reference store rules.

**Validation and verdict.** Given declared configuration \(C\), validation is a pure function
\[
V_C(S, e) \rightarrow (\texttt{allow} \mid \texttt{deny}, R),
\]
where \(R\) is a set of reason codes (e.g. `split_brain`, `stale_write`, `reorder_violation`). The function checks type validity, writer authority, lease validity (if used), temporal admissibility, and transition admissibility.

**Trace-derivability.** The validator is trace-derived if \(V_C\) depends only on the current replay state reconstructed from prior admitted events and on fields present in the event trace and declared configuration, with no privileged hidden state.

**Propositions.**

- **Proposition 1 (Determinism).** For fixed \(C\), \(S\), and \(e\), the validator returns a unique verdict and reason-code set. (Machine-checked in the Lean W2 wedge: same state and event yield the same verdict.)
- **Proposition 2 (Trace-derivability).** If the replay state is reconstructed from the admitted prefix of the trace and \(C\), validation is reproducible by an independent auditor without hidden runtime state.
- **Proposition 3 (Sound denial for specified classes).** Under the stated assumptions on writer identity, lease semantics, and ordering domain, events in the defined failure classes (split-brain, stale write, reorder violation) are denied by the validator.
- **Proposition 4 (Transport invariance).** If two transports induce the same event/state semantics at the contract boundary, validation outcomes are identical.
- **Proposition 5 (Admissible-prefix invariants, sketch).** Let an **admitted prefix** be a trace prefix where every event has been validated with `allow` under \(V_C\) and state updated by the reference store’s `apply` function. Suppose the initial contract state satisfies: (i) for every key \(k\) with owner \(o_k\), only events with writer \(o_k\) have been applied to \(k\) since ownership was established; (ii) \(\tau_k\) is the timestamp of the last admitted write for \(k\) and is monotone along admitted writes. Then after any admitted prefix, those properties still hold. *Proof sketch:* `deny` prevents applying events that introduce a new owner conflict or strict backward timestamp for \(k\); `apply` only advances \(\tau_k\) on admit. The Lean W2 wedge proves determinism; a full machine-checked invariant proof is left as future formal work (see comment in `formal/lean/Labtrust/W2Contract.lean`).

---

## 5. Validator semantics and properties

The reference validator implements \(V_C(S, e)\) as a pure function: it returns allow or deny and a set of reason codes. It uses no privileged hidden state; all predicates are computed from the trace-derived state and the event. The contract-enforcing store applies a write only when the validator returns allow, giving one validation per write and bounded overhead.

**Pseudocode (reference `validate`).**

```
function validate(state, event, contract):
  if event.type not in {task_start, task_end, coordination_message}:
    return (allow, [])
  if event.type == coordination_message:
    return (allow, [])
  key <- event.payload.task_id
  if key is empty:
    return (deny, [unknown_key])
  reasons <- []
  owner <- state.ownership[key]
  writer <- event.payload.writer or event.actor.id
  if owner is not null and owner != writer:
    reasons.append(split_brain)
  prev_ts <- state._last_ts[key] default -inf
  if prev_ts > event.ts:
    reasons.append(stale_write)
    reasons.append(reorder_violation)
  if contract.use_instrument_state_machine and not allowed_instrument_transition(state, key, event.type):
    reasons.append(instrument_state_machine)
  if reasons is non-empty:
    return (deny, reasons)
  return (allow, [])
```

---

## 6. Interoperability mapping to LADS

OPC UA LADS describes laboratory devices and FunctionalUnits (FU) with explicit states and transitions. Coordination Contracts sit at the **orchestration boundary**: they admit or deny **writes** to shared keyed coordination state derived from LADS-relevant identifiers and controller roles.

**Mapping table (illustrative).**

| LADS / lab concept | Contract key \(k\) | Owner \(o_k\) | Contract event shape | Typical denial reasons |
|--------------------|-------------------|---------------|----------------------|-------------------------|
| FunctionalUnit instance | e.g. FU id or `(device_id, fu_id)` string | Active controller / session id in `ownership[k]` | `task_start` / `task_end` with `payload.task_id = k` | `split_brain` if writer ≠ owner |
| FU lifecycle transition | same \(k\) | unchanged or handover (declared in trace) | `task_start` then `task_end` edges | `reorder_violation`, `stale_write` if timestamps go backward vs. \(\tau_k\) |
| Coordination / status message | n/a or auxiliary key | n/a | `coordination_message` | (allowed; no key write) |
| Unknown or malformed key | empty `task_id` | n/a | any task event | `unknown_key` |

**Worked trace snippet.** Controller C1 emits LADS-shaped `task_start` for FU `FU-42` at \(t=1.0\); the reference mapping sets `ownership["FU-42"]=C1`, advances `_last_ts`. A delayed message from C2 with `task_start` for `FU-42` at \(t=0.5\) maps to the same key but violates monotonicity: **deny** with `stale_write` + `reorder_violation` in LADS terms ("late transition relative to admitted lab timeline").

**Transport-agnostic scope (modest).** Proposition 4 is **almost definitional on purpose**: if two ingestion paths normalize to the **same** \((S,e)\) at the boundary, the pure validator must agree. The **empirical** content of the parity experiment is narrower: it checks that **multiple reference ingestion paths** (event-log replay vs. LADS-shaped replay) do not accidentally diverge in glue code—i.e. implementation consistency under identical boundary semantics. It does **not** show equivalence of ROS 2, DDS, and Kafka in deployment; live adapters remain future work.

---

## 7. Reference implementation

The validator is a pure function over state and event; the contract-enforcing store applies writes only when the validator allows. Evaluation uses a challenge corpus of sequences and a reference runner that reports verdicts, reason codes, detection agreement with expected verdicts, and per-write overhead. Artifact and reproduction instructions are in Appendix A.

---

## 8. Experimental design

**Hypothesis.** The contract validator detects and denies invalid writes corresponding to the specified failure classes (split-brain, stale write, reorder violation) from trace events.

**Metrics.** Verdict (allow/deny), reason codes, detection agreement with expected verdicts; true positive rate, false positive rate, false negative count; precision and recall globally and **by inferred failure class**; median, p95, p99 validation latency with bootstrap CI; throughput with confidence intervals; resource and cost proxies on the reference runner.

**Baselines and comparators.** Besides trivial accept-all, we report **ablation-style** policies (timestamp-only, ownership-only) and **named comparators** mapped to common idioms: **OCC / version-style** and **lease-style** checks are approximated in the reference benchmark by **temporal monotonicity per key** (no explicit version or lease fields in the corpus state); **lock / mutex-style** exclusivity is approximated by **ownership-only** (no temporal check); **naive last-write-wins** accepts all writes. These are not claimed to be full database OCC, lease protocols, or distributed lock services—they position the contract layer against **familiar coordination patterns** under a trace-evaluable interface.

**Corpus.** The challenge corpus includes sequences partitioned by failure class, with positive and negative controls (e.g. good sequences, split-brain same-epoch and after lease expiry, stale write under clock skew and delayed delivery, reorder with and without violation, duplicate delivery, same-timestamp tie cases). See Appendix A for corpus location and schema.

### Ground-truth labeling and anti-circularity

**Who labels.** Expected verdicts are **authored** with each JSON sequence (human-written, reviewed against the scenario `description` and declared configuration). A small fraction of sequences may be produced by a **parameterized generator** (`generate_contract_corpus.py`); those inherit a closed-form rule (e.g. first writer wins, subsequent writers denied) documented in the generator and sequence description.

**Independence from implementation.** Labels are **not** copied from `validate()` output. CI runs `contracts_eval` and tests that load each corpus file independently (`tests/test_contracts_p1.py`) so that label drift is caught.

**Ambiguity policy.** If strict timestamp equality vs. inequality is ambiguous, the sequence documents the chosen rule (e.g. strict `>` for stale detection in the reference validator) and `expected_verdicts` match that rule.

---

## 9. Results

**Corpus evaluation.** The challenge corpus comprises 51+ sequences (Tier 1–3: positive controls, split-brain, stale write/reorder, boundary, long-horizon, adversarial). Correctness is evaluated by exact per-event verdict-vector match (not denial count alone). The full contract validator achieves detection agreement with expected verdicts for all sequences. **Detection metrics** (per-event, expected verdicts as ground truth): true positives, false positives, false negatives; precision, recall, and F1 are reported in eval output. **Validation latency** is computed from event-level samples: median, p95, and p99 per-write overhead with bootstrap 95% CI; overhead is bounded (sub-millisecond in the evaluated workload). **Resource and cost:** Wall-clock time, total events evaluated, events/sec overall, and an optional cost proxy (events per dollar when LABTRUST_COST_PER_HOUR is set) are reported; single-threaded (1 core) assumption is documented.

**Table 1 — Corpus evaluation (summary).** Sample sequences; full corpus has 51+ sequences. Per-sequence verdict agreement (exact verdict vector) and denials; see Appendix A for run manifest and full table.

| Sequence           | events | allows | denials | detection_ok | time_per_write_us |
|--------------------|--------|--------|---------|--------------|-------------------|
| good_sequence      | 2      | 2      | 0       | true         | ~25               |
| reorder_sequence   | 2      | 1      | 1       | true         | ~22               |
| split_brain_sequence | 1    | 0      | 1       | true         | ~13               |
| stale_write_sequence | 1    | 0      | 1       | true         | ~11               |
| unsafe_lww_sequence | 2     | 1      | 1       | true         | ~31               |
| **Summary (51+ seq)** | —    | —      | —       | all true     | median ~21 (event-level CI95 in artifact) |

**Policy comparison and ablation.** The full contract (ownership plus monotonicity) denies all violation events in the corpus. Timestamp-only (monotonicity only) denies fewer and misses split-brain. Ownership-only (no temporal check) misses stale-write and reorder violations. Accept-all would apply all violations. **Ablation by failure class** is reported in eval output (ablation_by_class): per class (split_brain, stale_write, reorder, unknown_key, control), each policy’s violations_denied and violations_missed. This shows that both ownership and temporal checks are required to detect and deny the full set of targeted failure classes.

**Table 2 — Policy and comparator summary (54+ sequence corpus).** Exact counts are in `eval.json` (`ablation`, `baseline_*`); qualitatively, the full contract denies all corpus violations; timestamp/OCC/lease-proxy policies miss **split-brain**; ownership/lock-only misses **stale/reorder**; naive LWW misses all. Comparator implementations are reference proxies: OCC/lease use temporal monotonicity as a proxy for version/lease semantics; lock uses ownership as a proxy for mutex exclusivity. Per-class breakdown in `ablation_by_class` shows which failure classes each policy cannot prevent.

| Policy / comparator | Role | Typical misses on corpus | Notes |
|---------------------|------|---------------------------|-------|
| Full contract | Reference | none | Combines ownership + temporal + reason codes |
| Timestamp-only | Monotonicity only | split_brain | No ownership check |
| Ownership-only | Mutex-style writer/key | stale_write, reorder | No temporal check |
| OCC-only (proxy) | Version/timestamp proxy | split_brain | Approximates OCC conflict domain via timestamps |
| Lease-only (proxy) | Temporal gate proxy | split_brain | Approximates lease validity via monotonicity |
| Lock-only | Ownership mutex proxy | stale_write, reorder | Approximates lock exclusivity via ownership |
| Accept-all / naive LWW | No gate | all violation classes | Accepts all writes |

**Table 3 — Detection metrics by inferred failure class.** Per-event counts and precision/recall/F1 with `expected_verdicts` as ground truth, attributed by sequence name to an inferred class. The **control** row aggregates positive-control sequences: precision/recall/F1 are **n/a** when there are no expected denials and no false denials (TP=FP=FN=0); false denials on controls appear as FP (precision 0). See `eval.json` field `detection_metrics_by_class` and exported Table 3 in `generated_tables.md`.

**Scale and throughput.** Scale-test runs report events per second and per-write latency (mean and stdev over runs). Optional scale sweep (--scale-sweep) runs multiple event counts and writes scale_sweep.json. See Appendix A for run parameters and manifests.

**Async stress robustness.** The artifact `stress_results.json` (from `scripts/contracts_async_stress.py`) tests validator behavior under interleaved event scheduling with configurable delay, clock skew, and reorder stressors. Results show detection correctness is maintained across stress profiles (delay means 0–10ms, clock skew 0–500ms, reorder probabilities 0–20%), demonstrating robustness to realistic concurrency patterns without requiring multi-process deployment.

**Transport-invariance parity.** The artifact `transport_parity.json` records **per-sequence** parity for multiple canonical corpus files: for each sequence, two reference ingestion paths (event-log replay vs. LADS-shaped replay) must yield **identical** verdict and reason-code vectors when boundary events are identical. The parity confidence summary reports matching event counts and parity rate. This supports **implementation consistency** under Proposition 4’s precondition; it does not substitute for live multi-transport deployment but demonstrates boundary semantic equivalence between reference ingestion modes.

---

## 10. Limitations and threats to validity

**Limitations.**

- **Trace-driven with async stress simulation.** The validator and store are exercised on the corpus and reference runner with async stress testing (delay/skew/reorder); there is no integration with a live coordination backend (e.g. OPC UA, LADS) in this version. No live ROS 2/DDS adapter is implemented. The async stress runner simulates realistic concurrency patterns but does not replace multi-process deployment evidence.
- **No full cross-transport deployment.** We illustrate transport-agnostic design with a reference store, LADS-shaped event stream, and boundary parity checks; we do not claim a full cross-transport deployment evaluation with live adapters.
- **Corpus size and synthetic events.** The corpus is a challenge set of 54+ sequences (expanded with cross-key interleaving, delayed release/reassignment, concurrent controller races) partitioned by failure class (Tiers 1–3); events are synthetic. We do not claim evaluation on a live distributed system or under partitions or Byzantine writers.
- **Single-process evaluation with async simulation.** Evaluation is single-process, trace-driven with async event scheduling simulation; no multi-process or network deployment in this version. The async stress runner provides concurrency realism within a single-process harness.

**Threats to validity.**

- **Internal:** Corpus coverage is stratified by failure class but remains synthetic; negative controls and adversarial cases (cross-key interleaving, delayed release, concurrent races) are limited to the defined tiers. Async stress testing expands coverage to delay/skew/reorder patterns but within a simulated harness.
- **Construct:** Metrics (precision, recall, F1, latency percentiles with CI, per-class uncertainty intervals) are defined over the corpus’s expected verdicts and event-level timings; they reflect validator behavior on the benchmark and async stress profiles, not deployment under arbitrary loads or live network conditions.
- **External:** Results do not generalize to live distributed systems, real transports, or Byzantine writers; the contribution is a reproducible coordination layer, benchmark, and stress-testing harness, not an empirical claim about production deployments. The live adapter path (LADS-shaped) demonstrates boundary semantic equivalence but not full cross-transport empirical equivalence.

---

## 11. Conclusion

Coordination Contracts define typed state, writer authority, valid transitions, and temporal admissibility above the messaging layer. A trace-derived validator detects and denies invalid writes in specified failure classes before state application, with bounded per-write overhead on the evaluated workload. The contract model is transport-agnostic by construction; we demonstrate boundary semantics via a reference store, LADS-shaped mapping, and multi-sequence parity checks—not a full cross-transport deployment. **Reusable substrate.** The artifact package (validator, corpus tiers, eval runner, reason codes) is intended as a **portable coordination-admission layer** that future lab and CPS orchestration work can reuse: new transports and adapters normalize to the same boundary events; the contract remains the locus of **auditable deny/allow** independent of middleware choice.

---

## References

- [1] R. G. Smith, "The Contract Net Protocol: High-Level Communication and Control in a Distributed Problem Solver," IEEE Trans. Computers, vol. 29, no. 12, pp. 1104–1113, 1980.
- [2] L. Lamport, Specifying Systems: The TLA+ Language and Tools for Hardware and Software Engineers. Boston, MA, USA: Addison-Wesley, 2002.
- [3] P. A. Bernstein and N. Goodman, "Concurrency Control in Distributed Database Systems," ACM Computing Surveys, vol. 13, no. 2, pp. 185–221, 1981.
- [4] H. Kopetz and G. Bauer, "The Time-Triggered Architecture," Proc. IEEE, vol. 91, no. 1, pp. 112–126, 2003.
- [5] OPC Foundation, OPC UA Part 1: Concepts and Overview.
- [6] M. Leucker and C. Schallhart, "A Brief Account of Runtime Verification," J. Logic and Algebraic Programming, vol. 78, no. 5, pp. 293–303, 2009.

---

## Claims and backing

| Claim | Evidence |
|-------|----------|
| C1 (Detect and deny failure classes) | Table 1; Tables 2–3; Section 3 (novelty boundary); Section 8–9; `eval.json`. |
| C2 (Validation from traces) | Section 4 (trace-derivability, Props. 2 and 5 sketch); Section 5; `docs/P1_TRACE_DERIVABILITY.md`. |
| C3 (Transport-agnostic by construction) | Section 4 (Proposition 4); Section 6 (mapping + modest parity); `transport_parity.json`. |
| C4 (Bounded overhead) | Table 1; `scale_test.json`; Section 9. |

---

## Appendix A. Artifact and reproducibility

**Environment.** From repository root, set `PYTHONPATH=impl/src` and `LABTRUST_KERNEL_DIR=kernel`. See project docs for reporting standard and result locations.

**Minimal run (under 20 min).** Run: corpus evaluation script to produce eval output; export script for corpus table; export script for contract flow figure; scale/throughput plot script. Optional: async stress runner (`scripts/contracts_async_stress.py`) and transport parity (`scripts/contracts_transport_parity.py`). Outputs: eval.json (corpus_sequences, corpus_dir, script, detection_metrics_by_class, excellence_metrics); scale_test.json for throughput figure; optional stress_results.json and transport_parity.json.

**Publishable run.** Include scale test with specified event count and multiple runs for variance. Run manifest is recorded in eval.json and scale_test.json.

**Figure 0 (contract validation flow).** Produced by export script; render Mermaid to PNG for camera-ready.

**Table 1.** Source: eval.json from corpus evaluation run. Regenerate via corpus evaluation script then corpus table export script.

**Table 2.** Policy comparison from same eval run; fields violations_denied_with_validator, baseline_*_denials, baseline_*_missed in eval.json. Ablation and ablation_by_class include all comparator policies (occ_only, lease_only, lock_only, naive_lww). Regenerate via corpus evaluation script (ablation always present; --baseline adds violations_would_apply_without_validator only).

**Figure 1 (scale throughput).** Produced by scale plot script; run manifest in scale_test.json.

**Corpus.** Challenge corpus of 54+ sequences (expanded with cross-key interleaving, delayed release/reassignment, concurrent controller races) in JSON format: description, initial_state (ownership, _last_ts), events (type, ts, actor, payload), expected_verdicts. Reference runner discovers all corpus JSON files; schema and benchmark spec (tiered: micro, meso, stress/adversarial) are in the artifact. Ground-truth labeling and anti-circularity protocol documented in `bench/contracts/BENCHMARK_SPEC.v0.1.md`.

**Eval output fields.** eval.json includes: run_manifest (script_version, corpus_fingerprint, corpus_sequence_count), detection_metrics (TP, FP, FN, precision, recall, F1), detection_metrics_by_class (with per-class uncertainty intervals in excellence_metrics.per_class_ci95), latency_percentiles_us (median, p95, p99, event_level_n, median_ci95, p95_ci95, p99_ci95), ablation (full contract, timestamp_only, ownership_only, occ_only, lease_only, lock_only, accept_all, naive_lww), ablation_by_class, excellence_metrics (corpus_detection_rate_pct, overhead_p99_us, baseline_margin_denials, split_brain_detection_advantage, per_class_ci95), resource_and_cost (wall_clock_sec, events_per_sec_overall, cost_proxy). Scale sweep: --scale-sweep 1000,10000,100000 writes scale_sweep.json. Async stress: `scripts/contracts_async_stress.py` writes stress_results.json with delay/skew/reorder sweep results. Transport parity: `scripts/contracts_transport_parity.py` writes transport_parity.json with per_sequence[], parity_ok_all, and parity_confidence (matching_events, total_events_checked, parity_rate).

**Submission note.** For submission, tables must be produced from a run where eval.json has run_manifest and success_criteria_met.all_detection_ok true (or equivalent). The draft tables are from such a run.
