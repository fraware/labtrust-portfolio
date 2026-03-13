# Lab Profile v0.1 (Reference Organism)

## Why this exists
ADePT-style autonomous labs are **robot-centric, instrument-connected, exception-heavy** systems. The portfolio needs a concrete reference organism that is representative of:
- resource contention (stations, instruments, robots),
- branching workflows and recovery,
- calibration/drift and state validity,
- auditability constraints (IP/regulatory),
- optional planning components (including LLMs, but not assumed).

This profile is intentionally minimal: it provides the smallest domain instantiation needed to drive MADS-CPS, Contracts, Replay, and CPS-MAESTRO.

## What this profile defines
- State types and authority model (`state_types.yaml`)
- Points of no return (PONRs) (`ponrs.yaml`)
- Fault model (`fault_model.yaml`)
- Minimum telemetry fields required for admissibility checks (`telemetry_min_fields.yaml`)

## ADePT alignment
ADePT decomposes autonomy maturity into Adaptability/Learning, Dexterity, Perception, Task Complexity.
This profile is not trying to “measure ADePT.” It uses ADePT as a reminder of operational reality:
- unattended operation removes “we’ll intervene” as a safety crutch,
- connected instruments make authority semantics unavoidable,
- digital twins matter, but fidelity varies; control-plane evidence remains central.

## Agent count vs. resource graph framing
This profile anchors on a **resource graph** (robots, stations, instruments, buffers) and campaign concurrency. Agent count can scale, but the primary difficulty is heterogeneity + contention + recovery, not N=1000 by default.

## MAESTRO scenario alignment
The MAESTRO scenario **toy_lab_v0** (`bench/maestro/scenarios/toy_lab_v0.yaml`) is the thin-slice scenario for this profile. Its task list (receive_sample, centrifuge, analyze, report_results) and fault model (e.g. drop_completion for synthetic thin-slice) are the reference for the minimal runnable pipeline.

## Assurance mapping (P7) and non-goals
The lab profile is used with the assurance pack instantiation (`assurance_pack_instantiation.json`) for standards mapping (P7). **Non-goals:** No certification claim; the mapping is a translation layer only. It does not constitute regulatory certification (e.g. 21 CFR Part 11 or OECD GLP).

