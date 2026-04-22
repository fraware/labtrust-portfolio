# MADS-CPS: A Machine-Checkable Minimum Assurance Bar for Agentic Cyber-Physical Workflows

**Manuscript draft (v0.2). Paper ID: P0_MADS-CPS.** Evaluation artifacts use **MAESTRO_REPORT schema v0.2** (`kernel/eval/MAESTRO_REPORT.v0.2.schema.json`) for `maestro_report.json` validation in Tier 1.

**Central claim.** A minimum assurance bar for agentic CPS can be defined in terms of machine-checkable evidence obligations and conformance predicates, independently of the internal decision policy, and can be verified by third parties under both full and restricted audit modes.

---

## Reproducibility (tables and figures)

From repository root, set `PYTHONPATH=impl/src` and `LABTRUST_KERNEL_DIR=kernel`. On PowerShell: `$env:PYTHONPATH="impl/src"; $env:LABTRUST_KERNEL_DIR="kernel"`. JSON summaries include `run_manifest` (seeds, scenarios, fault flags, script name, optional `version` commit hash when `git` is available).

- **Figure 1 (assurance pipeline):** `python scripts/export_p0_assurance_pipeline.py` (writes `docs/figures/p0_assurance_pipeline.mmd`; optional PNG/PDF via `python scripts/render_p0_mermaid_figures.py` if Mermaid CLI is installed).
- **Table 1 (E1 conformance corpus):** `python scripts/build_p0_conformance_corpus.py --out datasets/runs/p0_conformance_corpus`, then `python scripts/export_e1_corpus_table.py --corpus datasets/runs/p0_conformance_corpus`.
- **Table 2 (E2 verification-mode admissibility matrix):** `python scripts/e2_redaction_demo.py --out datasets/runs/e2_redaction_demo`, then `python scripts/export_e2_admissibility_matrix.py`.
- **Table 3 (E3 + E4 replay-link and controller-independence):** `python scripts/produce_p0_e3_release.py --runs 20 --scenarios lab_profile_v0,toy_lab_v0 --standalone-verifier` (writes `datasets/runs/e3_summary.json`, `datasets/runs/p0_e3_variance.json`, and `datasets/releases/p0_e3_release/` with the verifier in a **separate process**). Canonical frozen release is `lab_profile_v0` (`--release-scenario` defaults to the first scenario). **E4:** `python scripts/run_p0_e4_controller_matrix.py --seeds 20 --scenarios toy_lab_v0,lab_profile_v0,rep_cps_scheduling_v0 --regimes baseline,moderate,stress,coordination_shock --out datasets/runs/p0_e4_controller_matrix.json` (writes `datasets/runs/p0_e4_raw_summary.json`, `datasets/runs/p0_e4_normalized_summary.json`, `datasets/runs/p0_e4_per_seed.jsonl`, `datasets/runs/p0_e4_diagnostics.json`, `datasets/runs/p0_e4_controller_pairs.jsonl`, `datasets/runs/p0_e4_raw_failure_reasons.json`). Then `python scripts/export_p0_table3.py --e3 datasets/runs/e3_summary.json --e4-raw-summary datasets/runs/p0_e4_raw_summary.json --e4-normalized-summary datasets/runs/p0_e4_normalized_summary.json` (prefers strong replay from E4 raw baseline rows and E3 strong replay when present). Focused anomaly exports: `python scripts/export_p0_e4_controller_divergence_table.py` and `python scripts/export_p0_e4_claim_matrix.py`. Semantic interpretation note: `docs/P0_E4_COORDINATION_SHOCK_NOTE.md`. To refresh `e3_summary.json` only (runs already on disk), run `python scripts/replay_link_e3.py --runs 20 --scenarios lab_profile_v0,toy_lab_v0 --standalone-verifier --out datasets/runs/e3_summary.json`.
- **Figure 2 (tier lattice):** `python scripts/export_p0_tier_lattice.py` (writes `docs/figures/p0_tier_lattice.mmd`).
- **Figure 3 (redaction preservation / loss):** `python scripts/export_p0_redaction_figure.py` (writes `docs/figures/p0_redaction_figure.mmd`).
- **E3 latency plot (optional if cited):** `python scripts/plot_e3_latency.py --summary datasets/runs/e3_summary.json --out docs/figures/p0_e3_latency.png`.

