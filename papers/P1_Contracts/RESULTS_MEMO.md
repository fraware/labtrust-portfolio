# P1 Results Memo

## Dataset summary
- Corpus set now includes benchmark corpus (`bench/contracts/corpus`) and three non-synthetic families in `datasets/contracts_real/`.
- Non-synthetic total: 90 traces (30 per family).
- Governance and annotation artifacts:
  - `datasets/contracts_real/DATASET_GOVERNANCE.md`
  - `datasets/contracts_real/ANNOTATION_PROTOCOL.md`
  - `datasets/contracts_real/inter_annotator_agreement.json`

## Baseline definitions
- Strong baselines B1-B5 are formally documented in `papers/P1_Contracts/STRONG_BASELINES.md`.
- Integrated into evaluator in `scripts/contracts_eval.py` with unified output contract.

## Main tables
- Table package is provided at `papers/P1_Contracts/TABLE_PACKAGE.md`.
- Primary run outputs:
  - `datasets/runs/contracts_eval/eval.json`
  - `datasets/runs/contracts_eval_real/eval.json`
  - `datasets/runs/contracts_eval_real_sim/eval.json`
  - `datasets/runs/contracts_eval_real_incident/eval.json`

## Case study summary
- Full case study: `papers/P1_Contracts/CASE_STUDY_LAB_HANDOVER.md`.
- Includes split-brain and timing-sensitive invalidity, replay excerpt, reason-code output, and baseline comparison.

## Formal results summary
- Lean artifact upgraded in `formal/lean/Labtrust/W2Contract.lean`:
  - admitted-prefix invariants (`denied_no_state_change`, `admitted_preserves_owner`, `admitted_preserves_lastTs`)
  - replay reproducibility theorem (`replay_reproducibility`)

## Claim-envelope updates
- Claim lock applied in:
  - `papers/P1_Contracts/DRAFT.tex`
  - `papers/P1_Contracts/claims.yaml`
  - `papers/P1_Contracts/AUTHORING_PACKET.md`
- Exclusions explicitly encoded for consensus/full-distributed/live-transport/arbitrary-perturbation/synthetic-to-field overclaims.
