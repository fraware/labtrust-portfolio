# Incorporating External Reviewer Feedback (Decision + Implementation Notes)

This repository/paper portfolio is intentionally structured as **one normative assurance spine (MADS-CPS)** plus eight **non-overlapping, citeable “hard objects”**. The external reviewer feedback is largely directionally correct: it tightens scope, reduces overreach risk, and improves adoption realism for *robot-centric, unmanned autonomous labs* (ADePT-style).

This document records what we incorporate **now** (v0.1.x additions) versus what we defer to **v0.2+** (schema changes).

**P2 REP-CPS (reviewer-hardening):** Rebuttal matrix and attack-surface ledger: [papers/P2_REP-CPS/REVIEWER_REBUTTAL_MATRIX.md](../papers/P2_REP-CPS/REVIEWER_REBUTTAL_MATRIX.md), [papers/P2_REP-CPS/REVIEWER_ATTACK_SURFACE_LEDGER.md](../papers/P2_REP-CPS/REVIEWER_ATTACK_SURFACE_LEDGER.md).

## A. Decisions (what we incorporate)

### A1. Align the “reference organism” with autonomous labs
- We adopt an **autonomous lab profile** as the canonical reference organism: `profiles/lab/v0.1/`.
- We explicitly treat “thousand-agent” as a *stress case*, not the primary anchor; labs are framed as **resource graphs + campaign concurrency + heterogeneity + fault recovery**.

### A2. Make “third-party verification” compatible with regulated/IP-constrained reality
- Verification is defined as **restricted-access auditability** by default, with **first-class redaction hooks**.
- Public openness is treated as one possible verification mode, not the default.
- See `kernel/mads/VERIFICATION_MODES.v0.1.md`.

### A3. Reframe replay claims: fidelity levels, not “full determinism” on hardware
- We introduce **Replay Levels** (L0 control-plane replay; L1 twin replay; L2 hardware-assisted replay) and a **nondeterminism budget** concept.
- The core guarantee becomes **nondeterminism detection + localization**, not “full determinism everywhere.”
- See `kernel/trace/REPLAY_LEVELS.v0.1.md`.

### A4. Make optional modules explicitly conditional
We treat the following as **conditional modules** with explicit trigger criteria:
- LLM Planning (#6): only if an LLM is in the control plane (planning/toolcalling) or if typed-plan firewalls are needed.
- Meta-coordination (#8): only if multiple regimes are deployed and mode-thrashing/collapse is observed under fault mixtures.
- REP-CPS (#2): sensitivity sharing materially influences scheduling/actuation **in scope**; **rep_cps_scheduling_v0** provides harness-level task influence under gated aggregate; toy/lab scenarios remain parity-scoped (see CONDITIONAL_TRIGGERS P2).
- Scaling laws (#5): only once MAESTRO datasets support out-of-sample prediction beyond trivial baselines.

### A5. Interoperability alignment: OPC UA LADS as a likely device modeling substrate
- We add an explicit interoperability mapping and adapter expectations.
- See `kernel/interop/OPC_UA_LADS_MAPPING.v0.1.md`.

### A6. Lean wedge: formal verification as a credibility amplifier on small kernels
We explicitly scope Lean-based verification to a narrow wedge:
- Gatekeeper/PONR kernel properties,
- Contract validator properties,
- Evidence bundle verifier properties,
- Trace parser/replay semantics at defined replay levels.

See `formal/lean/README.md`.

## B. What we defer (v0.2+)
We do **not** make breaking schema changes in v0.1.

Planned v0.2 changes (if adopted) include:
- Adding `verification_mode` and `redaction_manifest` fields to the EvidenceBundle schema.
- Adding `replay_level` and structured nondeterminism diagnostics fields to TRACE.
- Adding “profile bindings” to MAESTRO reports.

## C. Where feedback was applied
- Paper authoring packets updated to reflect: ADePT alignment, conditional modules, replay levels, restricted verification posture, LADS mapping, Lean wedge.
- New profile skeleton added for labs (`profiles/lab/v0.1/`).

