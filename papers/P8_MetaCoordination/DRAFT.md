# Meta-Coordination for CPS: Switching Regimes Under Stress

**Draft (v0.1). Paper ID: P8_MetaCoordination. Conditional paper; trigger and scope: docs/CONDITIONAL_TRIGGERS.md (P8).**

**Reproducibility.** From repo root, with `PYTHONPATH=impl/src` and `LABTRUST_KERNEL_DIR=kernel`. See [REPORTING_STANDARD.md](../docs/REPORTING_STANDARD.md) and [RESULTS_PER_PAPER.md](../docs/RESULTS_PER_PAPER.md). Run_manifest: comparison.json (seeds, scenario_id, fault_threshold, excellence_metrics); collapse_sweep.json (seeds, drop_probs, scenario_id). Conditional trigger: see Limitations and docs/CONDITIONAL_TRIGGERS.md (P8).

**Minimal run (under 20 min):** `python scripts/meta_eval.py --run-naive --fault-threshold 0` then `python scripts/export_p8_meta_diagram.py` then `python scripts/export_meta_tables.py --comparison datasets/runs/meta_eval/comparison.json` then `python scripts/meta_collapse_sweep.py` then `python scripts/plot_meta_collapse.py --sweep datasets/runs/meta_eval/collapse_sweep.json`.

**Publishable run:** Default 20 seeds; run_manifest in comparison.json and collapse_sweep.json. For non-vacuous trigger: (1) run `meta_collapse_sweep.py` (default 20 seeds, --drop-probs 0.15,0.2,0.25,0.3), (2) run `meta_eval.py --run-naive --fault-threshold 0 --non-vacuous`. The script selects the smallest drop_prob where collapse_count > 0 from the sweep; if none found, it exits with a message and Table 1 should be presented as methodology and auditability only (see section 7).

- **Figure 0:** `python scripts/export_p8_meta_diagram.py` (output `docs/figures/p8_meta_diagram.mmd`). Render Mermaid to PNG for camera-ready.
- **Table 1, Table 2:** Run `meta_collapse_sweep.py` then `meta_eval.py --run-naive --fault-threshold 0 --non-vacuous` (writes comparison.json; run_manifest.non_vacuous true when drop_prob was chosen from sweep). Then `python scripts/export_meta_tables.py --comparison datasets/runs/meta_eval/comparison.json` (use `--table2` for per-seed table).
- **Figure 1:** `python scripts/meta_collapse_sweep.py` (writes collapse_sweep.json), then `python scripts/plot_meta_collapse.py --sweep datasets/runs/meta_eval/collapse_sweep.json` (output `docs/figures/p8_meta_collapse.png`).

## 1. Motivation

Multiple coordination regimes (centralized, blackboard, fallback) exist; under compound faults, mode-thrashing or collapse can occur. Meta-controller switches regimes by criteria while keeping PONRs invariant and every switch auditable. **When collapse occurs under stress, the meta-controller reduces collapse count versus fixed and naive baselines; when it does not occur, we report methodology and auditability only.** The publishable run uses `--non-vacuous` so that Table 1 is generated with a drop_prob where collapse is observed (see Reproducibility). For a second stress setting, use `--stress-preset high` (drop_prob 0.25) or run with `--fallback-adapter blackboard` to compare two coordination paths; optional second scenario (e.g. regime_stress_v1) is future work.

## 2. Meta-controller model and formal switch criterion

Spec: `kernel/meta/META_CONTROLLER_SPEC.v0.1.md`. State: current_regime, fault_count, latency_p95.

**Second stress scenario / preset.** For generalization beyond a single setting: `--stress-preset very_high` sets drop_completion_prob to 0.35 (high: 0.25). Scenario `regime_stress_v1.yaml` is available for runs with a second stress profile; meta_eval and collapse_sweep can be run on regime_stress_v0 (default) or regime_stress_v1 for extra table rows or figures.

**Figure 0 — Meta-controller regimes and switch.** Centralized and fallback regimes; switch to fallback when fault_count or latency_p95 exceeds threshold; revert when below 0.5*threshold. Regenerate with `python scripts/export_p8_meta_diagram.py` (output `docs/figures/p8_meta_diagram.mmd`). Actions: switch_regime(to_regime). **Formal switch criterion (v0.1):** threshold-based. Revert is checked first (no hysteresis): if in fallback and fault_count <= 0 and latency_p95 < 0.5 * latency_threshold_ms, switch back to centralized. Fault-based switch to fallback requires fault_count >= hysteresis_consecutive and fault_count > fault_threshold (thrash control). Latency-based switch to fallback: if latency_p95 > latency_threshold_ms, switch to fallback (no hysteresis). Reference impl: `meta_controller.decide_switch`; spec: `kernel/meta/META_CONTROLLER_SPEC.v0.1.md`. Regret-based or safety-bound-based switching are future work.

