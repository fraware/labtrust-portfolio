# Meta-Coordination for CPS: Switching Regimes Under Stress

**Draft (v0.1). Paper ID: P8_MetaCoordination. Conditional paper; trigger and scope: docs/CONDITIONAL_TRIGGERS.md (P8).**

**Reproducibility.** From repo root, with `PYTHONPATH=impl/src` and `LABTRUST_KERNEL_DIR=kernel`. See [REPORTING_STANDARD.md](../docs/REPORTING_STANDARD.md) and [RESULTS_PER_PAPER.md](../docs/RESULTS_PER_PAPER.md). Run_manifest: comparison.json (seeds, scenario_id, fault_threshold, excellence_metrics); collapse_sweep.json (seeds, drop_probs, scenario_id). Conditional trigger: see Limitations and docs/CONDITIONAL_TRIGGERS.md (P8).

**Minimal run (under 20 min):** `python scripts/meta_eval.py --run-naive --fault-threshold 0` then `python scripts/export_p8_meta_diagram.py` then `python scripts/export_meta_tables.py --comparison datasets/runs/meta_eval/comparison.json` then `python scripts/meta_collapse_sweep.py` then `python scripts/plot_meta_collapse.py --sweep datasets/runs/meta_eval/collapse_sweep.json`.

**Publishable run:** For publishable tables, the default procedure is (1) run `meta_collapse_sweep.py` (default 20 seeds, --drop-probs 0.15,0.2,0.25,0.3), (2) run `meta_eval.py --run-naive --fault-threshold 0 --non-vacuous` so that Table 1 uses a drop_prob where collapse_count > 0; optionally (3) add `--fallback-adapter retry_heavy` for two-regime comparison. Run manifests in comparison.json and collapse_sweep.json. If no drop_prob in the sweep has collapse, the script exits with a message and Table 1 should be presented as methodology and auditability only (see section 7).

- **Figure 0:** `python scripts/export_p8_meta_diagram.py` (output `docs/figures/p8_meta_diagram.mmd`). Render Mermaid to PNG for camera-ready.
- **Table 1:** Run `python scripts/meta_collapse_sweep.py` then `python scripts/meta_eval.py --run-naive --fault-threshold 0 --non-vacuous` (writes comparison.json), then `python scripts/export_meta_tables.py --comparison datasets/runs/meta_eval/comparison.json`.
- **Table 2:** Same run; `python scripts/export_meta_tables.py --comparison datasets/runs/meta_eval/comparison.json --table2` (per-seed table).
- **Figure 1:** `python scripts/meta_collapse_sweep.py` (writes collapse_sweep.json), then `python scripts/plot_meta_collapse.py --sweep datasets/runs/meta_eval/collapse_sweep.json` (output `docs/figures/p8_meta_collapse.png`).

## 1. Motivation

Multiple coordination regimes (centralized, blackboard, fallback) exist; under compound faults, mode-thrashing or collapse can occur. Meta-controller switches regimes by criteria while keeping PONRs invariant and every switch auditable. **Primary evidence tier:** auditable, safety-constrained regime switching with replayable traces. **Secondary (collapse):** under pre-specified stress, we report **non-inferiority on paired collapse counts** versus the fixed regime (`meta_non_worse_collapse` / legacy `meta_reduces_collapse`: meta collapse_count <= fixed) and separately **strict improvement** (`meta_strictly_reduces_collapse`), McNemar on discordant pairs, and Wilson intervals on marginal collapse rates (`collapse_paired_analysis`, `excellence_metrics`). **Supporting:** performance tradeoff when using `--fallback-adapter` (e.g. retry_heavy). When collapse is not observed under a sweep, we report methodology and auditability only. The publishable run uses `--non-vacuous` with a recorded `stress_selection_policy` in `run_manifest`. For a second stress setting, use `--stress-preset high` (drop_prob 0.25) or `--stress-preset very_high` (0.35), or `--scenario regime_stress_v1` (see multi-scenario paths below).

