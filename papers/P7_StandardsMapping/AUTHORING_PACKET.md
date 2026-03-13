# From Coordination to Safety Case: A Traceable Assurance Argument for Multi-Agent CPS

**Paper ID:** P7_StandardsMapping  
**Tag:** core-kernel  
**Board path:** Spec → MVP → Eval → Draft  
**Kernel ownership:** assurance-pack templates (hazards→controls→evidence→audit traces)

## 1) One-line question
How do we translate the portfolio’s executable artifacts (gates, traces, evidence bundles) into **auditor-legible** assurance arguments without compliance cosplay?

## 2) Scope anchors
- UL 4600 is safety-case oriented; IEC 62443 is lifecycle security for industrial control; neither implies “certification by mapping.”
- Regulated lab expectations emphasize secure audit trails and lifecycle/data-flow discipline (e.g., 21 CFR Part 11 audit trails; OECD GLP data integrity). citeturn1search0turn1search1

## 3) Claims
- **C1:** A structured “assurance pack” template enables traceable mapping: hazards → controls/invariants → evidence artifacts → audit traces.
- **C2:** The mapping is mechanically checkable (artifact presence + trace reconstruction), not narrative.
- **C3:** One worked example (lab profile) demonstrates audit completeness and replayability.

## 4) Outline
1. Why standards mappings often fail (template theater)
2. Assurance pack structure and schemas
3. Mapping rules to portfolio artifacts (Gatekeeper, trace, bundle)
4. Example instantiation (lab profile)
5. What this does *not* claim (no certification)

## 5) Experiment plan
- Not performance. Evidence quality.
- Show that an independent reviewer can:
  - verify evidence bundle,
  - reconstruct PONR causal chains,
  - map denials/allows to hazards and controls.

## 6) Artifact checklist
- `kernel/assurance_pack/ASSURANCE_PACK.v0.1.schema.json`
- hazard log template + invariant registry template
- worked instantiation using `profiles/lab/v0.1/`
- checker that validates mapping completeness

## 7) Kill criteria
- **K1:** mapping cannot be made mechanical; becomes prose.
- **K2:** cannot produce a worked example that survives hostile review.
- **K7:** If mapping becomes "template theater" (prose without machine-checkable linkage), stop and tighten: every claim in the mapping must be checkable by script or schema.

## 8) Target venues
- arXiv first (cs.SE, cs.RO, cs.CR)
- safety/assurance workshops; dependability venues

## 9) Integration contract
- Depends on MADS definitions for tiers/PONRs.
- Depends on Replay and MAESTRO for trace/report artifacts.

