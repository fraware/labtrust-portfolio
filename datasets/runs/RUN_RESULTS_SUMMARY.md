# Run results summary (portfolio snapshot)

This file is a **compact index** of committed or publishable run artifacts for papers that point here from the root README and [docs/RESULTS_PER_PAPER.md](../../docs/RESULTS_PER_PAPER.md). For full semantics, paths for every paper (P0–P8), and eval options, use that document and [docs/EVALS_RUNBOOK.md](../../docs/EVALS_RUNBOOK.md). For a **regenerated** P5/P6/P8 markdown block from JSON on disk, run `python scripts/export_key_results_p5_p6_p8.py`.

---

## P4 — MAESTRO (publishable fault sweep)

Canonical frozen copy: `datasets/releases/p4_publishable_v1/` (mirrors the evidence cited in `papers/P4_CPS-MAESTRO/claims.yaml`).

### Parameters

- **MAESTRO_REPORT schema**: v0.2 (`kernel/eval/MAESTRO_REPORT.v0.2.schema.json`)
- **Seeds per sweep cell**: 20 (seeds 1..20)
- **Scenarios in fault sweep**: `toy_lab_v0`, `lab_profile_v0`, `warehouse_v0`, `traffic_v0`, `regime_stress_v0`
- **Fault settings**: `no_drop`, `drop_005`, `drop_02`, `delay_01`, `drop_005_delay_01`, `calibration_invalid_01`, `recovery_stress_aux` (see `multi_sweep.json` `run_manifest`)
- **Baselines**: `Centralized`, `Blackboard`, `RetryHeavy`, `NoRecovery`, `ConservativeSafeShutdown` on `toy_lab_v0`, regimes `fault_free` and `drop_0_2` (drop_completion_prob=0.2)

### Primary artifacts

| Artifact | Path |
|----------|------|
| Fault sweep bundle | `datasets/runs/maestro_fault_sweep/multi_sweep.json` |
| Anti-gaming | `datasets/runs/maestro_antigaming/antigaming_results.json` |
| Baseline JSON | `bench/maestro/baseline_summary.json` |
| Baseline markdown | `bench/maestro/baseline_results.md` |
| Exported paper tables | `papers/P4_CPS-MAESTRO/generated_tables.md` |
| Recovery figure | `docs/figures/p4_recovery_curve.png` |
| Safety figure | `docs/figures/p4_safety_violations.png` |
| Efficiency figure | `docs/figures/p4_efficiency_messages.png` |
| Metric semantics | `bench/maestro/RECOVERY_AND_SAFETY_METRICS.md` |
| Scoring | `bench/maestro/SCORING.md` |

Regenerate: `PYTHONPATH=impl/src` then `python scripts/maestro_fault_sweep.py`, `python scripts/maestro_baselines.py`, `python scripts/maestro_antigaming_eval.py`, `python scripts/export_maestro_tables.py --out papers/P4_CPS-MAESTRO/generated_tables.md`, `python scripts/plot_maestro_recovery.py`.

---

## P5 — Scaling (held-out MAE and triggers)

**Primary artifact:** `datasets/runs/scaling_eval/heldout_results.json` (default leave-one-scenario-out; optional `scaling_eval_family/` for leave-one-family-out).

**Also in tree (alternate holdouts / sweeps):** `datasets/runs/scaling_eval_fault/`, `scaling_eval_regime/`, `scaling_eval_agent_count/` — each may contain its own `heldout_results.json`; cite the path you actually used in prose.

**Typical fields:** `overall_baseline_mae`, `overall_per_scenario_baseline_mae`, `overall_regression_mae`, `regression_skipped_reason`, `success_criteria_met` (e.g. `beat_baseline_out_of_sample`, `trigger_met`), optional `scaling_fit` (exponent, R²).

Regenerate (publishable-style example): `python scripts/generate_multiscenario_runs.py` then `python scripts/scaling_heldout_eval.py` with the profile and seed count you document; tables via `scripts/export_scaling_tables.py`. Spec: `docs/P5_SCALING_SPEC.md`.

---

## P6 — LLM Planning (camera-ready Table 1b + engineering audit freeze)

### Canonical camera-ready directory

**Path:** `datasets/runs/llm_eval_camera_ready_20260424/`

**Table 1b (OpenAI, committed snapshot):** Models `gpt-4.1-mini`, `gpt-4.1`; `--real-llm-suite full`; **3** runs per case; **25** cases per model (**75** trials per model). Each model **75/75** passes (100.0%, Wilson 95% CI [95.1, 100.0]). Canonical command (from repo root, after API keys in `.env`):

```bash
PYTHONPATH=impl/src python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval_camera_ready_20260424 \
  --real-llm --real-llm-provider auto --real-llm-models gpt-4.1-mini,gpt-4.1 \
  --real-llm-runs 3 --real-llm-suite full
```

