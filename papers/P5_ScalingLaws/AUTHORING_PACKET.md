# When More Agents Hurt: Empirical Predictors of Coordination Tax and Error Amplification in CPS

**Paper ID:** P5_ScalingLaws  
**Tag:** conditional  
**Board path:** Spec → MVP → Eval → Draft  
**Kernel ownership:** none; consumes MAESTRO datasets and emits a predictive model/tool.

## 1) Trigger condition
Proceed only after MAESTRO provides **multi-scenario** datasets sufficient for out-of-sample validation. Otherwise this reads as overclaim.

## 2) One-line question
Can we predict coordination overhead and collapse risk from task properties (resource graph structure, sequential depth, tool density, deadline tightness) to guide architecture choice?

## 3) Claims
- **C1:** Coordination tax and error amplification are predictable from a compact CPS task feature set.
- **C2:** The predictors generalize out-of-sample across scenario families and beat trivial baselines.
- **C3:** The model supports architecture selection decisions with calibrated uncertainty.

## 4) Outline
1. Coordination tax as a systems effect
2. Task feature indices (resource graph + workflow dependency depth + tool density)
3. Response variables (tail latency, MTTR, safety violations, collapse probability)
4. Modeling approach (modest, rigorous)
5. Results: cross-scenario validation + decision rules
6. Limits + data requirements

## 5) Experiment plan
- Data: MAESTRO runs across architectures + fault mixtures
- Baselines: N-only heuristics; simple linear; fixed thresholds
- Validation: held-out scenario family; held-out fault mixtures
- Success criteria: beats baselines + calibrated collapse probability

## 6) Artifact checklist
- feature extractor (from scenario specs + traces)
- dataset builder (MAESTRO → modeling table)
- modeling code + evaluation script
- architecture recommendation CLI

## 7) Kill criteria
- **K1:** does not beat trivial baselines out-of-sample.
- **K2:** features are not computable from public artifacts.
- **K3:** model is scenario-specific and non-actionable.

## 8) Target venues
- NeurIPS / CoRL / RSS (depending on empirical framing)
- arXiv first (cs.RO, cs.LG)

## 9) Integration contract
Consumes: MAESTRO datasets + Replay traces.
Produces: decision guidance for Meta-coordination and system design.

