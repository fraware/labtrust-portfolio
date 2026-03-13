# Meta-Coordination for CPS: Switching Regimes Under Stress

**Draft (v0.1). Paper ID: P8_MetaCoordination. Conditional paper; trigger and scope: docs/CONDITIONAL_TRIGGERS.md (P8).**

**Reproducibility.** From repo root, with `PYTHONPATH=impl/src` and `LABTRUST_KERNEL_DIR=kernel`. See [REPORTING_STANDARD.md](../docs/REPORTING_STANDARD.md) and [RESULTS_PER_PAPER.md](../docs/RESULTS_PER_PAPER.md). Run_manifest: comparison.json (seeds, scenario_id, fault_threshold, excellence_metrics); collapse_sweep.json (seeds, drop_probs, scenario_id). Conditional trigger: see Limitations and docs/CONDITIONAL_TRIGGERS.md (P8).

**Minimal run (under 20 min):** `python scripts/meta_eval.py --run-naive --fault-threshold 0` then `python scripts/export_p8_meta_diagram.py` then `python scripts/export_meta_tables.py --comparison datasets/runs/meta_eval/comparison.json` then `python scripts/meta_collapse_sweep.py` then `python scripts/plot_meta_collapse.py --sweep datasets/runs/meta_eval/collapse_sweep.json`.

**Publishable run:** Default 20 seeds; run_manifest in comparison.json and collapse_sweep.json. For non-vacuous trigger: run meta_collapse_sweep first, pick drop_prob where collapse_count > 0, then meta_eval with that --drop-prob (see section 7).

- **Figure 0:** `python scripts/export_p8_meta_diagram.py` (output `docs/figures/p8_meta_diagram.mmd`). Render Mermaid to PNG for camera-ready.
- **Table 1, Table 2:** `python scripts/meta_eval.py --run-naive --fault-threshold 0` (writes comparison.json), then `python scripts/export_meta_tables.py --comparison datasets/runs/meta_eval/comparison.json` (use `--table2` for per-seed table).
- **Figure 1:** `python scripts/meta_collapse_sweep.py` (writes collapse_sweep.json), then `python scripts/plot_meta_collapse.py --sweep datasets/runs/meta_eval/collapse_sweep.json` (output `docs/figures/p8_meta_collapse.png`).
- For non-vacuous trigger: run meta_collapse_sweep.py first, then meta_eval with that --drop-prob (see section 7).

## 1. Motivation

Multiple coordination regimes (centralized, blackboard, fallback) exist; under compound faults, mode-thrashing or collapse can occur. Meta-controller switches regimes by criteria while keeping PONRs invariant and every switch auditable.

## 2. Meta-controller model and formal switch criterion

Spec: `kernel/meta/META_CONTROLLER_SPEC.v0.1.md`. State: current_regime, fault_count, latency_p95.

**Figure 0 — Meta-controller regimes and switch.** Centralized and fallback regimes; switch to fallback when fault_count or latency_p95 exceeds threshold; revert when below 0.5*threshold. Regenerate with `python scripts/export_p8_meta_diagram.py` (output `docs/figures/p8_meta_diagram.mmd`). Actions: switch_regime(to_regime). **Formal switch criterion (v0.1):** threshold-based. Revert is checked first (no hysteresis): if in fallback and fault_count <= 0 and latency_p95 < 0.5 * latency_threshold_ms, switch back to centralized. Fault-based switch to fallback requires fault_count >= hysteresis_consecutive and fault_count > fault_threshold (thrash control). Latency-based switch to fallback: if latency_p95 > latency_threshold_ms, switch to fallback (no hysteresis). Reference impl: `meta_controller.decide_switch`; spec: `kernel/meta/META_CONTROLLER_SPEC.v0.1.md`. Regret-based or safety-bound-based switching are future work.

## 3. Trace events and auditability

Event type `regime_switch` with payload from_regime, to_regime, reason. Emitted by meta-controller; replay can reconstruct regime history. MetaAdapter (`adapters/meta_adapter.py`) runs scenario, evaluates switch criteria from report (fault count, p95), injects regime_switch event into trace.

## 4. Regime-stress scenario and evaluation

`bench/maestro/scenarios/regime_stress_v0.yaml`: high fault load to trigger meta-controller. Evaluation: `scripts/meta_eval.py` with `--run-naive` and `--fault-threshold 0` compares fixed (CentralizedAdapter), meta-controller, and naive switching baseline. Output: `comparison.json` (fixed, meta_controller, naive_switch_baseline, meta_reduces_collapse, no_safety_regression).

**Table 1 — Comparison (fixed vs meta vs naive).** Source: `datasets/runs/meta_eval/comparison.json`. Run `meta_eval.py --run-naive --fault-threshold 0` to regenerate; run manifest (seeds, scenario_id, fault_threshold) in comparison.json. Example (regime_stress_v0, fault_threshold=0, 10 seeds):

| Regime | tasks_completed_mean | collapse_count | regime_switch_count_total |
|--------|----------------------|----------------|---------------------------|
| fixed (Centralized) | 3.00 | 1 | — |
| meta_controller | 3.00 | 1 | 6 |
| naive (fault_threshold=0) | 3.00 | — | 6 |