## 2. Meta-controller model and formal switch criterion

Spec: `kernel/meta/META_CONTROLLER_SPEC.v0.1.md`. State: current_regime, fault_count, latency_p95.

**Second stress scenario / preset.** For external validity, `meta_eval.py` and `meta_collapse_sweep.py` accept `--scenario regime_stress_v0` (default) or `regime_stress_v1`. Publishable portfolio run (`run_paper_experiments.py --paper P8`) writes `datasets/runs/meta_eval/comparison.json` (v0) and `datasets/runs/meta_eval/scenario_regime_stress_v1/comparison.json` (v1), each with its own `collapse_sweep.json` under the same output directory prefix. `--stress-preset very_high` sets drop_completion_prob to 0.35 (high: 0.25).

**Figure 0 — Meta-controller regimes and switch.** Centralized and fallback regimes; switch to fallback when fault_count or latency_p95 exceeds threshold; revert when below 0.5*threshold. Regenerate with `python scripts/export_p8_meta_diagram.py` (output `docs/figures/p8_meta_diagram.mmd`). Actions: switch_regime(to_regime). **Formal switch criterion (v0.1):** threshold-based. Revert is checked first (no hysteresis): if in fallback and fault_count <= 0 and latency_p95 < 0.5 * latency_threshold_ms, switch back to centralized. Fault-based switch to fallback requires fault_count >= hysteresis_consecutive and fault_count > fault_threshold (thrash control). Latency-based switch to fallback: if latency_p95 > latency_threshold_ms, switch to fallback (no hysteresis). Reference impl: `meta_controller.decide_switch`; spec: `kernel/meta/META_CONTROLLER_SPEC.v0.1.md`. Regret-based or safety-bound-based switching are future work.

## 3. Trace events and auditability

Event type `regime_switch` with payload from_regime, to_regime, reason. Emitted by meta-controller; replay can reconstruct regime history. MetaAdapter (`adapters/meta_adapter.py`) runs scenario, evaluates switch criteria from report (fault count, p95), injects regime_switch event into trace.

## 4. Regime-stress scenario and evaluation

**Headline:** Under regime_stress_v0 (and optionally regime_stress_v1), the meta-controller switches on measurable stress (fault_count, latency_p95), preserves `no_safety_regression`, and reports **non-inferior collapse counts vs fixed** (`meta_non_worse_collapse`); **strict** reduction and paired binary tests are in `collapse_paired_analysis` / `excellence_metrics` (comparison.json). Naive baseline collapse_count is exported in Table 1 when `--run-naive` is used.

**Key results.** (1) `success_criteria_met.trigger_met`: `no_safety_regression` and **non-inferior collapse counts** (`meta_non_worse_collapse`); (2) `no_safety_regression`: meta >= 90% of fixed tasks_completed; (3) When non-vacuous, `run_manifest.stress_selection_policy` documents the pre-specified rule choosing `drop_completion_prob`; (4) `meta_strictly_reduces_collapse`, McNemar p-value, Wilson CIs for marginal collapse rates; (5) Excellence metrics: `collapse_reduction_vs_fixed`, `switch_audit_trail_total`, bootstrap `difference_ci95` for paired tasks_completed; (6) With `--fallback-adapter retry_heavy`: `fallback_tasks_completed_mean` (two real regimes); publishable run uses `run_paper_experiments.py --paper P8` (per-scenario collapse_sweep then meta_eval `--non-vacuous`, v0 and v1). When collapse_count = 0 under a sweep: present as methodology and auditability only. *Numbers from comparison.json and collapse_sweep.json. See [RUN_RESULTS_SUMMARY.md](../../datasets/runs/RUN_RESULTS_SUMMARY.md).*