### Synthetic suites (same canonical run)

| Suite | Result (camera-ready) | Artifact |
|-------|-------------------------|------------|
| Red-team (15) | 15/15, `all_block_unsafe_pass` true | `red_team_results.json` `cases[]` |
| Confusable deputy (6) | 6/6 | `confusable_deputy_results.json` |
| Jailbreak-style (4) | 4/4 | `red_team_results.json` `jailbreak_style` |

### Adapter and baselines (committed)

- **Adapter latency:** `adapter_latency.json` — e.g. `tail_latency_p95_mean_ms` **36.70** (3 scenarios × 20 seeds); optional `denial_trace_stats.json` with `--run-adapter --denial-stats`.
- **Tool-level baseline:** `baseline_comparison.json` — denials gated/weak/ungated **60 / 60 / 0** (denial-injection plan).
- **Argument-level baseline:** `baseline_comparison_args.json` — gated **60** denials on path-traversal-style args; weak/ungated **0** (safe_args ablation).
- **Benign / false positives:** `baseline_benign.json` when generated with `--baseline-plan benign`.
- **Task-critical injection slice:** `task_critical_injection.json` (see `scripts/run_p6_task_critical_injection.py`).
- **Mock deny vs execute:** `mock_execution_harness.json`.
- **E2E denial example:** `e2e_denial_trace.json`.

### Replay verification (wording discipline)

- **`replay_denials.json`** is a **frozen summary** used for deterministic replay checks; the camera-ready narrative may cite **60/60** **matches** for that artifact’s row set.
- A **full recursive scan** of all `trace.json` files under `llm_eval_camera_ready_20260424/` can list **more** `metadata.denied_steps` entries than summarized in `replay_denials.json`. That is **not** a validator inconsistency by itself; see `datasets/runs/p6_final_audit_20260424/reproducibility_check.json` (`replay_fresh_trace_scan`, `replay_frozen_vs_trace_scan`).

### Supplementary GPT-5.x runs (never merge denominators with Table 1b)

| Directory | Model | n_pass / n_runs | pass_rate % | Wilson CI95 |
|-----------|-------|-----------------|---------------|-------------|
| `datasets/runs/llm_eval_openai_gpt54_postpatch_20260424` | `gpt-5.4` | 73 / 75 | 97.3 | [90.8, 99.3] |
| `datasets/runs/llm_eval_openai_gpt54pro_postpatch2_n3_20260424` | `gpt-5.4-pro` | 54 / 75 | 72.0 | [61.0, 80.9] |

Treat as **compatibility / behavior characterization**; failure interpretation should follow `p6_final_audit_20260424/gpt5_failure_audit.*` (harness/API empty responses, sparse `run_details` on some models).

### Final engineering audit bundle

**Path:** `datasets/runs/p6_final_audit_20260424/`  
**Regenerate:** `python scripts/export_p6_final_audit_bundle.py --out-dir datasets/runs/p6_final_audit_20260424`

Bundled outputs include `FINAL_AUDIT_SUMMARY.md`, `reproducibility_check.json`, `gpt5_failure_audit.json`, `paper_claims_checklist.md`, parser stress and extended replay notes, and SHA256 tables (`artifact_hashes.json`). **Harness alignment:** typed-step JSON parsing for real-LLM eval uses `_parse_step_from_response` in `impl/src/labtrust_portfolio/llm_planning.py`, imported by `scripts/llm_redteam_eval.py` (single source of truth).

**Venue / freeze docs:** `papers/P6_LLMPlanning/sat-cps2026/EXPERIMENTS_RUNBOOK.md` §9, `SUBMISSION_STANDARD.md`, `FREEZE_SUBMISSION_NOTES_2026-04-24.md`, `ENGINEERING_TRUTH_PACKAGE_2026-04-24.md`.

---

## P8 — Meta-controller (collapse and regime switching)

**Primary aggregate artifact:** `datasets/runs/meta_eval/comparison.json` (`no_safety_regression`, `meta_reduces_collapse` / non-inferior framing, `meta_strictly_reduces_collapse`, optional `excellence_metrics.mcnemar_exact_p_value_two_sided`, `fallback_tasks_completed_mean`, etc.).

**Scenario-specific and robustness campaign copies** may live under `datasets/runs/meta_eval/scenario_*` and `datasets/runs/meta_eval/robustness_campaign/`; cite the path your text uses.

Regenerate: see [docs/EVALS_RUNBOOK.md](../../docs/EVALS_RUNBOOK.md) P8 and `papers/P8_MetaController/DRAFT.md`; use `--non-vacuous` when comparing collapse counts if the fixed baseline has zero collapses.