**Regenerate `papers/P0_MADS-CPS/generated_tables.md`:** `python scripts/generate_paper_artifacts.py --paper P0` once the artifact paths above exist (or `... --skip-eval-check` to emit partial tables when regenerating piecemeal).

---

## Abstract

Agentic cyber-physical systems (CPS) increasingly couple planning, tool use, sensing, and actuation in workflows where failures are systemic rather than model-local. Existing risk and assurance frameworks provide important guidance, but they do not by themselves specify a minimal set of machine-checkable evidence obligations by which a third party can determine whether a concrete agentic CPS run is admissible for audit, replay, and release under operational constraints. We introduce MADS-CPS, a normative minimum assurance bar for agentic CPS workflows. MADS-CPS defines (i) a declared assurance envelope, (ii) conformance tiers based on artifact presence, schema validity, replay status, and point-of-no-return (PONR) coverage, (iii) verification modes that support restricted auditability through structured redaction, and (iv) fail-closed release gating for irreversible or authoritative transitions. The framework is intentionally agnostic to the internal coordination or planning algorithm: conformance is defined over interfaces and evidence rather than internal optimization. We instantiate MADS-CPS in a robot-centric autonomous laboratory profile and evaluate it through a thin-slice implementation comprising a trace, an evaluation report, an evidence bundle, and a release manifest. Across a conformance challenge set, structured redaction experiments, and replay-link tests, we show that the proposed tiers are mechanically decidable under a declared envelope and that restricted auditability preserves a useful subset of admissibility checks while exposing the limits of replay under redaction. We do not claim certification or regulatory compliance; rather, we provide a concrete, reproducible assurance substrate that makes such assessments more disciplined, auditable, and toolable.

---

## 1. Introduction

Agentic cyber-physical system (CPS) failures are systemic, not model-local. Coordination, sensing, and actuation interact in ways that cannot be verified by examining a single component. When planning, tool use, and actuation are coupled in autonomous workflows, the assurance question shifts from component-level correctness to whether a run produced admissible evidence for audit, replay, and release.

Existing risk and assurance frameworks—including risk-management guidance, capability benchmarking, and safety standards—do not by themselves specify a minimal set of machine-checkable evidence obligations by which a third party can determine whether a concrete agentic CPS run is admissible. The missing object is not more risk guidance or capability metrics, but an operational, machine-checkable admissibility layer for agentic CPS evidence.

**Contributions.** This paper makes four contributions. First, it defines a machine-checkable assurance object for agentic CPS workflows in terms of a declared envelope, evidence admissibility predicates, conformance tiers, and PONR-gated release. Second, it separates assurance from controller internals by defining conformance over externally verifiable artifacts rather than over planning or coordination logic. Third, it introduces restricted verification modes that preserve structural auditability under redaction while making explicit which admissibility checks are lost. Fourth, it provides a thin-slice reference instantiation in an autonomous laboratory profile together with a reproducible conformance checker and replay-link evaluation.

**Scope and delimitation.** We scope the framework to agentic CPS workflows whose interfaces emit trace, evaluation report, evidence bundle, and release manifest under a declared envelope. ADePT is a capability framework for autonomous laboratory robotics; MADS-CPS specifies the assurance envelope and admissibility conditions for runs. We do not claim that MADS-CPS replaces risk frameworks, safety cases, or regulatory quality systems. MADS-CPS is a machine-checkable evidence substrate that can support them.

---

## 2. Problem setting and scope

We consider agentic CPS workflows in which a controller (or coordination layer) produces a trace of events, an evaluation report, an evidence bundle, and a release manifest. The assurance question is: under what conditions can a third party verify that a run is admissible for audit, replay, and release without access to the internal decision policy?

The scope is limited to runs that (i) operate under a declared envelope (scenario/profile and required artifacts), (ii) produce the four artifact types above, and (iii) are evaluated by a conformance checker that depends only on those artifacts and the envelope. We do not address certification, regulatory compliance, or bit-identical hardware replay; we address the minimal evidence obligations and conformance predicates that make third-party verification and restricted auditability possible.

---

## 3. Related work and positioning

**Capability benchmarking for autonomous labs.** ADePT evaluates robotic capability dimensions such as adaptability, dexterity, perception, and task complexity. MADS-CPS instead specifies an assurance envelope and admissibility conditions for runs; the two are complementary (capability vs assurance).

