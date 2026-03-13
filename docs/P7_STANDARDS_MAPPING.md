# P7 Explicit standards mapping (assurance pack to standard clauses)

This table maps assurance-pack elements (hazard, control, evidence type) to specific clauses or tables of selected standards. It makes the translation layer checkable by standards experts. **No certification or compliance claim** is made; the mapping is for traceability and audit support only.

## Reference standard: ISO 62304 (Medical device software — Life cycle processes)

| Assurance-pack element | Type | ISO 62304 reference | Notes |
|------------------------|------|---------------------|-------|
| H-001 (incorrect/unauthorized sample disposition) | Hazard | Clause 5.1 (Risk management), 7.1 (Software safety requirements) | Hazard corresponds to risk; disposition failure is a software-related hazard. |
| C-001 (PONR gate requires admissible evidence, Tier 2 conformance) | Control | Clause 5.5 (Software verification), 7.2 (Traceability) | Gate and evidence support verification and traceability. |
| C-002 (Disposition action recorded in trace and evidence bundle) | Control | Clause 7.3 (Documentation), 5.7 (Software integration) | Recorded trace and bundle provide documentation and integration evidence. |
| evidence_artifact_types: trace | Evidence | Clause 7.3 (Software documentation), Annex B (Documentation) | Trace is executable/documentation artifact. |
| evidence_artifact_types: evidence_bundle | Evidence | Clause 5.5 (Verification), 7.2 (Traceability) | Bundle supports verification and traceability of safety requirements. |

## Reference standard: ISO 26262-6 (Automotive — Product development: software level)

| Assurance-pack element | Type | ISO 26262-6 reference | Notes |
|------------------------|------|------------------------|-------|
| H-001 | Hazard | Part 3, Clause 7 (Hazard analysis and risk assessment); Part 6 Table 1 (SW safety requirements) | Hazard maps to item failure mode / safety goal. |
| C-001 | Control | Part 6, Clause 7 (Software unit design), 8 (Verification) | Gate and evidence support verification of safety requirements. |
| C-002 | Control | Part 6, Clause 9 (Software integration), Part 8 (Supporting processes, documentation) | Trace and bundle as integration and documentation evidence. |
| trace | Evidence | Part 6 Clause 9 (Integration verification); Part 8 documentation | Trace as verification artifact. |
| evidence_bundle | Evidence | Part 6 Clause 8 (Verification), traceability | Bundle as verification and traceability artifact. |

## Usage

- **Lab profile** (`profiles/lab/v0.1/assurance_pack_instantiation.json`): H-001, C-001, C-002 as above.
- **Warehouse profile** (`profiles/warehouse/v0.1/assurance_pack_instantiation.json`): Same structure; hazard/control IDs (e.g. H-W01, C-W01, C-W02) map to the same clause types (hazard → risk/safety requirements; control → verification/documentation; evidence → traceability/verification).
- Review and audit scripts (`audit_bundle.py`, `review_assurance_run.py`) operate on the pack structure; this document is for human and standards-expert review only.
