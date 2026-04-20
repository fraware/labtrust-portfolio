# Meta-Coordination for CPS: Switching Regimes Under Stress

**Draft (v0.2). Paper ID: P8_MetaCoordination. Conditional paper; trigger and scope: `docs/CONDITIONAL_TRIGGERS.md` (P8).**

**Reproducibility.** From repo root, set `PYTHONPATH=impl/src` and `LABTRUST_KERNEL_DIR=kernel`. See [`REPORTING_STANDARD.md`](../docs/REPORTING_STANDARD.md) and [`RESULTS_PER_PAPER.md`](../docs/RESULTS_PER_PAPER.md). Primary artifacts: `datasets/runs/meta_eval/comparison.json` (**`schema_version`: `p8_meta_eval_v0.3`**), `collapse_sweep.json`, and optionally `datasets/runs/meta_eval/robustness_campaign/campaign_summary.json`.

**Minimal path (portfolio default).** One command reproduces the primary v0 + v1 sweeps and evals:

`python scripts/run_paper_experiments.py --paper P8`

Then regenerate markdown tables (primary + per-seed + campaign matrix):

`python scripts/export_meta_tables.py --comparison datasets/runs/meta_eval/comparison.json --table2 --campaign datasets/runs/meta_eval/robustness_campaign/campaign_summary.json`

Write output to `papers/P8_MetaCoordination/generated_tables.md` if you want a frozen table file.

**Figures.** Figure 0 (diagram): `python scripts/export_p8_meta_diagram.py` → `docs/figures/p8_meta_diagram.mmd`. Figure 1 (collapse sweep): `python scripts/meta_collapse_sweep.py` (writes `collapse_sweep.json` under `--out`) then `python scripts/plot_meta_collapse.py --sweep <path>/collapse_sweep.json` → `docs/figures/p8_meta_collapse.png`.

**Publishable evaluation semantics (v0.3).**

1. **Non-vacuous stress:** `meta_eval.py --non-vacuous --non-vacuous-select max_drop_any_collapse` reads (or runs) a collapse sweep and selects the **largest** `drop_completion_prob` in the grid where the **fixed** arm still shows at least one collapsed run—stronger stress than the legacy “smallest drop with collapse” rule.
2. **Calibration vs evaluation seeds:** pass `--calibration-seeds` for the sweep only; `--seeds` are the held-out evaluation seeds. The portfolio uses calibration `1–10` and evaluation `11–30` (recorded under `run_manifest.stress_selection_policy`).
3. **Two coordination paths:** `--fallback-adapter retry_heavy` runs Centralized vs RetryHeavy; after a meta decision to switch, **reported meta outcomes** (`tasks_completed`, recovery, safety counters) follow the fallback run (`outcome_attribution_note` in `comparison.json`).
4. **Naive baseline:** `--run-naive` adds a third arm where the naive policy uses **`fault_threshold=0`** inside `meta_eval.py`. The **meta** arm for publishable rows uses the default **`fault_threshold=1`** (do not pass `--fault-threshold 0` on the CLI for publishable meta).

**Robustness campaign (Table 3).** `python scripts/p8_robustness_campaign.py --strict-publishable` builds a multi-profile matrix (baseline non-vacuous, latency- and contention-isolation profiles, hysteresis ablations) for `regime_stress_v0` and `regime_stress_v1`. Isolation profiles reuse the **same** `drop_completion_prob` as the scenario’s baseline non-vacuous row so severity is aligned. `python scripts/verify_p8_meta_artifacts.py --strict-publishable` checks primary and campaign bundles.

**Optional scenario.** `scenario_lab_profile_v0` under `datasets/runs/meta_eval/scenario_lab_profile_v0/` when that sweep + eval is run (same scripts; different `--scenario` and output directory).

---

## 1. Motivation

Multiple coordination regimes exist; under compound faults, fixed choice can collapse or thrash. A meta-controller switches regime using explicit, logged criteria while preserving PONRs. We report **auditability**, **safety proxies**, and—when stress is non-vacuous—**paired collapse non-inferiority** and optional **strict** improvement.

## 2. Meta-controller model and formal switch criterion

Spec: `kernel/meta/META_CONTROLLER_SPEC.v0.1.md`. Reference implementation: `meta_controller.decide_switch`. MetaAdapter injects `regime_switch` events with payload (`from_regime`, `to_regime`, `reason`).

**Scenarios.** `regime_stress_v0` (primary comparison path), `regime_stress_v1` (secondary), optional `lab_profile_v0` for an alternate lab-shaped stress slice.