**Risk-management frameworks.** NIST AI RMF and its Generative AI Profile provide governance-oriented risk framing but do not define the specific conformance tiers or replay-linked evidence object proposed here. MADS-CPS operates at the level of operational, machine-checkable evidence obligations.

**Autonomous-product safety standards.** UL 4600 is goal-based and safety-case oriented for autonomous products. Our work is narrower and more operational at the artifact/checker level: machine-checkable admissibility and release gating for agentic CPS runs.

**Assurance-case formalisms.** SACM/GSN represent structured arguments and evidence relationships. MADS-CPS contributes machine-checkable admissibility and release gating for agentic CPS runs, not a replacement for assurance-case structure.

**Regulated data integrity.** OECD GLP and FDA 21 CFR Part 11 motivate trustworthy records, traceability, and audit trails. These support our restricted-auditability story without implying regulatory compliance; we supply auditable artifacts compatible with such expectations.

---

## 4. MADS-CPS model

We propose a normative framework that constrains interfaces and evidence, not internal optimization. The following definitions are the source of the conformance checker and release gate.

### 4.1 Declared envelope

**Definition 1 (Declared envelope).** The *declared envelope* is the scenario/profile and scope under which claims are evaluated. It includes the set of required artifacts, the PONR task set for the scenario, and the verification posture (e.g. public, evaluator, regulator). For a fixed envelope, conformance is defined over externally observable artifact predicates only.

### 4.2 Artifacts

Required artifacts for a run are: (i) trace (`TRACE.v0.1`), (ii) evaluation report (`maestro_report.json`, **MAESTRO_REPORT v0.2**), (iii) evidence bundle (`EVIDENCE_BUNDLE.v0.1`), (iv) release manifest (`RELEASE_MANIFEST.v0.1`). Each has a versioned schema; artifact presence and schema validity are the first-layer predicates.

### 4.3 Evidence bundle and admissibility

**Definition 2 (Evidence bundle).** The *evidence bundle* is the tuple of artifacts (trace, evaluation report, evidence bundle file, release manifest) together with the validation predicates required for admissibility: schema validity, integrity (content-addressed hashes), and replay status at declared fidelity. Evidence is admissible when it has integrity, traceability (trace and report), and replay at declared fidelity; logs or transcripts that lack integrity binding, trace-to-report linkage, or declared replay semantics are insufficient for admissible third-party verification.

### 4.4 Conformance tiers

**Definition 3 (Conformance tier).** *Conformance tiers* form a monotone hierarchy of machine-checkable predicates.

- **Tier 1:** All required artifacts are present and validate against the kernel schemas (including `maestro_report.json` against **MAESTRO_REPORT v0.2**).
- **Tier 2:** Tier 1 plus replay succeeds (state hashes match) and the evidence bundle reports schema_validation_ok and replay_ok (where replay is required by verification mode). This is the default bar for admissible evidence.
- **Tier 3:** Tier 2 plus PONR coverage: for each PONR-aligned task required by the scenario, the trace contains at least one corresponding task_end event.

A run that fails Tier 2 must not be used as the basis for an authoritative release without an explicit, auditable override.

### 4.5 PONR

**Definition 4 (PONR).** A *point of no return (PONR)* is a transition class that requires admissible evidence before authorization. The gate is fail-closed: if admissibility cannot be confirmed, the transition is denied. Overrides are possible but must be logged and auditable. PONR-gated release converts a qualitative notion of "high impact" into an enforceable control: irreversible or authoritative transitions are denied unless admissibility predicates hold or an auditable override is recorded.

### 4.6 Verification modes

**Definition 5 (Verification mode).** *Verification mode* is one of: public, evaluator, regulator (and optionally redacted). It determines required_artifacts and whether replay_ok is required. Under redaction, payloads may be replaced by content-addressed references; structure (event types, order, timestamps, state_hash_after) is preserved, but replay is not run on redacted trace, so replay_ok is false for redacted bundles.

### 4.7 Replay fidelity (L0 / L1)

**Definition 6 (Replay fidelity).** *L0* is control-plane replay: decision and enforcement outcomes are recomputable from the trace. *L1* is L0 plus recorded observations from the trace (no live simulator required for the minimal L1 contract). We do not guarantee bit-identical hardware replay; we guarantee replay levels and nondeterminism detection relative to the declared contract.

