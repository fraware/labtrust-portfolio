# From Coordination to Safety Case: A Traceable Assurance Argument for Multi-Agent CPS

**Draft (v0.3). Paper ID: P7_StandardsMapping.**

**Reproducibility.** From repo root, set `PYTHONPATH=impl/src` and `LABTRUST_KERNEL_DIR=kernel` for eval scripts. See [REPORTING_STANDARD.md](../docs/REPORTING_STANDARD.md) and [RESULTS_PER_PAPER.md](../docs/RESULTS_PER_PAPER.md). **No certification claim**; mapping is a translation and audit-support layer only (section 2 Non-goals).

## Governance problem (framing)

The governance failure mode is not only **lack** of evidence files, but **inability to distinguish** admissible, scenario-consistent, commitment-complete evidence from well-packaged but unsupported or misleading claims. Existing pipelines can produce governance theater: many artifacts, little **reviewability**. This paper defines a **reviewability interface**: runtime artifacts plus an assurance pack are converted into checkable governance claims with **stable failure codes** ([docs/P7_REVIEW_FAILURE_CODES.md](../docs/P7_REVIEW_FAILURE_CODES.md)) so that rejection is **attributable** (auditor-usable diagnosis), not a single opaque boolean.

## Empirical questions

- **Q1 — Stability (positive controls):** Does the review layer continue to accept **valid** evidence under runtime stress? Answered by the **400-run** robust matrix (`robust_results.json`); high pass rates here are informative **only** as positive controls, not as proof of real-world trustworthiness alone.
- **Q2 — Discrimination (negative controls):** Does the review layer **reject** invalid, incomplete, inconsistent, or misleading evidence? Answered by `negative_results.json` from `run_assurance_negative_eval.py` (families: pack structure, artifact admissibility, scenario consistency, adversarial/misleading).
- **Q3 — Attribution:** When a case is rejected, is the **reason** consistent with the injected fault (localization)? Rows include `failure_reason_codes`, `failure_stage`, and `reason_matches_expected`.

## Threat model (what we check vs out of scope)

**In scope (mechanical):** malformed or missing JSON; schema-invalid trace/bundle/manifest; structurally invalid packs; **trace `scenario_id` vs declared review scenario**; missing PONR-aligned commitment tasks for the scenario; **control evidence types not all satisfied** by artifacts present in the run; **SHA256 mismatch** between evidence bundle / release manifest and files on disk (swapped or stale bundles, tampered manifest).

**Out of scope:** semantic correctness of hazard text; domain ontology completeness; collusion that replaces the entire artifact chain coherently; cryptographic proof of non-repudiation; regulator-ready sufficiency; any **compliance** or **certification** claim.

## Reviewer ablations

`review_assurance_run.py` supports `--review-mode`:

| Mode | Intent |
|------|--------|
| `schema_only` | Pack validation + optional trace/bundle **schema** if files exist (may **miss** missing files or governance inconsistencies). |
| `schema_plus_presence` | Pack + required artifacts **present** and schema-valid (still **misses** PONR/scenario/provenance rules). |
| `full_review` | Governance path: presence, schemas, scenario alignment, PONR coverage, **all** declared evidence types per control, bundle and release **provenance** checks. |

Ablation CSV: `papers/P7_StandardsMapping/p7_ablation_summary.csv` (from `export_p7_negative_tables.py`). Example committed profile: `schema_only` shows **higher false-accept** on injected negatives than `full_review` — the full pipeline is **necessary** for governance-relevant checks, not incremental ornamentation.

## Full evidence run (baseline + robust + negative + tables + figures)

Use this sequence to regenerate committed artifacts, `generated_tables.md`, and negative CSVs:

```bash
PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/run_assurance_eval.py --out datasets/runs/assurance_eval
PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/run_assurance_robust_eval.py --out datasets/runs/assurance_eval
PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/run_assurance_negative_eval.py --out datasets/runs/assurance_eval
python scripts/export_p7_mapping_flow.py
python scripts/export_assurance_gsn.py --out docs/figures/p7_gsn.mmd
python scripts/export_assurance_tables.py --results datasets/runs/assurance_eval/results.json
python scripts/export_p7_negative_tables.py
python scripts/render_p7_mermaid_figures.py
```

