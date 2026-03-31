# P1 formal alignment: Lean wedge vs Python vs prose

This memo scopes what the repository’s formal artifact proves, what the implementation guarantees, and which manuscript claims may cite the formalization without over-stating coverage.

## Lean (`formal/lean/Labtrust/W2Contract.lean`)

**Model.** A deliberately minimal state (`owner`, `lastTs` per key) and event (`taskId`, `ts`, `writer`) with a simplified `validate` / `replayStep` / `applyAllowed` that mirrors a **subset** of the coordination story (ownership + strict timestamp regression as denial).

**Theorems present (exact names).**

| Theorem | Statement (informal) |
|---------|----------------------|
| `validate_deterministic` | `validate s e = validate s e` (reflexivity placeholder for purity) |
| `validate_congr` | Equal state and event imply equal verdict |
| `denied_no_state_change` | If `validate s e = deny`, then `replayStep s e = s` |
| `admitted_preserves_owner` | After an admitted step, owner at the key matches the writer |
| `admitted_preserves_lastTs` | After an admitted step, `lastTs` at the key equals the event timestamp |
| `replay_verdict_deterministic` | Same as deterministic stub on verdict |
| `replay_reproducibility` | `s1 = s2` and `e1 = e2` implies equal `validate` outcomes |

**Explicitly not proved in Lean (commented future work).** Full **invariant preservation** along admitted prefixes (general monotonicity and owner consistency across multi-step traces) matching the full Python reference semantics and reason-code taxonomy.

## Python (`impl/src/labtrust_portfolio/contracts.py`)

**Implemented and used in evaluation.**

- Full boundary validator: `validate(state, event, contract=None) -> ContractVerdict` with **reason codes** including `split_brain`, `stale_write`, `reorder_violation`, `unknown_key` (and optional instrument state machine hook).
- **Replay discipline (eval-facing):** `prepare_replay_state` seeds `_observed_ts_max` from committed `_last_ts` and handover ledgers; after each event (allow or deny), drivers call `finalize_event_observation` so trace-order monotonicity is enforced against observed timestamps, not only against applied state.
- **Declared key scope (quasi-real):** `build_contract_config_from_trace` supplies `allowed_keys` from `datasets/contracts_real/evaluation_scope.json` (family allowlist) plus `scenario_family_id` and initial-state keys — **not** from gold verdicts or annotation `failure_class` (see `datasets/contracts_real/EVALUATION_INDEPENDENCE_P1.md`).
- **Handover contention:** non-owner `task_start` paired with a subsequent owner `task_end` can yield `split_brain` via `_non_owner_task_start_pending` (replay-internal ledger).
- `apply_event_to_state` for replay state update on admitted writes.
- Semantics are **richer** than the Lean wedge (multiple denial reasons, configuration, observation ordering, payload/actor normalization assumptions as exercised by `scripts/contracts_eval.py`).

**Test / eval grounding.** Quasi-real and bench metrics are properties of this Python kernel plus trace gold labels, not of the Lean file.

## Lean vs upgraded Python (what is still not formalized)

The Lean wedge still models only a **subset** of the Python kernel: per-key owner and last committed timestamp with denial on strict timestamp regression. It does **not** currently capture:

- declared `allowed_keys` / family allowlists from `evaluation_scope.json`,
- `_observed_ts_max` trace-order monotonicity,
- `_non_owner_task_start_pending` handover contention,
- the full reason-code bundle ordering or deduplication behavior.

**Safe manuscript claims** remain: Lean supports *determinism-style* and *denied-step state discipline* statements **in the simplified model**; **F1, recall, class-level recall, B5 comparisons, and external corpus numbers** stay empirical and must cite Python eval outputs (`datasets/runs/...`), not Lean.

## Prose-only (typical paper material)

- Operational interpretation of traces, case-study narrative, and external validity of `datasets/contracts_real`.
- Claims that require **deployment**, **live transport**, or **third-party system** behavior unless backed by a named artifact (e.g. parity harness scope in `claims.yaml` C3).

## Safe linkage from manuscript claims to Lean

| Claim style | Safe? |
|-------------|--------|
| “Replay is deterministic given equal normalized state and event” (kernel-scoped) | Yes, point to `replay_reproducibility` / `validate_congr` with **explicit** “simplified model” caveat |
| “Denied events do not mutate replay state” | Yes, in the **Lean model** via `denied_no_state_change`; Python matches this pattern for `replayStep`-style loops in eval |
| “Full contract reason-code completeness / split-brain policy matches production” | **No** — cite Python + tests; Lean does not encode reason codes |
| “External corpus F1 / recall” | **No** — empirical; cite `datasets/runs/...` eval outputs |

**Bottom line.** The Lean artifact is **supportive**: it anchors replay discipline and determinism in a checked model. The **definitive** operational semantics for P1 empirical claims remain **`contracts.py` + trace eval**, until the formalization is extended to the full reason-coded kernel.
