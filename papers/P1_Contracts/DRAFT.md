# Coordination Contracts: Typed State, Ownership, and Valid Transitions Above Messaging for Cyber-Physical Systems

**Draft (v0.2).**

## Abstract

In cyber-physical systems, message delivery is not the same as coordination. A distributed workflow may successfully exchange messages while still admitting stale writes, conflicting ownership claims, orphaned authority, or unsafe last-write-wins behavior. We propose Coordination Contracts, a transport-agnostic contract layer for shared CPS state that defines typed state, writer authority, valid transitions, and temporal admissibility above the messaging substrate. The core design principle is trace-derivability: validation must be executable from event traces plus declared configuration alone, without privileged hidden state. This property makes contract enforcement auditable and supports replay-based debugging. We present a pure-function validator, a contract-enforcing reference store, and a challenge corpus of coordination failure scenarios. On this corpus, the validator detects and denies the targeted invalid-write classes while adding bounded per-write overhead. We also show how the contract surface maps to laboratory automation state semantics through an OPC UA LADS-aligned event model, illustrating portability above transport. The current paper does not claim full cross-transport deployment or live distributed evaluation; rather, it establishes a precise, reproducible coordination layer that separates communication from authority and makes invalid coordination explicit at the level of state transitions.

---

## 1. Introduction

In CPS, "communication is not coordination." Messaging does not imply authority. A minimal contract layer makes coordination pathologies explicit as invalid state transitions and allows a validator to detect and deny them before application. For a declared contract model and trace-derived validator, invalid writes belonging to a specified failure class are detected and denied before state application. We need contracts for shared state ownership, valid transitions, time semantics, and conflict resolution so that coordination is auditable and replayable.

---

## 2. Problem setting and failure model

**Failure classes.** We target coordination pathologies that arise when multiple writers or delayed delivery affect shared keyed state:

- **Split-brain ownership:** Two writers believe they own the same key; both attempt to write. Detected when an event claims to write a key that is owned by another writer in state and no handover is defined.
- **Stale write:** A write is accepted that is based on an outdated view of state. Detected when event timestamp or sequence is before the last update for that key and the contract requires monotonicity.
- **Unsafe last-write-wins under delay/reorder:** Messages are reordered; a later write (by wall clock) is applied after an earlier one, violating intended ordering. Detected when conflict semantics require ordering and event order is violated.

**Assumptions.** We state explicitly: (i) writer identity is as given in the trace (no Byzantine or spoofed writers in the evaluated model); (ii) lease and ordering semantics are defined in the declared configuration; (iii) validation is applied before state application; (iv) we do not claim prevention in live distributed deployment, under partitions, or with Byzantine writers—only that the validator detects and denies the specified failure classes on the event stream and state as defined.

---

## 3. Related work and positioning

**Distributed coordination and concurrency.** Contract Net [1] and TLA+ [2] address protocol-level coordination and specification. We contribute a concrete contract layer over keyed state with trace-derived validation rather than consensus or full protocol verification.

**State-machine and formal specification.** Formal methods and state-machine correctness (e.g. LADS device state machines) provide semantics for single components. Our contract layer defines valid transitions and authority at the boundary of shared state, above transport.

**Transport substrates: ROS 2/DDS and event logs.** ROS 2 and DDS provide transport, discovery, and QoS but not a portable authority model for keyed shared state. Event-log architectures (e.g. Kafka-style) preserve ordered records and, with compaction, retain the latest value per key, but they do not by themselves decide whether a write was valid.

**Industrial interoperability: OPC UA LADS.** OPC UA LADS provides semantically rich laboratory device and FunctionalUnit state machines, which are highly relevant for interoperation. LADS does not, however, provide a generic contract semantics for write authority and conflict handling across heterogeneous controllers.

**Positioning.** This paper sits above all three: we add a contract layer for valid writes and authority, defined over event/state semantics, so that coordination pathologies become explicit invalid state transitions that a validator can detect and deny before application.

---

## 4. Coordination contract model

We give explicit definitions so the semantics are extractable from the manuscript.

**Contract state.** Let \(S\) denote the contract state for a keyed resource graph. For each key \(k\), the state includes (i) a typed value \(v_k\), (ii) an ownership record \(o_k\), (iii) a version or logical time summary \(\tau_k\) (e.g. last accepted write time), and (iv) optional lease metadata \(\ell_k\). The implementation maintains at least `ownership` (key to writer) and `_last_ts` (key to last accepted timestamp).

**Events.** An event \(e\) is a tuple \((k, a, w, t_e, t_p, \sigma, \Delta)\): target key \(k\), action type \(a\), claimed writer identity \(w\), event time \(t_e\), processing time \(t_p\), ordering token or sequence number \(\sigma\), and proposed state update payload \(\Delta\). In the reference implementation these appear as `type`, `ts`, `actor`/`payload.writer`, and `payload` with `task_id` (key).