- **Baseline only (~minutes):** Stop after `run_assurance_eval.py` if you only need `results.json` and Tables 1–2.
- **Robust default:** `run_assurance_robust_eval.py` uses **20 seeds** (400 runs: 4 scenarios × 5 fault regimes × 20 seeds). Override seeds only with explicit justification ([P7_ROBUST_EXPERIMENT_PLAN.md](../docs/P7_ROBUST_EXPERIMENT_PLAN.md)).
- **Publishable bundle:** `results.json` + `robust_results.json` under `datasets/runs/assurance_eval/`, with `mapping_check.ok` and `mapping_check.ponr_coverage_ok` true, populated `reviews`, `per_profile`, `aggregate`, `by_scenario`, `real_world_proxy`, and `rows`.

**Artifacts per deliverable**

| Deliverable | Script / path |
|-------------|----------------|
| Figure 0 | `export_p7_mapping_flow.py` → `docs/figures/p7_mapping_flow.mmd`; camera-ready `p7_mapping_flow.png` / `.pdf` via `render_p7_mermaid_figures.py` or `npx -y -p @mermaid-js/mermaid-cli mmdc -i docs/figures/p7_mapping_flow.mmd -o docs/figures/p7_mapping_flow.png` |
| Table 1–2 | After baseline eval: `export_assurance_tables.py --results datasets/runs/assurance_eval/results.json` (Table 1 uses primary review for **`lab_profile_v0`** — kernel PONR **`disposition_commit`**) |
| Table 3 | Same export loads `robust_results.json` when present (robust aggregate) |
| Figure 1 | `export_assurance_gsn.py` → `docs/figures/p7_gsn.mmd`; render with `render_p7_mermaid_figures.py` |
| Audit | `audit_bundle.py --run-dir <path>` or `audit_bundle.py --release datasets/releases/portfolio_v0.1` |
| Negative controls + ablations | `run_assurance_negative_eval.py` → `negative_results.json`; `export_p7_negative_tables.py` → `p7_negative_family_summary.csv`, `p7_ablation_summary.csv`, `p7_failure_reason_breakdown.csv` |

**Admissible evidence package (informal definition).** For a declared scenario and pack, a run directory is **admissible** under `full_review` when: the pack passes structure checks; required artifacts exist and validate; trace scenario matches the review scenario; every control’s **full** set of `evidence_artifact_types` is satisfied by artifacts in the run; required PONR tasks appear in the trace; bundle and release manifest digests match on-disk files.

## 1. Why standards mappings often fail

Template theater: narrative mappings that are not mechanically checkable. This work uses a structured assurance pack with schema validation, mapping completeness checks, and scripted review so that hazard–control–evidence links and PONR-aligned task coverage (where defined per scenario) can be reproduced from repository scripts.

## 2. Assurance pack structure and relationship to standards

Assurance pack: `hazards` (array), `controls` (array), `evidence_map` (object).

**Figure 0 — Mapping flow.** Hazards → controls → evidence artifact types → audit (`audit_bundle` / `review_assurance_run`). Regenerate: `scripts/export_p7_mapping_flow.py` → `docs/figures/p7_mapping_flow.mmd`. Schema: `kernel/assurance_pack/ASSURANCE_PACK.v0.1.schema.json`. Hazard items may include optional `ponr_ids`. Templates: `HAZARD_LOG_TEMPLATE.v0.1.yaml`, `INVARIANT_REGISTRY_TEMPLATE.v0.1.yaml`.

**Relationship to standards.** The pack shape matches the hazard–control–evidence traceability *pattern* common in standards such as ISO 26262 and ISO 62304 for **mapping and audit discussion only**. Clause-level mapping and methodology: [docs/P7_STANDARDS_MAPPING.md](../docs/P7_STANDARDS_MAPPING.md). **No certification or compliance claim.**

**Non-goals.** Translation layer only: no attestation of compliance with 21 CFR Part 11, OECD GLP, or any regulation. Non-goals: (1) certification; (2) replacement for formal quality or regulatory process; (3) legal or liability coverage.

## 3. Mapping rules to portfolio artifacts

Gatekeeper (P0), trace (P3), evidence bundle (P0). Controls reference `trace` and `evidence_bundle`. PONR-aligned task names appear in the trace when the scenario defines them (`SCENARIO_PONR_TASK_NAMES` in `impl/src/labtrust_portfolio/conformance.py`).

