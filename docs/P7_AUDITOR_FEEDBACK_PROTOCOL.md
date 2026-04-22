# P7 Auditor feedback protocol

This document describes how a practicing auditor or domain expert can use the assurance review script and pack, and what to ask so that feedback can be documented (what they could check mechanically, what they would do manually, what was missing).

## Steps for the reviewer

1. **Run the scripted review:** From repo root with `PYTHONPATH=impl/src` and `LABTRUST_KERNEL_DIR=kernel`, run:
   - `python scripts/audit_bundle.py --run-dir <path_to_run>` to check evidence bundle and artifacts.
   - `python scripts/review_assurance_run.py <run_dir> [--scenario-id <id>] [--pack <path_to_assurance_pack>] [--review-mode full_review|schema_only|schema_plus_presence] [--profile-dir profiles/lab/v0.1]` to produce the machine-readable outcome (`evidence_bundle_ok`, `trace_ok`, `ponr_events`, `failure_reason_codes`, etc.). Default is **`full_review`**. See [P7_REVIEW_FAILURE_CODES.md](P7_REVIEW_FAILURE_CODES.md) for code meanings.
   - Optional: run the full **negative-control** suite (`scripts/run_assurance_negative_eval.py`) and inspect `negative_results.json` / `papers/P7_StandardsMapping/p7_perturbation_reject_matrix.csv` to see which injected faults are missed by weaker reviewer modes ([P7_PERTURBATION_CHECKLIST.md](P7_PERTURBATION_CHECKLIST.md)).

2. **Inspect a run directory:** A run directory (e.g. from `run_thin_slice` or `run_assurance_eval`) contains trace.json, evidence_bundle.json, maestro_report.json, release_manifest.json. The reviewer can open these and compare with the script output.

3. **Use the assurance pack:** The pack (e.g. `profiles/lab/v0.1/assurance_pack_instantiation.json`) maps hazards to controls to evidence types. The reviewer can check whether the run’s artifacts satisfy the evidence_map and whether the script’s control_coverage_ratio and ponr_coverage match their expectation.

## Questions to document (for practitioner feedback)

- **What could you check mechanically?** Which of the script’s checks (schema validation, PONR event presence, control coverage) would you treat as sufficient for a first pass?
- **What would you still do manually?** Which aspects of a real safety case or audit would require human judgment or additional evidence not produced by the script?
- **What was missing?** Any hazard, control, or evidence type that the pack or script did not cover but you would expect in your domain?

## When feedback is obtained

Add a short "Practitioner feedback" subsection in P7 DRAFT (without identifying the party if needed) and cite this protocol. The feedback does not constitute endorsement; it is used to improve the documentation and script coverage.
