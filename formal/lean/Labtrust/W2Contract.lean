/-
  W2 — Contract validator kernel (Lean wedge).
  Minimal model: state (ownership, last_ts), event (task_id, ts, writer); validate returns verdict.
  Determinism: same state and event yield the same verdict (pure function).
  Aligns with kernel/contracts/CONTRACT_MODEL.v0.1.md and impl contracts.validate.
-/

namespace Labtrust.W2

/-- Verdict: allow or deny. -/
inductive Verdict where
  | allow
  | deny
  deriving Repr, BEq

/-- Simplified state: ownership and last timestamp per key (keyed by task_id). -/
structure State where
  owner : String → Option String  -- task_id -> writer
  lastTs : String → Float

/-- Simplified event for task_start/task_end. -/
structure Event where
  taskId : String
  ts : Float
  writer : String
  deriving Repr, BEq

/-- Validator: pure function state -> event -> verdict. -/
def validate (s : State) (e : Event) : Verdict :=
  match s.owner e.taskId with
  | some owner => if (owner == e.writer) = false then Verdict.deny else
                  if s.lastTs e.taskId > e.ts then Verdict.deny else Verdict.allow
  | none => if s.lastTs e.taskId > e.ts then Verdict.deny else Verdict.allow

/-- Determinism: same state and event produce the same verdict. -/
theorem validate_deterministic (s : State) (e : Event) :
    validate s e = validate s e := rfl

/-- Determinism (congruence): equal states and events yield equal verdicts. -/
theorem validate_congr (s1 s2 : State) (e1 e2 : Event)
    (hs : s1 = s2) (he : e1 = e2) :
    validate s1 e1 = validate s2 e2 := by
  rw [hs, he]

end Labtrust.W2
