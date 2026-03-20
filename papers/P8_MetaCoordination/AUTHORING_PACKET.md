# Meta-Coordination for CPS: Switching Coordination Regimes Under Stress

**Paper ID:** P8_MetaCoordination  
**Tag:** conditional  
**Board path:** Spec → MVP → Eval → Draft  
**Kernel ownership:** meta-controller spec (switching criteria + safety constraints)

## 1) Trigger condition
Proceed only if:
- multiple coordination regimes are actually deployed (centralized, market, swarm, fallback), and
- mode-thrashing/collapse occurs under compound faults.

## 2) Claims
- **C1:** A meta-controller can switch regimes based on measurable stress signals (tail latency, contention, fault rate) while preserving safety constraints.
- **C2:** Switching is auditable and replayable: every regime change is justified by logged criteria and does not silently violate higher-level intent.
- **C3:** Under pre-specified stress, meta-coordination is **non-inferior on paired collapse counts** versus the fixed regime (meta_collapses <= fixed_collapses) while preserving the safety proxy; **strict** count reduction (meta < fixed) is reported separately (`meta_strictly_reduces_collapse`, McNemar on discordant pairs, Wilson CIs on marginal rates). Do not headline “reduces collapse” when the evidence is a tie unless the draft states non-inferiority explicitly.

## 3) Outline
1. Why fixed regimes fail at scale under compound faults
2. Meta-controller model: state, actions, switching criteria
3. Safety conditions: what must never change across regimes
4. Auditability and evidence: how switching becomes admissible
5. Evaluation on MAESTRO fault mixtures

## 4) Experiment plan
- Compare:
  - best fixed regime,
  - naive switching,
  - meta-controller switching.
- Metrics:
  - collapse probability,
  - MTTR,
  - safety violations (must remain 0 for PONRs),
  - mode-thrashing rate.

## 5) Artifact checklist
- meta-controller spec + reference implementation
- switching criteria definitions + thresholds
- MAESTRO scenarios designed to trigger regime stress
- trace events for mode changes + replay compatibility

## 6) Interpretation policy (camera-ready)

- **Non-inferior / tie on counts:** `meta_non_worse_collapse` true (same as legacy `meta_reduces_collapse`: meta collapse_count <= fixed).
- **Strict improvement on counts:** `meta_strictly_reduces_collapse` true (meta collapse_count < fixed).
- **Paired binary inference:** `collapse_paired_analysis.mcnemar_exact_p_value_two_sided` on discordant pairs; marginal rates use Wilson 95% CIs.
- **Continuous paired outcome:** `excellence_metrics.difference_mean` and `difference_ci95` (bootstrap on paired resampling) for tasks_completed; `tasks_completed_ci95` per arm uses Student t on the mean.

## 7) Kill criteria
- **K1:** cannot meet non-inferior collapse vs fixed with no safety regression (trigger_met false).
- **K2:** switching criteria are not measurable or are unstable.
- **K3:** introduces safety regressions or audit gaps.

## 8) Target venues
- arXiv first (cs.RO, cs.AI, eess.SY)
- robotics systems venues if results are strong

## 9) Integration contract
- Must use MAESTRO for evaluation and Replay for auditability.
- Must treat safety constraints (PONRs) as invariant across regimes (MADS).