`bench/maestro/scenarios/regime_stress_v0.yaml`: high fault load to trigger meta-controller. Evaluation: `scripts/meta_eval.py` with `--run-naive` and `--fault-threshold 0` compares fixed (CentralizedAdapter), meta-controller, and naive switching baseline. Output: `comparison.json` (fixed, meta_controller, naive_switch_baseline, meta_reduces_collapse, no_safety_regression). **Two real coordination algorithms:** With `--fallback-adapter retry_heavy`, the primary regime (Centralized) and the fallback (RetryHeavy) are architecturally different (retry-on-drop vs no retry); when a switch is decided, the fallback adapter is run and `fallback_tasks_completed` is recorded in trace metadata and in comparison.json (`fallback_tasks_completed_mean`). So "meta switches regime" is an empirical claim about different algorithms; use `--fallback-adapter retry_heavy` for tables comparing tasks_completed and collapse for regime A vs regime B.

**Table 1 — Comparison (fixed vs meta vs naive).** Source: `datasets/runs/meta_eval/comparison.json`. Units: tasks_completed_mean (count), collapse_count, regime_switch_count_total. Run_manifest in comparison.json. Run meta_eval.py --run-naive --fault-threshold 0 (optionally --non-vacuous) to regenerate. From non-vacuous run (collapse_count > 0) when available; see Reproducibility.

**Submission note (Table 1).** The numbers in Table 1 must come from a non-vacuous run: run `meta_collapse_sweep` then `meta_eval --run-naive --fault-threshold 0 --non-vacuous`. If no drop_prob in the sweep yields collapse_count > 0, do not claim "meta reduces collapse"; present Table 1 as methodology and auditability only and state so in the table caption or the first paragraph of Section 4. The latest comparison.json used here has `run_manifest.non_vacuous=true`, `drop_completion_prob=0.15`, and `collapse_count=1` for fixed and meta; success_criteria_met.trigger_met and no_safety_regression are true.

| Regime | tasks_completed_mean | collapse_count | regime_switch_count_total |
|--------|----------------------|----------------|---------------------------|
| fixed (Centralized) | 3.40 | 1 | — |
| meta_controller | 3.40 | 1 | 8 |
| naive (fault_threshold=0) | 3.40 | 1 | 8 |

**Results summary (excellence metrics).** From comparison.json: **non-inferior collapse counts** (`meta_non_worse_collapse`); **strict improvement** (`meta_strictly_reduces_collapse`); **paired binary** (McNemar, Wilson CIs in `collapse_paired_analysis`); **no_safety_regression**; **switch audit trail** (regime_switch_count_total in trace). See [STANDARDS_OF_EXCELLENCE.md](../docs/STANDARDS_OF_EXCELLENCE.md) (P8).

**Non-vacuous evaluation.** Under default stress, collapse_count may be 0, so "meta reduces collapse" is vacuously true. For a meaningful trigger: (1) run `meta_collapse_sweep.py --drop-probs 0.2,0.25,0.3,0.35 --seeds 1,2,...,20` (or default 20 seeds); (2) from collapse_sweep.json choose a drop_prob where collapse_count > 0; (3) run `meta_eval.py --run-naive --fault-threshold 0 --drop-prob <that_drop_prob>`. Exact commands are in the Reproducibility block (Section 7).

**Table 2 — Per-seed.** Per-seed tasks_completed (count), regime_switch_count, collapse. Run_manifest in comparison.json. Regenerate with `python scripts/export_meta_tables.py --comparison datasets/runs/meta_eval/comparison.json --table2`.

**Thrashing vs hysteresis (empirical).** Run meta_eval with `--hysteresis 1`, `--hysteresis 2`, and `--hysteresis 3` (same seeds and drop_prob); comparison.json reports `excellence_metrics.switch_audit_trail_total` and fixed/meta collapse_count. Build a small table: hysteresis H=1, H=2, H=3 vs regime_switch_count_total and collapse_count. With hysteresis H ≥ 2, thrashing is typically bounded (switch count lower). Kernel lemma: `kernel/meta/META_CONTROLLER_SPEC.v0.1.md` states that with hysteresis_consecutive = K, fault-driven switching requires K consecutive fault observations, reducing rapid toggling. **Figure 1 — Collapse sweep.** tasks_completed (mean, count) and collapse rate vs drop_completion_prob (fraction, or % when scaled) from collapse_sweep.json. Run_manifest in collapse_sweep.json. Regenerate: `python scripts/meta_collapse_sweep.py` then `python scripts/plot_meta_collapse.py --sweep datasets/runs/meta_eval/collapse_sweep.json` (output `docs/figures/p8_meta_collapse.png`).

