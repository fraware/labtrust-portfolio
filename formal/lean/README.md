# Lean Wedge (Formal Verification Plan)

## Purpose
Formal verification is high leverage when applied to **small, stable kernels** that are safety/security critical and reused across deployments.

This directory defines a Lean-based wedge for the portfolio. The goal is credibility and correctness for the kernels that make auditability real—not to “verify the lab.”

## Build and run

From this directory (`formal/lean/`):

```bash
lake build
```

Requires [elan](https://github.com/leanprover/elan) and Lean 4 (toolchain in `lean-toolchain`). The library target is `Labtrust`; W3 (evidence bundle verifier) is in `Labtrust/W3EvidenceBundle.lean`.

## Implemented wedges

- **W1 — Gatekeeper/PONR:** Implemented. Minimal model (RunState: conformance_ok, contracts_ok); `allow_release check_contracts s` = conformance_ok ∧ (¬check_contracts ∨ contracts_ok). Fail-closed theorems: conformance false ⇒ deny; contracts checked and false ⇒ deny. See `Labtrust/W1Gatekeeper.lean`. Aligns with `impl/.../gatekeeper.allow_release` and kernel/mads/PONR_ENFORCEMENT.v0.1.md.
- **W2 — Contract validator:** Implemented. Minimal model (State: owner, lastTs; Event: taskId, ts, writer); `validate s e` returns allow/deny. Determinism: same state and event yield the same verdict (validate_congr). See `Labtrust/W2Contract.lean`. Aligns with impl/.../contracts.validate and kernel/contracts/CONTRACT_MODEL.v0.1.md.
- **W3 — Evidence bundle verifier:** Implemented. Encodes required artifact presence, schema validity, and SHA256 format checks; soundness lemmas state that if `verify b = .ok` then required artifacts are present and verification flags hold. See `Labtrust/W3EvidenceBundle.lean`. The two soundness theorem proofs currently use `sorry` (full proofs require Std/Mathlib list tactics).

## Alignment with impl

The W3 spec matches the kernel and impl semantics:

- **Required paths:** `requiredPaths` = trace.json, maestro_report.json, evidence_bundle.json (same as kernel EVIDENCE_BUNDLE expected artifacts).
- **Artifact entry:** path, sha256 (64-char hex), schema_id — same as `impl/src/labtrust_portfolio/evidence.py` `build_evidence_bundle` output and kernel schema.
- **Verification:** schema_validation_ok, replay_ok, replay_diagnostics — same as kernel and impl verification block.

A Python test `tests/test_w3_evidence_bundle.py` checks that impl bundles satisfy the same conditions (has_required_artifacts, valid SHA256 format, verification flags) so the proof and code stay aligned.

## What we will verify (realistic targets)
### W1 — Gatekeeper/PONR kernel (MADS-CPS)
Prove discrete-state properties such as:
- No Tier T2/T3 (PONR-relevant) actuation without a recorded authorization decision.
- Fail-closed: missing admissibility inputs imply deny.
- Override governance invariants: every override is logged, references a reason code, and triggers required post-checks.

### W2 — Contract validator kernel (Contracts)
Prove that the validator enforces:
- ownership/lease invariants,
- valid transition rules,
- temporal ordering constraints (authorization precedes actuation),
- determinism of verdicts given the same event stream.

### W3 — Evidence bundle verifier kernel (MADS + Replay)
Prove correctness of:
- hash chain / signature verification logic,
- required artifact presence checks,
- schema validity checks,
- replay verdict integrity relative to declared replay levels.

### W4 — Trace parser + replay semantics (Replay)
We do **not** promise bit-identical replay on hardware; we promise **replay levels and nondeterminism detection** (detection and localization of divergence).
We do aim to prove:
- the trace parser is total and unambiguous,
- replay scheduling semantics are consistent with the declared replay level,
- nondeterminism detection logic is sound relative to the declared contract.

## What we will not claim
- “We verified the autonomous lab end-to-end.”
- “We verified the LLM planner’s correctness.”
- “We eliminate prompt injection.”

## Near-term execution plan
1) Pick one wedge first: **Evidence bundle verifier (W3)** is the best initial target (small surface, high trust impact).
2) Encode the verifier spec in Lean as a pure function over bundle manifests and hash/signature primitives.
3) Prove basic soundness lemmas: if verifier returns OK, tampering is detectable under the cryptographic assumptions.
4) Bind Lean spec to a reference implementation test harness.