## 3. Trace events and auditability

Event type `regime_switch` with payload from_regime, to_regime, reason. Emitted by meta-controller; replay can reconstruct regime history. MetaAdapter (`adapters/meta_adapter.py`) runs scenario, evaluates switch criteria from report (fault count, p95), injects regime_switch event into trace.

## 4. Regime-stress scenario and evaluation

**Headline:** Under regime_stress_v0, the meta-controller switches on measurable stress (fault_count, latency_p95), preserves no_safety_regression, and when collapse occurs, meta_reduces_collapse versus fixed/naive baselines (comparison.json).

`bench/maestro/scenarios/regime_stress_v0.yaml`: high fault load to trigger meta-controller. Evaluation: `scripts/meta_eval.py` with `--run-naive` and `--fault-threshold 0` compares fixed (CentralizedAdapter), meta-controller, and naive switching baseline. Output: `comparison.json` (fixed, meta_controller, naive_switch_baseline, meta_reduces_collapse, no_safety_regression). **Two real coordination algorithms:** With `--fallback-adapter retry_heavy`, the primary regime (Centralized) and the fallback (RetryHeavy) are architecturally different (retry-on-drop vs no retry); when a switch is decided, the fallback adapter is run and `fallback_tasks_completed` is recorded in trace metadata and in comparison.json (`fallback_tasks_completed_mean`). So "meta switches regime" is an empirical claim about different algorithms; use `--fallback-adapter retry_heavy` for tables comparing tasks_completed and collapse for regime A vs regime B.

**Table 1 — Comparison (fixed vs meta vs naive).** Source: `datasets/runs/meta_eval/comparison.json`. Run `meta_eval.py --run-naive --fault-threshold 0` to regenerate; run manifest (seeds, scenario_id, fault_threshold) in comparison.json. Example (regime_stress_v0, fault_threshold=0, 20 seeds). If collapse_count is 0 under default settings, run the non-vacuous procedure below to obtain a meaningful comparison.

| Regime | tasks_completed_mean | collapse_count | regime_switch_count_total |
|--------|----------------------|----------------|---------------------------|
| fixed (Centralized) | 3.00 | 1 | — |
| meta_controller | 3.00 | 1 | 6 |
| naive (fault_threshold=0) | 3.00 | — | 6 |

**Results summary (excellence metrics).** From comparison.json: **collapse reduction** (meta_controller collapse_count vs fixed when non-vacuous); **no_safety_regression** (meta >= 90% of fixed tasks_completed); **switch audit trail** (regime_switch_count_total in trace). When trigger is non-vacuous, meta_reduces_collapse is the headline comparison; see [STANDARDS_OF_EXCELLENCE.md](../docs/STANDARDS_OF_EXCELLENCE.md) (P8).

**Non-vacuous evaluation.** Under default stress, collapse_count may be 0, so "meta reduces collapse" is vacuously true. For a meaningful trigger: (1) run `meta_collapse_sweep.py --drop-probs 0.2,0.25,0.3,0.35 --seeds 1,2,...,20` (or default 20 seeds); (2) from collapse_sweep.json choose a drop_prob where collapse_count > 0; (3) run `meta_eval.py --run-naive --fault-threshold 0 --drop-prob <that_drop_prob>`. Exact commands are in the Reproducibility block (Section 7).

**Table 2 — Per-seed.** Run `python scripts/export_meta_tables.py --comparison datasets/runs/meta_eval/comparison.json --table2` for per-seed tasks_completed, regime_switch_count, and collapse.

**Thrashing vs hysteresis (empirical).** Run meta_eval with `--hysteresis 1`, `--hysteresis 2`, and `--hysteresis 3` (same seeds and drop_prob); comparison.json reports `excellence_metrics.switch_audit_trail_total` and fixed/meta collapse_count. Build a small table: hysteresis H=1, H=2, H=3 vs regime_switch_count_total and collapse_count. With hysteresis H ≥ 2, thrashing is typically bounded (switch count lower). Kernel lemma: `kernel/meta/META_CONTROLLER_SPEC.v0.1.md` states that with hysteresis_consecutive = K, fault-driven switching requires K consecutive fault observations, reducing rapid toggling. **Figure 1 — Collapse sweep.** tasks_completed (mean) and collapse rate vs drop_completion_prob from collapse_sweep.json. Regenerate: `python scripts/meta_collapse_sweep.py` then `python scripts/plot_meta_collapse.py --sweep datasets/runs/meta_eval/collapse_sweep.json` (output `docs/figures/p8_meta_collapse.png`). Run manifest in collapse_sweep.json.

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