## 5. Contribution to the literature and comparison to prior work

**Contribution to the literature.** Meta-learning and regime-switching work often focus on regret or bandit policy selection; fault-tolerant control often focuses on Lyapunov or mode-dependent dynamics with closed-loop guarantees. We contribute (1) **auditability**: every regime_switch is logged in the trace with reason (fault_count, latency_p95) so that mode changes are justified and replayable; (2) **PONR invariance**: safety constraints (e.g. no Tier 2/3 actuation without authorization) are preserved across switches; (3) comparison to **fixed and naive baselines** and, with `--fallback-adapter retry_heavy`, to a **second real coordination algorithm** (RetryHeavy vs Centralized); (4) when collapse occurs we report collapse reduction; when it does not we report methodology and auditability only. We do not claim learning-theoretic or control-theoretic optimality.

| Aspect | P8 (this work) | Context-dependent / MAB policy selection | Fault-tolerant control mode switching |
|--------|----------------|------------------------------------------|----------------------------------------|
| Switch criterion | Threshold-based (fault_count, latency_p95) | Often regret or bandit reward | Stability / Lyapunov or heuristic |
| Execution path | Thin-slice; with --fallback-adapter two real regimes | Policy selects among options | Mode switch changes controller |
| **Auditability** | **regime_switch events in trace; PONR invariant** | Varies | Often closed-loop only |
| Safety | no_safety_regression (meta >= 90% fixed) | Learning-theoretic bounds (when present) | Control-theoretic guarantees |

We emphasize auditability and PONR invariance; no claim to learning or control-theoretic optimality.

## 6. Limitations

Scope and conditional triggers: [EXPERIMENTS_AND_LIMITATIONS.md](../docs/EXPERIMENTS_AND_LIMITATIONS.md). Per-paper:

- **Conditional paper:** Trigger requires meta to beat best fixed regime in at least one stress regime with no safety regression (trigger_met, no_safety_regression in comparison.json). If collapse_count is 0 under default settings, trigger is vacuous; run collapse_sweep then meta_eval with higher drop_prob for non-vacuous evaluation. When collapse_count = 0, present results as methodology and auditability only; do not claim "meta reduces collapse." See [CONDITIONAL_TRIGGERS.md](../docs/CONDITIONAL_TRIGGERS.md) (P8).
- **Two-regime comparison:** When `--fallback-adapter retry_heavy` is used, the fallback regime (RetryHeavy) is a distinct coordination algorithm; comparison.json then reports fallback_tasks_completed_mean and supports the claim that meta switches between two real algorithms. Without --fallback-adapter, meta and naive differ only by regime_switch event injection (same thin-slice execution).
- **Collapse may not be observed:** Under default stress (e.g. drop_completion_prob=0.15), tasks_completed may stay above threshold so collapse_count = 0; "meta reduces collapse" is then vacuously true. For non-vacuous evaluation, run `meta_collapse_sweep.py` to find a drop_prob where collapse occurs, then run `meta_eval.py` with that drop_prob (see Reproducibility).
- **Toy:** Thin-slice only; no real stress (e.g. network partitions). With --fallback-adapter, two real algorithms (e.g. Centralized vs RetryHeavy) are compared.
- **Future work:** Additional fallback options beyond retry_heavy; regret-based or safety-bound-based switch criterion; real stress (e.g. network partitions). See kernel/meta/META_CONTROLLER_SPEC.v0.1.md.

