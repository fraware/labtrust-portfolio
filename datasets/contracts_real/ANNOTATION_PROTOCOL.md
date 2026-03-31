# P1 Contracts Real/Quasi-Real Annotation Protocol (v1)

## Scope
- Applies to all non-synthetic trace families in `datasets/contracts_real/`.
- Unit of annotation is each candidate shared-state mutation event.

## Required labels per event
- `admissible`: `true` or `false`.
- `failure_class` when inadmissible: `split_brain`, `stale_write`, `reorder_sensitive_invalidity`, `unknown_key`.
- Optional `handover_invalid`: `true` when ownership transfer semantics are violated.
- Optional `explanation_note`: short human-readable rationale.

## Admissibility decision rules
1. **Authority check**: event writer must match active owner for the keyed resource.
2. **Temporal check**: event timestamp must not regress relative to admitted key history.
3. **Boundary reconstruction check**: event must include enough key/writer/timestamp fields to evaluate rule 1 and 2.
4. **Unknown-key handling**: key absent from declared resource scope is `unknown_key` deny.

## Failure-class assignment rubric
- `split_brain`: write by non-owner while another owner is active.
- `stale_write`: timestamp regresses under the active key history.
- `reorder_sensitive_invalidity`: invalidity appears because replay order violates declared temporal admissibility.
- `unknown_key`: resource key is out of declared scope.

## Ambiguity handling
- Ambiguous timestamps: prefer declared source timestamp; if absent, use ingest timestamp and mark in `explanation_note`.
- Ambiguous handovers: unresolved transfer windows default to deny with `handover_invalid=true`.
- `unknown_key` vs malformed key: malformed schema is ingestion error; syntactically valid but undeclared keys are `unknown_key`.

## Inherited assumptions
- Identity fields are trusted as declared by the trace corpus contract.
- Configuration (resource scope and authority model) is fixed per family and versioned in `manifest.json`.

## Adjudication workflow
1. Two annotators label independently.
2. Compute disagreement rate at event level and trace level.
3. Resolve disagreements by rule priority: authority > temporal > key-scope.
4. Record final adjudication reason in agreement report.
