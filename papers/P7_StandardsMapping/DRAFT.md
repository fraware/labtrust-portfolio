# From Coordination to Safety Case: A Traceable Assurance Argument for Multi-Agent CPS

**Draft (v0.1). Paper ID: P7_StandardsMapping.**

**Reproducibility.** From repo root, with `PYTHONPATH=impl/src` and `LABTRUST_KERNEL_DIR=kernel`. See [REPORTING_STANDARD.md](../docs/REPORTING_STANDARD.md) and [RESULTS_PER_PAPER.md](../docs/RESULTS_PER_PAPER.md). No certification claim; mapping is translation layer only (see section 2 Non-goals).

**Minimal run (under 20 min):** `python scripts/run_assurance_eval.py --out datasets/runs/assurance_eval` then `python scripts/export_p7_mapping_flow.py` then `python scripts/export_assurance_tables.py --results datasets/runs/assurance_eval/results.json` then `python scripts/export_assurance_gsn.py --out docs/figures/p7_gsn.mmd`.

**Publishable run:** run_manifest and results in `datasets/runs/assurance_eval/results.json` (mapping_check_ok, ponr_coverage_ok, per_profile).

- **Figure 0:** `python scripts/export_p7_mapping_flow.py` (output `docs/figures/p7_mapping_flow.mmd`). Render Mermaid to PNG for camera-ready.
- **Table 1:** `python scripts/run_assurance_eval.py --out datasets/runs/assurance_eval`, then `python scripts/export_assurance_tables.py --results datasets/runs/assurance_eval/results.json` (mapping and review summary).
- **Table 2:** Same run; Table 2 from export_assurance_tables.py (per-scenario review from results.json).
- **Figure 1:** `python scripts/export_assurance_gsn.py --out docs/figures/p7_gsn.mmd` (GSN-lite from assurance_pack_instantiation.json). Render Mermaid to PNG for camera-ready.
- **One-command audit:** `python scripts/audit_bundle.py --run-dir <path>` or `python scripts/audit_bundle.py --release datasets/releases/portfolio_v0.1`.

## 1. Why standards mappings often fail

Template theater: narrative mappings that are not mechanically checkable. We require a structured assurance pack that enables traceable mapping from hazards to controls to evidence artifacts to audit traces, with mechanical checks.

## 2. Assurance pack structure and relationship to standards

Assurance pack: hazards (array), controls (array), evidence_map (object).

**Figure 0 — Mapping flow.** Hazards to controls to evidence artifacts to audit (audit_bundle / review). Regenerate with `python scripts/export_p7_mapping_flow.py` (output `docs/figures/p7_mapping_flow.mmd`). Schema: `kernel/assurance_pack/ASSURANCE_PACK.v0.1.schema.json`. Hazard items may include optional `ponr_ids` (array of PONR ids from the lab profile). Hazard log template: `HAZARD_LOG_TEMPLATE.v0.1.yaml`. Invariant registry template: `INVARIANT_REGISTRY_TEMPLATE.v0.1.yaml`. Mapping rules: each hazard has control_ids; each control has evidence_artifact_types; evidence_map links hazards and artifacts to controls.

**Relationship to standards.** The pack structure (hazards, controls, evidence_map) is compatible with the hazard–control–evidence traceability pattern found in standards such as ISO 26262 (functional safety) or ISO 62304 (medical device software) for mapping and audit only. No certification or compliance claim is made. An **explicit standards mapping table** maps each assurance-pack element (hazard, control, evidence type) to specific clauses or tables of one standard: see [docs/P7_STANDARDS_MAPPING.md](../docs/P7_STANDARDS_MAPPING.md) (ISO 62304 and ISO 26262-6). That makes the translation layer checkable by standards experts.

**Non-goals.** This mapping is a translation layer only. We make no certification claim and no claim of compliance with 21 CFR Part 11, OECD GLP, or any other regulation. The assurance pack and review scripts supply auditable artifacts that can support an auditor; they do not constitute regulatory certification. Explicit non-goals: (1) certification or attestation of compliance; (2) replacement for a formal quality or regulatory process; (3) legal or liability coverage.

## 3. Mapping rules to portfolio artifacts

Gatekeeper (P0), trace (P3), evidence bundle (P0) are the portfolio artifacts. Controls reference trace and evidence_bundle. PONR causal chains are reconstructible from trace; denials/allows map to hazards and controls via the assurance pack.

## 4. Worked instantiation (lab, warehouse, medical)

Three instantiations: **lab** (`profiles/lab/v0.1/assurance_pack_instantiation.json`), **warehouse** (`profiles/warehouse/v0.1/`), **medical** (`profiles/medical_v0.1/assurance_pack_instantiation.json`). The medical profile is a minimal regulator-style instantiation (one hazard, two controls, evidence_map) for software-as-medical-device traceability; no PONR ids. run_assurance_eval runs review with each pack; results.json includes per_profile (lab_v0.1, warehouse_v0.1, medical_v0.1). Mapping is reusable across domains. Hazard H-001 (incorrect sample disposition) has control_ids C-001, C-002 and optional ponr_ids (e.g. PONR-A, PONR-B) linking to the lab profile. Controls C-001, C-002 with evidence_artifact_types trace, evidence_bundle. Instantiation is validated by check_assurance_mapping.py (schema + mapping + PONR coverage).

