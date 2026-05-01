# LabTrust Portfolio (MADS-CPS + MAESTRO/Replay release train)

This repository is a **portfolio workspace** for a coherent paper + artifact program around
**assurance, reproducibility, and evaluation of large-scale agentic cyber-physical systems (CPS)**.

## What exists today (v0.1)
- `kernel/` — versioned JSON Schemas and supporting docs (TRACE, MAESTRO_REPORT, EVIDENCE_BUNDLE, RELEASE_MANIFEST, COORD_CONTRACT, REP_CPS_PROFILE, TYPED_PLAN, ASSURANCE_PACK)
- `impl/` — thin-slice pipeline (TRACE → MAESTRO report → Replay → Evidence bundle → Release manifest); adapters (Centralized, Blackboard, REP-CPS, LLM Planning, Meta); contract validator; REP-CPS aggregator; scaling (regression, collapse, scaling exponent) and assurance tooling
- `bench/` — MAESTRO scenarios (toy_lab, lab_profile, warehouse, traffic, regime_stress v0/v1, rep_cps_scheduling, etc.) with YAML `family` taxonomy; fault sweep; baselines (Centralized vs Blackboard); Replay corpus (`bench/replay/corpus`: core traps, expanded traps, benign/field-style pass traces, `twin_config.json`; eval `replay_eval.py` writes `schema_version: p3_replay_eval_v0.2`, `corpus_space_summary`, per-trace localization/space fields, baselines, multi-seed overhead; `export_replay_corpus_table.py` Table 1 + Table 1b, `generate_p3_replay_corpus_traces.py` for auxiliary traces, `verify_p3_replay_summary.py`, `plot_replay_overhead.py`; L1 stub / `--l1-twin`; L2 design in kernel); contract corpus (see bench/contracts/README.md)
- `papers/` — paper folders (P0–P8) with AUTHORING_PACKET, DRAFT, claims.yaml, and PHASE3_PASSED per paper. **All nine papers are at Draft stage**; Phase 3 (submission-readiness) checklist passed 2025-03-11. Next: submission prep per [docs/PRE_SUBMISSION_CHECKLIST.md](docs/PRE_SUBMISSION_CHECKLIST.md).
- `datasets/` — run and release layout; eval outputs under `datasets/runs/` (e3_summary, e2_redaction_demo, replay_eval, rep_cps_eval, scaling_eval, llm_eval, meta_eval, contracts_eval, assurance_eval, **assurance_eval_aies**, maestro_fault_sweep, multiscenario_runs, etc.). Summary JSONs include optional `excellence_metrics`; run `python scripts/export_excellence_summary.py` to print a one-line summary per paper. [datasets/runs/RUN_RESULTS_SUMMARY.md](datasets/runs/RUN_RESULTS_SUMMARY.md) snapshots **P5/P6/P8**; other papers read their own paths (see [docs/RESULTS_PER_PAPER.md](docs/RESULTS_PER_PAPER.md)).
- **P5 reviewer quick path:** [papers/P5_ScalingLaws/README.md](papers/P5_ScalingLaws/README.md) — frozen 7,200-row coordination-scaling grid, held-out protocols, `papers/P5_ScalingLaws/CLAIM_LOCK_NEURIPS2026.md`, and `python scripts/check_p5_claim_sources.py`.
- **Tests:** Unit and integration tests; P1–P8 each have a real-eval integration test that runs the eval script and asserts on the produced artifact; P8 has unit tests for the meta-controller (`decide_switch` revert/latency/hysteresis); W3 evidence-bundle conditions are tested in `tests/test_w3_evidence_bundle.py` (alignment with formal/lean). See [docs/STATE_OF_THE_ART_CRITERIA.md](docs/STATE_OF_THE_ART_CRITERIA.md).

## Quickstart

Validate kernel schemas (no env vars needed):
```bash
python scripts/validate_kernel.py
```

Run the thin slice end-to-end and run tests. Use one of the following depending on your shell.

**Bash / Git Bash / WSL:**
```bash
export PYTHONPATH=impl/src
python -m labtrust_portfolio run-thinslice --out-dir datasets/runs/demo

export LABTRUST_KERNEL_DIR=kernel
python -m unittest discover -s tests
```

