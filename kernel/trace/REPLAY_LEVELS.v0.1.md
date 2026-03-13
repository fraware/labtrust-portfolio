# Replay Levels v0.1

## Purpose
In physical CPS—especially robot-centric laboratories—**bit-identical replay on hardware** is often unattainable due to sensor noise, device nondeterminism, and timing jitter. The assurance objective therefore shifts to **replay levels and nondeterminism detection**:

- **Primary guarantee:** detect and localize nondeterminism relative to a declared replay contract.
- **Secondary guarantee:** reproduce *control-plane* decisions and safety-relevant gating outcomes.

This document defines replay fidelity levels used by the **Replay** paper (P3) and referenced by **MADS-CPS** (P0) and **CPS-MAESTRO** (P4).

## Definitions
- **Control plane:** agent reasoning, tool selection, gate decisions, state transition authorization.
- **Data plane:** raw sensor streams, high-rate telemetry, continuous control loops.
- **Twin:** a simulator/digital twin used to execute the same control-plane decisions under modeled physics.

## Levels
### L0 — Control-plane replay (default)
**Goal:** replay decision-making and enforcement outcomes.

**Required capture:**
- Tool call inputs/outputs (or cryptographic references to them),
- Gate decisions (allow/deny + reason codes),
- State snapshots referenced by admissibility checks,
- Deterministic seeds for injected faults and stochastic components in the harness.

**Guarantee:**
- Given the captured trace, an independent verifier can recompute the same safety metrics and confirm whether the Gatekeeper/PONR checks were correctly applied.

**Expected nondeterminism sources:**
- Wall-clock scheduling, thread timing, asynchronous delivery; these MUST NOT affect control-plane outcomes at L0.

### L1 — Control-plane replay with recorded observations
**Goal:** replay control plane using the trace as the sole source of observations (no live simulator required for the minimal L1 contract).

**L1 definition:** L1 = **control-plane replay with recorded observations**, not physics replay. Observations (event payloads, timestamps, state hashes) are read from the trace; no live simulator or hardware is required for the minimal L1 contract.

**L1 claim (P3):** Observations (event payloads, timestamps, state hashes) are read from the trace; no live simulator or hardware is required for the minimal L1 contract. All observations (event payloads, timestamps, state hashes) come from the trace. A third party can reproduce L1 from the trace and public spec alone, without simulator internals. Twin config validation (stub) implements the L1 contract (L0 + config); full twin replay with a live simulator is future work.

**Required capture (full L1 / twin):**
- All L0 capture,
- Twin configuration identity (build hash, model parameters, environment randomization seeds),
- Explicit mapping from observed sensor events to twin observation interfaces.

**Guarantee:**
- Minimal L1: same as L0 (replay from trace only). Full L1/twin: under declared twin fidelity assumptions, a third party can re-run the episode and reproduce aggregate outcome distributions within declared tolerance.

### L2 — Hardware-assisted replay (aspirational)
**Goal:** replay with physical hardware in the loop.

**Required capture:**
- All L0 capture,
- Hardware configuration identity (device models, firmware versions, calibration state),
- Time synchronization model and jitter bounds,
- Snapshot/restore semantics (or a principled lack thereof).

**Guarantee:**
- Typically distributional (not bitwise). The primary objective becomes auditability and nondeterminism localization.

## Determinism contract (L0)

- **Contract:** For the same trace, replay produces the same state at each event and at final state. State is represented by state_hash_after per event and final_state_hash.
- **Divergence:** If at any event the recomputed state hash differs from the trace’s state_hash_after, or the final state hash differs from final_state_hash, the run has diverged. The replay engine emits structured diagnostics (event seq, expected hash, got hash).
- **Tolerance:** At L0 there is no tolerance for divergence; one bit of difference implies non-replayable.

## Nondeterminism budget
At each level, the system MUST declare a **nondeterminism budget**:

- which sources are tolerated,
- how they are detected,
- what tolerance thresholds apply (e.g., time-window equivalence, distributional acceptance).

For L0, the budget SHOULD be extremely tight: if control-plane outputs diverge, the system is non-replayable.

## What counts as success
- A replay attempt that re-derives the same safety-relevant gating outcomes (especially for PONR actions) and recomputes the same MAESTRO metrics.

## What counts as failure
- Divergent Gatekeeper decisions for the same trace inputs.
- Inability to reconstruct causal chains leading to Tier T2/T3 actions.
- Trace references that cannot be resolved due to missing artifacts or unverifiable integrity.

## Trace corpus (P3)

- **Nondeterminism trap** (`bench/replay/corpus/nondeterminism_trap_trace.json`): first event has wrong state_hash_after; expected divergence at seq 0.
- **Reorder trap** (`bench/replay/corpus/reorder_trap_trace.json`): two events at same logical time; state_hash_after for seq 1 is wrong (as if recorded in different order). Replay in seq order diverges at seq 1. Expected outcome: divergence or pass depending on replay order; with strict seq order, divergence at seq 1.
- **Timestamp reorder trap** (`bench/replay/corpus/timestamp_reorder_trap_trace.json`): two events with distinct timestamps (ts 0.0 and 0.1); state_hash_after for seq 1 is wrong. L0 orders by seq; replay diverges at seq 1. Expected: divergence at seq 1.