## 5. Mapping completeness and schema validation

Script `scripts/check_assurance_mapping.py`: (1) Validates the lab instantiation against `kernel/assurance_pack/ASSURANCE_PACK.v0.1.schema.json` (jsonschema); fail if invalid. (2) Checks mapping completeness: every hazard has at least one control_id, every control_id exists in controls, every control has evidence_artifact_types. (3) Optional PONR coverage: when the lab profile has `ponrs.yaml` and any hazard has `ponr_ids`, every PONR id in the profile must appear in at least one hazard's `ponr_ids`. Exit 0 if all checks pass. Output includes a final JSON line with `mapping_ok` and `ponr_coverage_ok` for run_assurance_eval.

## 6. Mapping table and review process

**Table — Hazard to controls to evidence (lab instantiation):**

| Hazard | Controls | Evidence types |
|--------|----------|----------------|
| H-001 (incorrect/unauthorized disposition) | C-001, C-002 | trace, evidence_bundle |

Controls: C-001 (PONR gate requires Tier 2 conformance), C-002 (disposition in trace and bundle). Diagram: hazard H-001 → controls C-001, C-002 → evidence types trace, evidence_bundle.

**Review checklist:** `docs/P7_REVIEW_CHECKLIST.md` gives an independent reviewer steps. Script `scripts/review_assurance_run.py <run_dir> [--scenario-id <id>]` produces a machine-readable outcome. When `--scenario-id` is set, PONR events use kernel PONR task names (same as conformance Tier 3); when `--scenario-id` is omitted, PONR events use a heuristic (not kernel PONR task names). Scripted review is partial and does not constitute a full safety-case proof. Output includes evidence_bundle_ok, trace_ok, ponr_events, controls_covered, ponr_coverage (required_task_names, found_in_trace, ratio), control_coverage_ratio.

**Table 1 — Mapping and review results.** Source: `results.json`. Run `python scripts/run_assurance_eval.py`; regenerate tables with `python scripts/export_assurance_tables.py`.

| mapping_check_ok | ponr_coverage_ok | review_exit_ok | ponr_events_count | ponr_coverage_ratio | control_coverage_ratio |
|------------------|------------------|----------------|-------------------|---------------------|-------------------------|
| yes | yes | yes | 4 | 1.00 | 1.00 |

**Table 2 — Per-scenario review (kernel PONR).** Eval runs review for toy_lab_v0 and lab_profile_v0; lab_profile_v0 requires disposition_commit (kernel PONR task). Source: results.json key `reviews`. Units: ponr_coverage_ratio, control_coverage_ratio (ratio); exit_ok (yes/no). Run_manifest in results.json. Regenerate with export_assurance_tables.py.

| scenario_id | exit_ok | ponr_coverage_ratio | control_coverage_ratio |
|-------------|---------|---------------------|-------------------------|
| lab_profile_v0 | yes | 1.00 | 1.00 |
| toy_lab_v0 | yes | 1.00 | 1.00 |

**Figure 1 — Assurance case graph skeleton (GSN-lite).** Argument structure from top-level hazards to controls to evidence artifacts, auto-generated from the lab instantiation. Regenerate with `python scripts/export_assurance_gsn.py` (reads assurance_pack_instantiation.json; outputs Mermaid diagram).

**Key results.** (1) Mapping: mapping_check_ok (results.mapping_check.ok), ponr_coverage_ok from results.json. For submission tables, use a run where results.json has mapping_check_ok and ponr_coverage_ok true. The run used for tables (datasets/runs/assurance_eval/results.json) has mapping_check.ok and mapping_check.ponr_coverage_ok true. (2) Per-profile: lab_v0.1, warehouse_v0.1, medical_v0.1 in results.per_profile (reusable across domains); each profile has review outcome and optional PONR coverage. (3) Review: run review with --scenario-id toy_lab_v0 and --scenario-id lab_profile_v0 so PONR coverage uses kernel task names; review_exit_ok, ponr_coverage_ratio, control_coverage_ratio per scenario in results.reviews and Table 2. (4) No certification claim (translation layer only). Numbers from results.json. Regenerate with `python scripts/run_assurance_eval.py` and `python scripts/export_assurance_tables.py`. See [RUN_RESULTS_SUMMARY.md](../../datasets/runs/RUN_RESULTS_SUMMARY.md).