**PowerShell (Windows):**
```powershell
$env:PYTHONPATH = "impl/src"
python -m labtrust_portfolio run-thinslice --out-dir datasets/runs/demo

$env:LABTRUST_KERNEL_DIR = "kernel"
$env:PYTHONPATH = "impl/src"
python -m unittest discover -s tests
```

## Cross-cutting workflow

1. **Validate kernel** — `python scripts/validate_kernel.py`
2. **Run thin-slice** — Set `PYTHONPATH=impl/src` then `python -m labtrust_portfolio run-thinslice --out-dir datasets/runs/<run_id>`
3. **Check conformance** — Set `LABTRUST_KERNEL_DIR=kernel` and `PYTHONPATH=impl/src` then `python -m labtrust_portfolio check-conformance datasets/runs/<run_id>`
4. **Release dataset (optional)** — With `PYTHONPATH=impl/src`: `python -m labtrust_portfolio release-dataset datasets/runs/<run_id> <release_id>`

**PowerShell (Windows)** — Set env vars first, then run commands; or use the helper scripts from repo root:
```powershell
.\scripts\run_tests.ps1
.\scripts\run_workflow.ps1
```
Or manually:
```powershell
$env:LABTRUST_KERNEL_DIR = "kernel"
$env:PYTHONPATH = "impl/src"
python -m labtrust_portfolio run-thinslice --out-dir datasets/runs/demo
python -m labtrust_portfolio check-conformance datasets/runs/demo
python -m labtrust_portfolio release-dataset datasets/runs/demo my_release
```

For **P6 real-LLM mode** (optional): use OpenAI/Anthropic keys with `--real-llm-provider auto`, or Prime Inference with `--real-llm-provider prime` and `PRIME_INTELLECT_API_KEY` (fallback `PRIME_API_KEY`, optional `PRIME_TEAM_ID`). The camera-ready OpenAI snapshot (`datasets/runs/llm_eval_camera_ready_20260424`) uses `--real-llm-runs 3` and `--real-llm-suite full` (red-team + confusable deputy + jailbreak-style). Use `--real-llm-suite core` only for red+confusable-only denominators. Example Prime matrix command: `llm_redteam_eval.py --real-llm --real-llm-provider prime --real-llm-models x-ai/grok-4-fast,google/gemini-2.5-flash,openai/gpt-4.1-mini,qwen/qwen3-30b-a3b-instruct-2507 --real-llm-runs 3`. `.env` is in `.gitignore` and must not be committed. See [docs/EXPERIMENTS_AND_LIMITATIONS.md](docs/EXPERIMENTS_AND_LIMITATIONS.md).

The portfolio anchor scenario is **lab_profile_v0** (`bench/maestro/scenarios/lab_profile_v0.yaml`); every paper touches it at least once. See [docs/VALIDATING_A_RUN.md](docs/VALIDATING_A_RUN.md) for conformance tiers and details. For paper ownership and dependencies see [docs/INTEGRATION_CONTRACTS.md](docs/INTEGRATION_CONTRACTS.md) and [docs/CONDITIONAL_TRIGGERS.md](docs/CONDITIONAL_TRIGGERS.md). Before submission, run the Phase 3 checklist in [docs/STATE_OF_THE_ART_CRITERIA.md](docs/STATE_OF_THE_ART_CRITERIA.md) section 3. Kernel versioning: [kernel/README.md](kernel/README.md).

## Evaluation pipelines

Per-paper evaluation scripts write results under `datasets/runs/`:

