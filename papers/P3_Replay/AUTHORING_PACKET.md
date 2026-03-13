# Deterministic Replay for Agentic CPS: Replay Levels, Trace Format, and Nondeterminism Detection

**Paper ID:** P3_Replay  
**Tag:** core-kernel  
**Board path:** MVP → Eval → Draft  
**Kernel ownership:** trace/replay kernel (trace semantics, replay levels, divergence detection)

## 1) One-line question
How do we turn “logs” into **replayable causal programs** suitable for audit, forensics, and reproducible evaluation—without overclaiming full determinism on hardware?

## 2) Scope anchors
- Replay is defined in **levels** (L0 control-plane replay default; L1 twin replay; L2 hardware-assisted). This avoids non-credible “full determinism” claims. citeturn0search0
- The primary guarantee is **nondeterminism detection + localization** relative to a declared replay contract.

## 3) Claims
- **C1:** A CPS-aware trace format plus a determinism contract enables replay sufficient for third-party verification at L0.
- **C2:** Hidden nondeterminism is detectable: same trace ≠ same control-plane behavior triggers structured diagnostics.
- **C3:** Replay supports time-travel debugging: control-plane decisions and enforcement events can be reconstructed and audited.
- **C4:** The toolchain integrates with evidence bundles so replay outcomes are admissible evidence (MADS).

## 4) Outline
1. Motivation: replayability as the missing glue between robotics, distributed systems, and safety cases
2. Replay Levels and nondeterminism budgets (formalized)
3. Trace format: event ontology, causal links, time model
4. Replay engine: deterministic scheduling for L0; twin bindings for L1
5. Divergence detection + attribution
6. Evaluation: nondeterminism traps + fault recovery curves
7. Evidence integration

## 5) Experiment plan
- Scenarios:
  - one MAESTRO scenario;
  - one “nondeterminism trap” scenario (timing race + async reorder).
- Metrics:
  - replay fidelity (L0 exactness),
  - divergence detection rate,
  - localization accuracy,
  - overhead (log size, replay time).
- Baselines: naive logging; partial tracing; best-effort replays.
- Stressors: scheduling jitter, tool flakiness, message reorder.

## 6) Artifact checklist
- `kernel/trace/TRACE.v0.1.schema.json`
- `kernel/trace/REPLAY_LEVELS.v0.1.md`
- replay engine CLI + divergence detector
- trace corpus with expected outputs
- evidence-bundle integration hooks

## 7) Kill criteria
- **K1:** cannot define a determinism contract that is both sufficient and practical.
- **K2:** replay depends on hidden simulator internals (not portable).
- **K3:** If replay fidelity cannot be bounded clearly (e.g. no clear pass/fail, or dependency on simulator internals), narrow claims to **detection/localization only** (no strong fidelity guarantee).

## 8) Target venues
- NSDI/OSDI/DSN (systems + dependability)
- ICSE/FSE (tooling + reproducibility)
- arXiv first (cs.RO, cs.DC)

## 9) Integration contract
- Replay defines trace/replay semantics.
- MAESTRO consumes traces to produce comparable reports.
- MADS consumes replay outputs as admissible evidence.