---

## 5. Properties

**Proposition 1 (Tier monotonicity).** If a run satisfies Tier 3, then it satisfies Tier 2 and Tier 1.  
*Proof sketch.* By definition, Tier 3 implies Tier 2 (PONR coverage is additive), and Tier 2 implies Tier 1 (replay and schema checks are additive to artifact presence and validity).

**Proposition 2 (Controller-independence).** For a fixed declared envelope and artifact semantics, conformance is invariant to internal controller structure, conditional on identical externally observed artifact predicates.  
*Proof sketch.* The conformance checker reads only artifacts and envelope (e.g. scenario_id, required PONR tasks); it does not branch on adapter or controller identity. Thus any two runs that produce the same artifact predicates receive the same conformance result.

**Proposition 3 (Redaction preservation boundary).** Structure-preserving redaction can preserve schema and integrity predicates while invalidating replay predicates that depend on unreleased payload content.  
*Proof sketch.* Redaction replaces payloads with content-addressed refs; schema and hashes remain checkable. Replay requires payload content to recompute state; hence replay_ok is false under redaction, while schema_validation_ok and integrity_ok can remain true.

---

## 6. Reference instantiation

We instantiate MADS-CPS in a robot-centric autonomous laboratory profile. The thin-slice pipeline produces trace, MAESTRO report, evidence bundle, and release manifest. The conformance checker computes Tier 1/2/3 from these artifacts; the release path enforces the gate (release refused unless Tier 2 or higher). The lab profile defines PONR tasks (e.g. disposition_commit for lab_profile_v0); toy_lab_v0 has no PONR tasks in scope. This instantiation is a reference organism, not a deployed production system; it does not certify any specific deployment.

---

## 7. Experimental design

**Hypothesis.** A minimum assurance bar defined over interfaces and evidence is third-party verifiable under full and restricted audit modes.

**Experiments.**

- **E1 (Conformance corpus):** A challenge set of positive and negative run directories (missing artifact, schema-invalid artifact, hash mismatch, replay mismatch, missing PONR event, etc.). The checker is run on each; we report expected vs observed tier and agreement.
- **E2 (Restricted auditability):** Which predicates remain checkable under full vs redacted trace and under different verification modes (full, evaluator, regulator, public/redacted). We report a verification-mode admissibility matrix.
- **E3 (Replay link):** An independent verifier recomputes the evaluation report from the trace. We run over multiple seeds and report match rate and variance (e.g. tasks_completed, p95 latency) with 95% CIs. The verifier is implemented as a distinct path (standalone script or subprocess) that does not depend on the producer pipeline.
- **E4 (Algorithm-independence):** At least two internally different coordination/planning methods (centralized and rep_cps adapters) emit the same interface-level artifacts. We run the same conformance checker on both and show that conformance depends on artifacts and envelope, not controller identity.

**Metrics.** Tier 1/2/3 pass/fail; checker agreement on challenge set; admissibility matrix (predicate × mode); replay match rate and latency variance; conformance rate per adapter/scenario.

---

## 8. Results

**E1 — Conformance challenge set.** Table 1 summarizes the conformance corpus: for each fault injected, the expected tier outcome, the observed outcome, and whether the checker agreed. The corpus includes valid runs (toy_lab, lab_profile), missing artifact, schema-invalid artifact, hash mismatch, replay mismatch, missing PONR event, and stale release manifest. Regenerate with `build_p0_conformance_corpus.py` and `export_e1_corpus_table.py` (see Appendix).

**E2 — Verification-mode admissibility matrix.** Table 2 shows which predicates (schema_validation_ok, integrity_ok, replay_ok, PONR coverage) remain checkable in full mode, evaluator mode, regulator mode, and public/redacted mode. Under redaction, replay_ok is lost while schema and integrity remain checkable; this supports a subset of admissibility checks under redaction rather than full verification. Regenerate with `e2_redaction_demo.py` and `export_e2_admissibility_matrix.py`.

**E3 — Replay link.** An independent verifier recomputes the evaluation report from the trace over multiple seeds. The verifier can be run as a separate process (`verify_maestro_from_trace.py`) so that the producer and verifier are distinct code paths. Table 3 (with E4) reports replay match rate, latency mean and 95% CI, and conformance rate per scenario and per controller. Use `replay_link_e3.py --standalone-verifier` to use the standalone verifier.

