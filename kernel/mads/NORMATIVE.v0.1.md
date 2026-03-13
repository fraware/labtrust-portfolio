# MADS-CPS Normative Scope (v0.1)

## Object of the standard

MADS-CPS defines a **normative minimum assurance bar** for agentic cyber-physical workflows. The object of the standard is to specify what must exist—controls, telemetry, evidence admissibility, and conformance tiers—so that a third party can verify system-level safety and security **under realistic lab constraints**, without prescribing coordination algorithms or internal optimization.

## Boundary

- **In scope:** Interfaces and evidence. Required artifacts (trace, evaluation report, evidence bundle, release manifest), their schemas, conformance tiers, and the rule that breaking changes require a kernel version bump.
- **Out of scope:** Coordination logic, planning algorithms, hardware determinism, and certification claims. MADS constrains *what is produced and how it is verified*, not how the system produces it.

## Envelope

- **Reference organism:** Robot-centric autonomous lab workflow (see `profiles/lab/v0.1/`). ADePT describes the capability envelope; MADS defines the assurance envelope.
- **Primary scaling anchor:** Resource graphs, campaign concurrency, heterogeneity, and fault recovery—not “thousand agents” by default.
- **Verification posture:** Default is **restricted auditability** (IP/regulatory compatible). Public openness is an optional mode (V0). See [VERIFICATION_MODES.v0.1.md](VERIFICATION_MODES.v0.1.md).

## Definitions (cite kernel)

- **Conformance tier:** A level of assurance tested by artifact presence, schema validation, and (for Tier 2+) replay and evidence-bundle verification. Tier 1: artifacts present and schema-valid. Tier 2: Tier 1 plus replay ok and schema_validation_ok. Tier 3: Tier 2 plus PONR coverage—for each PONR in the lab profile that the scenario can trigger, the trace contains at least one corresponding event (e.g. task_end for a PONR-aligned task).
- **Evidence admissibility:** Evidence is admissible when it has integrity (content-addressed), traceability (trace and report), and replay at declared fidelity (see Replay Levels). Raw logs or transcripts alone are insufficient.
- **Kernel:** The set of versioned JSON Schemas and supporting documents under `kernel/`; the only stable interfaces across papers.
