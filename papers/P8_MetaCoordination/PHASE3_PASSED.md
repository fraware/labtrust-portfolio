# Phase 3 passed

Submission-readiness checklist (`docs/STATE_OF_THE_ART_CRITERIA.md` section 3) verified on **2026-04-20** against the current P8 artifact bundle.

- **Claim–evidence:** All claims in `claims.yaml` have `artifact_paths` and at least one `table_id` or `figure_id` where applicable.
- **Schema:** Primary `comparison.json` uses `p8_meta_eval_v0.3` (outcome attribution note, calibration vs evaluation seeds in `run_manifest.stress_selection_policy` when non-vacuous).
- **Repro:** Portfolio path `python scripts/run_paper_experiments.py --paper P8` (or the explicit command blocks in `DRAFT.md`); then `export_meta_tables.py` and optional `p8_robustness_campaign.py --strict-publishable`.
- **Variance:** Run manifest records seeds, scenario, `fault_threshold`, hysteresis and trigger thresholds, fallback adapter, and stress selection policy.
- **No kernel redefinition:** Draft cites `META_CONTROLLER_SPEC` and TRACE schema; does not redefine tiers or evidence tiers.
- **Overclaim:** Conditional paper; trigger (`trigger_met`, `no_safety_regression`) and scope are stated in Limitations and `docs/CONDITIONAL_TRIGGERS.md` (P8). Naive baseline uses `fault_threshold=0` only for the naive arm inside `meta_eval.py` when `--run-naive` is set; the meta arm uses the configured default (`fault_threshold=1`) for publishable rows.
- **Verifier:** `python scripts/verify_p8_meta_artifacts.py --comparison datasets/runs/meta_eval/comparison.json --sweep datasets/runs/meta_eval/collapse_sweep.json --strict-publishable` passes on the checked-in primary bundle.
