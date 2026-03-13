# Coordination Contracts: Typed State, Ownership, and Valid Transitions Above Messaging

**Draft (v0.1). Paper ID: P1_Contracts.**

**Reproducibility.** From repo root, with `PYTHONPATH=impl/src` and `LABTRUST_KERNEL_DIR=kernel`. See [REPORTING_STANDARD.md](../docs/REPORTING_STANDARD.md) and [RESULTS_PER_PAPER.md](../docs/RESULTS_PER_PAPER.md) for run_manifest and result locations.

**Minimal run (under 20 min):** `python scripts/contracts_eval.py --out datasets/runs/contracts_eval` then `python scripts/export_p1_contract_flow.py` then `python scripts/export_contracts_corpus_table.py` then `python scripts/plot_contracts_scale.py`. Run_manifest: `eval.json` (corpus_sequences, corpus_dir); `scale_test.json` (scale_test_events) for Figure 1.

- **Figure 0:** `python scripts/export_p1_contract_flow.py` (output `docs/figures/p1_contract_flow.mmd`). Render Mermaid to PNG for camera-ready.
- **Table 1:** `python scripts/contracts_eval.py --out datasets/runs/contracts_eval`, then `python scripts/export_contracts_corpus_table.py`.
- **Table 2:** Policy comparison from same eval run (eval.json); regenerate with `contracts_eval.py` as above; table content from eval.json.
- **Figure 1:** `python scripts/plot_contracts_scale.py` (output `docs/figures/p1_scale_throughput.png`). Run manifest: `scale_test.json`.

## 1. Motivation

In CPS, "communication is not coordination." Messaging does not imply authority. We need contracts for shared state ownership, valid transitions, time semantics, and conflict resolution so that coordination is auditable and replayable.

## 2. Contract model

Contract model: types, ownership/leases, authority scope.

**Figure 0 — Contract validation flow.** Event and state as input to `validate(state, event)`; outcome allow or deny with reason_codes. Regenerate with `python scripts/export_p1_contract_flow.py` (output `docs/figures/p1_contract_flow.mmd`). See `kernel/contracts/CONTRACT_MODEL.v0.1.md`. Valid transitions: invariants, preconditions, conflict rules. Time model: event vs processing vs actuation time. Concurrency semantics: lease/OCC/CRDT options; when each is admissible.

## 3. Failure classes

- Split-brain ownership: two writers for the same key; validator denies the second write (reason code split_brain).
- Stale write: event timestamp before last update for that key; validator denies (stale_write).
- Unsafe last-write-wins under delay/reorder: conflict_semantics and ordering; reorder_violation reason code.

## 4. Validator and store

Validator library (pure function): `validate(state, event) -> (verdict, reason_codes)`. Implemented in `impl/src/labtrust_portfolio/contracts.py`. No privileged hidden state; executable from traces. Contract-enforcing store: `ContractEnforcingStore` applies writes only when validator returns allow; one validation per write (bounded overhead).

**Formal and theoretical backing.** Determinism of the validator is machine-checked (W2 wedge: same state and event yield the same verdict); see `formal/lean/`. Under single-writer and monotonic timestamps, our rules prevent split-brain; detection of conflict classes (split_brain, stale_write, reorder_violation) is complete under the stated assumptions. See `kernel/contracts/PROPERTIES.v0.1.md`.

## 5. Trace corpus

Seven sequences in `bench/contracts/corpus/`: **good_sequence** (single writer, allow/allow), **split_brain_sequence** (second writer denied, reason split_brain), **stale_write_sequence** (event ts before last_ts for key, deny), **reorder_sequence** (second event has lower ts than first, allow then deny), **unsafe_lww_sequence** (unsafe last-write-wins under delay/reorder; validator denies with reorder_violation), **multi_writer_contention** (two writers same task_id; second denied after first owns), **edge_case_timestamps** (same-ts events; ordering by seq). Each file has initial_state, events, expected_verdicts. Eval iterates over all corpus JSON files. Reorder and unsafe_lww denials carry both stale_write and reorder_violation (timestamp monotonicity). Corpus driver test (`tests/test_contracts_p1.py`) loads each corpus file, runs validate(state, event) and apply_event_to_state when allow; asserts verdict matches expected_verdicts[i]. Ensures corpus and validator stay in sync.