## 4. Worked instantiations (lab, warehouse, medical)

Three JSON instantiations: **lab** (`profiles/lab/v0.1/assurance_pack_instantiation.json`), **warehouse** (`profiles/warehouse/v0.1/`), **medical** (`profiles/medical_v0.1/assurance_pack_instantiation.json`). Medical is a minimal regulator-style template (SaMD-style traceability illustration); it does not embed lab PONR ids. Baseline eval runs **`per_profile`** on **scenario-matched** thin-slice runs (`run_manifest.per_profile_scenario` in `results.json`): lab on `lab_profile_v0`, warehouse on `warehouse_v0`, medical on `traffic_v0`. The medical-on-traffic pairing **stress-tests** scheduler, trace, bundle, and review mechanics with a minimal pack; it is **not** a claim that traffic physics aligns with SaMD content (`run_manifest.medical_pack_traffic_run_note`). Lab hazard H-001 uses controls C-001, C-002 and optional `ponr_ids`. Validation: `check_assurance_mapping.py`.

## 5. Mapping completeness and schema validation

`scripts/check_assurance_mapping.py`: (1) jsonschema validation against `ASSURANCE_PACK.v0.1.schema.json`; (2) mapping completeness (hazards have controls, controls exist, evidence types present); (3) optional PONR id coverage when `ponrs.yaml` and hazard `ponr_ids` are used. Emits final JSON line with `mapping_ok`, `ponr_coverage_ok`.

## 6. Tables, review, and figures

**Hazard → controls → evidence (lab)**

| Hazard | Controls | Evidence types |
|--------|----------|----------------|
| H-001 (incorrect/unauthorized disposition) | C-001, C-002 | trace, evidence_bundle |

**Review.** `docs/P7_REVIEW_CHECKLIST.md`; `scripts/review_assurance_run.py <run_dir> [--scenario-id <id>]`. Scripted review is **partial**. PONR coverage uses scenario-id and `SCENARIO_PONR_TASK_NAMES` (e.g. lab `disposition_commit`, warehouse `place`, traffic `actuate`); `toy_lab_v0` has no required tasks (vacuous ratio).

**Table 1 — Mapping and review (primary row = lab PONR).** Source: `results.json`, field `review` (scenario `lab_profile_v0`). *Regenerate with `export_assurance_tables.py`.*

| mapping_check_ok | ponr_coverage_ok | review_exit_ok | ponr_events_count | ponr_coverage_ratio | control_coverage_ratio |
|------------------|------------------|----------------|-------------------|---------------------|-------------------------|
| yes | yes | yes | 1 | 1.00 | 1.00 |

**Table 2 — Per-scenario review.** Source: `results.json` → `reviews`.

| scenario_id | exit_ok | ponr_coverage_ratio | control_coverage_ratio |
|-------------|---------|---------------------|-------------------------|
| lab_profile_v0 | yes | 1.00 | 1.00 |
| toy_lab_v0 | yes | 1.00 | 1.00 |

**Table 3 — Robustness aggregate.** Source: `robust_results.json` → `aggregate` (20 seeds, 400 runs in default matrix).

| review_pass_rate | evidence_bundle_ok_rate | trace_ok_rate | ponr_coverage_ratio_mean | control_coverage_ratio_mean | latency_p95_ms_median |
|------------------|-------------------------|---------------|--------------------------|-----------------------------|----------------------|
| 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 47.53 |

**Table 4 — Negative-control families (`full_review`).** Source: `p7_negative_family_summary.csv` (per-family reject rate and localization accuracy on injected negatives). Regenerate: `export_p7_negative_tables.py`.

**Table 5 — Ablation: reviewer mode vs discrimination.** Source: `p7_ablation_summary.csv`. Columns include `valid_accept_rate`, `invalid_reject_rate`, `false_accept_rate`, `false_reject_rate`, `localization_accuracy`. **Interpretation:** `schema_only` and `schema_plus_presence` **must** show higher false accepts than `full_review` on the same negative suite, or the ablation is not doing its job.

**Table 6 — Failure reason breakdown (`full_review` rejections).** Source: `p7_failure_reason_breakdown.csv`.