## 3. Trace events and auditability

Event type `regime_switch` is emitted on each switch; replay reconstructs regime history. This supports C2 and integration tests.

## 4. Regime-stress evaluation and current headline numbers

**Primary `comparison.json` (regime_stress_v0, evaluation seeds 11–30, `drop_completion_prob` 0.35, `retry_heavy`, non-vacuous `max_drop_any_collapse`).** Table 1 aggregates (see also `papers/P8_MetaCoordination/generated_tables.md`):

| Regime | tasks_completed_mean | collapse_count | regime_switch_count_total |
|--------|------------------------|----------------|---------------------------|
| fixed (Centralized) | 2.70 | 1 | — |
| meta_controller | 3.45 | 0 | 8 |
| naive (fault_threshold=0) | 3.85 | 0 | 17 |

**Paired collapse (same seeds):** `collapse_paired_analysis` has `fixed_collapse_count` = 1, `meta_collapse_count` = 0 → **`meta_non_worse_collapse`** and **`meta_strictly_reduces_collapse`** true; **`trigger_met`** true with **`no_safety_regression`** true. McNemar two-sided *p* is 1.0 on discordant pairs when discordant counts are small; Wilson CIs on marginal rates are still reported.

**Recovery / safety row (meta arm):** `time_to_recovery_ms_mean` ≈ 106 ms when aggregated; PONR and safety violation totals 0 in the checked-in bundle (`generated_tables.md`).

**Interpretation.** Under this pre-specified stress, meta is **strictly better** than fixed on paired collapse counts while meeting the safety proxy. The naive arm completes more tasks on average but switches more aggressively; the paper treats naive as a **diagnostic** baseline, not the safety anchor.

## 5. Contribution and related work

We emphasize **trace-level auditability** and **PONR invariance** under explicit switching rules, with statistical reporting suited to **paired** collapse outcomes and marginal Wilson bounds. We do not claim learning-theoretic optimality.

## 6. Limitations

See [`EXPERIMENTS_AND_LIMITATIONS.md`](../docs/EXPERIMENTS_AND_LIMITATIONS.md) and [`CONDITIONAL_TRIGGERS.md`](../docs/CONDITIONAL_TRIGGERS.md) (P8). Thin-slice harness only; external validity beyond MAESTRO stress YAMLs is open. Latency-only isolation rows in the robustness campaign may show **ties** on strict collapse improvement while still exhibiting latency-driven switches; the baseline non-vacuous rows carry the primary strict-reduction evidence.

## 7. Methodology and commands (copy-paste)

**Portfolio P8:**

`PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/run_paper_experiments.py --paper P8`

**Verifier (primary):**

`PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/verify_p8_meta_artifacts.py --comparison datasets/runs/meta_eval/comparison.json --sweep datasets/runs/meta_eval/collapse_sweep.json --strict-publishable`

**Robustness campaign:**

`PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/p8_robustness_campaign.py --strict-publishable`

**Manual equivalent (v0 only, illustrative):**

1. `python scripts/meta_collapse_sweep.py --out datasets/runs/meta_eval --scenario regime_stress_v0 --drop-probs 0.15,0.2,0.25,0.3,0.35 --seeds 1,2,3,4,5,6,7,8,9,10`  
2. `python scripts/meta_eval.py --out datasets/runs/meta_eval --scenario regime_stress_v0 --seeds 11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30 --run-naive --non-vacuous --non-vacuous-select max_drop_any_collapse --fallback-adapter retry_heavy --collapse-sweep-path datasets/runs/meta_eval/collapse_sweep.json --calibration-seeds 1,2,3,4,5,6,7,8,9,10`

**Tests:** `tests/test_meta_p8.py`, `tests/test_stats_p8_tools.py`.

---

**Claims and backing**

| Claim | Artifact / backing |
|-------|---------------------|
| C1 Spec + impl | `META_CONTROLLER_SPEC`, `decide_switch`, `regime_switch` events, campaign latency/contention rows |
| C2 PONRs + audit | Trace schema; MetaAdapter; `campaign_summary.json` |
| C3 Scenario + paired collapse | `comparison.json` (`collapse_paired_analysis`, `meta_non_worse_collapse`, `meta_strictly_reduces_collapse`), `collapse_sweep.json`, campaign baseline rows |
| Two regimes | `--fallback-adapter retry_heavy`, `fallback_tasks_completed_mean`, outcome attribution fields |
