# MAESTRO Reproducibility

Canonical scenario set for the benchmark is defined in `BENCHMARK_RELEASE.v0.1.md` and `benchmark_scenarios.v0.1.json`.

## Benchmark release

The v0.1 benchmark release consists of five scenarios: toy_lab_v0, lab_profile_v0, warehouse_v0, traffic_v0, regime_stress_v0. The machine-readable list is in `benchmark_scenarios.v0.1.json` (key `scenario_ids`). Use this file to drive automated runs (e.g. CI, sweep scripts). For train/val/test or held-out evaluation, see P5 (scaling_heldout_eval). Version is fixed in the filename (`BENCHMARK_RELEASE.v0.1.md`); do not change the scenario set for v0.1 without a new release document.

## P4 publishable bundle

Thin-slice runs checked in for the P4 manuscript use **MAESTRO_REPORT v0.2** (`kernel/eval/MAESTRO_REPORT.v0.2.schema.json`). A frozen copy of the sweep, antigaming eval, baselines, and exported tables lives under `datasets/releases/p4_publishable_v1/`. Regenerate sources from repo root (see `datasets/runs/RUN_RESULTS_SUMMARY.md`).

## Dataset format

Runs are stored under `datasets/runs/<run_id>/` with:

- trace.json (TRACE schema)
- maestro_report.json (MAESTRO_REPORT schema; P4 publishable uses v0.2)
- evidence_bundle.json
- release_manifest.json

Releases are copied to `datasets/releases/<release_id>/` via `labtrust_portfolio release-dataset`. Each release has a manifest with artifact paths and SHA256 hashes.

## Reproducing a run

1. Set `LABTRUST_KERNEL_DIR` and `PYTHONPATH=impl/src`.
2. Run the same adapter with the same scenario_id and seed:
   - Centralized: `run_thin_slice(out_dir, seed=N, ...)` or use `CentralizedAdapter().run("toy_lab_v0", out_dir, seed=N)`.
   - Blackboard: `BlackboardAdapter().run("lab_profile_v0", out_dir, seed=N)`.
3. Compare trace and report to the released artifacts (same seed yields same trace modulo run_id/uuid).

## Variance

For stochastic scenarios, run multiple seeds and report mean and stdev of metrics (e.g. tasks_completed, p95 latency). Use `scripts/produce_p0_e3_release.py` for multi-seed replay-link checks.