**Threats to validity.** *Internal:* Default tables use regime_stress_v0; publishable pipeline also emits regime_stress_v1 under `scenario_regime_stress_v1/`; with `--fallback-adapter retry_heavy` a second coordination algorithm is wired. *External:* Generalization to other regimes or real stress (e.g. network partitions) is untested. *Construct:* collapse_count and tasks_completed below threshold are proxies for regime collapse; no control-theoretic stability measure.

## 7. Methodology and reproducibility

**Methodology:** Hypothesis—meta-controller reduces collapse vs best fixed regime under compound faults; PONRs remain invariant. Metrics: regime_switch count, collapse (e.g. tasks_completed below threshold), mode-thrashing rate. Kill criterion: safety regression at PONRs or audit gap (regime change not logged). Baselines: best fixed regime, naive switching. Portfolio criteria: `docs/STATE_OF_THE_ART_CRITERIA.md`.

**Publishable run:** For publishable Table 1, use **non-vacuous** evaluation: `run_paper_experiments.py --paper P8` runs (1) meta_collapse_sweep.py (20 seeds, drop_probs 0.15–0.3), (2) meta_eval.py --run-naive --fault-threshold 0 --non-vacuous --fallback-adapter retry_heavy so Table 1 uses a drop_prob where collapse_count > 0 and two real regimes are compared. If no drop_prob in the sweep has collapse, present Table 1 as methodology and auditability only. **For submission:** verify comparison.json has `success_criteria_met.trigger_met` true and `no_safety_regression` true for the run used for tables; state in the draft that the conditional trigger is met, or present as methodology/auditability only per [CONDITIONAL_TRIGGERS.md](../docs/CONDITIONAL_TRIGGERS.md) (P8).

**Reproducibility:** Run full eval: `python scripts/meta_eval.py --run-naive --fault-threshold 0` (writes `datasets/runs/meta_eval/comparison.json`). Tables: `python scripts/export_meta_tables.py --comparison datasets/runs/meta_eval/comparison.json` (add `--table2` for per-seed). Figure 1: `python scripts/meta_collapse_sweep.py` then `python scripts/plot_meta_collapse.py --sweep datasets/runs/meta_eval/collapse_sweep.json` (Wilson bands on collapse rate; t-CI on mean tasks_completed). Schema check: `python scripts/verify_p8_meta_artifacts.py --comparison datasets/runs/meta_eval/comparison.json` (add `--sweep` / `--strict-publishable` as needed). Run manifests: comparison.json (`schema_version`, seeds, scenario_id, fault_threshold, `stress_selection_policy` when `--non-vacuous`, success_criteria_met, excellence_metrics, collapse_paired_analysis); collapse_sweep.json (`schema_version`, seeds, drop_probs, scenario_id). For a **non-vacuous trigger**: (1) `meta_collapse_sweep.py` (optionally `--scenario regime_stress_v1` and wider `--drop-probs` for v1); (2) `meta_eval.py --run-naive --fault-threshold 0 --non-vacuous` with matching `--scenario` and `--out`. Optionally `--fallback-adapter retry_heavy`. Integration tests: `tests/test_meta_p8.py`, `tests/test_stats_p8_tools.py`. Scenario YAMLs: `bench/maestro/scenarios/regime_stress_v0.yaml`, `regime_stress_v1.yaml`. Spec: `kernel/meta/META_CONTROLLER_SPEC.v0.1.md`.

---

**Claims and backing**

| Claim | Artifact / backing |
|-------|---------------------|
| C1 Spec + impl | META_CONTROLLER_SPEC, decide_switch, regime_switch_event |
| C2 PONRs + audit | Safety condition in spec; regime_switch payload (from_regime, to_regime, reason) |
| C3 Scenario + adapter | regime_stress_v0/v1, MetaAdapter trace events, comparison.json (`meta_non_worse_collapse`, `meta_strictly_reduces_collapse`, `collapse_paired_analysis`) |
| Two regimes (optional) | With --fallback-adapter retry_heavy, comparison.json reports fallback_tasks_completed_mean; two real algorithms compared |
| Collapse may be vacuous | Use --non-vacuous for publishable; otherwise present as methodology/auditability only |
