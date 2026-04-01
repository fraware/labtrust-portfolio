# From Coordination to Safety Case: A Traceable Assurance Argument for Multi-Agent CPS

**Paper ID:** P7_StandardsMapping  
**Tag:** core-kernel  
**Board path:** Spec → MVP → Eval → Draft  
**Kernel ownership:** assurance-pack templates (hazards→controls→evidence→audit traces)

## 1) One-line question
How do we translate the portfolio’s executable artifacts (gates, traces, evidence bundles) into **auditor-legible** assurance arguments without compliance cosplay?

## 2) Scope anchors
- UL 4600 is safety-case oriented; IEC 62443 is lifecycle security for industrial control; neither implies “certification by mapping.”
- Regulated lab expectations emphasize secure audit trails and lifecycle/data-flow discipline (e.g., 21 CFR Part 11 audit trails; OECD GLP data integrity).

## 3) Claims
- **C1:** A structured “assurance pack” template enables traceable mapping: hazards → controls/invariants → evidence artifacts → audit traces.
- **C2:** The mapping is mechanically checkable (artifact presence + trace reconstruction), not narrative.
- **C3:** Worked examples across lab and real-world proxy scenarios (warehouse, traffic) demonstrate audit completeness and replayability under stressed conditions.

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
- Execute robust matrix (scenario x fault-regime x seed) with
  `scripts/run_assurance_robust_eval.py`, and report aggregate pass-rate,
  evidence/trace validity rates, and real-world proxy performance.

## 6) Artifact checklist
- `kernel/assurance_pack/ASSURANCE_PACK.v0.1.schema.json`
- hazard log template + invariant registry template
- worked instantiations using `profiles/lab/v0.1/`,
  `profiles/warehouse/v0.1/`, and `profiles/medical_v0.1/`
- checker that validates mapping completeness
- robust eval artifact `datasets/runs/assurance_eval/robust_results.json`

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