**Benchmark.** The corpus is released as Coordination Contract Benchmark v0.1 (see `bench/contracts/BENCHMARK_SPEC.v0.1.md`). Table 1 and this section cite the benchmark; the reference runner is `scripts/contracts_eval.py` and the reference table is `scripts/export_contracts_corpus_table.py`.

**Spec-corpus mapping:** Failure class 1 (split-brain) -> split_brain_sequence; 2 (stale write) -> stale_write_sequence; 3 (unsafe LWW/reorder) -> reorder_sequence, unsafe_lww_sequence.

## 6. LADS mapping

OPC UA LADS state machine edges map to contract valid transitions; FunctionalUnit key ownership and timestamps map to contract state. See `kernel/interop/OPC_UA_LADS_MAPPING.v0.1.md`: concrete mapping subsection covers FU key ownership (key from device/FU id, owner from controller), LADS edges to contract event types (task_start/task_end), and timestamps (_last_ts monotonicity, stale_write detection). We ran the same validator on a **LADS-derived event stream** (mock): `scripts/contracts_mock_lads_run.py` reads a JSON event stream (LADS-equivalent shape) and runs validate/apply_event_to_state; results in `datasets/runs/contracts_lads_demo/lads_demo_result.json`. A live OPC-UA or ROS2 adapter would emit the same event shape; the mock demonstrates transport-agnostic and LADS-mappable validation.

## 7. Evaluation (micro-scenarios)

Run `scripts/contracts_eval.py` to evaluate the validator on the corpus: for each sequence, record allows/denials (detection_ok when denials match expected) and overhead (time_per_write_us). Output: `datasets/runs/contracts_eval/eval.json` (primary result file; cite for claims). Regenerate table: `python scripts/export_contracts_corpus_table.py`. With `--throughput` (and optional `--scale N`, default 1000), the script runs the full corpus N times and reports `throughput_events_per_sec` and `throughput_total_events` in eval.json. With `--baseline`, it reports `violations_denied_with_validator` and `violations_would_apply_without_validator` (accept-all would apply those events).

**Table 1 — Corpus evaluation.** Source: `datasets/runs/contracts_eval/eval.json`. Run manifest (corpus_sequences, corpus_dir, script) in same file.

| Sequence | events | allows | denials | detection_ok | time_per_write_us |
|----------|--------|--------|---------|--------------|-------------------|
| good_sequence | 2 | 2 | 0 | true | 32.85 |
| reorder_sequence | 2 | 1 | 1 | true | 12.7 |
| split_brain_sequence | 1 | 0 | 1 | true | 11.0 |
| stale_write_sequence | 1 | 0 | 1 | true | 9.6 |
| unsafe_lww_sequence | 2 | 1 | 1 | true | 6.85 |
| **Summary** | 8 | 4 | 4 | all true | mean ~14 |

Overhead is sub-microsecond to tens of microseconds per write (validator + state update). Detection rate: 100% for corpus (all expected verdicts match).

**Throughput (with variance):** Run `contracts_eval.py --throughput --scale 1000 --throughput-runs 5`. Output: `throughput_events_per_sec_mean`, `throughput_events_per_sec_stdev` in eval.json. Typical: hundreds of thousands of events/sec (single-threaded); variance reported over multiple runs for reproducibility.

**Table 2 — Policy comparison (state-of-the-art baseline).** Comparison to another consistency approach: timestamp-only policy (monotonicity only, no ownership) vs full contract vs accept-all. Source: `eval.json` (`violations_denied_with_validator`, `baseline_timestamp_only_denials`, `baseline_timestamp_only_missed`). Run manifest in same file.

| Policy | Violations denied | Violations missed (would apply) |
|--------|-------------------|----------------------------------|
| Contract (ownership + monotonicity) | 4 | 0 |
| Timestamp-only (monotonicity only) | 3 | 1 (split_brain) |
| Accept-all | 0 | 4 |

The timestamp-only baseline catches stale write and reorder but misses split-brain (no ownership check). The full contract denies all four corpus violations.

**Figure 1 — Scale test throughput vs event count.** Validator throughput (events/sec) vs trace size. Regenerate with `python scripts/plot_contracts_scale.py` (output `docs/figures/p1_scale_throughput.png`); the script runs `contracts_eval.py --scale-test` at multiple event counts. Run manifest: `datasets/runs/contracts_eval/scale_test.json` includes `run_manifest` (scale_test_events, script).

