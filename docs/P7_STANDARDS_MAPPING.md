# P7 Explicit standards mapping (assurance pack to standard clauses)

This table maps assurance-pack elements (hazard, control, evidence type) to specific clauses or tables of selected standards. It makes the translation layer checkable by standards experts. **No certification or compliance claim** is made; the mapping is for traceability and audit support only.

## Mapping methodology

**Why ISO 62304 and ISO 26262-6.** These standards are widely used references for (1) medical device software life-cycle traceability and (2) automotive software safety requirements and verification. They are chosen as *illustrative* anchors so readers can relate the portfolio’s hazard–control–evidence structure to familiar regulated documentation patterns. This paper does **not** claim that running the portfolio scripts satisfies either standard in full.

**What “structural compatibility” means here.** We assert only that the assurance-pack *shape* (hazards with links to controls; controls with declared evidence artifact types; optional PONR ids; machine-readable instantiation JSON) supports the same *kind* of traceability work products that those standards expect at a documentation level: hazards or safety requirements linked to implementation evidence. “Structural” means schema-level and script-checkable linkage—not semantic equivalence to any particular hazard analysis in a real product.

**Audit-support artifacts vs traceability support.** The portfolio produces concrete artifacts (trace, evidence bundle, release manifest, scripted review output) that an auditor could inspect. That is **audit support** (material exists and can be walked). **Structural traceability support** means the pack and checkers maintain internal consistency (hazard→control→evidence references resolve). Neither implies that an external certification body would accept the bundle without additional process evidence.

**What is out of scope.** Product-specific risk management files, tool qualification, full software safety requirement decomposition, on-road or clinical validation, quality management system evidence, notified-body or registrar engagement, and any statement of regulatory compliance. **Certification and attestation are explicitly not claimed.**

## Reference standard: ISO 62304 (Medical device software — Life cycle processes)

| Assurance-pack element | Type | ISO 62304 reference | Notes |
|------------------------|------|---------------------|-------|
| H-001 (incorrect/unauthorized sample disposition) | Hazard | Clause 5.1 (Risk management), 7.1 (Software safety requirements) | Hazard corresponds to risk; disposition failure is a software-related hazard. |
| C-001 (PONR gate requires admissible evidence, Tier 2 conformance) | Control | Clause 5.5 (Software verification), 7.2 (Traceability) | Gate and evidence support verification and traceability. |
| C-002 (Disposition action recorded in trace and evidence bundle) | Control | Clause 7.3 (Documentation), 5.7 (Software integration) | Recorded trace and bundle provide documentation and integration evidence. |
| evidence_artifact_types: trace | Evidence | Clause 7.3 (Software documentation), Annex B (Documentation) | Trace is executable/documentation artifact. |
| evidence_artifact_types: evidence_bundle | Evidence | Clause 5.5 (Verification), 7.2 (Traceability) | Bundle supports verification and traceability of safety requirements. |

### Worked chain A (lab — sample disposition)

1. **Hazard:** H-001 — incorrect or unauthorized disposition of an analytical sample.
2. **Controls:** C-001 (evidence gate before irreversible disposition), C-002 (disposition recorded in trace and bundle).
3. **Evidence:** `trace` and `evidence_bundle` artifact types attached to controls; scripted checks ensure controls declare expected artifact types and that review can find PONR-aligned task names in the trace when the scenario defines them (e.g. `disposition_commit` for `lab_profile_v0`).
4. **Non-claim:** This chain demonstrates *checkable linkage* in the toy instantiation, not validated clinical software.

## Reference standard: ISO 26262-6 (Automotive — Product development: software level)

| Assurance-pack element | Type | ISO 26262-6 reference | Notes |
|------------------------|------|------------------------|-------|
| H-001 | Hazard | Part 3, Clause 7 (Hazard analysis and risk assessment); Part 6 Table 1 (SW safety requirements) | Hazard maps to item failure mode / safety goal. |
| C-001 | Control | Part 6, Clause 7 (Software unit design), 8 (Verification) | Gate and evidence support verification of safety requirements. |
| C-002 | Control | Part 6, Clause 9 (Software integration), Part 8 (Supporting processes, documentation) | Trace and bundle as integration and documentation evidence. |
| trace | Evidence | Part 6 Clause 9 (Integration verification); Part 8 documentation | Trace as verification artifact. |
| evidence_bundle | Evidence | Part 6 Clause 8 (Verification), traceability | Bundle as verification and traceability artifact. |

### Worked chain B (cross-domain template — warehouse-style motion)

The warehouse profile reuses the same pack *pattern* with different ids (e.g. H-W01, C-W01). Mapping to ISO 26262-6 follows the same hazard→control→evidence column intent as chain A: a hazard statement, controls tied to verification artifacts, and trace/bundle as evidence of implementation. **Non-claim:** The bench scenario `warehouse_v0` is a minimal CPS toy; mapping illustrates document structure, not automotive product evidence.

1. **Hazard (instantiation-specific):** e.g. incorrect pick/place or dropped load (profile-specific hazard id in JSON).
2. **Controls:** controls that require trace and evidence_bundle types for mechanical verification in review scripts.
3. **Evidence:** trace and bundle; optional scripted PONR-style task coverage uses scenario-defined final tasks (e.g. `place` for `warehouse_v0`) so coverage is not vacuous when that scenario is named.
4. **Explicit non-claim:** No ASIL assignment, no safety goal from a real item definition, no proof of field safety.

## Usage

- **Lab profile** (`profiles/lab/v0.1/assurance_pack_instantiation.json`): H-001, C-001, C-002 as in the tables above; primary Table 1 row in P7 uses scenario `lab_profile_v0` so kernel PONR coverage references `disposition_commit`.
- **Warehouse profile** (`profiles/warehouse/v0.1/assurance_pack_instantiation.json`): Same structural mapping pattern; scenario `warehouse_v0` uses PONR-aligned task names from the scenario YAML for scripted coverage (see `SCENARIO_PONR_TASK_NAMES` in `impl/src/labtrust_portfolio/conformance.py`).
- **Medical profile** (`profiles/medical_v0.1/assurance_pack_instantiation.json`): Minimal SaMD-style template; in robust eval it is paired with `traffic_v0` runs to stress the review pipeline—**not** a claim that traffic semantics match medical device hazards (see `run_manifest.scenario_profile_note` in `robust_results.json`).
- Review and audit scripts (`audit_bundle.py`, `review_assurance_run.py`) operate on the pack structure; this document is for human and standards-expert review only.

## Distinctions (summary)

| Concept | What we claim |
|--------|----------------|
| Structural traceability support | Schema-valid pack; hazard→control→evidence references; mechanical checks. |
| Audit-support artifacts | Trace, bundle, manifests, review JSON an auditor can open. |
| Certification / compliance | **Not claimed** — translation layer and tooling only. |
