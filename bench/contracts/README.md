# P1 Coordination Contracts

Corpus under `corpus/`: 51+ sequences (tiered: micro, meso, stress/adversarial—positive controls, split-brain, stale write/reorder, boundary, long-horizon, adversarial). Eval: `scripts/contracts_eval.py` iterates over all JSON files in corpus; add new sequences with the same schema (description, initial_state, events, expected_verdicts).

## Benchmark

The corpus is released as **Coordination Contract Benchmark v0.1**. See [BENCHMARK_SPEC.v0.1.md](BENCHMARK_SPEC.v0.1.md) for the full spec: N=51+ sequences, tiered protocol (Tier 1 micro, Tier 2 meso, Tier 3 stress/adversarial), failure classes (split_brain, stale_write, reorder_violation, unknown_key, control), schema, discovery rule, and version. Reference runner: `scripts/contracts_eval.py` (use `--baseline` for policy comparison and ablation). Reference table: `scripts/export_contracts_corpus_table.py`. Scale sweep: `--scale-sweep 1000,10000,100000`. Transport parity: `scripts/contracts_transport_parity.py` writes `transport_parity.json`.

## Corpus expansion

- **Schema:** Each corpus file is JSON with: `description` (string), `initial_state` (object: ownership, _last_ts, etc.), `events` (array of event objects with type, ts, actor, payload), `expected_verdicts` (array of "allow"|"deny", length = events.length).
- **How to add:** Add a new `.json` file under `corpus/` with the same schema. The eval discovers all `*.json` in the corpus dir via `sorted(args.corpus.glob("*.json"))`.
- **Contribution checklist:** One failure class per sequence (e.g. split_brain, stale_write); ensure `expected_verdicts.length == events.length`; document the scenario in `description`.
- **Generator:** `python scripts/generate_contract_corpus.py --writers W --tasks T [--out path]` produces one corpus JSON (N-writer contention: first allow, rest deny per task). Default output: `bench/contracts/corpus/gen_Wwriter_Ttask.json`.

**Lab-aligned state machine:** Contract type "single-writer per task" / "no transition from running without task_end" is aligned with the minimal instrument state machine in `impl/src/labtrust_portfolio/instrument_state_machine.py`. States: idle, running, calibration, cleaning. Transitions: task_start only from idle to running; task_end only from running to idle. Validator remains pure (state + event + declared config); set contract `use_instrument_state_machine: true` to enforce the same rule via the state machine.

**Trace-derivability:** All contract predicates are computed from trace alone (no privileged hidden state). Predicate-to-trace-field mapping: `docs/P1_TRACE_DERIVABILITY.md`. Tables/figures: `scripts/export_contracts_corpus_table.py`, `scripts/plot_contracts_scale.py`.