**Results summary (excellence metrics).** From results.json: **mapping completeness** (mapping_check_ok; all hazards have control_ids, all controls have evidence_artifact_types); **PONR coverage ratio** (ponr_coverage_ratio from reviews; target 1.0 for lab profile); **review pass** (review_exit_ok, evidence_bundle_ok, trace_ok). No certification claim: this mapping is a translation layer only; see Limitations and [STANDARDS_OF_EXCELLENCE.md](../docs/STANDARDS_OF_EXCELLENCE.md) (P7). Submission tables use the lab instantiation; results.json per_profile contains lab_v0.1, warehouse_v0.1, and medical_v0.1 for cross-domain reuse.

## 7. Comparison to other assurance and safety-case frameworks

| Aspect | P7 (this work) | GSN/CAE safety case | ISO 26262 hazard analysis |
|--------|----------------|---------------------|---------------------------|
| Structure | Hazards, controls, evidence_map; schema-validated | Goal–strategy–evidence nodes | Hazard log, safety goals, ASIL |
| Mechanical checks | Schema + mapping completeness + PONR coverage (optional) | Often narrative; tool support varies | Traceability tables; tool-dependent |
| Review | Scripted (evidence_bundle, trace, PONR events, coverage ratio) | Manual or tool-assisted | Document-based review |
| Certification | None claimed | Used in safety cases | Compliance process (out of scope here) |

We emphasize mechanically checkable mapping and scripted review over narrative-only assurance; no certification or compliance claim.

## 8. Limitations

Scope: [EXPERIMENTS_AND_LIMITATIONS.md](../docs/EXPERIMENTS_AND_LIMITATIONS.md). Per-paper (no certification):

- **Three instantiations:** Lab v0.1, warehouse v0.1, and medical v0.1; run_assurance_eval runs mapping and review for each (per_profile in results.json). Instantiation is minimal; no real certification process or external auditor. This limits the scope of claims to the translation layer only (no certification).
- **Review is scripted and partial:** Scripted review checks schema, mapping completeness, PONR task presence in trace, and control coverage; it does not replace human judgment or full safety-case proof. PONR coverage requires `--scenario-id` from the known list (toy_lab_v0, lab_profile_v0); when scenario is unknown, no heuristic is used and the script reports which scenario-ids are supported.
- **Completeness:** No guarantee beyond the defined checks (mapping + optional PONR-coverage). "All PONRs have a control" holds only when hazard `ponr_ids` are populated and the checker is run.
- **Coverage metrics:** PONR coverage ratio and control coverage ratio are defined for the run and scenario; they are not system-wide safety-case completeness metrics.
- **Standards link:** Relationship to ISO 26262 (or similar) is structural only (hazard–control–evidence traceability pattern); no certification or compliance claim.
- **K7 (no template theater):** Every claim in the mapping must be checkable by script or schema; prose-only linkage is out of scope.

## 9. Methodology and reproducibility

**Methodology:** Hypothesis—structured assurance pack enables traceable, mechanically checkable mapping from hazards to controls to evidence. Metrics: schema validation, mapping completeness, PONR coverage (optional), review outcome (evidence_bundle_ok, trace_ok, ponr_coverage_ratio, control_coverage_ratio). Kill criterion: if mapping cannot be checked by script or reviewer cannot reconstruct PONR chain, the approach fails. No certification claim. Portfolio criteria: `docs/STATE_OF_THE_ART_CRITERIA.md`.

**Reproducibility:** Run full eval: `python scripts/run_assurance_eval.py` (writes results.json). Validate instantiation: `python scripts/check_assurance_mapping.py`. Review a run: `python scripts/review_assurance_run.py <run_dir> --scenario-id toy_lab_v0`. Integration test: `tests/test_assurance_p7.py`. Checklist: `docs/P7_REVIEW_CHECKLIST.md`. Artifacts: assurance_pack_instantiation.json, results.json, review outcome JSON.

**Submission note.** No certification or compliance claim is made. Review is scripted and partial; PONR coverage uses `--scenario-id` when available (toy_lab_v0, lab_profile_v0). For submission, ensure the reported tables come from a run where results.json has mapping_check.ok and ponr_coverage_ok true and per_profile populated (lab_v0.1, warehouse_v0.1, medical_v0.1); verify and state in the draft that no certification claim is made and that review is scripted and partial.

## 10. Non-claims

No certification. No compliance claim with 21 CFR Part 11 or OECD GLP; we supply auditable artifacts compatible with regulated expectations.

---

**Claims and backing**

| Claim | Artifact / backing |
|-------|---------------------|
| C1 Traceable mapping | Assurance pack schema, hazard→control→evidence table, lab instantiation (with optional ponr_ids) |
| C2 Mechanically checkable | check_assurance_mapping.py (schema + completeness + PONR coverage), review_assurance_run.py |
| C3 Worked example | Lab profile instantiation, results.json, review checklist outcome |
| C4 Quantitative coverage | ponr_coverage_ratio, control_coverage_ratio in review output; Table 1 |
| No certification | Non-claims section; Limitations |
