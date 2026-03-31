# P1 Appendix Package

## Annotation protocol
- `datasets/contracts_real/ANNOTATION_PROTOCOL.md`

## Inter-annotator agreement
- `datasets/contracts_real/inter_annotator_agreement.json`
- Subset size: 20 traces, disagreement rate reported at event and trace level.

## Extra perturbation outputs
- Stress runner now emits semantic interpretation fields:
  - `profile_semantics.perturbed_dimensions`
  - `profile_semantics.dominant_failure_class`
  - `profile_semantics.semantically_expected_divergence`
  - `profile_semantics.interpretation`
- Script: `scripts/contracts_async_stress.py`

## Reproducibility notes
- Core evaluator and baseline metrics: `scripts/contracts_eval.py`
- Transport boundary sanity (including reason-code parity and mapping validation): `scripts/contracts_transport_parity.py`
- Corpus generator for non-synthetic replay families: `scripts/generate_contracts_real_corpus.py`
- Main run artifacts:
  - `datasets/runs/contracts_eval/eval.json`
  - `datasets/runs/contracts_eval_real/eval.json`
  - `datasets/runs/contracts_eval_real_sim/eval.json`
  - `datasets/runs/contracts_eval_real_incident/eval.json`
