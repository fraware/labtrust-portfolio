# P1 Dataset Governance (contracts_real_v1)

## Family registry
- `lab_orchestration_partner_like`
  - source: partner-like operational log exports (de-identified)
  - domain: laboratory functional unit orchestration
  - trace type: quasi-real
  - annotators: `annotator_a`, `annotator_b`
- `simulator_documented_semantics`
  - source: simulator run logs with documented event semantics
  - domain: automation simulator
  - trace type: simulator-generated
  - annotators: `annotator_a`, `annotator_b`
- `incident_reconstructed`
  - source: incident-inspired reconstruction from workflow incident notes
  - domain: multi-controller automation cell
  - trace type: reconstructed
  - annotators: `annotator_a`, `annotator_b`

## Review procedure
- Primary labeling follows `ANNOTATION_PROTOCOL.md`.
- Weekly review batch with spot checks on denials and handover transitions.
- Adjudication owner: `review_lead`.

## Ambiguity adjudication rule
- If source timestamps conflict, prefer canonical event timestamp field from family schema.
- If ownership transfer window is unclear, classify as deny and include `handover_invalid=true`.
- If key exists in raw trace but not declared configuration, classify as `unknown_key`.

## P1 evaluation independence (contract `allowed_keys`)

Gold labels and annotations are used **only** for scoring, not to build the validator configuration. Declared key scope for quasi-real traces comes from `evaluation_scope.json` plus `scenario_family_id` and initial-state keys. See `EVALUATION_INDEPENDENCE_P1.md`.