**Table 2 — Per-seed.** Run `python scripts/export_meta_tables.py --comparison datasets/runs/meta_eval/comparison.json --table2` for per-seed tasks_completed, regime_switch_count, and collapse. **Figure 1 — Collapse sweep.** tasks_completed (mean) and collapse rate vs drop_completion_prob from collapse_sweep.json. Regenerate: `python scripts/meta_collapse_sweep.py` then `python scripts/plot_meta_collapse.py --sweep datasets/runs/meta_eval/collapse_sweep.json` (output `docs/figures/p8_meta_collapse.png`). Run manifest in collapse_sweep.json.

## 5. Comparison to other meta-learning and regime-switching work

| Aspect | P8 (this work) | Context-dependent / MAB policy selection | Fault-tolerant control mode switching |
|--------|----------------|------------------------------------------|----------------------------------------|
| Switch criterion | Threshold-based (fault_count, latency_p95) | Often regret or bandit reward | Stability / Lyapunov or heuristic |
| Execution path | Single thin-slice; switch = trace event only (v0.1) | Policy selects among options | Mode switch changes controller |
| Auditability | regime_switch events in trace; PONR invariant | Varies | Often closed-loop only |
| Safety | no_safety_regression (meta >= 90% fixed) | Learning-theoretic bounds (when present) | Control-theoretic guarantees |

We emphasize auditability and PONR invariance; no claim to learning or control-theoretic optimality.

## 6. Limitations

Scope and conditional triggers: [EXPERIMENTS_AND_LIMITATIONS.md](../docs/EXPERIMENTS_AND_LIMITATIONS.md). Per-paper:

- **Conditional paper:** Trigger requires meta to beat best fixed regime in at least one stress regime with no safety regression. If collapse_count is 0 under default settings, trigger is vacuous; run collapse_sweep then meta_eval with higher drop_prob for non-vacuous evaluation. See docs/CONDITIONAL_TRIGGERS.md.
- **No actual regime implementation difference:** Meta and naive both use the same thin-slice; only the decision to inject a regime_switch event differs. No second coordination algorithm (e.g. blackboard vs centralized) is invoked; future work: wire meta to delegate to different adapters.
- **Collapse may not be observed:** Under default stress (e.g. drop_completion_prob=0.15), tasks_completed may stay above threshold so collapse_count = 0; "meta reduces collapse" is then vacuously true. For non-vacuous evaluation, run `meta_collapse_sweep.py` to find a drop_prob where collapse occurs, then run `meta_eval.py` with that drop_prob (see Reproducibility).
- **Toy:** Regimes are the same thin-slice execution; no real multiple coordination algorithms or real stress (e.g. network partitions).
- **Future work:** Second coordination regime (meta delegating to Blackboard vs Centralized); regret-based or safety-bound-based switch criterion; real stress (e.g. network partitions). See kernel/meta/META_CONTROLLER_SPEC.v0.1.md.

## 7. Methodology and reproducibility

**Methodology:** Hypothesis—meta-controller reduces collapse vs best fixed regime under compound faults; PONRs remain invariant. Metrics: regime_switch count, collapse (e.g. tasks_completed below threshold), mode-thrashing rate. Kill criterion: safety regression at PONRs or audit gap (regime change not logged). Baselines: best fixed regime, naive switching. Portfolio criteria: `docs/STATE_OF_THE_ART_CRITERIA.md`.

**Reproducibility:** Run full eval: `python scripts/meta_eval.py --run-naive --fault-threshold 0` (writes `datasets/runs/meta_eval/comparison.json`). Tables: `python scripts/export_meta_tables.py --comparison datasets/runs/meta_eval/comparison.json` (add `--table2` for per-seed). Figure 1: `python scripts/meta_collapse_sweep.py` then `python scripts/plot_meta_collapse.py --sweep datasets/runs/meta_eval/collapse_sweep.json`. Run manifests: comparison.json (seeds, scenario_id, fault_threshold, script; success_criteria_met, excellence_metrics); collapse_sweep.json (seeds, drop_probs, scenario_id, script). For a **non-vacuous trigger** (collapse actually occurs so meta_reduces_collapse is meaningful): (1) Run `python scripts/meta_collapse_sweep.py --drop-probs 0.2,0.25,0.3,0.35 --seeds 1,2,3,4,5,6,7,8,9,10`; from collapse_sweep.json identify a drop_prob where collapse_count > 0. (2) Run `python scripts/meta_eval.py --run-naive --fault-threshold 0 --drop-prob <that_drop_prob>`. Integration test: `tests/test_meta_p8.py` runs meta_eval with --out <temp>, asserts comparison.json (no_safety_regression, meta_reduces_collapse, regime_switch_count_total >= 1), and runs export_meta_tables.py; unit tests cover decide_switch and regime_switch_event. Scenario: `bench/maestro/scenarios/regime_stress_v0.yaml`. Spec: `kernel/meta/META_CONTROLLER_SPEC.v0.1.md`.

---

**Claims and backing**

| Claim | Artifact / backing |
|-------|---------------------|
| C1 Spec + impl | META_CONTROLLER_SPEC, decide_switch, regime_switch_event |
| C2 PONRs + audit | Safety condition in spec; regime_switch payload (from_regime, to_regime, reason) |
| C3 Scenario + adapter | regime_stress_v0 scenario, MetaAdapter trace events, comparison.json |
| No regime impl difference | Limitations; meta and naive same thin-slice |
| Collapse may be vacuous | Limitations; collapse_count = 0 under current stress |
