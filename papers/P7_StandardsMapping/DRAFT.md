# From Coordination to Safety Case: A Traceable Assurance Argument for Multi-Agent CPS

**Draft (v0.2). Paper ID: P7_StandardsMapping.**

**Reproducibility.** From repo root, set `PYTHONPATH=impl/src` and `LABTRUST_KERNEL_DIR=kernel` for eval scripts. See [REPORTING_STANDARD.md](../docs/REPORTING_STANDARD.md) and [RESULTS_PER_PAPER.md](../docs/RESULTS_PER_PAPER.md). **No certification claim**; mapping is a translation and audit-support layer only (section 2 Non-goals).

## Full evidence run (baseline + robust + tables + figures)

Use this sequence to regenerate committed artifacts and `generated_tables.md`:

```bash
PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/run_assurance_eval.py --out datasets/runs/assurance_eval
PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/run_assurance_robust_eval.py --out datasets/runs/assurance_eval
python scripts/export_p7_mapping_flow.py
python scripts/export_assurance_gsn.py --out docs/figures/p7_gsn.mmd
python scripts/export_assurance_tables.py --results datasets/runs/assurance_eval/results.json
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

**Figure 1 — GSN-lite.** `scripts/export_assurance_gsn.py` from lab `assurance_pack_instantiation.json`.

**Key results.** (1) **Mapping:** `mapping_check.ok`, `mapping_check.ponr_coverage_ok` in `results.json`. (2) **Per-profile:** `per_profile` on scenario-matched runs. (3) **Robust:** `robust_results.json` reports pass rates and latency median; `run_manifest.scenario_profile_alignment` and `scenario_profile_note` document traffic↔medical proxy. (4) **Non-claim:** no certification. Regenerate tables: `generated_tables.md` or stdout from `export_assurance_tables.py`. Optional summary: [RUN_RESULTS_SUMMARY.md](../../datasets/runs/RUN_RESULTS_SUMMARY.md).

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

## 9. Methodology and reproducibility

**Metrics:** Schema validation, mapping completeness, PONR coverage (where scenario tasks are defined), review JSON (`evidence_bundle_ok`, `trace_ok`, ratios). **Kill criterion:** mapping not checkable by script or PONR chain not reconstructible from trace → approach fails for this paper’s claims. Portfolio bar: [STATE_OF_THE_ART_CRITERIA.md](../docs/STATE_OF_THE_ART_CRITERIA.md).

**Commands:** `run_assurance_eval.py`; `check_assurance_mapping.py`; `review_assurance_run.py <run_dir> --scenario-id lab_profile_v0`; `tests/test_assurance_p7.py`; `docs/P7_REVIEW_CHECKLIST.md`.

**Submission note.** Ship `results.json` and `robust_results.json` with successful mapping and review checks; Table 1 must reflect **`lab_profile_v0`** primary review; default robust run uses **20 seeds** unless justified.

## 10. Non-claims

No certification. No compliance claim with 21 CFR Part 11 or OECD GLP. Auditable artifacts only.

---

**Claims and backing**

| Claim | Artifact / backing |
|-------|---------------------|
| C1 Traceable mapping | Schema, instantiations, `results.json`, `robust_results.json`, [P7_STANDARDS_MAPPING.md](../docs/P7_STANDARDS_MAPPING.md) |
| C2 Mechanically checkable | `check_assurance_mapping.py`, `review_assurance_run.py`, `audit_bundle.py` |
| C3 Stress / proxy scenarios | `robust_results.json`, `P7_ROBUST_EXPERIMENT_PLAN.md`, `P7_REVIEW_CHECKLIST.md` |
| No certification | This section; Limitations |