**Declared configuration.** \(C\) is the contract configuration (e.g. conflict semantics, use of instrument state machine). The validator is parameterized by \(C\); no hidden state is required beyond what is in the trace and \(C\).

**Ownership and authority scope.** The owner of key \(k\) in state \(S\) is \(o_k\). Writer \(w\) is authorized for key \(k\) iff \(w = o_k\) or the contract defines an admissible handover. Lease validity, when present, is evaluated from \(\ell_k\) and the current time or sequence.

**Valid transition predicate.** A transition \((S, e) \rightarrow S'\) is valid iff: type validity holds for the payload, the writer has authority for the affected key(s), lease validity holds when required, temporal admissibility holds (e.g. \(t_e \geq \tau_k\) for monotonicity), and the transition is admissible under the contract (e.g. allowed state-machine edge).

**Temporal order relation.** For monotonicity we require event time not to go backward per key: \(t_e \geq \tau_k\) where \(\tau_k\) is the last accepted write time for key \(k\). Violations yield reason codes such as `stale_write` and `reorder_violation`.

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

---

## 5. Validator semantics and properties

The reference validator implements \(V_C(S, e)\) as a pure function: it returns allow or deny and a set of reason codes. It uses no privileged hidden state; all predicates are computed from the trace-derived state and the event. The contract-enforcing store applies a write only when the validator returns allow, giving one validation per write and bounded overhead.

---

## 6. Interoperability mapping to LADS

OPC UA LADS state machine edges map to contract valid transitions; FunctionalUnit key ownership and timestamps map to contract state. The concrete mapping covers: FU key ownership (key from device/FU id, owner from controller); LADS edges to contract event types (e.g. task_start, task_end); and timestamps (_last_ts monotonicity, stale_write detection).

The contract surface is transport-agnostic by construction because it is defined over state/event semantics rather than transport behavior. We illustrate this with a LADS-shaped event stream and an event-log (reference store) implementation; we do not yet provide a full cross-transport deployment evaluation. A mock LADS path runs the same validator on a LADS-equivalent event stream; a live OPC UA or ROS 2 adapter would emit the same event shape and call the same validator.

---

## 7. Reference implementation

The validator is a pure function over state and event; the contract-enforcing store applies writes only when the validator allows. Evaluation uses a challenge corpus of sequences and a reference runner that reports verdicts, reason codes, detection agreement with expected verdicts, and per-write overhead. Artifact and reproduction instructions are in Appendix A.

---

## 8. Experimental design

**Hypothesis.** The contract validator detects and denies invalid writes corresponding to the specified failure classes (split-brain, stale write, reorder violation) from trace events.

**Metrics.** Verdict (allow/deny), reason codes, detection agreement with expected verdicts; true positive rate, false positive rate, false negative count; precision and recall by failure class; median, p95, p99 validation latency; throughput with confidence intervals; overhead as function of event count.

**Baselines.** We compare: accept-all; timestamp-only (monotonicity only, no ownership); lease-only (if in scope); version/OCC-only (if in scope); last-write-wins; full contract validator.

**Corpus.** The challenge corpus includes sequences partitioned by failure class, with positive and negative controls (e.g. good sequences, split-brain same-epoch and after lease expiry, stale write under clock skew and delayed delivery, reorder with and without violation, duplicate delivery, same-timestamp tie cases). See Appendix A for corpus location and schema.

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

**Table 2 — Policy comparison.** Violations denied vs missed (51+ sequence corpus).

| Policy                            | Violations denied | Violations missed (would apply) |
|-----------------------------------|-------------------|----------------------------------|
| Contract (ownership + monotonicity) | all               | 0                                |
| Timestamp-only (monotonicity only)  | partial           | split_brain                      |
| Ownership-only (no temporal)       | partial           | stale/reorder                    |
| Accept-all                        | 0                 | all                              |

**Scale and throughput.** Scale-test runs report events per second and per-write latency (mean and stdev over runs). Optional scale sweep (--scale-sweep) runs multiple event counts and writes scale_sweep.json. See Appendix A for run parameters and manifests.

**Transport-invariance parity.** A parity experiment runs the same canonical event stream through the reference store (event-log path) and records verdict and reason-code vectors; the same stream is processed in LADS-shaped style. The artifact transport_parity.json records parity_ok when the two outcome vectors are identical, supporting Proposition 4 (transport invariance) at the contract boundary.

---

## 10. Limitations and threats to validity

**Limitations.**

- **Trace-driven only.** The validator and store are exercised on the corpus and reference runner; there is no integration with a live coordination backend (e.g. OPC UA, LADS) in this version. No live ROS 2/DDS adapter is implemented.
- **No full cross-transport deployment.** We illustrate transport-agnostic design with a reference store and LADS-shaped event stream; we do not claim a full cross-transport deployment evaluation.
- **Corpus size and synthetic events.** The corpus is a challenge set of 51+ sequences partitioned by failure class (Tiers 1–3); events are synthetic. We do not claim evaluation on a live distributed system or under partitions or Byzantine writers.
- **Single-process evaluation.** Evaluation is single-process, trace-driven; no multi-process or network deployment in this version.

**Threats to validity.**

- **Internal:** Corpus coverage is stratified by failure class but remains synthetic; negative controls and adversarial cases are limited to the defined tiers.
- **Construct:** Metrics (precision, recall, F1, latency percentiles with CI) are defined over the corpus’s expected verdicts and event-level timings; they reflect validator behavior on the benchmark, not deployment under arbitrary loads.
- **External:** Results do not generalize to live distributed systems, real transports, or Byzantine writers; the contribution is a reproducible coordination layer and benchmark, not an empirical claim about production deployments.

---

## 11. Conclusion

Coordination Contracts define typed state, writer authority, valid transitions, and temporal admissibility above the messaging layer. A trace-derived validator detects and denies invalid writes in specified failure classes before state application, with bounded per-write overhead. The contract model is transport-agnostic by construction; we demonstrate this via a reference store and a LADS-aligned event mapping, not a full cross-transport deployment. The contribution is a precise, reproducible coordination layer that makes invalid coordination explicit at the level of state transitions.

---

## References

- [1] R. G. Smith, "The Contract Net Protocol: High-Level Communication and Control in a Distributed Problem Solver," IEEE Trans. Computers, vol. 29, no. 12, pp. 1104–1113, 1980.
- [2] L. Lamport, Specifying Systems: The TLA+ Language and Tools for Hardware and Software Engineers. Boston, MA, USA: Addison-Wesley, 2002.

---

## Claims and backing

| Claim | Evidence |
|-------|----------|
| C1 (Detect and deny failure classes) | Table 1 (corpus verdicts); Table 2 (vs timestamp-only and accept-all); Section 8–9. |
| C2 (Validation from traces) | Section 4 (trace-derivability); Section 5; corpus driver and artifact. |
| C3 (Transport-agnostic by construction) | Section 4 (Proposition 4); Section 6 (LADS mapping and reference store); no full cross-transport claim. |
| C4 (Bounded overhead) | Table 1 (time_per_write_us); scale-test results; Section 9. |

---

## Appendix A. Artifact and reproducibility

**Environment.** From repository root, set `PYTHONPATH=impl/src` and `LABTRUST_KERNEL_DIR=kernel`. See project docs for reporting standard and result locations.

**Minimal run (under 20 min).** Run: corpus evaluation script to produce eval output; export script for corpus table; export script for contract flow figure; scale/throughput plot script. Outputs: eval.json (corpus_sequences, corpus_dir, script); scale_test.json for throughput figure.

**Publishable run.** Include scale test with specified event count and multiple runs for variance. Run manifest is recorded in eval.json and scale_test.json.

**Figure 0 (contract validation flow).** Produced by export script; render Mermaid to PNG for camera-ready.

**Table 1.** Source: eval.json from corpus evaluation run. Regenerate via corpus evaluation script then corpus table export script.

**Table 2.** Policy comparison from same eval run; fields violations_denied_with_validator, baseline_timestamp_only_denials, baseline_timestamp_only_missed in eval.json. Regenerate with baseline flag.

**Figure 1 (scale throughput).** Produced by scale plot script; run manifest in scale_test.json.

**Corpus.** Challenge corpus of 51+ sequences in JSON format: description, initial_state (ownership, _last_ts), events (type, ts, actor, payload), expected_verdicts. Reference runner discovers all corpus JSON files; schema and benchmark spec (tiered: micro, meso, stress/adversarial) are in the artifact.

**Eval output fields.** eval.json includes: run_manifest (script_version, corpus_fingerprint, corpus_sequence_count), detection_metrics (TP, FP, FN, precision, recall, F1), latency_percentiles_us (median, p95, p99, event_level_n, median_ci95, p95_ci95, p99_ci95), ablation, ablation_by_class, resource_and_cost (wall_clock_sec, events_per_sec_overall, cost_proxy). Scale sweep: --scale-sweep 1000,10000,100000 writes scale_sweep.json. Transport parity: scripts/contracts_transport_parity.py writes transport_parity.json (parity_ok).

**Submission note.** For submission, tables must be produced from a run where eval.json has run_manifest and success_criteria_met.all_detection_ok true (or equivalent). The draft tables are from such a run.