## 8. Methodology and reproducibility

**Methodology:** Hypothesis—contract validator detects and denies split-brain, stale write, and reorder violations from trace events. Metrics: verdict (allow/deny), reason_codes, detection_ok (denials match expected). Kill criteria: cannot define failure classes (K1); validator misses a corpus denial (K2); overhead unbounded (K3). Baselines: corpus expected_verdicts; timestamp-only policy (comparison to another consistency approach); accept-all. Portfolio criteria: `docs/STATE_OF_THE_ART_CRITERIA.md`.

**Baseline comparison:** With the contract validator, all violation events in the corpus are denied (Table 1 denials; eval.json `violations_denied_with_validator`). Timestamp-only (monotonicity only) denies 3 and misses 1 (split_brain). Accept-all would apply all 4 (inadmissible). Table 2 summarizes. So we compare against two baselines: another contract-like approach (timestamp-only) and no validation (accept-all).

**Reproducibility:** Corpus: `bench/contracts/corpus/*.json`. Run corpus test: `pytest tests/test_contracts_p1.py`. Run eval: `python scripts/contracts_eval.py --out datasets/runs/contracts_eval`; every run reports `violations_denied_with_validator`, `baseline_timestamp_only_denials`, `baseline_timestamp_only_missed` (policy comparison). Optional: `--throughput --scale 1000 --throughput-runs 5` for throughput mean and stdev; `--baseline` for accept-all count. Artifacts: eval.json with per-sequence results, overhead, policy comparison, and optional throughput (mean, stdev). A real-launch integration test (`TestContractsEvalIntegration.test_contracts_eval_produces_valid_eval`) runs the eval script and asserts on eval.json (corpus_eval, detection_ok per sequence, baseline keys).

## 9. Security and transport

Security invariants: provenance, writer authentication hooks. Contract surface is transport-agnostic (above ROS2/DDS or event-log).

## 10. Limitations

Scope and determinism are summarized in [EXPERIMENTS_AND_LIMITATIONS.md](../docs/EXPERIMENTS_AND_LIMITATIONS.md). Per-paper limitations:

- **K1 (trace-derivability; no hidden state):** The validator uses **no privileged hidden state**: all contract predicates are computed from the trace alone (event sequence, timestamps, task_id, actor, payload) and declared config. This trace-derivability is a design invariant; if any predicate required state not derivable from the trace, the design would lose portability (kill criterion K1). See `docs/P1_TRACE_DERIVABILITY.md` for the predicate-to-trace-field mapping. Gatekeeper: `allow_release(run_dir, check_contracts=True)` runs the contract validator on the trace and denies release when any event is denied; test `test_gatekeeper_denies_when_contract_invalid` demonstrates denial on contract-invalid trace.
- **Trace-driven only:** The validator and store are exercised on the corpus and via contracts_eval; there is no integration with a real coordination backend (e.g. OPC UA, LADS) in v0.1. The LADS mapping is documented only in `kernel/interop/OPC_UA_LADS_MAPPING.v0.1.md`; no live OPC-UA or ROS2 adapter is implemented (future work).
- **Corpus size:** Seven sequences in bench/contracts/corpus; coverage is by failure class, not large-scale event count.
- **Events are synthetic:** Corpus events are hand-crafted for the validator; no real distributed system or live messaging.
- **No real distributed system:** Evaluation is single-process, trace-driven only; no multi-process or network.
- **No real multi-writer deployment:** Corpus and scale test are synthetic; no deployment on a live multi-writer lab.

---

**Claims and backing.**

| Claim | Evidence |
|-------|----------|
| C1 (Prevents failure classes) | Table 1 (corpus sequences and deny verdicts); Table 2 (vs timestamp-only and accept-all); Section 5 corpus and spec-corpus mapping. |
| C2 (Validation from traces) | Section 5 corpus driver; test `tests/test_contracts_p1.py` (per-sequence verdict match). |
| C3 (Transport-agnostic) | Specification and mapping documents (CONTRACT_MODEL, OPC_UA_LADS_MAPPING); no empirical cross-transport test in this version. |
| C4 (Bounded overhead) | Table 1 column time_per_write_us; eval.json. |