| Paper | Script(s) | Output under `datasets/runs/` |
|-------|-----------|-------------------------------|
| P0 | `build_p0_conformance_corpus.py`, `produce_p0_e3_release.py`, `replay_link_e3.py`, `e2_redaction_demo.py`, `run_p0_e4_controller_matrix.py`, `export_p0_e4_admissibility_vs_productivity.py`, `run_p0_e5_model_evolution.py`, `build_p0_conformance_summary.py` | E1: `p0_conformance_corpus/`; E2: `e2_redaction_demo/`; E3: `e3_summary.json`, `p0_e3_variance.json`, `e3/<scenario>/seed_<n>/`, release to `releases/p0_e3_release`; E4: `p0_e4_controller_matrix.json`, `p0_e4_raw_summary.json`, `p0_e4_normalized_summary.json`, `p0_e4_per_seed.jsonl`, `p0_e4_diagnostics.json`, `p0_e4_controller_pairs.jsonl`, `p0_e4_raw_failure_reasons.json`; E4 paper-facing export: `p0_e4_admissibility_vs_productivity.json/.csv`, `p0_e4_coordination_shock_focus.json/.csv`; E5: `p0_e5_model_evolution.json`, `p0_e5_model_evolution_per_seed.jsonl`, `p0_e5_model_evolution_summary.csv`; portfolio summary: `releases/portfolio_v0.1/p0_conformance_summary.json`. Evidence bundle: `verification_mode` required. |
| P1 | `contracts_eval.py`, `contracts_async_stress.py`, `contracts_transport_parity.py` | `contracts_eval/eval.json` (per-sequence `detection_ok`, `ablation` / `ablation_by_class` with occ_only, lease_only, lock_only, naive_lww proxies, `detection_metrics` and `detection_metrics_by_class`, `excellence_metrics` with per_class_ci95, latency CI, `resource_and_cost`; `--baseline` adds `violations_would_apply_without_validator` only); `scale_test.json` (--scale-test); optional `scale_sweep.json`; `stress_results.json` (async delay/skew/reorder sweep); `transport_parity.json` (`parity_ok_all`, `per_sequence[]`, `parity_confidence`, optional `--sequences`). Gatekeeper: `allow_release(..., check_contracts=True)`. Trace-derivability: docs/P1_TRACE_DERIVABILITY.md. Benchmark labeling: bench/contracts/BENCHMARK_SPEC.v0.1.md. Tables/figures: `export_contracts_corpus_table.py` (Tables 1–3 + ablation + stress/parity summaries), `export_p1_appendix_tex.py`, `export_p1_contract_flow.py`, `render_p1_flow_figure.py`, `plot_contracts_scale.py`, `plot_p1_paper_figures.py`; `generate_paper_artifacts.py --paper P1`. |
| P2 | `rep_cps_eval.py` | `rep_cps_eval/summary.json` (delay_fault_prob sweep, optional drop_completion_prob sweep via `--drop-sweep`, three scenarios default: toy_lab_v0, lab_profile_v0, rep_cps_scheduling_v0; per_scenario summaries, excellence_metrics with comparison statistics, scheduling_dependent_eval, freshness_replay_evidence, sybil_vs_spoofing_evidence, messaging_sim, dynamic_aggregation_series; optional --aggregation-steps, convergence_achieved, aggregation_variants, sybil_sweep, trigger_met), `safety_gate_denial.json`. Tables: `export_rep_cps_tables.py` (includes per-scenario summary, comparison statistics, messaging_sim and dynamic_aggregation_series blocks). Figures: `plot_rep_cps_summary.py`, `plot_rep_cps_latency.py`. |
| P3 | `replay_eval.py` | `replay_eval/summary.json` (`schema_version: p3_replay_eval_v0.2`; `per_trace[]` with **`corpus_category`** (synthetic_trap, field_proxy, real_ingest, synthetic_pass), localization + trace/diagnostic size fields; `corpus_space_summary`; `process_peak_rss_bytes` best-effort; `baseline_overhead`, `multi_seed_overhead`, `corpus_outcome_wilson_ci95`, empirical p95/p99, `overhead_curve` with `--overhead-curve`; `--l1-twin` for twin metrics including **`l1_twin_summary`** (multi-seed aggregate)). **Use `--out datasets/runs/replay_eval/summary.json`** (file path). Tables: `export_replay_corpus_table.py --out-md papers/P3_Replay/generated_tables.md` (Table 1 + Table 1b). Verify: `verify_p3_replay_summary.py`. Figure: `plot_replay_overhead.py`. Diagram: `export_p3_replay_levels_diagram.py`. Corpus regen: `generate_p3_replay_corpus_traces.py`, `generate_real_bucket_example.py`. L1 = L0 + twin config; L2 design in REPLAY_LEVELS. |
| P4 | `maestro_fault_sweep.py`, `maestro_antigaming_eval.py`, `maestro_baselines.py` | `maestro_fault_sweep/` (multi_sweep.json; recovery metrics: steps_to_completion_after_first_fault, tasks_completed_after_fault), `maestro_antigaming/antigaming_results.json` (scoring_proof), `bench/maestro/adapter_costs.json`, baseline_summary.json. Adapters: Centralized, Blackboard, RetryHeavy. Tables: `export_maestro_tables.py`. Figure: `plot_maestro_recovery.py`. |
| P5 | `generate_multiscenario_runs.py`, `scaling_heldout_eval.py` | `multiscenario_runs/`, `scaling_eval/heldout_results.json` (leave-one-scenario-out default; optional `scaling_eval_family/` for leave-one-family-out; `secondary_targets` for coordination_tax_proxy / error_amplification_proxy; `mean_regression_pi_coverage_95`; regression MAE CI across folds; per_scenario_baseline_mae, trigger_met, regression_skipped_reason, stump_mae, scaling_fit). `--profile all|real_world|core`; publishable: 12--20+ seeds, `--fault-mix`. Tables: `export_scaling_tables.py`. Figure: `plot_scaling_mae.py`. See `docs/P5_SCALING_SPEC.md`. |
| P6 | `llm_redteam_eval.py`, `p6_publish_bundle.py`, `verify_p6_camera_ready_bundle.py`, `export_p6_final_audit_bundle.py` | **Canonical (committed):** `llm_eval_camera_ready_20260424/` — `red_team_results.json` (expanded red-team + confusable + jailbreak_style; run_manifest, attribution incl. `ponr_gate_only`, cross_model_summary when 2+ models), `confusable_deputy_results.json`, `e2e_denial_trace.json`, `adapter_latency.json` (--run-adapter; optional --latency-decomposition), `baseline_comparison.json`, `baseline_comparison_args.json`, `baseline_benign.json`, `denial_trace_stats.json`, `replay_denials.json`, `mock_execution_harness.json`, `task_critical_injection.json`, `p6_artifact_hashes.json`. **Final audit (freeze):** `p6_final_audit_20260424/` — recomputed checks, hashes, GPT-5.x forensics, replay frozen-vs-trace-scan (`reproducibility_check.json`), claims checklist; run `export_p6_final_audit_bundle.py --out-dir datasets/runs/p6_final_audit_20260424`. **Scratch regen:** default `--out datasets/runs/llm_eval/` (gitignored). Optional: `p6_adaptive_results.json` from `p6_adaptive_suite_run.py`. Validator stack: allow_list + safe_args + ponr_gate + privilege heuristic (containment). Exports: `export_llm_redteam_table.py`, `export_p6_baseline_table.py`, `export_p6_artifact_hashes.py`, `export_p6_reproducibility_table.py`, `export_p6_layer_attribution.py`, `export_p6_failure_analysis.py`, `export_p6_cross_model_heatmap.py`, `export_p6_latency_decomposition.py`. Optional experiments: p6_concurrency_benchmark, p6_capture_ablation, p6_storage_benchmark, p6_cost_model, p6_policy_sweep, p6_replanning_benchmark, p6_adaptive_suite_run. OWASP: docs/P6_OWASP_MAPPING.md. Figure: `plot_llm_adapter_latency.py`. success_criteria_met.trigger_met. |
| P7 | `run_assurance_eval.py`, `run_assurance_negative_eval.py`, `export_bounded_review_packet.py`, `export_aies_assurance_tables.py`, `export_aies_review_packet_figure.py`, `audit_bundle.py` | `assurance_eval/results.json` (three profiles: lab v0.1, warehouse v0.1, medical v0.1; per_profile) and `assurance_eval_aies/` (AIES bundle: `baseline_summary.json`, `institutional_positive_summary.json`, `negative_summary.json`, `bounded_review_packet/`, `tables/`, `figures/`, `RUN_MANIFEST.json`). Standards mapping table: docs/P7_STANDARDS_MAPPING.md. AIES sprint docs: `docs/AIES_2026_ASSURANCE_SPRINT.md`, `docs/AIES_2026_ENGINEERING_DELIVERY.md`. Auditor: `audit_bundle.py` (mapping + PONR; `--release` for one-command audit). PONR requires --scenario-id from known list. Part 11: docs/PART11_AUDIT_TRAIL_ALIGNMENT.md. Figure: `export_assurance_gsn.py`. |
| P8 | `meta_eval.py`, `meta_collapse_sweep.py`, `verify_p8_meta_artifacts.py` | `meta_eval/comparison.json` (schema_version, meta_non_worse_collapse, meta_strictly_reduces_collapse, collapse_paired_analysis, trigger_met; stress_selection_policy when `--non-vacuous`). Publishable: `run_paper_experiments.py --paper P8` runs v0 + `scenario_regime_stress_v1/`; or manual per-scenario `meta_collapse_sweep.py` + `meta_eval.py --non-vacuous` with `--scenario`. Optional `--fallback-adapter retry_heavy`. Tables: `export_meta_tables.py`. Figure: `plot_meta_collapse.py` (t- and Wilson uncertainty). |