**Figure 1 — GSN-lite.** `scripts/export_assurance_gsn.py` from lab `assurance_pack_instantiation.json`.

**Key results.** (1) **Mapping:** `mapping_check.ok`, `mapping_check.ponr_coverage_ok` in `results.json`. (2) **Per-profile:** `per_profile` on scenario-matched runs. (3) **Robust (Q1):** `robust_results.json` — positive-control stability under stress; not claimed as discriminative power. (4) **Negative suite (Q2–Q3):** `negative_results.json` with `aggregate.governance_evidence_discrimination_accuracy` and per-mode rates. (5) **Non-claim:** no certification. Optional summary: [RUN_RESULTS_SUMMARY.md](../../datasets/runs/RUN_RESULTS_SUMMARY.md).

## 7. Comparison to other assurance frameworks

| Aspect | P7 (this work) | GSN/CAE | ISO 26262 hazard analysis |
|--------|----------------|---------|---------------------------|
| Structure | Hazards, controls, evidence_map; validated | Goal–strategy–evidence | Hazard log, safety goals, ASIL |
| Mechanical checks | Schema + mapping + optional PONR lines | Varies | Tool-dependent |
| Review | Scripted bundle/trace/PONR coverage | Often manual | Document-based |
| Certification | **Not claimed** | Used in cases | Compliance out of scope |

## 8. Limitations

See [EXPERIMENTS_AND_LIMITATIONS.md](../docs/EXPERIMENTS_AND_LIMITATIONS.md).

- **Instantiations** are minimal teaching examples, not product safety cases.
- **Review** does not replace human safety judgment or full assurance cases.
- **Coverage metrics** are defined per run and scenario, not global completeness.
- **Standards:** structural analogy and documentation pattern only ([P7_STANDARDS_MAPPING.md](../docs/P7_STANDARDS_MAPPING.md)).
- **K7:** No template theater—claims must tie to schema or script.
- **Negative suite:** Perturbations are **not** tuned for a perfect scorecard; some false accepts under weak modes are expected and informative. Sensitivity depends on perturbation family; semantic sufficiency remains out of scope.

## 9. Methodology and reproducibility

**Metrics:** (Positive) schema/mapping, robust pass rates. (Negative) `valid_accept_rate`, `invalid_reject_rate`, `false_accept_rate`, `false_reject_rate`, per-family reject rate, localization accuracy, `governance_evidence_discrimination_accuracy` in `negative_results.json`. **Kill criterion:** mapping not checkable by script, or discrimination suite shows **no** gap between `full_review` and weaker modes on governance-relevant negatives. Portfolio bar: [STATE_OF_THE_ART_CRITERIA.md](../docs/STATE_OF_THE_ART_CRITERIA.md).

**Commands:** `run_assurance_eval.py`; `run_assurance_negative_eval.py`; `check_assurance_mapping.py`; `review_assurance_run.py <run_dir> --scenario-id lab_profile_v0 --review-mode full_review`; `tests/test_assurance_p7.py`, `tests/test_assurance_negative_eval.py`; `docs/P7_REVIEW_CHECKLIST.md`.

**Submission note.** Ship `results.json`, `robust_results.json`, and **`negative_results.json`** with the negative eval and exports; Table 1 must reflect **`lab_profile_v0`** primary review; default robust run uses **20 seeds** unless justified.

## 10. Non-claims

No certification. No compliance claim with 21 CFR Part 11 or OECD GLP. Auditable artifacts only.

---

**Claims and backing**

| Claim | Artifact / backing |
|-------|---------------------|
| C1 Traceable mapping | Schema, instantiations, `results.json`, `robust_results.json`, [P7_STANDARDS_MAPPING.md](../docs/P7_STANDARDS_MAPPING.md) |
| C2 Mechanically checkable | `check_assurance_mapping.py`, `review_assurance_run.py`, `audit_bundle.py` |
| C3 Stress / proxy scenarios | `robust_results.json`, `P7_ROBUST_EXPERIMENT_PLAN.md`, `P7_REVIEW_CHECKLIST.md` |
| C4 Discrimination + ablations | `negative_results.json`, `run_assurance_negative_eval.py`, `export_p7_negative_tables.py`, CSV Tables 4–6 |
| No certification | This section; Limitations |
