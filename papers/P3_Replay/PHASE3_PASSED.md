# Phase 3 passed

Submission-readiness checklist (docs/STATE_OF_THE_ART_CRITERIA.md section 3) verified for **P3 freeze 2026-04-19**.

- **Claim-evidence:** `claims.yaml` maps each claim to `artifact_paths` and table/figure IDs; canonical numbers come from `datasets/runs/replay_eval/summary.json`.
- **Repro:** Publishable command documented in `DRAFT.md` and `README.md` (includes `--l1-twin`, `--overhead-curve`, multi-seed thin-slice); minimal CI uses reduced `--overhead-runs` / seeds—do not cite as publishable.
- **Variance:** `run_manifest` records corpus_dir, overhead_runs, thin_slice_seeds, bootstrap_reps, platform, `l1_twin_real_ingest_n`.
- **No kernel redefinition:** Draft cites TRACE and REPLAY_LEVELS; does not redefine tiers or evidence bundle schema.
- **No overclaim:** L0/L1/L2 scope explicit; no fleet or hardware determinism; L1 is control-plane twin only; two **real_ingest** lanes separated from synthetic/field-proxy.
- **L1:** Multi-seed thin-slice + **second family** via `real_ingest_traces` in `l1_twin_summary` when `--l1-twin` is used.
- **Overhead curve:** Multi-prefix `overhead_curve`; `verify_p3_replay_summary.py --strict-curve` requires ≥2 points.
- **Figures:** `scripts/export_p3_paper_figures.py`; assets under `papers/P3_Replay/figures/`.
- **Tables:** `scripts/export_replay_corpus_table.py --out-md papers/P3_Replay/generated_tables.md` after replay_eval.
