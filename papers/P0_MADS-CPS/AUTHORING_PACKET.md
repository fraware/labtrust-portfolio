# MADS-CPS: A Normative Minimum Assurance Bar for Agentic Cyber-Physical Workflows

**Paper ID:** P0_MADS-CPS  
**Tag:** core-kernel  
**Board path:** Spec → MVP → Eval → Draft  
**Kernel ownership:** assurance kernel (tiers, admissibility, PONRs, evidence bundle semantics)  

## 1) One-line question
What must exist—controls, telemetry, evidence admissibility, and conformance tiers—so a third party can verify system-level safety/security for agentic CPS workflows **under realistic lab constraints**?

## 2) Scope anchors (ADePT-aligned, no overreach)
- **Reference organism:** robot-centric autonomous lab workflow (see `profiles/lab/v0.1/`). ADePT describes the *capability envelope*; MADS defines the *assurance envelope*. citeturn0search0
- **Primary scaling anchor:** resource graphs + campaign concurrency + heterogeneity + fault recovery (not “thousand agents” by default).
- **Verification posture:** default is **restricted auditability** (IP/regulatory compatible), with public openness as an optional mode (see `kernel/mads/VERIFICATION_MODES.v0.1.md`). citeturn1search0turn1search1

## 3) Claims (citable, falsifiable)
- **C1 (Minimum bar):** A normative minimum assurance bar is separable from any particular coordination algorithm; it constrains *interfaces and evidence*, not internal optimization.
- **C2 (Objective conformance):** Conformance tiers can be tested by artifact presence + runtime checks + replayable evidence, enabling objective pass/fail under a declared envelope.
- **C3 (Admissibility):** Evidence admissibility requires integrity + traceability + replay at declared fidelity levels; raw logs/transcripts are insufficient.
- **C4 (PONR discipline):** PONR enforcement operationalizes “high impact” by requiring mechanically checkable admissibility before irreversible/authoritative transitions.

## 4) Outline (camera-ready skeleton)
1. Motivation: agentic CPS failures are systemic, not model-local
2. Object of standard: boundary, envelope, definitions (short; cite kernel)
3. Conformance tiers (Tier 1/2/3) + global hard-fails
4. Gatekeeper + PONR semantics (admissibility packs, fail-closed, overrides)
5. Telemetry/trace obligations (flight recorder semantics)
6. Evidence admissibility (bundle contents, integrity, restricted verification modes)
7. Evaluation admissibility (what counts as evidence; link to MAESTRO)
8. Reference organism instantiation (lab profile) + thin-slice demo
9. Limitations and non-goals (no certification claims; no “open data by default”)

## 5) Experiment plan (minimum credible)
- **E1 (Thin-slice conformance):** one lab scenario demonstrating Tier checks:
  - missing artifact → fails,
  - present + validated → passes.
- **E2 (Restricted auditability demo):** same run supports verification with redacted payloads (structure preserved; sensitive blobs referenced).
- **E3 (Replay link):** independent verifier recomputes MAESTRO metrics from TRACE (Replay L0 control-plane).

Reporting rules:
- repeated trials where stochasticity exists,
- explicit variance reporting,
- all runs produce admissible evidence bundles.

## 6) Artifact checklist (must ship)
- `kernel/mads/EVIDENCE_BUNDLE.v0.1.schema.json`
- `kernel/policy/RELEASE_MANIFEST.v0.1.schema.json`
- `kernel/mads/VERIFICATION_MODES.v0.1.md` (restricted verification posture)
- `profiles/lab/v0.1/` (PONRs, fault model, minimal telemetry fields)
- reference thin-slice pipeline producing: TRACE + MAESTRO_REPORT + EvidenceBundle + ReleaseManifest
- conformance checker: Tier pass/fail computed from artifacts

## 7) Kill criteria (stop or re-scope hard)
- **K0 (admissibility):** If any "admissibility" condition cannot be computed from logged fields (trace + evidence bundle + release manifest), it must be demoted to **non-normative** (document only). Conformance checker and gatekeeper must only use mechanically checkable predicates from artifacts.
- **K1:** tiers cannot be made objective without collapsing into subjective audits.
- **K2:** admissibility cannot be made mechanically checkable (becomes “framework theater”).
- **K3:** evidence bundle verification cannot be independently executed by a third party.

## 8) Target venues
- arXiv first (cs.SE, cs.CR, cs.RO)
- later: DSN / ICSE / robotics assurance workshops (depending on framing)

## 9) Integration contract (portfolio coherence)
- Owns the normative meaning of: tiering, admissibility, PONRs.
- Must not re-own: trace/replay mechanics (P3), benchmark substrate (P4), coordination semantics (P1).
- All claims must be provable from artifacts produced in `datasets/` with a release manifest.

