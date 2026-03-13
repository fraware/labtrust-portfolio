/-
  W1 — Gatekeeper/PONR kernel (Lean wedge).
  Minimal model: conformance and contract checks; allow_release is fail-closed.
  Aligns with kernel/mads/PONR_ENFORCEMENT.v0.1.md and impl gatekeeper.allow_release.
-/

namespace Labtrust.W1

/-- Run state relevant to release decision: conformance passed (Tier 2+), contracts OK when checked. -/
structure RunState where
  conformance_ok : Bool
  contracts_ok : Bool
  deriving Repr, BEq

/-- Release is allowed iff conformance passed and (we do not check contracts, or contracts are OK). -/
def allow_release (check_contracts : Bool) (s : RunState) : Bool :=
  s.conformance_ok && (!check_contracts || s.contracts_ok)

/-- Fail-closed: if conformance is not OK, release is denied. -/
theorem fail_closed_conformance (check_contracts : Bool) (s : RunState) (h : s.conformance_ok = false) :
    allow_release check_contracts s = false := by
  unfold allow_release
  rw [h]
  rfl

/-- Fail-closed: when contracts are checked and not OK, release is denied. -/
theorem fail_closed_contracts (s : RunState) (hc : s.contracts_ok = false) :
    allow_release true s = false := by
  unfold allow_release
  rw [hc]
  simp only [Bool.not_true, Bool.false_or, Bool.and_false]

end Labtrust.W1
