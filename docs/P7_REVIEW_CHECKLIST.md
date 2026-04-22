# P7 Assurance Pack: Independent Review Checklist

An independent reviewer can use this checklist to verify that a run's evidence supports the assurance pack mapping (hazards, controls, evidence).

## 1. Evidence bundle verification

- [ ] **Path:** Run directory contains `evidence_bundle.json` (or path supplied).
- [ ] **Schema:** Evidence bundle validates against `kernel/mads/EVIDENCE_BUNDLE.v0.1.schema.json`.
- [ ] **Artifacts:** Bundle lists artifact paths (e.g. trace, maestro_report) and schema IDs; hashes present if required.

## 2. PONR causal chain from trace

- [ ] **Trace path:** Run directory contains `trace.json`; validate against `kernel/trace/TRACE.v0.1.schema.json`.
- [ ] **PONR-relevant events:** List events that touch PONR (e.g. task_end for disposition_commit, or events that reference PONR-B in payload/profile). Reconstruct order: which events precede and follow the PONR transition.
- [ ] **State hashes:** Note state_hash_after at PONR-relevant events for replay linkage.

## 3. Map denials/allows to hazards and controls

- [ ] **Assurance pack:** Load `profiles/lab/v0.1/assurance_pack_instantiation.json` (or system-specific pack). For each hazard (e.g. H-001), list control_ids (e.g. C-001, C-002).
- [ ] **Evidence types per control:** For each control, note required evidence_artifact_types (e.g. trace, evidence_bundle).
- [ ] **Run evidence:** Confirm run supplies the required artifacts and that conformance (Tier 2) passes so that "denials" (e.g. missing artifact, failed replay) would have blocked release; "allows" correspond to admissible evidence.

## 4. Review outcome

Document outcome: PASS (all items checked, evidence supports mapping) or FAIL (item unchecked or evidence gap). Attach short summary (e.g. "Run X: evidence bundle valid, PONR-B chain has 3 events, controls C-001/C-002 satisfied by trace + evidence_bundle").

## Scripted review (optional)

Run `scripts/review_assurance_run.py <run_dir> [--pack path] [--scenario-id <id>] [--review-mode schema_only|schema_plus_presence|full_review] [--profile-dir profiles/lab/v0.1]` to produce a machine-readable review outcome (`evidence_bundle_ok`, `trace_ok`, `ponr_events`, `controls_covered`, `ponr_coverage`, `control_coverage_ratio`, `failure_stage`, `failure_reason_codes`). Default mode is **`full_review`** (scenario/trace alignment, PONR task coverage, **all** `evidence_artifact_types` per control, bundle trace SHA, release manifest artifact SHAs). Weaker modes are **ablation baselines** for discrimination experiments.

- **Failure codes:** Stable strings documented in [P7_REVIEW_FAILURE_CODES.md](P7_REVIEW_FAILURE_CODES.md).
- **Implementation:** `impl/src/labtrust_portfolio/assurance_review_pipeline.py` (shared with `run_assurance_negative_eval.py`).

PONR events use kernel PONR task names from conformance for known scenario IDs. If scenario support is missing, the script reports known scenario IDs and returns no PONR coverage ratio for that case. Use output as "review outcome" attachment.

**Negative controls (suite):** `scripts/run_assurance_negative_eval.py` materializes deterministic invalid cases and writes `datasets/runs/assurance_eval/negative_results.json` (`generation`, `by_scenario`, `by_perturbation`, lift metrics; run with `--submission-mode` for redacted manifests). `scripts/export_p7_negative_tables.py` emits manuscript CSVs including `p7_negative_by_scenario.csv`, `p7_boundary_case_summary.csv`, and provenance sidecars (`p7_submission_manifest_redacted.json`, `p7_generation_metadata.json`). **`tests/test_assurance_negative_eval.py`** smoke-tests quick mode, known rejections, baseline false-accept presence, submission-mode redaction, and CSV↔JSON consistency checks.

**Auditor walk-through:** Run `scripts/audit_bundle.py [--run-dir <run_dir>] [--inst path] [--profile-dir path]` for a single pass/fail report on mapping completeness and PONR coverage; with `--run-dir`, also runs review_assurance_run and reports review_exit_ok. For one-command audit over a release directory: `scripts/audit_bundle.py --release datasets/releases/portfolio_v0.1` (runs mapping + PONR; if the release dir contains evidence_bundle.json, review runs there). Output is human-readable and optionally JSON (`--json-only`). See [EVALS_RUNBOOK.md](EVALS_RUNBOOK.md). For Part 11-style audit trail alignment (each requirement mapped to artifact path and field), see [PART11_AUDIT_TRAIL_ALIGNMENT.md](PART11_AUDIT_TRAIL_ALIGNMENT.md).
