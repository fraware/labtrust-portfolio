# OPC UA LADS Mapping v0.1 (Interoperability Anchor)

## Why this exists
A credible assurance kernel for autonomous laboratories cannot ignore the likely substrate for device modeling and state semantics. **OPC UA LADS (Laboratory and Analytical Devices)** is an OPC UA Companion Specification that defines device/functional-unit state machines and status variables suitable for connected lab instruments.

This mapping is not a dependency for v0.1, but it reduces “parallel universe risk” by defining how our kernels (Contracts, Replay, MADS) can align with LADS-style semantics.

## LADS concepts (high-level)
- A **LADS Device** contains one or more **FunctionalUnits**.
- Each FunctionalUnit has an **independent state machine** (process-oriented), potentially with sub-state machines (e.g., Running). (See OPC Foundation LADS reference.)

## Mapping to our portfolio
### 1) Contracts (P1): authority and valid transitions
- Treat each FunctionalUnit state machine as a **typed state** with:
  - an authoritative owner (controller, orchestrator, or device-internal authority),
  - admissible transitions (the state machine edges),
  - temporal semantics (event time vs actuation time).

**Contract wedge:**
- The contract layer asserts: “only authorized writers can request transitions,” “device-reported transitions must be consistent with expected machine edges,” and “actuation-time transitions cannot precede authorization events.”

### 2) Replay (P3): trace completeness
- LADS state transitions become first-class trace events:
  - FunctionalUnit transition events
  - Device status changes
  - ControlFunction invocations

Replay at L0 does not require full physical determinism; it requires that:
- state transitions are captured,
- tool invocations and responses that drove those transitions are captured,
- timing is represented in a declared model.

### 3) MADS-CPS (P0): PONRs and admissibility
- PONRs in a lab profile can often be expressed as **state transitions** in LADS-aligned devices (or in orchestration layers interfacing them).
- Admissibility checks can reference:
  - FunctionalUnit state
  - interlock status
  - custody/provenance predicates

## Adapter expectations
We recommend building an explicit `lads_adapter/` (v0.2+) that:
- Ingests OPC UA LADS state updates,
- Emits typed events into TRACE,
- Exposes a normalized “state snapshot” interface to Gatekeeper admissibility checks.

## Concrete mapping (LADS to contract transitions)

- **FU key ownership:** Each LADS FunctionalUnit is mapped to a contract key (e.g. `fu_<deviceId>_<fuId>`). The owner is the controller or orchestrator that holds authority for that FU (from LADS DeviceState or operational context).
- **LADS state machine edges:** A LADS transition (e.g. Idle→Running, Running→Complete) becomes a contract event type (e.g. `task_start`, `task_end`). The event payload carries `task_id` (or fu key), `writer` (actor id), and optional timestamp. Valid transitions are those allowed by the LADS state machine; the contract validator enforces that only the current owner can request the transition and that event time is not before the last accepted write for that key (monotonicity).
- **Timestamps:** Event timestamp (`ts`) is the time of the transition request or device-reported transition. Contract state `_last_ts` per key records the last accepted write time; a write with `ts <= _last_ts[key]` is rejected (stale_write). Reordered delivery (later-ts event applied before earlier-ts) is detected as stale_write when the later event has already been applied.

## Practical guardrail
Do not put LADS-specific code into the kernel.
- Kernel should define abstract types and invariants.
- LADS integration lives in adapters/shims.

