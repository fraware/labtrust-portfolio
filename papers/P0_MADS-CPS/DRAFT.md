# MADS-CPS: A Normative Minimum Assurance Bar for Agentic Cyber-Physical Workflows

**Draft (v0.1). Paper ID: P0_MADS-CPS.**

**Reproducibility.** From repo root, with `PYTHONPATH=impl/src` and `LABTRUST_KERNEL_DIR=kernel`. See [REPORTING_STANDARD.md](../docs/REPORTING_STANDARD.md) and [RESULTS_PER_PAPER.md](../docs/RESULTS_PER_PAPER.md) for run_manifest and result locations.

**Minimal run (under 20 min):** `python scripts/produce_p0_e3_release.py --runs 3` then `python scripts/export_p0_assurance_pipeline.py` then `python scripts/export_e3_table.py` then `python scripts/export_e2_admissibility_matrix.py` then `python scripts/plot_e3_latency.py`. E2: `python scripts/e2_redaction_demo.py --out datasets/runs/e2_redaction_demo`.

**Publishable run:** Use `--runs 20` (default) for publishable tables; run_manifest (seeds, scenario_id) is in e3_summary.json and release_manifest.json.

- **Figure 0:** `python scripts/export_p0_assurance_pipeline.py` (output `docs/figures/p0_assurance_pipeline.mmd`). Render Mermaid to PNG for camera-ready.
- **Table 1:** `python scripts/produce_p0_e3_release.py` (writes e3_summary.json; default 20 runs), then `python scripts/export_e3_table.py`.
- **Table 2:** `python scripts/e2_redaction_demo.py --out datasets/runs/e2_redaction_demo`, then `python scripts/export_e2_admissibility_matrix.py`.
- **Figure 1:** `python scripts/plot_e3_latency.py` (output `docs/figures/p0_e3_latency.png`).
- Conformance summary: `python scripts/build_p0_conformance_summary.py`. Check conformance: `labtrust_portfolio check-conformance <run_dir>`.

## 1. Motivation

Agentic cyber-physical system (CPS) failures are systemic, not model-local. Coordination, sensing, and actuation interact in ways that cannot be verified by examining a single component. This paper defines a **normative minimum assurance bar** so that a third party can verify system-level safety and security for agentic CPS workflows under realistic lab constraints.

## 2. Object of the standard

The object of the standard is to constrain **interfaces and evidence**, not internal optimization.

**Figure 0 — Assurance pipeline.** Trace to MAESTRO report to evidence bundle to conformance check to release. Regenerate with `python scripts/export_p0_assurance_pipeline.py` (output `docs/figures/p0_assurance_pipeline.mmd`). Render the Mermaid diagram to PNG for inclusion in the camera-ready draft. Boundary, envelope, and definitions are given in the kernel: see `kernel/mads/NORMATIVE.v0.1.md`, `kernel/mads/VERIFICATION_MODES.v0.1.md`, and `profiles/lab/v0.1/`. The reference organism is a robot-centric autonomous lab workflow; the primary scaling anchor is resource graphs, campaign concurrency, heterogeneity, and fault recovery.

## 3. Conformance tiers and global hard-fails

**Table 1 — E1 conformance and E3 replay-link.** E1: missing artifact yields Tier 1 FAIL; present and validated yields Tier 2 PASS. E3: independent verifier recomputes MAESTRO from TRACE over 20 seeds (publishable bar); variance and 95% CIs are in `e3_summary.json` / `p0_e3_variance.json`. Table below is from a specific run (script: `produce_p0_e3_release.py --runs 20`; release: `p0_e3_release`). Example table may show n=10; publishable uses 20 runs. Regenerate with `python scripts/export_e3_table.py`.

| Seed | tasks_completed | coordination_messages | p95_latency_ms | match |
|------|----------------|----------------------|----------------|-------|
| 1 | 4 | 4 | 25.26 | yes |
| 2 | 4 | 4 | 75.59 | yes |
| 3 | 4 | 4 | 28.09 | yes |
| 4 | 4 | 4 | 41.26 | yes |
| 5 | 4 | 4 | 42.64 | yes |
| 6 | 4 | 4 | 26.54 | yes |
| 7 | 4 | 4 | 10.68 | yes |
| 8 | 4 | 4 | 19.02 | yes |
| 9 | 4 | 4 | 29.77 | yes |
| 10 | 4 | 4 | 45.64 | yes |
| **Summary (n=10)** | mean 4.00, stdev 0.00 | — | mean 34.45, stdev 18.08 | true |

