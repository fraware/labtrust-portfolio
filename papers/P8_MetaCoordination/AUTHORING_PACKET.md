# Meta-Coordination for CPS: Switching Coordination Regimes Under Stress

**Paper ID:** P8_MetaCoordination  
**Tag:** conditional  
**Board path:** Spec → MVP → Eval → Draft  
**Kernel ownership:** meta-controller spec (switching criteria + safety constraints)

## 1) Trigger condition

Proceed only if:

- multiple coordination regimes are actually deployed (centralized, market, swarm, fallback), and
- mode-thrashing or collapse occurs under compound faults.

## 2) Claims

- **C1:** A meta-controller can switch regimes based on measurable stress signals (tail latency, contention, fault rate) while preserving safety constraints.
- **C2:** Switching is auditable and replayable: every regime change is justified by logged criteria and does not silently violate higher-level intent.
- **C3:** Under pre-specified stress, meta-coordination is **non-inferior on paired collapse counts** versus the fixed regime (`meta_non_worse_collapse`; legacy alias `meta_reduces_collapse` means meta ≤ fixed on counts). **Strict** improvement (`meta_strictly_reduces_collapse`) and McNemar / Wilson marginal rates are reported separately in `collapse_paired_analysis`. Headlines must distinguish non-inferiority from strict reduction.

## 3) Outline

1. Why fixed regimes fail at scale under compound faults  
2. Meta-controller model: state, actions, switching criteria  
3. Safety conditions: what must never change across regimes  
4. Auditability and evidence: how switching becomes admissible  
5. Evaluation on MAESTRO fault mixtures and robustness matrix  

## 4) Experiment plan

- Compare: best **fixed** regime (centralized thin slice), **meta-controller** (`fault_threshold=1`, hysteresis, latency/contention triggers), and **naive** switching (`fault_threshold=0` for the naive arm only, via `meta_eval.py --run-naive`).
- Optional two-path stress: `--fallback-adapter retry_heavy` so post-switch outcomes are attributed to the RetryHeavy run (`outcome_attribution_note` in `comparison.json`).
- Metrics: paired collapse counts, `tasks_completed` (with paired bootstrap CI where exported), recovery latency proxy (`time_to_recovery_ms_mean` when recorded), PONR and safety violation totals, regime switch counts, robustness campaign rows (`campaign_summary.json`).

## 5) Artifact checklist

- `kernel/meta/META_CONTROLLER_SPEC.v0.1.md` + `impl/src/labtrust_portfolio/meta_controller.py` + `impl/src/labtrust_portfolio/adapters/meta_adapter.py`
- Primary: `datasets/runs/meta_eval/comparison.json`, `collapse_sweep.json` (`p8_meta_eval_v0.3`)
- v1 mirror: `datasets/runs/meta_eval/scenario_regime_stress_v1/comparison.json` (and sweep under same prefix)
- Optional lab slice: `datasets/runs/meta_eval/scenario_lab_profile_v0/comparison.json`
- Robustness: `datasets/runs/meta_eval/robustness_campaign/campaign_summary.json`
- Tables: `papers/P8_MetaCoordination/generated_tables.md` (from `export_meta_tables.py`)

## 6) Interpretation policy (camera-ready)

- **Non-inferior on counts:** `meta_non_worse_collapse` true (meta paired collapse count ≤ fixed).
- **Strict improvement on counts:** `meta_strictly_reduces_collapse` true (meta < fixed on paired counts).
- **Paired binary inference:** `collapse_paired_analysis.mcnemar_exact_p_value_two_sided`; Wilson 95% CIs on marginal collapse rates.
- **Continuous paired outcome:** `excellence_metrics.difference_mean` and `difference_ci95` (bootstrap on paired resampling); per-arm mean CIs use Student *t* on the arm mean.

## 7) Kill criteria

- **K1:** cannot meet non-inferior collapse vs fixed with no safety regression (`trigger_met` false).
- **K2:** switching criteria are not measurable or are unstable.
- **K3:** introduces safety regressions or audit gaps.

## 8) Target venues

- arXiv first (cs.RO, cs.AI, eess.SY)
- robotics systems venues if results are strong

## 9) Integration contract

- Must use MAESTRO for evaluation and Replay for auditability.
- Must treat safety constraints (PONRs) as invariant across regimes (MADS).

## 10) Publishable commands (reference)

- Full portfolio slice: `PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/run_paper_experiments.py --paper P8`
- Tables (primary + campaign matrix):  
  `python scripts/export_meta_tables.py --comparison datasets/runs/meta_eval/comparison.json --table2 --campaign datasets/runs/meta_eval/robustness_campaign/campaign_summary.json`
- Strict verifier:  
  `python scripts/verify_p8_meta_artifacts.py --comparison datasets/runs/meta_eval/comparison.json --sweep datasets/runs/meta_eval/collapse_sweep.json --strict-publishable`
- Robustness campaign:  
  `python scripts/p8_robustness_campaign.py --strict-publishable`
