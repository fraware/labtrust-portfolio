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
4. Replay engine: deterministic scheduling for L0; baselines (apply-only, final-hash-only); twin bindings for L1
5. Divergence detection + attribution (witness slices)
6. Evaluation: corpus traps + field-style pass trace + multi-seed thin-slice overhead + baselines (not fault recovery curves; recovery-style metrics belong to P4 MAESTRO)
7. Evidence integration

## 5) Experiment plan
- Scenarios:
  - MAESTRO thin-slice (multi-seed family for sensitivity);
  - trap corpus (nondeterminism, reorder, timestamp reorder, hash mismatch);
  - field-style pass trace (TRACE-conformant proxy for external mapping).
- Metrics:
  - replay fidelity (L0 pass/fail per trace),
  - corpus outcome accuracy and Wilson CI,
  - localization at expected seq for traps,
  - overhead: empirical mean, stdev, p95, p99; bootstrap CIs; overhead vs trace size.
- Baselines (implemented in `replay_eval.py`): apply-only (no hash); final-hash-only (no per-event localization); witness_window=0 ablation on pass path.
- Cross-reference: fault sweeps and recovery proxies are evaluated in P4 (`maestro_fault_sweep`), not in P3.

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