Commands and options: [docs/EVALS_RUNBOOK.md](docs/EVALS_RUNBOOK.md). To run a focused set of experiments per paper in one go: `python scripts/run_paper_experiments.py` (or `--quick` for fewer seeds, `--paper P2` for a single paper). For presentable key numbers for P5/P6/P8, see [RUN_RESULTS_SUMMARY.md](datasets/runs/RUN_RESULTS_SUMMARY.md) or run `python scripts/export_key_results_p5_p6_p8.py`. For P3 (and other papers), use the eval JSON paths in [docs/RESULTS_PER_PAPER.md](docs/RESULTS_PER_PAPER.md). Interpretation of results and experiment plan: [docs/EVAL_RESULTS_INTERPRETATION.md](docs/EVAL_RESULTS_INTERPRETATION.md). CI runs the evaluation scripts in the `conditional-evals` job. The test job runs all tests, including integration tests that launch P1–P8 eval scripts and assert on their outputs.

**External use.** We invite external groups to run our evals and report `run_manifest` and key metrics. Benchmarks: [bench/contracts](bench/contracts) (P1 Coordination Contract Benchmark), [bench/maestro](bench/maestro) (P4 MAESTRO scenarios and adoption). See [docs/EVALS_RUNBOOK.md](docs/EVALS_RUNBOOK.md) for commands and [bench/maestro/README.md](bench/maestro/README.md) for MAESTRO adoption (add your adapter, run one scenario, submit a results snippet).

