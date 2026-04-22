# Assurance pack (P7 Standards mapping)

Schema: `ASSURANCE_PACK.v0.1.schema.json`. Used for traceable mapping from hazards to controls to evidence artifacts.

**Mechanical checks:** `scripts/check_assurance_mapping.py` validates instantiations against this schema and mapping completeness. **`scripts/review_assurance_run.py`** (see `impl/src/labtrust_portfolio/assurance_review_pipeline.py`) performs scripted review with optional **`--review-mode`** (`full_review` vs ablation baselines). **`scripts/run_assurance_negative_eval.py`** exercises injected faults; stable failure code strings are documented in **`docs/P7_REVIEW_FAILURE_CODES.md`**.

**Paper / docs:** `docs/P7_STANDARDS_MAPPING.md`, `papers/P7_StandardsMapping/DRAFT.md`, `docs/P7_ROBUST_EXPERIMENT_PLAN.md`, `docs/P7_PERTURBATION_CHECKLIST.md`, `docs/P7_REVIEW_CHECKLIST.md`.

**Non-goals.** This pack is a translation layer for structuring assurance evidence. No certification claim; no claim of compliance with 21 CFR Part 11, OECD GLP, or any other regulation. Instantiation and review scripts support auditors but do not constitute regulatory certification.
