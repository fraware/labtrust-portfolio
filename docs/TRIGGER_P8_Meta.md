# P8 Meta-Coordination: Trigger decision

**Trigger (portfolio):** Proceed only if multiple coordination regimes are actually deployed (centralized, market, swarm, fallback) and mode-thrashing or collapse occurs under compound faults. Canonical wording: [CONDITIONAL_TRIGGERS.md](CONDITIONAL_TRIGGERS.md) (P8).

**Decision: GO (portfolio planning).** Multiple coordination regimes exist in the thin slice (e.g. Centralized, Blackboard, optional RetryHeavy fallback); MAESTRO regime-stress scenarios exercise compound faults. The paper remains **conditional** until `comparison.json` shows the machine-checkable trigger for the run used in the draft.

## Evidence the repo expects today

- **Primary artifact:** `datasets/runs/meta_eval/comparison.json` (and, after publishable `run_paper_experiments.py --paper P8`, `datasets/runs/meta_eval/scenario_regime_stress_v1/comparison.json`).
- **Machine-checkable trigger:** `success_criteria_met.trigger_met` requires `no_safety_regression` and **non-inferior paired collapse counts** vs fixed (`meta_non_worse_collapse`; legacy field name `meta_reduces_collapse`). **Strict** count reduction is reported separately as `meta_strictly_reduces_collapse` with McNemar / Wilson fields under `collapse_paired_analysis` and `excellence_metrics`.
- **Non-vacuous stress:** When using `meta_eval --non-vacuous`, `run_manifest.stress_selection_policy` records the pre-specified rule that picks `drop_completion_prob` from `collapse_sweep.json`.
- **Verification:** `python scripts/verify_p8_meta_artifacts.py --comparison <comparison.json>` (optional `--sweep`, `--strict-publishable` for release gates).
- **Figures/tables:** `export_meta_tables.py`, `plot_meta_collapse.py` (uncertainty bands), `export_p8_meta_diagram.py`. See [EVALS_RUNBOOK.md](EVALS_RUNBOOK.md) P8 section and [RESULTS_PER_PAPER.md](RESULTS_PER_PAPER.md).

**Dependencies:** P4 (MAESTRO), P3 (Replay), P0 (MADS PONRs invariant across regimes).