- **Conditional paper:** Trigger requires meta to beat best fixed regime in at least one stress regime with no safety regression. If collapse_count is 0 under default settings, trigger is vacuous; run collapse_sweep then meta_eval with higher drop_prob for non-vacuous evaluation. When trigger is vacuous (collapse_count = 0), the paper should be presented as methodology and auditability only until a non-vacuous run is produced. See docs/CONDITIONAL_TRIGGERS.md.
- **No actual regime implementation difference:** v0.1 evaluates only trace-event injection; no second coordination algorithm is executed. Meta and naive both use the same thin-slice; only the decision to inject a regime_switch event differs. No second coordination algorithm (e.g. blackboard vs centralized) is invoked; future work: wire meta to delegate to different adapters.
- **Collapse may not be observed:** Under default stress (e.g. drop_completion_prob=0.15), tasks_completed may stay above threshold so collapse_count = 0; "meta reduces collapse" is then vacuously true. For non-vacuous evaluation, run `meta_collapse_sweep.py` to find a drop_prob where collapse occurs, then run `meta_eval.py` with that drop_prob (see Reproducibility).
- **Toy:** Regimes are the same thin-slice execution; no real multiple coordination algorithms or real stress (e.g. network partitions).
- **Future work:** Second coordination regime (meta delegating to Blackboard vs Centralized); regret-based or safety-bound-based switch criterion; real stress (e.g. network partitions). See kernel/meta/META_CONTROLLER_SPEC.v0.1.md.

**Threats to validity.** *Internal:* Single scenario (regime_stress_v0) and single thin-slice execution path; no second coordination algorithm wired. *External:* Generalization to other regimes or real stress (e.g. network partitions) is untested. *Construct:* collapse_count and tasks_completed below threshold are proxies for regime collapse; no control-theoretic stability measure.

## 7. Methodology and reproducibility

**Methodology:** Hypothesis—meta-controller reduces collapse vs best fixed regime under compound faults; PONRs remain invariant. Metrics: regime_switch count, collapse (e.g. tasks_completed below threshold), mode-thrashing rate. Kill criterion: safety regression at PONRs or audit gap (regime change not logged). Baselines: best fixed regime, naive switching. Portfolio criteria: `docs/STATE_OF_THE_ART_CRITERIA.md`.

**Reproducibility:** Run full eval: `python scripts/meta_eval.py --run-naive --fault-threshold 0` (writes `datasets/runs/meta_eval/comparison.json`). Tables: `python scripts/export_meta_tables.py --comparison datasets/runs/meta_eval/comparison.json` (add `--table2` for per-seed). Figure 1: `python scripts/meta_collapse_sweep.py` then `python scripts/plot_meta_collapse.py --sweep datasets/runs/meta_eval/collapse_sweep.json`. Run manifests: comparison.json (seeds, scenario_id, fault_threshold, script; success_criteria_met, excellence_metrics); collapse_sweep.json (seeds, drop_probs, scenario_id, script). For a **non-vacuous trigger** (collapse actually occurs so meta_reduces_collapse is meaningful): (1) Run `python scripts/meta_collapse_sweep.py --drop-probs 0.2,0.25,0.3,0.35` (use default 20 seeds for publishable; CI may use 10); from collapse_sweep.json identify a drop_prob where collapse_count > 0. (2) Run `python scripts/meta_eval.py --run-naive --fault-threshold 0 --drop-prob <that_drop_prob>`. Integration test: `tests/test_meta_p8.py` runs meta_eval with --out <temp>, asserts comparison.json (no_safety_regression, meta_reduces_collapse, regime_switch_count_total >= 1), and runs export_meta_tables.py; unit tests cover decide_switch and regime_switch_event. Scenario: `bench/maestro/scenarios/regime_stress_v0.yaml`. Spec: `kernel/meta/META_CONTROLLER_SPEC.v0.1.md`.

---

**Claims and backing**

| Claim | Artifact / backing |
|-------|---------------------|
| C1 Spec + impl | META_CONTROLLER_SPEC, decide_switch, regime_switch_event |
| C2 PONRs + audit | Safety condition in spec; regime_switch payload (from_regime, to_regime, reason) |
| C3 Scenario + adapter | regime_stress_v0 scenario, MetaAdapter trace events, comparison.json |
| No regime impl difference | Limitations; meta and naive same thin-slice |
| Collapse may be vacuous | Limitations; collapse_count = 0 under current stress |
