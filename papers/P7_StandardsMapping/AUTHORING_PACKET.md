# From Coordination to Safety Case: A Traceable Assurance Argument for Multi-Agent CPS

**Paper ID:** P7_StandardsMapping  
**Tag:** core-kernel  
**Board path:** Spec → MVP → Eval → Draft  
**Kernel ownership:** assurance-pack templates (hazards→controls→evidence→audit traces)

## 1) One-line question

How do we translate the portfolio’s executable artifacts (gates, traces, evidence bundles) into **auditor-legible** assurance arguments **without** compliance cosplay or certification claims?

## 2) Scope anchors

- **Audit-support, not attestation:** Outputs are machine-checkable traceability and review JSON; they support an auditor’s walk-through; they do not substitute for a QMS, notified-body review, or regulatory filing.
- **Standards as illustrative anchors:** ISO 62304 / ISO 26262-6 mappings in `docs/P7_STANDARDS_MAPPING.md` are for expert readability and structural analogy—**not** a claim of compliance with those standards.
- **Broader context:** UL 4600 (safety case), IEC 62443 (lifecycle security), 21 CFR Part 11 / OECD GLP (audit trail expectations) inform motivation only; **no** “certification by mapping.”

## 3) Claims (see `claims.yaml`)

- **C1:** Structured assurance pack enables traceable mapping: hazards → controls → evidence artifact types → reviewable traces/bundles.
- **C2:** Mapping is **mechanically checkable** (schema + `check_assurance_mapping.py` + `audit_bundle.py` + scripted `review_assurance_run.py` with review modes), not narrative-only.
- **C3:** Lab + warehouse + traffic-proxy scenarios under a **20-seed × 5 fault-regime** robust matrix demonstrate **positive-control** stability under stress (`robust_results.json`). **Non-claim:** traffic↔medical pack pairing is a documented pipeline/proxy test, not semantic alignment of domains.
- **C4:** **Discrimination:** injected negatives (pack, artifact, scenario, misleading families) are rejected under `full_review` with attributable codes; `schema_only` / `schema_plus_presence` show **higher false accepts** on the same suite (`negative_results.json`, Tables 4–6).

## 4) Outline (manuscript)

1. Why standards-style mappings fail in practice (template theater).
2. Assurance pack structure, schema, and relationship to standards (structural compatibility only)—`docs/P7_STANDARDS_MAPPING.md`.
3. Mapping rules to portfolio artifacts (P0 gatekeeper, trace, evidence bundle).
4. **Three** worked instantiations: lab, warehouse, medical (minimal SaMD-style template); baseline eval uses **scenario-matched** thin-slice runs per profile (`run_manifest.per_profile_scenario` in `results.json`).
5. Robust evaluation matrix and aggregate metrics (`robust_results.json`).
6. Limitations and explicit **non-claims** (no certification).

## 5) Experiment plan

- **Baseline:** `run_assurance_eval.py` → `results.json`. Table 1 flagship row uses **`lab_profile_v0`** (kernel PONR `disposition_commit`), not `toy_lab_v0`.
- **Robust:** `run_assurance_robust_eval.py` — default **20 seeds**, **400 runs** (4 scenarios × 5 regimes × 20 seeds). Details: `docs/P7_ROBUST_EXPERIMENT_PLAN.md`.
- **PONR semantics:** Per-scenario task names in `SCENARIO_PONR_TASK_NAMES` (`conformance.py`); lab / warehouse / traffic have non-vacuous definitions where listed; `toy_lab_v0` has no required PONR tasks (vacuous ratio by definition).

## 6) Artifact checklist (submission)

- `kernel/assurance_pack/ASSURANCE_PACK.v0.1.schema.json`
- Hazard / invariant templates (`HAZARD_LOG_TEMPLATE.v0.1.yaml`, `INVARIANT_REGISTRY_TEMPLATE.v0.1.yaml`)
- `profiles/lab/v0.1/`, `profiles/warehouse/v0.1/`, `profiles/medical_v0.1/` instantiations
- `scripts/check_assurance_mapping.py`, `scripts/review_assurance_run.py`, `scripts/audit_bundle.py`, `scripts/run_assurance_negative_eval.py`, `scripts/export_p7_negative_tables.py`
- `impl/src/labtrust_portfolio/assurance_review_pipeline.py`, `assurance_negative_controls.py`, `assurance_failure_codes.py`
- `datasets/runs/assurance_eval/results.json`, `robust_results.json`, **`negative_results.json`** (`by_perturbation`, aggregate lift metrics)
- `papers/P7_StandardsMapping/p7_negative_family_summary.csv`, `p7_ablation_summary.csv`, `p7_failure_reason_breakdown.csv`, `p7_perturbation_reject_matrix.csv`, `p7_aggregate_lift_metrics.csv`, `p7_latency_by_mode.csv`
- `docs/P7_STANDARDS_MAPPING.md`, `P7_ROBUST_EXPERIMENT_PLAN.md`, `P7_REVIEW_CHECKLIST.md`, `P7_REVIEW_FAILURE_CODES.md`, `P7_PERTURBATION_CHECKLIST.md`
- Figures: `docs/figures/p7_mapping_flow.*`, `p7_gsn.*`, `p7_review_stages.*` (Mermaid + optional PNG/PDF via `render_p7_mermaid_figures.py`); table index `papers/P7_StandardsMapping/generated_tables.md`
- `tests/test_assurance_p7.py`, **`tests/test_assurance_negative_eval.py`**

## 7) Kill criteria

- **K1:** Mapping cannot be made mechanical; becomes prose-only.
- **K2:** No worked example that survives script + checklist review.
- **K7:** Template theater—if a claim is not checkable by schema or script, remove or narrow it.

## 8) Target venues

- arXiv (cs.SE, cs.RO, cs.CR); assurance / dependability workshops.

## 9) Integration contract

- Depends on MADS / tiers / PONR definitions in kernel and portfolio.
- Depends on Replay + MAESTRO for trace and report artifacts consumed by review.
