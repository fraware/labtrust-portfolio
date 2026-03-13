# PONR Enforcement Semantics (v0.1)

## Purpose

Points of no return (PONRs) operationalize “high impact” by requiring **mechanically checkable admissibility** before irreversible or authoritative transitions. This document specifies when admissibility is checked, fail-closed behavior, and overrides.

## When admissibility is checked

- **Before a PONR transition:** Any transition classified as a PONR in the lab profile (e.g. decision commit, sample disposition change) must be gated. The gate checks that the evidence required for that PONR is admissible: trace and evidence bundle are present, schema-valid, and (for Tier 2) replay has succeeded.
- **At release:** A release manifest is produced only when the run’s evidence bundle is admissible (conformance Tier 2 or higher).

## Fail-closed behavior

- If admissibility cannot be confirmed (missing artifact, schema failure, replay failure), the system **must not** treat the transition as authorized. Default is **deny**.
- The conformance checker returns FAIL when any required check fails; a run that fails Tier 2 must not be used as the basis for an authoritative release without explicit override (see below).

## Overrides

- **Override** is an explicit, logged exception that allows a transition or release despite a conformance failure. Overrides are out of scope for the normative kernel in v0.1; implementations that support overrides must log them in the trace or evidence bundle (e.g. reason code, policy identifier) so that auditors can see that an override was applied.
- MADS does not define who may authorize an override; that is an organizational policy. The kernel only requires that the override be auditable.

## Relation to Gatekeeper

The Gatekeeper (or equivalent component) enforces PONR semantics by (1) requiring admissible evidence before allowing a PONR transition, and (2) failing closed when evidence is missing or invalid. The lab profile defines which transitions are PONRs (see `profiles/lab/v0.1/ponrs.yaml`).
