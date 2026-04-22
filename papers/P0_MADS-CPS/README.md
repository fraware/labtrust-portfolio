# MADS-CPS: A Machine-Checkable Minimum Assurance Bar for Agentic Cyber-Physical Workflows

P0 defines a machine-checkable minimum assurance bar for agentic CPS: conformance tiers (E1), restricted auditability and redaction (E2), replay-link (E3), and algorithm-independence (E4). Draft and claim table: [DRAFT.md](DRAFT.md), [claims.yaml](claims.yaml). Tables and figures: [VISUALS_PER_PAPER.md](../docs/VISUALS_PER_PAPER.md), [RESULTS_PER_PAPER.md](../docs/RESULTS_PER_PAPER.md). Outline: [AUTHORING_PACKET.md](AUTHORING_PACKET.md). Submission checklist: [PHASE3_PASSED.md](PHASE3_PASSED.md).

**Central claim.** A minimum assurance bar for agentic CPS can be defined in terms of machine-checkable evidence obligations and conformance predicates, independently of the internal decision policy, and verified by third parties under both full and restricted audit modes. MADS-CPS is not a replacement for risk frameworks, safety cases, or regulatory quality systems; it is a machine-checkable evidence substrate that can support them.

**Environment (repo root).** `PYTHONPATH=impl/src`, `LABTRUST_KERNEL_DIR=kernel` (PowerShell: `$env:PYTHONPATH="impl/src"; $env:LABTRUST_KERNEL_DIR="kernel"`).

**E1 (Conformance corpus):** Challenge set under `datasets/runs/p0_conformance_corpus/` with `corpus_manifest.json`. Tier 1 validates `maestro_report.json` against `kernel/eval/MAESTRO_REPORT.v0.2.schema.json`. Build: `python scripts/build_p0_conformance_corpus.py --out datasets/runs/p0_conformance_corpus`; Table 1: `python scripts/export_e1_corpus_table.py --corpus datasets/runs/p0_conformance_corpus`.

**E2 (Restricted auditability):** `python scripts/e2_redaction_demo.py --out datasets/runs/e2_redaction_demo` produces full and redacted traces/bundles. Table 2: `python scripts/export_e2_admissibility_matrix.py`. Normative modes: `kernel/mads/VERIFICATION_MODES.v0.1.md`.

**E3 (Replay link):** Publishable path uses **20 seeds**, scenarios **`lab_profile_v0,toy_lab_v0`**, and **`--standalone-verifier`** (verifier in a separate process). Canonical frozen release scenario is `lab_profile_v0`:

`python scripts/produce_p0_e3_release.py --runs 20 --scenarios lab_profile_v0,toy_lab_v0 --standalone-verifier`

Writes `datasets/runs/e3_summary.json`, `datasets/runs/p0_e3_variance.json`, and `datasets/releases/p0_e3_release/`. To freeze a different scenario while keeping run order, set `--release-scenario <scenario_id>`. To refresh summaries from on-disk runs: `python scripts/replay_link_e3.py --runs 20 --scenarios lab_profile_v0,toy_lab_v0 --standalone-verifier --out datasets/runs/e3_summary.json`. Per-seed markdown: `python scripts/export_e3_table.py`; optional latency figure: `python scripts/plot_e3_latency.py --summary datasets/runs/e3_summary.json --out docs/figures/p0_e3_latency.png`.

Frozen release integrity in `datasets/releases/p0_e3_release/release_manifest.json` hashes `trace.json`, `maestro_report.json`, `evidence_bundle.json`, and `conformance.json` using release-local relative paths.

**E4 (Algorithm-independence):** `python scripts/run_p0_e4_controller_matrix.py --seeds 20 --scenarios toy_lab_v0,lab_profile_v0,rep_cps_scheduling_v0 --regimes baseline,moderate,stress,coordination_shock --out datasets/runs/p0_e4_controller_matrix.json`. Outputs include `datasets/runs/p0_e4_raw_summary.json`, `datasets/runs/p0_e4_normalized_summary.json`, `datasets/runs/p0_e4_per_seed.jsonl`, `datasets/runs/p0_e4_diagnostics.json`, `datasets/runs/p0_e4_controller_pairs.jsonl`, and `datasets/runs/p0_e4_raw_failure_reasons.json` (plus matrix JSON). `coordination_shock` is the explicit source of controller-separating evidence; use diagnostics + controller pairs for divergence evidence, and `p0_e4_raw_failure_reasons.json` for raw-failure causal accounting of failed raw rows.

**Conformance CLI:** `python -m labtrust_portfolio check-conformance <run_dir>` (or `labtrust_portfolio check-conformance` if installed). Implementation: `impl/src/labtrust_portfolio/conformance.py`. Operator guide: `docs/VALIDATING_A_RUN.md`. Committed evidence index: `datasets/releases/p0_e3_release/release_manifest.json`, `datasets/runs/e3_summary.json` (`run_manifest`).
