# P1 evaluation independence (contracts_real_v1)

This memo documents configuration inputs for the **submission-grade** P1 quasi-real evaluation. It is intended for an appendix or dataset governance cross-reference.

## Principle

Scoring uses `expected_verdicts` and `annotations` **only** as held-out labels. **No field of the contract configuration** is derived from gold deny/allow verdicts, from annotation `failure_class`, or from rules that peek at which events are labeled `unknown_key`.

## Inputs used for `allowed_keys` (non-gold)

| Input | Source file / field | Available before scoring? | Uses gold? |
|-------|----------------------|---------------------------|------------|
| Family allowlist | `datasets/contracts_real/evaluation_scope.json` → `family_declared_keys[<family_id>]` | Yes (versioned artifact) | **No** |
| Trace family id | Each trace JSON → `scenario_family_id` (dataset metadata; mirrors directory family) | Yes | **No** |
| Initial-state keys | `initial_state.ownership`, `initial_state._last_ts` | Yes | **No** |

The validator computes:

`allowed_keys = family_declared_keys[scenario_family_id] ∪ keys(initial_state.ownership) ∪ keys(initial_state._last_ts)`.

## What is *not* used for configuration

- `expected_verdicts`
- `annotations` (including `failure_class`, `admissible`, `event_idx` for scope)
- Any rule of the form “include a key iff gold says allow” or “exclude keys that only appear on gold unknown_key denials”

## Bench corpus (`bench/contracts/corpus`)

Traces have **no** `annotations`. `allowed_keys` is the **synthetic union** of all `task_id` values appearing in events plus initial-state keys. No `evaluation_scope.json` is required.

## Frozen run metadata

Contract evaluation drivers record in `run_manifest`:

- `allowed_keys_policy`: `non_gold_family_allowlist` when `evaluation_scope.json` is loaded from the corpus root; otherwise `synthetic_union_no_annotations`.
- `evaluation_scope_path` and `evaluation_scope_schema_version` when applicable.
- `script_version` on `scripts/contracts_eval.py` (v0.5+ for this discipline).

## Formal (Lean)

Unchanged: Lean remains a simplified model; it does not encode `evaluation_scope.json` or family allowlists. Empirical claims refer to the Python kernel and these artifacts.