95% CI for mean: tasks_completed [4, 4]; p95_latency_ms [21.51, 47.38].

- **Tier 1:** All required artifacts (trace, MAESTRO report, evidence bundle, release manifest) are present and validate against kernel schemas.
- **Tier 2:** Tier 1 plus replay succeeds (state hashes match) and the evidence bundle reports schema_validation_ok and replay_ok. This is the default bar for admissible evidence.
- **Tier 3:** Tier 2 plus PONR coverage: for each PONR-aligned task required by the scenario (e.g. disposition_commit for lab_profile_v0), the trace must contain at least one corresponding task_end event.
- **Global hard-fail:** A run that fails Tier 2 must not be used as the basis for an authoritative release without an explicit, auditable override.

The conformance checker (`labtrust_portfolio check-conformance`) computes pass/fail from artifacts; missing artifact or validation failure yields Tier 1 FAIL; replay or verification flag failure yields Tier 2 FAIL; Tier 3 adds PONR coverage (trace contains required PONR-relevant events). The release path (`release_dataset` in `impl/src/labtrust_portfolio/release.py`) enforces the gate: release is refused unless conformance is Tier 2 or higher.

## 4. Gatekeeper and PONR semantics

PONR (point of no return) enforcement requires mechanically checkable admissibility before irreversible or authoritative transitions. The gate is executed at release time: `release_dataset` calls `check_conformance` and raises if the run does not meet Tier 2. When admissibility is checked, fail-closed behavior applies: if evidence is missing or invalid, the transition is denied. Overrides are possible but must be logged. See `kernel/mads/PONR_ENFORCEMENT.v0.1.md`. **Formal verification:** Gatekeeper policy (fail-closed, no Tier 2/T3 actuation without recorded authorization) is machine-checked in the W1 wedge; see `formal/lean/`. Table 1 (E3) shows runs where conformance and replay hold.

## 5. Telemetry and trace obligations

Telemetry follows flight-recorder semantics: trace format is defined by the kernel (`kernel/trace/TRACE.v0.1.schema.json`). Events carry type, timestamp, actor, payload, and state_hash_after so that replay and third-party verification can reconstruct control-plane behavior without requiring full hardware determinism.

## 6. Evidence admissibility

Evidence is admissible when it has integrity (content-addressed hashes), traceability (trace and evaluation report), and replay at declared fidelity. We guarantee **replay levels and nondeterminism detection** (detection and localization of divergence), not bit-identical deterministic replay on hardware (see Replay Levels). Raw logs or transcripts alone are insufficient. The evidence bundle schema (`kernel/mads/EVIDENCE_BUNDLE.v0.1.schema.json`) and verification modes (`kernel/mads/VERIFICATION_MODES.v0.1.md`) define restricted auditability (redacted payloads, hashed references) as the default.

**Table 2 — E2 redaction admissibility matrix.** For full vs redacted trace, which admissibility conditions remain checkable. Regenerate with `python scripts/export_e2_admissibility_matrix.py`.

| Admissibility condition | Full trace | Redacted trace |
|-------------------------|------------|----------------|
| schema_validation_ok    | yes        | yes            |
| integrity_ok (hashes)   | yes        | yes            |
| replay_ok (L0/L1)      | yes        | no (audit-only) |
| PONR coverage           | yes        | N/A (structure only) |

Redacted trace preserves event order, timestamps, and state_hash_after; payloads are replaced by content-addressed refs. Replay is not run on redacted trace (replay expects full payloads). See `kernel/mads/VERIFICATION_MODES.v0.1.md`.

## 7. Evaluation admissibility and link to MAESTRO

What counts as evidence for evaluation is defined by the release train: TRACE and MAESTRO_REPORT. An independent verifier can recompute MAESTRO metrics from TRACE (E3 experiment); repeated trials and variance reporting are required where stochasticity exists. All runs must produce admissible evidence bundles (see `scripts/produce_p0_e3_release.py` and datasets).

**Figure 1 — E3 p95 latency distribution (per scenario).** Distribution of p95_latency_ms across seeds per scenario from E3 runs. Regenerate with `python scripts/plot_e3_latency.py` (output `docs/figures/p0_e3_latency.png`). With multi-scenario E3 (`produce_p0_e3_release.py --runs 20 --scenarios toy_lab_v0,lab_profile_v0`), the figure shows variance across scenarios and seeds.