**Key documentation:** [PORTFOLIO_BOARD.md](PORTFOLIO_BOARD.md) (paper stages, next actions) | [docs/VALIDATING_A_RUN.md](docs/VALIDATING_A_RUN.md) (conformance) | [docs/INTEGRATION_CONTRACTS.md](docs/INTEGRATION_CONTRACTS.md) (ownership) | [docs/CONDITIONAL_TRIGGERS.md](docs/CONDITIONAL_TRIGGERS.md) (P2/P5/P6/P8) | [docs/STATE_OF_THE_ART_CRITERIA.md](docs/STATE_OF_THE_ART_CRITERIA.md) (rigor, peer-review bar) | [docs/PRE_SUBMISSION_CHECKLIST.md](docs/PRE_SUBMISSION_CHECKLIST.md) (before submit: tag, final pass, venue format, conditional papers P2/P5/P6/P8) | [docs/STANDARDS_OF_EXCELLENCE.md](docs/STANDARDS_OF_EXCELLENCE.md) (optional excellence metrics per paper) | [docs/VISUALS_PER_PAPER.md](docs/VISUALS_PER_PAPER.md) (tables + figures) | [docs/REPORTING_STANDARD.md](docs/REPORTING_STANDARD.md) (publishable tables/figures) | [docs/EXPERIMENTS_AND_LIMITATIONS.md](docs/EXPERIMENTS_AND_LIMITATIONS.md) (strengthened experiments, known limitations) | [docs/DRAFT_CONVERSION_CHECKLIST.md](docs/DRAFT_CONVERSION_CHECKLIST.md) (Eval to Draft) | [docs/RESULTS_PER_PAPER.md](docs/RESULTS_PER_PAPER.md) (per-paper result locations and how to read summaries) | [docs/PAPER_GENERATION_WORKFLOW.md](docs/PAPER_GENERATION_WORKFLOW.md) (repro workflow) | [docs/PAPER_BY_PAPER_NEXT_STEPS_PLAN.md](docs/PAPER_BY_PAPER_NEXT_STEPS_PLAN.md) (implementation roadmap) | [kernel/README.md](kernel/README.md) (schemas, versioning).

## Design constraint

The **kernel** is the shared spine. Papers may add optional fields, but **breaking changes require a version bump**. MAESTRO + Replay are the default release train; every other paper either produces artifacts compatible with them or consumes their datasets.
