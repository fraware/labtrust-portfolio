# P7 — Standards Mapping (Assurance Pack)

P7 provides a traceable assurance argument with a structured assurance pack
(`hazards`, `controls`, `evidence_map`), schema validation, mapping
completeness checks, and scripted review (`PONR` coverage where applicable and
control coverage).

Current repository state includes:

- **Baseline eval:** `scripts/run_assurance_eval.py` writes
  `datasets/runs/assurance_eval/results.json`.
- **Robust eval matrix:** `scripts/run_assurance_robust_eval.py` writes
  `datasets/runs/assurance_eval/robust_results.json` across scenario x
  fault-regime x seed.
- **Paper runner integration:** `scripts/run_paper_experiments.py --paper P7`
  executes baseline and robust eval.

Profiles and domains:

- `profiles/lab/v0.1/assurance_pack_instantiation.json`
- `profiles/warehouse/v0.1/assurance_pack_instantiation.json`
- `profiles/medical_v0.1/assurance_pack_instantiation.json`

Standards mapping and audit docs:

- Standards mapping table:
  [docs/P7_STANDARDS_MAPPING.md](../docs/P7_STANDARDS_MAPPING.md)
- Auditor feedback protocol:
  [docs/P7_AUDITOR_FEEDBACK_PROTOCOL.md](../docs/P7_AUDITOR_FEEDBACK_PROTOCOL.md)
- Robust experiment protocol:
  [docs/P7_ROBUST_EXPERIMENT_PLAN.md](../docs/P7_ROBUST_EXPERIMENT_PLAN.md)

Paper files:

- Draft: `papers/P7_StandardsMapping/DRAFT.md`
- Claims: `papers/P7_StandardsMapping/claims.yaml`
- Outline packet: `papers/P7_StandardsMapping/AUTHORING_PACKET.md`

No certification claim is made; P7 is a translation and audit-support layer.
