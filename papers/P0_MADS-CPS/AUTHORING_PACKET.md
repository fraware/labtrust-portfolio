# MADS-CPS: A Machine-Checkable Minimum Assurance Bar for Agentic Cyber-Physical Workflows

**Paper ID:** P0_MADS-CPS  
**Tag:** core-kernel  
**Board path:** Spec to MVP to Eval to Draft  
**Kernel ownership:** assurance kernel (tiers, admissibility, PONRs, evidence bundle semantics)

## 1) Central claim
A minimum assurance bar for agentic CPS can be defined in terms of machine-checkable evidence obligations and conformance predicates, independently of the internal decision policy, and can be verified by third parties under both full and restricted audit modes.

## 2) One-line question
What must exist—controls, telemetry, evidence admissibility, and conformance tiers—so a third party can verify conformance to the proposed assurance bar for agentic CPS workflows under realistic lab constraints?

## 3) Scope anchors (ADePT-aligned, no overreach)
- **Reference organism:** robot-centric autonomous lab workflow (see `profiles/lab/v0.1/`). ADePT describes the *capability envelope*; MADS-CPS defines the *assurance envelope*.
- **Primary scaling anchor:** resource graphs, campaign concurrency, heterogeneity, and fault recovery (not "thousand agents" by default).
- **Verification posture:** default is **restricted auditability** (IP/regulatory compatible), with public openness as an optional mode (see `kernel/mads/VERIFICATION_MODES.v0.1.md`).
- **Positioning:** MADS-CPS is not a replacement for risk frameworks, safety cases, or regulatory quality systems. It is a machine-checkable evidence substrate that can support them.

## 4) Claims (citable, falsifiable)
- **C1:** Within a fixed declared envelope, conformance can be defined over external artifacts and validation predicates without reference to the internal coordination or planning algorithm.
- **C2:** For a fixed schema set and declared envelope, conformance tiers reduce to machine-checkable predicates over artifact presence, schema validity, replay status, and PONR coverage.
- **C3:** Logs or transcripts that lack integrity binding, trace-to-report linkage, or declared replay semantics are insufficient for admissible third-party verification.
- **C4:** PONR-gated release converts a qualitative notion of "high impact" into an enforceable control: irreversible or authoritative transitions are denied unless admissibility predicates hold or an auditable override is recorded.

## 5) Outline (camera-ready skeleton)
1. Introduction
2. Problem setting and scope
3. Related work and positioning
4. MADS-CPS model (envelope, artifacts, admissibility, tiers, PONR, verification modes; formal definitions)
5. Properties (tier monotonicity, controller-independence, redaction preservation boundary)
6. Reference instantiation (autonomous lab profile)
7. Experimental design (E1–E4)
8. Results
9. Discussion
10. Limitations, non-goals, and certification boundary
11. Conclusion
Appendix: reproduction and artifact references

## 6) Experiment plan (E1–E4)
- **E1 (Conformance corpus):** Challenge set of run dirs (missing artifact, schema-invalid, hash mismatch, replay mismatch, missing PONR event, etc.); checker run on each; Table 1 (case ID, fault injected, expected tier, observed tier, agreement). Tier 1 includes schema validation of `maestro_report.json` against **MAESTRO_REPORT v0.2** (see kernel).
- **E2 (Restricted auditability):** Verification-mode admissibility matrix: predicate x full / evaluator / regulator / public-redacted; Table 2.
- **E3 (Replay link):** Independent verifier recomputes the evaluation report from the trace; for publishable evidence use **`--standalone-verifier`** (separate process) with **20 seeds** and scenarios **`lab_profile_v0,toy_lab_v0`**; canonical frozen release scenario is `lab_profile_v0` (or set `--release-scenario` explicitly); match rate and variance feed Table 3 and per-seed export.
- **E4 (Algorithm-independence):** At least two adapters (centralized, rep_cps) emit the same artifact interface; same checker; conformance by scenario/controller; Table 3.

Reporting rules: repeated trials where stochasticity exists; explicit variance reporting; all runs produce admissible evidence bundles.

## 7) Artifact checklist (must ship)
- `kernel/trace/TRACE.v0.1.schema.json`
- `kernel/eval/MAESTRO_REPORT.v0.2.schema.json` (Tier 1 validation for `maestro_report.json`)
- `kernel/mads/EVIDENCE_BUNDLE.v0.1.schema.json`
- `kernel/policy/RELEASE_MANIFEST.v0.1.schema.json`
- `kernel/mads/VERIFICATION_MODES.v0.1.md` (restricted verification posture)
- `profiles/lab/v0.1/` (PONRs, fault model, minimal telemetry fields)
- Reference thin-slice pipeline producing: trace, MAESTRO report, evidence bundle, release manifest
- Conformance checker: Tier pass/fail computed from artifacts; frozen release includes `datasets/releases/p0_e3_release/conformance.json` when produced via the release script
- Frozen release integrity object: `datasets/releases/p0_e3_release/release_manifest.json` lists `trace.json`, `maestro_report.json`, `evidence_bundle.json`, `conformance.json` with release-local relative paths (no machine-local absolute paths)
- E1 corpus (`corpus_manifest.json`) and Table 1 export; E2 matrix (4 columns); E3/E4 scripts and Table 3

## 8) Kill criteria (stop or re-scope hard)
- **K0 (admissibility):** If any "admissibility" condition cannot be computed from logged fields (trace + evidence bundle + release manifest), it must be demoted to **non-normative** (document only). Conformance checker and gatekeeper must only use mechanically checkable predicates from artifacts.
- **K1:** Tiers cannot be made machine-checkable under a declared envelope without collapsing into subjective audits.
- **K2:** Admissibility cannot be made mechanically checkable (becomes "framework theater").
- **K3:** Evidence bundle verification cannot be independently executed by a third party.

## 9) Target venues
- arXiv first (cs.SE, cs.CR, cs.RO)
- Later: DSN, ICSE, robotics assurance workshops (depending on framing)

## 10) Integration contract (portfolio coherence)
- Owns the normative meaning of: tiering, admissibility, PONRs.
- Must not re-own: trace/replay mechanics (P3), benchmark substrate (P4), coordination semantics (P1).
- All claims must be provable from artifacts produced in `datasets/` with a release manifest.
