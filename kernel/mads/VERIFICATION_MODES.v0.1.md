# Verification Modes v0.1 (Public vs Restricted Auditability)

## Motivation
In regulated or IP-constrained laboratory environments, “third-party verification” usually means **auditable evidence under controlled access**, not public disclosure.

Two external anchors motivate this posture:
- **21 CFR Part 11** requires secure, computer-generated, time-stamped audit trails and that record changes do not obscure prior information (and that audit trails be retained and available for agency review). (See eCFR Part 11.)
- **OECD GLP Data Integrity guidance** emphasizes a risk-based approach across the data lifecycle and understanding data flows to identify critical data. (See OECD 2021 GLP Data Integrity.)

MADS-CPS therefore treats verification as a *mode*, not a single ideology.

## Verification modes
Modes are first-class in the evidence bundle schema: **required** `verification_mode` (`"public"` | `"evaluator"` | `"regulator"`) and optional `redaction_manifest`. Conformance pass/fail is unchanged; modes affect what is considered complete for a given audit (see required_artifacts and redaction_rules below).

**Replay and verifiability:**
- **Public bundles** are verifiable (integrity, schema validation) but are **not** required to be replayable: for public-disclosure-only or when payloads are omitted, L0/L1 replay does not apply; conformance does not require replay_ok for public mode when replay is not applicable.
- **Restricted bundles** (evaluator/regulator) are replayable at L0/L1 when the full trace is available; when the trace is redacted, replay_ok is false and the bundle is audit-only (structure and integrity remain checkable).

### V0 — Public reproducibility (`public`)
- Goal: maximize external scrutiny.
- Constraint: only feasible for synthetic or non-sensitive datasets.
- **required_artifacts:** trace, maestro_report, evidence_bundle, release_manifest (all unredacted).
- **redaction_rules:** none; redaction_manifest must be absent.
- **replay:** public bundles are verifiable but not necessarily replayable (e.g. if payloads omitted for disclosure, replay_ok may be false).

### V1 — Partner / evaluator reproducibility (`evaluator`, restricted)
- Goal: independent verification by a trusted third party under NDA or controlled environment.
- Supports: redacted payloads + hashed references; remote attestation; gated artifact access.
- **required_artifacts:** trace (may be redacted), maestro_report, evidence_bundle, release_manifest.
- **redaction_rules:** if payloads are redacted, evidence_bundle must include redaction_manifest (policy_ref, redacted_artifacts, reason).
- **replay:** when full trace is available, replay at L0/L1 is required (replay_ok true); when trace is redacted, replay_ok false and bundle is audit-only.

### V2 — Regulator / auditor review (`regulator`, restricted, compliance-aligned)
- Goal: satisfy audit trail expectations and evidence admissibility with strict retention and integrity requirements.
- Supports: immutable logs, non-obscuring change history, provenance, role separation, controlled copying.
- **required_artifacts:** same as V1; redaction_manifest required when any artifact is redacted.
- **redaction_rules:** same as V1; access_policy and retention expectations may be documented in profile.
- **replay:** same as V1; full trace implies L0/L1 replay; redacted trace implies replay_ok false, audit-only.

## Redaction hooks (first-class)
Evidence must remain verifiable even when sensitive payloads are not shared.

### E2 redaction path (v0.1)
The same run can be published in redacted form for restricted auditability. Trace event payloads are replaced by content-addressed references: each payload is replaced with `{"_redacted_ref": "<sha256>"}` so that structure (event types, order, timestamps, state_hash_after) is preserved and the trace still validates against the TRACE schema. The evidence bundle then references the redacted trace (and optionally other redacted artifacts); integrity is verified via hashes. Causal structure (event order, types, hashes) remains reconstructible. L0 replay is not run on the redacted trace (replay expects full payloads such as task_id); the evidence bundle for the redacted run has replay_ok false with a note that the trace is audit-only. Implemented in `labtrust_portfolio.evidence.redact_trace_payloads`; demo in `scripts/e2_redaction_demo.py`; tests in `tests.test_thinslice_e2e.TestE2Redaction` verify that the redacted trace validates and that a bundle built from redacted artifacts validates.

Minimum redaction-compatible principle:
- **Do not redact structure.** Keep event types, timestamps, causal links, reason codes, policy identifiers, and cryptographic digests.
- **Redact payloads via references.** Replace sensitive blobs with content-addressed hashes and access handles.

Recommended bundle elements (v0.2 candidate):
- `redaction_manifest`: what was removed, why, under which policy.
- `access_policy`: who can access which blobs, under what process.

## What MADS-CPS guarantees under restricted modes
- Integrity verification of the evidence bundle.
- Reconstruction of causal chains for Tier T2/T3 actions.
- Replay at declared fidelity levels (see Replay Levels).
- Objective conformance checks (tiers) without requiring public disclosure.

## Non-goals
- MADS-CPS does not claim “open science by default.”
- MADS-CPS does not claim certification or compliance with any specific regulation; it supplies auditable artifacts compatible with regulated expectations.