**E4 — Algorithm-independence.** The controller matrix produces the same artifact interface across controller/scenario/regime rows. The same conformance checker is run on each; conformance outcome aligns with artifacts and declared envelope, not with internal controller identity. We run `run_p0_e4_controller_matrix.py --seeds 20 --scenarios toy_lab_v0,lab_profile_v0,rep_cps_scheduling_v0 --regimes baseline,moderate,stress,coordination_shock --out datasets/runs/p0_e4_controller_matrix.json`. The `coordination_shock` regime provides controller-separating evidence: in `rep_cps_scheduling_v0`, controller traces diverge with `maestro_core_hash_equality_rate = 0.0` and nonzero paired event-count differences (`p0_e4_diagnostics.json`), while easy-regime raw conformance remains schema-clean for both controllers.

**Figures.** Figure 1 is the assurance pipeline (trace to report to evidence bundle to conformance check to release); `export_p0_assurance_pipeline.py`. Figure 2 is the tier lattice (what each tier adds); `export_p0_tier_lattice.py`. Figure 3 summarizes what is preserved vs lost under redaction; `export_p0_redaction_figure.py`.

---

## 9. Discussion

The conformance challenge set (E1) demonstrates that the proposed tiers are mechanically decidable under a declared envelope: the checker correctly fails on missing or invalid artifacts, replay mismatch, and missing PONR events. The verification-mode matrix (E2) makes explicit which admissibility checks survive redaction and which do not, supporting restricted auditability without overclaiming full verification. The replay link (E3) shows that a third party can recompute metrics from the trace when the verifier is a distinct path. Algorithm-independence (E4) supports the claim that conformance is defined over external artifacts and envelope, not over the internal coordination or planning algorithm; importantly, raw-failure causal accounting is now explicit in `datasets/runs/p0_e4_raw_failure_reasons.json` and is dominated by Tier-3 PONR misses under stressed lab-profile runs, not adapter-specific MAESTRO schema violations.

---

## 10. Limitations, non-goals, and certification boundary

MADS-CPS does not claim certification or compliance with any specific regulation. It does not claim "open data by default"; the default is restricted auditability. It supplies auditable artifacts compatible with regulated expectations (e.g. 21 CFR Part 11, OECD GLP) without implying certification.

- **Thin-slice is synthetic:** Simulated tasks and timing; no real hardware or physical actuation. The pipeline demonstrates the assurance bar on a synthetic workload.
- **Lab profile is a reference organism:** It instantiates the framework for the portfolio; it is not a deployed production system.
- **PONR gate at release time:** The gate is enforced in code at release (and in conformance Tier 3); it is not executed in a live hardware control loop in this portfolio.
- **Admissibility from logged fields only (K0):** Every normative admissibility condition must be computable from logged fields (trace, evidence bundle, release manifest). Any condition that cannot be checked from these artifacts is non-normative (documentation only).

---

## 11. Conclusion

We introduced MADS-CPS, a machine-checkable minimum assurance bar for agentic CPS workflows. We defined the declared envelope, evidence bundle, conformance tiers, PONR semantics, and verification modes, and we stated three properties: tier monotonicity, controller-independence, and the redaction preservation boundary. We instantiated the framework in an autonomous laboratory profile and evaluated it with a conformance corpus, a verification-mode admissibility matrix, an independent replay link, and an algorithm-independence experiment. The results support the claim that a minimum assurance bar can be defined in terms of machine-checkable evidence obligations and conformance predicates, independently of the internal decision policy, and verified by third parties under full and restricted audit modes. We do not claim certification or regulatory compliance; we provide a concrete, reproducible assurance substrate that can support such assessments.

---

## Appendix: Reproduction and artifact references

**Artifact contents.** The artifact contains the schema set, reference implementation, conformance checker, and reproduction scripts. **Authoritative one-liner commands** for every table and figure are in the **Reproducibility** section at the top of this draft; the list below adds paths, optional steps, and reviewer-oriented pointers.

**Scripts and outputs.** From repo root with `PYTHONPATH=impl/src` and `LABTRUST_KERNEL_DIR=kernel`:

