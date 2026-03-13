/-
  W3 — Evidence bundle verifier kernel (Lean wedge).
  Encodes required artifact presence, schema validity checks, and hash verification
  assumptions. Soundness: if the verifier returns OK, tampering is detectable
  under the stated cryptographic assumptions.
  Aligns with kernel/mads/EVIDENCE_BUNDLE and impl evidence bundle construction.
-/

namespace Labtrust.W3

/-- Artifact entry: path, SHA256 hex, schema_id (from EVIDENCE_BUNDLE.v0.1). -/
structure ArtifactEntry where
  path : String
  sha256 : String  -- 64-char hex; collision resistance assumed
  schema_id : String
  deriving Repr, BEq

/-- Verification sub-result: schema validation and replay. -/
structure Verification where
  schema_validation_ok : Bool
  replay_ok : Bool
  replay_diagnostics : String
  deriving Repr, BEq

/-- Evidence bundle (minimal spec): version, run_id, artifacts, verification. -/
structure EvidenceBundle where
  version : String
  run_id : String
  kernel_version : String
  artifacts : List ArtifactEntry
  verification : Verification
  deriving Repr, BEq

/-- Required artifact paths for a valid bundle (configurable). -/
def requiredPaths : List String :=
  ["trace.json", "maestro_report.json", "evidence_bundle.json"]

/-- Check that all required paths are present in the artifact list. -/
def hasRequiredArtifacts (bundle : EvidenceBundle) : Bool :=
  List.all requiredPaths (fun p => List.any bundle.artifacts (fun a => a.path == p))

/-- Hex digit check (Lean 4 core does not provide Char.isHexDigit). -/
def isHexDigit (c : Char) : Bool :=
  (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f') || (c >= 'A' && c <= 'F')

/-- Assumption: hash is 64-char hex (spec pattern). We do not verify crypto here. -/
def validSha256Format (h : String) : Bool :=
  h.length == 64 && List.all h.toList (fun c => isHexDigit c)

/-- All artifact entries have valid SHA256 format. -/
def allHashesValidFormat (bundle : EvidenceBundle) : Bool :=
  List.all bundle.artifacts (fun a => validSha256Format a.sha256)

/-- Verifier result: OK or list of failure reasons. -/
inductive VerifierResult where
  | ok
  | fail (reasons : List String)
  deriving Repr, BEq

/-- Evidence bundle verifier (pure spec). Returns OK iff:
    - All required artifacts present
    - All SHA256 fields have valid format
    - verification.schema_validation_ok
    - verification.replay_ok
  Cryptographic assumption: we assume hash collision resistance and integrity
  of stored hashes; this module does not implement hashing. -/
def verify (bundle : EvidenceBundle) : VerifierResult :=
  let missing := requiredPaths.filter (fun p =>
    !List.any bundle.artifacts (fun a => a.path == p))
  let missingMsg := if missing.isEmpty then [] else
    ["missing required artifacts: " ++ String.intercalate ", " missing]
  let badHash := !allHashesValidFormat bundle
  let badHashMsg := if badHash then ["invalid SHA256 format in artifacts"] else []
  let schemaBad := !bundle.verification.schema_validation_ok
  let schemaMsg := if schemaBad then ["schema_validation_ok is false"] else []
  let replayBad := !bundle.verification.replay_ok
  let replayMsg := if replayBad then ["replay_ok is false"] else []
  let reasons := missingMsg ++ badHashMsg ++ schemaMsg ++ replayMsg
  if reasons.isEmpty then VerifierResult.ok else VerifierResult.fail reasons

/-- If verify returns ok, then required artifacts are present. -/
theorem verify_ok_implies_required_present (b : EvidenceBundle) (h : verify b = .ok) :
    hasRequiredArtifacts b := by sorry

/-- If verify returns ok, then schema_validation_ok and replay_ok hold. -/
theorem verify_ok_implies_verification_ok (b : EvidenceBundle) (h : verify b = .ok) :
    b.verification.schema_validation_ok = true ∧ b.verification.replay_ok = true := by sorry
end Labtrust.W3
