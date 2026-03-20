# Validating a run

This document describes how to produce a valid run and how to check that it conforms to the kernel and release train.

## Workflow

From the repo root. On **Windows PowerShell**, set env vars first:
`$env:LABTRUST_KERNEL_DIR = "kernel"; $env:PYTHONPATH = "impl/src"`. On **Bash**: `export LABTRUST_KERNEL_DIR=kernel PYTHONPATH=impl/src`.

1. **Produce a run** — Run the thin-slice pipeline to generate a run directory with trace, MAESTRO report, evidence bundle, and release manifest:
   ```bash
   python -m labtrust_portfolio run-thinslice --out-dir datasets/runs/<run_id>
   ```
   (Requires `PYTHONPATH=impl/src` or `$env:PYTHONPATH = "impl/src"`.)

2. **Check conformance** — Verify that the run passes Tier 2 (artifacts present, schema-valid, replay ok). The command also writes `conformance.json` under the run dir (tier, pass, reasons); schema: `kernel/conformance/CONFORMANCE.v0.1.schema.json`.
   ```bash
   python -m labtrust_portfolio check-conformance datasets/runs/<run_id>
   ```
   (Requires `LABTRUST_KERNEL_DIR=kernel` and `PYTHONPATH=impl/src`.) Exit code 0 means pass; non-zero means fail (see output for failure reasons).

   **Auditor walk-through (P7):** For mapping completeness and PONR coverage (and optional run review), run `python scripts/audit_bundle.py [--run-dir datasets/runs/<run_id>]`. For one-command audit over a release: `python scripts/audit_bundle.py --release datasets/releases/portfolio_v0.1` (runs mapping + PONR; if the release dir contains evidence_bundle.json, review runs there too). See [EVALS_RUNBOOK.md](EVALS_RUNBOOK.md) and [PART11_AUDIT_TRAIL_ALIGNMENT.md](PART11_AUDIT_TRAIL_ALIGNMENT.md).

**P0 conformance summary:** To aggregate conformance over all P0 runs (e.g. E3 run dirs, E2 redaction demo), run `python scripts/build_p0_conformance_summary.py`; output: `datasets/releases/portfolio_v0.1/p0_conformance_summary.json`. See [P0_CONFORMANCE_SUMMARY_SPEC.md](P0_CONFORMANCE_SUMMARY_SPEC.md).

**Run all paper experiments:** To run a tailored experiment set per paper (P0–P8) in one go, use `python scripts/run_paper_experiments.py` (from repo root with `PYTHONPATH=impl/src` and `LABTRUST_KERNEL_DIR=kernel`). Use `--quick` for fewer seeds; use `--paper P0` (or P1 … P8) to run only one paper. See [EVALS_RUNBOOK.md](EVALS_RUNBOOK.md).

3. **Release a dataset (optional)** — To publish the run as an immutable release, copy it to `datasets/releases/` with a release manifest:
   ```bash
   python -m labtrust_portfolio release-dataset datasets/runs/<run_id> <release_id>
   ```
   (Requires `PYTHONPATH=impl/src`.) For **strict PONR gating** (deny release when the trace fails contract validation), add `--check-contracts`. Default is conformance-only so existing thin-slice runs can release; use `--check-contracts` when contract-valid traces are required.

## Conformance tiers

- **Tier 1:** All required artifacts present (`trace.json`, `maestro_report.json`, `evidence_bundle.json`, `release_manifest.json`) and each validates against its kernel schema.
- **Tier 2:** Tier 1 plus replay succeeds (state hashes match when replaying the trace) and the evidence bundle reports `schema_validation_ok` and `replay_ok` true. For bundles with `verification_mode: "public"`, replay is not required (public bundles are verifiable but not necessarily replayable). Evidence bundle must include `verification_mode` (required in schema).
- **Tier 3:** Tier 2 plus PONR coverage: for each PONR-aligned task required by the scenario (e.g. disposition_commit for lab_profile_v0), the trace must contain at least one corresponding task_end event.

## CI

The **test** job runs the full `unittest` suite under `tests/` (including P1–P8 integration tests that launch eval scripts and assert on outputs; P8 adds meta-controller unit tests and `verify_p8_meta_artifacts` in the integration path). It also runs the thin-slice pipeline, lab profile load, conformance check, and release-dataset step.

The **conditional-evals** job runs per-paper evaluation scripts: P0 E3 (`produce_p0_e3_release.py --runs 10 --no-release`), P0 E2 (`e2_redaction_demo.py`; redacted trace is audit-only; `evidence_bundle_redacted` has `replay_ok` false), P3 `replay_eval` (with `--overhead-curve`, `--bootstrap-reps 50`, `--thin-slice-seeds 42`) then `verify_p3_replay_summary.py --strict-curve`, P4 `maestro_fault_sweep` (--seeds 5), P4 `maestro_baselines`, P1 `contracts_eval`, P7 `run_assurance_eval` + `export_assurance_tables`, P2 `rep_cps_eval` (--delay-sweep 0,0.05,0.1), P5 `generate_multiscenario_runs`, P5 `scaling_heldout_eval`, P6 `llm_redteam_eval`, P8 `meta_eval` (--seeds 1,2,3, `--run-naive`, `--fault-threshold` 0), P8 `meta_eval` smoke on `regime_stress_v1` (output under `/tmp/p8_meta_v1_ci` on Linux CI), P8 `verify_p8_meta_artifacts.py` on `datasets/runs/meta_eval/comparison.json`, then P8 `meta_collapse_sweep` into `datasets/runs/meta_eval`. Results are written under `datasets/runs/` and `bench/maestro/`. Publishable P8 also produces `scenario_regime_stress_v1/` when you run `run_paper_experiments.py --paper P8` locally (not all of that path runs in CI). See [EVALS_RUNBOOK.md](EVALS_RUNBOOK.md) and [STATE_OF_THE_ART_CRITERIA.md](STATE_OF_THE_ART_CRITERIA.md).