- **Figure 1 (assurance pipeline):** `python scripts/export_p0_assurance_pipeline.py` (output `docs/figures/p0_assurance_pipeline.mmd`). Camera-ready: `python scripts/render_p0_mermaid_figures.py` when Mermaid CLI is available.
- **Table 1 (conformance challenge set):** `python scripts/build_p0_conformance_corpus.py --out datasets/runs/p0_conformance_corpus`, then `python scripts/export_e1_corpus_table.py --corpus datasets/runs/p0_conformance_corpus`.
- **Table 2 (verification-mode admissibility matrix):** `python scripts/e2_redaction_demo.py --out datasets/runs/e2_redaction_demo`, then `python scripts/export_e2_admissibility_matrix.py`.
- **Table 3 (replay-link and conformance by scenario/controller):** E3 at publishable scale uses **20 seeds** per scenario on `lab_profile_v0` and `toy_lab_v0` via `produce_p0_e3_release.py` / `replay_link_e3.py` as in the top repro block; canonical frozen release is `lab_profile_v0`. E4 uses **20 seeds** per controller/scenario/regime row via `run_p0_e4_controller_matrix.py --seeds 20 --scenarios toy_lab_v0,lab_profile_v0,rep_cps_scheduling_v0 --regimes baseline,moderate,stress,coordination_shock --out datasets/runs/p0_e4_controller_matrix.json`, then `python scripts/export_p0_table3.py --e3 datasets/runs/e3_summary.json --e4-raw-summary datasets/runs/p0_e4_raw_summary.json --e4-normalized-summary datasets/runs/p0_e4_normalized_summary.json`. Use `datasets/runs/p0_e4_raw_failure_reasons.json` for raw-failure causal accounting and `datasets/runs/p0_e4_controller_pairs.jsonl` for paired per-seed controller-separating evidence. Legacy compatibility only: `run_p0_e4_multi_adapter.py` remains baseline-summary compatibility support and is not the primary publishable E4 workflow.
- **E3 independent verifier:** `scripts/verify_maestro_from_trace.py TRACE.json [OUTPUT.json]`. Use `replay_link_e3.py --standalone-verifier` so the verifier runs as a separate process.
- **Figure 2 (tier lattice):** `python scripts/export_p0_tier_lattice.py` (output `docs/figures/p0_tier_lattice.mmd`).
- **Figure 3 (redaction preservation/loss):** `python scripts/export_p0_redaction_figure.py` (output `docs/figures/p0_redaction_figure.mmd`).
- **Per-seed E3 markdown (supporting Table 3):** `python scripts/export_e3_table.py`. Run manifest: `datasets/runs/e3_summary.json` (`run_manifest`); release bundle: `datasets/releases/p0_e3_release/release_manifest.json`.

**Kernel and schema paths (for artifact reviewers).** Boundary, envelope, and definitions: `kernel/mads/NORMATIVE.v0.1.md`, `kernel/mads/VERIFICATION_MODES.v0.1.md`, `kernel/mads/PONR_ENFORCEMENT.v0.1.md`. Trace schema: `kernel/trace/TRACE.v0.1.schema.json`. MAESTRO report schema: `kernel/eval/MAESTRO_REPORT.v0.2.schema.json`. Evidence bundle schema: `kernel/mads/EVIDENCE_BUNDLE.v0.1.schema.json`. Release manifest schema: `kernel/policy/RELEASE_MANIFEST.v0.1.schema.json`. Lab profile: `profiles/lab/v0.1/`. Frozen E3 release bundle: `datasets/releases/p0_e3_release/` (includes `conformance.json` when produced via `produce_p0_e3_release.py`); release manifest artifact paths are release-local relative strings (`trace.json`, `maestro_report.json`, `evidence_bundle.json`, `conformance.json`), not host-specific absolute paths.

**Claims and backing.** C1 (controller-independence): Backed by kernel NORMATIVE and VERIFICATION_MODES; E4 (two adapters, same checker); Table 1, Table 3. C2 (machine-checkable tiers): Backed by conformance checker (including MAESTRO_REPORT v0.2 validation), E1 corpus, and `conformance.json` in the frozen release; Table 1, Table 2, Figure 1, Figure 2. C3 (admissibility): Backed by evidence bundle schema, MAESTRO trace-to-report linkage, E2 redaction and Table 2, E3 replay link; Figure 3. C4 (PONR-gated release): Backed by PONR_ENFORCEMENT and release gate in code; Table 2 documents what remains checkable under redaction.