## 8. Reference organism and thin-slice demo

The lab profile (`profiles/lab/v0.1/`) instantiates the reference organism. The thin-slice pipeline produces TRACE, MAESTRO report, evidence bundle, and release manifest; the conformance checker confirms Tier 1/2/3 (E1). E2 demonstrates redacted payloads with structure preserved (kernel VERIFICATION_MODES.v0.1.md); one redacted trace is produced by `scripts/e2_redaction_demo.py` and written to `datasets/runs/e2_redaction_demo/trace_redacted.json` (CI runs this step). E3 demonstrates replay link with variance. This demo does not certify any specific deployment.

## 9. Methodology and reproducibility

**Methodology:** Hypothesis—a minimum bar constraining interfaces and evidence is third-party verifiable. Metrics: Tier 1/2/3 pass/fail (artifact presence, schema validity, replay ok, PONR coverage); E3 replay-link match and variance (tasks_completed_stdev, p95_latency_ms_stdev over seeds) with 95% confidence intervals for the means (tasks_completed_ci_95, p95_latency_ms_ci_95 in e3_summary.json). Kill criterion: if conformance cannot be computed objectively from artifacts, the bar fails. All claims are backed by kernel docs, conformance checker, E1/E2/E3 experiments (see Claims and backing below). Portfolio-wide criteria: `docs/STATE_OF_THE_ART_CRITERIA.md`.

**Baseline comparison:** With the MADS gate, release is denied when conformance fails Tier 2 (e.g. missing artifact, replay_ok false). Without the gate, the same run could be released but would be inadmissible. Comparison: runs with intentional Tier 2 failure (e.g. evidence_bundle.verification.replay_ok=false); with gate 0/N released (release_dataset raises); without gate the run would be copyable. Test: `tests/test_thinslice_e2e.TestThinSliceE2E.test_release_denied_when_tier2_fails`.

**Reproducibility:** Produce E3 runs and release: `python scripts/produce_p0_e3_release.py` (with PYTHONPATH=impl/src, LABTRUST_KERNEL_DIR=kernel). Release paths (e.g. `datasets/releases/p0_e3_release/`) are produced when running without `--no-release`; for CI or runs without release, tables can be regenerated from `e3_summary.json` in `datasets/runs/` (export_e3_table.py reads from the run summary). Check conformance: `labtrust_portfolio check-conformance <run_dir>`. Artifacts: trace.json, maestro_report.json, evidence_bundle.json, release_manifest.json; release ID p0_e3_release. See `papers/P0_MADS-CPS/README.md` and `docs/VALIDATING_A_RUN.md`.

## 10. Limitations and non-goals

MADS-CPS does not claim certification or compliance with any specific regulation. It does not claim "open data by default"; default is restricted auditability. It supplies auditable artifacts compatible with regulated expectations (e.g. 21 CFR Part 11, OECD GLP) without implying certification. Scope and determinism levels are summarized in [EXPERIMENTS_AND_LIMITATIONS.md](../docs/EXPERIMENTS_AND_LIMITATIONS.md).

- **Thin-slice is synthetic:** Simulated tasks and timing; no real hardware or physical actuation. The pipeline demonstrates the assurance bar on a synthetic workload.
- **Lab profile is a reference organism:** It instantiates the standard for the portfolio; it is not a deployed production system.
- **PONR gate at release time:** The gate is enforced in code at release (and in conformance Tier 3); it is not executed in a live hardware control loop in this portfolio.
- **Admissibility from logged fields only (K0):** Every normative admissibility condition must be computable from logged fields (trace, evidence bundle, release manifest). Any condition that cannot be checked from these artifacts is non-normative (documentation only).

---

**Claims and backing.** C1 (Minimum bar separable): Backed by kernel NORMATIVE and VERIFICATION_MODES; the bar constrains only interfaces and evidence, not coordination logic. C2 (Objective conformance): Backed by conformance checker and E1—missing artifact fails, present+validated passes; Table 1, Table 2 (admissibility matrix), Figure 1 (E3 latency). C3 (Admissibility): Backed by evidence bundle schema, redaction path (E2) and Table 2, replay link (E3) and Figure 1; raw logs alone do not satisfy bundle or replay. C4 (PONR discipline): Backed by PONR_ENFORCEMENT.v0.1.md and conformance Tier 2 as the admissibility gate before release; Table 2 documents what remains checkable under redaction.
