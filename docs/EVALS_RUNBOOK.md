# Conditional Papers Evaluation Runbook

This runbook describes how to run the full evaluation pipelines for the conditional papers (P2, P5, P6, P8) and core evals (P0, P1, P3, P4, P7). Set `LABTRUST_KERNEL_DIR` to the repo `kernel/` directory (or rely on CI/default).

For interpretation of results and a plan for follow-up experiments across all papers, see [EVAL_RESULTS_INTERPRETATION.md](EVAL_RESULTS_INTERPRETATION.md). For reporting requirements (seeds, mean/stdev/p95/p99, CI, run manifest) on publishable tables, see [REPORTING_STANDARD.md](REPORTING_STANDARD.md). For moving a paper from Eval to Draft (claim table, evidence mapping, two tables + one figure, repro block), see [DRAFT_CONVERSION_CHECKLIST.md](DRAFT_CONVERSION_CHECKLIST.md) and [STATE_OF_THE_ART_CRITERIA.md](STATE_OF_THE_ART_CRITERIA.md#21-portfolio-wide-draft-conversion-checklist). Before submission, run the Phase 3 / hostile reviewer checklist in [STATE_OF_THE_ART_CRITERIA.md](STATE_OF_THE_ART_CRITERIA.md#3-submission-readiness-phase-3--hostile-reviewer-checklist). For the full peer-review visual set (Figure 0 overview diagram + tables + result figures per paper), see [VISUALS_PER_PAPER.md](VISUALS_PER_PAPER.md); overview diagrams are produced by `export_p0_assurance_pipeline.py` through `export_p8_meta_diagram.py` (output `.mmd` under `docs/figures/`). Integration tests (tests/test_contracts_p1.py, test_rep_cps_p2.py, test_replay_p3.py, test_maestro_p4.py, test_scaling_p5.py, test_llm_p6.py, test_assurance_p7.py, test_meta_p8.py) run the corresponding eval scripts and assert on output; P8 also includes unit tests for the meta-controller. Run with `python -m unittest discover -s tests` or `pytest tests`.

**CI vs publishable:** CI uses reduced seeds (e.g. 2–5) for speed. Publishable default is **20 seeds**; scripts default to 20. For any result table or figure used in a draft, use the default or regenerate with explicit seeds. Use `--seeds 10` for quick local runs; `--seeds 30` for sensitivity. Run manifest in each summary JSON records seeds and scenario. See [REPORTING_STANDARD.md](REPORTING_STANDARD.md).

**Excellence metrics:** Eval scripts write optional `excellence_metrics` to their summary JSONs (see [STANDARDS_OF_EXCELLENCE.md](STANDARDS_OF_EXCELLENCE.md)). To print a one-line excellence summary across all papers: `python scripts/export_excellence_summary.py` (or `--json` for machine output). Regenerate evals to populate excellence_metrics in JSONs that do not yet have them.

**Sensitivity (N=10, 20, 30):** To compare results across sample sizes, run the same eval at N=10, 20, 30 and compare `difference_mean`, `difference_ci95`, `difference_ci_width`, `paired_t_p_value` in the output JSONs. Or use `PYTHONPATH=impl/src python scripts/sensitivity_seed_sweep.py [--eval meta|rep_cps]` to run meta_eval (or rep_cps_eval) at N=10, 20, 30 and write `datasets/runs/sensitivity_sweep/sensitivity_summary.json` with one row per N. Use this to report "results stable at N=20, N=30" or "CI narrows with N."

**Camera-ready / key numbers:** For P5, P6, P8, see [RUN_RESULTS_SUMMARY.md](../datasets/runs/RUN_RESULTS_SUMMARY.md) (written when those evals are run; often via `run_paper_experiments.py`). To export a markdown "Key results" block: `python scripts/export_key_results_p5_p6_p8.py`. **P3** and other papers use their own JSON under `datasets/runs/` (see [RESULTS_PER_PAPER.md](RESULTS_PER_PAPER.md)); P3: `replay_eval/summary.json` and `verify_p3_replay_summary.py`.

## Paper-tailored experiment runner

To run a focused set of experiments per paper in one go:

```bash
# All papers (surgical params: delay sweep, multi-scenario, overhead curve, etc.)
PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/run_paper_experiments.py

# Quick mode (fewer seeds for faster smoke)
PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/run_paper_experiments.py --quick

# Single paper
PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/run_paper_experiments.py --paper P2
```

PowerShell: `$env:PYTHONPATH="impl\src"; $env:LABTRUST_KERNEL_DIR="$PWD\kernel"; python scripts/run_paper_experiments.py [--quick] [--paper P0|...|P8]`

Per-paper runs: P0 (E1 conformance corpus + E2 redaction + E3 replay link + E4 multi-adapter + Table 1/2/3 + Figures 1-3 + build_p0_conformance_summary); P1 (corpus eval + scale-test/scale-sweep + transport_parity.py + optional async stress + export_p1_appendix_tex + render_p1_flow_figure + plot_p1_paper_figures); P2 (delay sweep, three scenarios: toy_lab_v0, lab_profile_v0, rep_cps_scheduling_v0, 20 seeds; scheduling_dependent_eval, freshness_replay_evidence, sybil_vs_spoofing_evidence, messaging_sim, dynamic_aggregation_series); P3 (replay + expanded corpus + corpus_space_summary + Table 1/1b export + overhead curve + baselines + multi-seed thin-slice seeds + verify_p3_replay_summary; --overhead-runs 20; optional --l1-twin); P4 (fault sweep 20 seeds, two scenarios + antigaming + baselines); P5 (multiscenario: all scenario YAMLs by default via `--profile all`, 20 seeds + `--fault-mix`, `scaling_heldout_eval` with optional `--holdout-mode family` / `scaling_eval_family/`, secondary_targets, trigger_met); P6 (expanded red-team + confusable + jailbreak-style + adapter latency + baselines including benign + p6_adaptive_suite_run, 3 scenarios, 20 seeds; optional --real-llm [--real-llm-suite full|core] for Table 1b; --run-baseline [--baseline-plan benign|args_unsafe]; --denial-stats; --latency-decomposition; export_p6_reproducibility_table, export_p6_layer_attribution, export_p6_failure_analysis, export_p6_cross_model_heatmap, export_p6_latency_decomposition; optional p6_concurrency_benchmark, p6_capture_ablation, p6_storage_benchmark, p6_cost_model, p6_policy_sweep, p6_replanning_benchmark; scripts/p6_publish_bundle.py); P7 (assurance + three profiles + audit_bundle + export tables); P8 (collapse sweep then meta_eval --non-vacuous --fallback-adapter retry_heavy, 20 seeds; trigger_met and no_safety_regression). After a full run, see [datasets/runs/RUN_RESULTS_SUMMARY.md](../datasets/runs/RUN_RESULTS_SUMMARY.md) for a consolidated results summary. **P0 conformance summary:** `python scripts/build_p0_conformance_summary.py` writes `datasets/releases/portfolio_v0.1/p0_conformance_summary.json`. **P7 one-command audit:** `python scripts/audit_bundle.py --release datasets/releases/portfolio_v0.1` runs mapping + PONR and review if release dir contains evidence_bundle.json.

## Environment

```bash
export LABTRUST_KERNEL_DIR="$PWD/kernel"   # Linux/macOS
# PowerShell: $env:LABTRUST_KERNEL_DIR = "$PWD\kernel"
export PYTHONPATH="impl/src"
```

**Reproducibility:** Set **LABTRUST_FIXED_SEED** (integer) so stochastic steps (e.g. bootstrap in comparison stats) use a fixed seed; run_manifest still records the seeds used per run. Same seed list + same script + same LABTRUST_FIXED_SEED yields reproducible comparison stats. See [REPORTING_STANDARD.md](REPORTING_STANDARD.md).

## P1 — Contracts

- **Script:** `scripts/contracts_eval.py`
- **Output:** `datasets/runs/contracts_eval/eval.json` (corpus sequences, detection_ok by exact verdict vector, excellence_metrics with per_class_ci95 and split_brain_detection_advantage, ablation, ablation_by_class, **detection_metrics_by_class**, detection_metrics with F1, latency_percentiles_us with event-level CI95, resource_and_cost; run_manifest.script_version, corpus_fingerprint). With `--baseline`: adds `violations_would_apply_without_validator` (ablation/baselines are always present). With `--scale-test`: `scale_test.json` (use `--scale-test-runs 5` for mean/stdev). With `--scale-sweep 1000,10000,100000`: `scale_sweep.json`. Async stress: `python scripts/contracts_async_stress.py` writes `stress_results.json` with delay/skew/reorder sweep results. Transport parity: `python scripts/contracts_transport_parity.py` writes `transport_parity.json` with **`parity_ok_all`**, **`per_sequence[]`**, and **`parity_confidence`**; default multi-sequence stems; override with `--sequences stem1,stem2,...`. Publishable run includes corpus eval, scale test (or scale sweep), async stress (optional), and transport parity.
- **Gatekeeper:** `allow_release(run_dir, check_contracts=True)` runs contract validator on trace; use for strict PONR gating. CLI: `labtrust_portfolio release-dataset --check-contracts <run_dir> <release_id>` denies release when any trace event is contract-denied; default (no flag) is conformance-only so thin-slice runs can release.
- **State machine:** `impl/.../instrument_state_machine.py`; contract `use_instrument_state_machine: true` aligns single-writer with idle/running transitions. See `bench/contracts/README.md`.
- **Lab profile integration:** One PONR transition (release) is gated: contract-invalid trace leads to gatekeeper denying release. See `tests/test_thinslice_e2e.TestThinSliceE2E.test_gatekeeper_denies_when_contract_invalid` and `docs/P1_TRACE_DERIVABILITY.md`.
- **Tables/figures:** Corpus table: `python scripts/export_contracts_corpus_table.py`; appendix longtable: `python scripts/export_p1_appendix_tex.py`; Figure 0 (submission asset): `python scripts/render_p1_flow_figure.py`; scale throughput: `python scripts/plot_contracts_scale.py` (reads existing scale artifacts by default; `--rerun` forces fresh runs); journal figures (latency/comparator/coverage/stress): `python scripts/plot_p1_paper_figures.py`.

```bash
PYTHONPATH=impl/src python scripts/contracts_eval.py [--out datasets/runs/contracts_eval] [--baseline]
PYTHONPATH=impl/src python scripts/contracts_eval.py --scale-test [--scale-events 100000] [--scale-test-runs 5]
PYTHONPATH=impl/src python scripts/contracts_eval.py --scale-sweep 1000,10000,100000 [--scale-test-runs 5]
PYTHONPATH=impl/src python scripts/contracts_async_stress.py [--out datasets/runs/contracts_eval] [--delay-sweep 0,0.001,0.01] [--skew-sweep 0,0.1,0.5] [--reorder-probs 0,0.1,0.2]
PYTHONPATH=impl/src python scripts/contracts_transport_parity.py [--out datasets/runs/contracts_eval] [--sequences good_sequence,split_brain_sequence,reorder_sequence,actor_payload_writer_mismatch]
```

## P2 — REP-CPS (safety-gated profile)

- **Bottleneck scenario:** `toy_lab_v0` (configurable via `--scenario`).
- **Script:** `scripts/rep_cps_eval.py`
- **Output:** `datasets/runs/rep_cps_eval/summary.json` (and per-run dirs under `rep_cps/`, `centralized/`). Also: `aggregation_variants`, `sybil_sweep[]`, `magnitude_sweep[]`, `trim_fraction_sweep[]`, `resilience_envelope`, `latency_cost`, `profile_ablation[]` (Table 6), `safety_gate_denial` (including `safety_gate_campaign`, `denial_trace_recorded`), `per_scenario` (aggregated metrics per scenario_id), `n_sensitivity`, `excellence_metrics` (including comparison statistics: difference_mean, difference_ci95, paired_t_p_value, power_post_hoc).
- **Metrics:** adapter comparison (tasks_completed; adapter parity); aggregation under compromise (robust reduces observed bias vs naive); latency/cost (wall time per policy, aggregation compute ms, overhead vs centralized); resilience envelope (safe operating region, failure boundary); safety-gate campaign (pass/deny counts; denial when aggregate exceeds threshold); profile ablation; sybil/magnitude/trim sweeps; per-scenario summaries; comparison statistics (paired tests on non-scheduling scenarios). Trigger partially met on `rep_cps_scheduling_v0` (contribution is profile and harness). When `--aggregation-steps > 1`: optional convergence (steps_to_convergence, convergence_achieved_rate); Table 4 via `python scripts/export_rep_cps_convergence_table.py`. N-sensitivity: `python scripts/sensitivity_seed_sweep.py --eval rep_cps --ns 20,30`.
- **Options:** `--drop-sweep` (comma-separated drop_completion_prob values; default: 0.02 single value; use 0,0.01,0.02,0.05 for sweep).
- **Tables:** `python scripts/export_rep_cps_tables.py` (Tables 1–7 from summary.json, including latency Table 5, resilience Table 7, per-scenario summary, comparison statistics, messaging_sim, dynamic_aggregation_series, offline comparator blocks).
- **Figures (P2 set):**
  - Figure 0: `python scripts/export_p2_rep_profile_diagram.py` (Mermaid source); optional camera-ready render via `--render-png|--render-svg|--render-pdf`.
  - Figure 1: `python scripts/plot_rep_cps_summary.py` (global + per-scenario tasks outputs).
  - Figure 2: `python scripts/plot_rep_cps_gate_threshold.py` (gate-threshold sensitivity).
  - Figure 3: `python scripts/plot_rep_cps_dynamics.py` (dynamic aggregation series).
  - Figure 4: `python scripts/plot_rep_cps_latency.py` (latency by policy, mean + p95 tail whiskers).

```bash
# Publishable: default 20 seeds; default scenarios include rep_cps_scheduling_v0 (gate-linked scheduling). Quick/CI: --seeds 2 or --seeds 5.
PYTHONPATH=impl/src python scripts/rep_cps_eval.py [--scenario toy_lab_v0] [--out datasets/runs/rep_cps_eval]
# Delay sweep + multi-scenario (publishable default 20 seeds):
PYTHONPATH=impl/src python scripts/rep_cps_eval.py --delay-sweep 0,0.05,0.1,0.2 --scenarios toy_lab_v0,lab_profile_v0,rep_cps_scheduling_v0
# Optional drop_completion_prob sweep (broader fault coverage):
PYTHONPATH=impl/src python scripts/rep_cps_eval.py --delay-sweep 0,0.05,0.1 --scenarios toy_lab_v0,lab_profile_v0,rep_cps_scheduling_v0 --drop-sweep 0,0.01,0.02,0.05
python scripts/export_rep_cps_tables.py
python scripts/export_rep_cps_convergence_table.py [--summary datasets/runs/rep_cps_eval/summary.json]
PYTHONPATH=impl/src python scripts/plot_rep_cps_summary.py
PYTHONPATH=impl/src python scripts/plot_rep_cps_gate_threshold.py
PYTHONPATH=impl/src python scripts/plot_rep_cps_dynamics.py
PYTHONPATH=impl/src python scripts/plot_rep_cps_latency.py
```

## P3 — Replay

- **Script:** `scripts/replay_eval.py`
- **Output:** `datasets/runs/replay_eval/summary.json` (or `--out` path). **Use a file path for `--out`** (e.g. `datasets/runs/replay_eval/summary.json`), not a directory. Includes `schema_version`, `baseline_overhead`, `multi_seed_overhead`, `corpus_outcome_wilson_ci95`, `per_trace[]` with **`corpus_category`** (synthetic_trap, field_proxy, real_ingest, synthetic_pass), `root_cause_category`, **witness_slice**, **localization_matches_expected**, **trace_json_bytes**, **state_hash_after_count**, **diagnostic_payload_bytes_approx**; top-level **witness_slices**; **`corpus_space_summary`** (aggregate sizes); optional **`process_peak_rss_bytes`** (often null on Windows); `overhead_stats` (empirical p95/p99, bootstrap CIs); with `--overhead-curve`: `overhead_curve[]` (event_count, p95_replay_ms, optional CI fields). Tables: `python scripts/export_replay_corpus_table.py --out-md papers/P3_Replay/generated_tables.md` for Table 1 and Table 1b.
- **L1:** L1 stub (L0 + twin config validation) and L1 twin (`--l1-twin`: deterministic re-run of control-plane state machine across all thin-slice seeds; `l1_twin_ok`, `l1_twin_final_hash_match`, **`l1_twin_summary`** with multi-seed aggregate statistics: n_seeds, all_pass, mean_time_ms, stdev_time_ms, min/max_time_ms). L2 aspirational with design subsection in REPLAY_LEVELS. Corpus tables: `python scripts/export_replay_corpus_table.py` (stdout) or `--out-md papers/P3_Replay/generated_tables.md` for the paper snapshot. See `bench/replay/README.md` and `kernel/trace/REPLAY_LEVELS.v0.1.md`.
- **Figure:** `python scripts/plot_replay_overhead.py` (p95 replay ms vs event count from overhead_curve).

```bash
PYTHONPATH=impl/src python scripts/replay_eval.py --out datasets/runs/replay_eval/summary.json [--corpus-dir bench/replay/corpus] [--overhead-curve] [--overhead-runs 20] [--thin-slice-seeds 42,43,44,45,46] [--bootstrap-reps 500] [--l1-twin] [--warmup 0] [--no-baselines]
python scripts/plot_replay_overhead.py
python scripts/verify_p3_replay_summary.py --strict-curve
```

## P5 — Scaling

- **Prerequisite:** Multi-scenario runs. Generate with `scripts/generate_multiscenario_runs.py`, then run held-out eval.
- **Scenarios:** Default `--profile all` uses every `bench/maestro/scenarios/*.yaml` (currently seven ids including `regime_stress_v1`, `rep_cps_scheduling_v0`). Use `--profile real_world` to omit `toy_lab_v0`, or `--profile core` for the legacy five-scenario list. Override with `--scenarios id1,id2,...`. Shard with `--seed-min` / `--seed-max` for parallel workers.
- **Output:** `datasets/runs/scaling_eval/heldout_results.json` (default `--holdout-mode scenario`). Optional stricter generalization: second directory e.g. `scaling_eval_family/heldout_results.json` from `--holdout-mode family` (leave-one-taxonomy-family-out: lab / warehouse / traffic). Summary includes `holdout_mode`, `secondary_targets` (coordination_tax_proxy, error_amplification_proxy unless `--no-secondary`), `mean_regression_pi_coverage_95`, `overall_regression_mae_ci95_lower/upper`, `held_out_results[].regression_pi_coverage_95`, `scaling_fit`, `feature_ablation`, `success_criteria_met`, `excellence_metrics`.
- **Metrics:** Held-out MAE per fold (global mean, oracle per-scenario, admissible train-only baselines, num-tasks bucket, full P5 feature regression with ridge stabilization when the default feature vector has six or more columns, stump); collapse rate; exploratory log-log scaling exponent. Spec: [P5_SCALING_SPEC.md](P5_SCALING_SPEC.md). **Figures:** `plot_scaling_paper.py` (P5 pipeline) writes under `docs/figures/`. **Publishable:** `run_paper_experiments.py --paper P5` (not `--quick`): **30** seeds, **`--profile real_world`**, **`--coordination-grid`**, **`--agent-counts 1,2,4,8`**, **`--fault-settings no_drop,drop_005`**, `--clean` on `multiscenario_runs` → **7200** runs; then all five holdout modes, `scaling_sensitivity_sweep.py`, `scaling_recommend_eval.py`, `export_scaling_regime_agent_summary.py`, `export_scaling_tables.py`, `plot_scaling_paper.py`. **`--quick`:** fewer seeds, `core` profile, `--p5-lite` grid (CI smoke only).

```bash
PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/run_paper_experiments.py --paper P5
# Piecemeal (same as orchestrator uses internally):
PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/generate_multiscenario_runs.py --out datasets/runs/multiscenario_runs --seeds 30 --coordination-grid --clean --profile real_world --agent-counts 1,2,4,8 --fault-settings no_drop,drop_005
PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/scaling_heldout_eval.py --runs-dir datasets/runs/multiscenario_runs --out datasets/runs/scaling_eval --holdout-mode scenario
PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/scaling_sensitivity_sweep.py --runs-dir datasets/runs/multiscenario_runs --out-dir datasets/runs/sensitivity_sweep
PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/export_scaling_tables.py --results datasets/runs/scaling_eval/heldout_results.json --family-results datasets/runs/scaling_eval_family/heldout_results.json --agent-results datasets/runs/scaling_eval_agent_count/heldout_results.json --recommend-results datasets/runs/scaling_recommend/recommendation_eval.json --sensitivity-results datasets/runs/sensitivity_sweep/scaling_sensitivity.json --regime-agent-summary datasets/runs/scaling_summary/regime_agent_summary.json --out papers/P5_ScalingLaws/generated_tables.md
```

**Prime Intellect (disks + pods) for heavy P5/P8:** [PRIME_COMPUTE_P5_P8.md](PRIME_COMPUTE_P5_P8.md).

## P6 — LLM Planning

- **Script:** `scripts/llm_redteam_eval.py`
- **Output:** **Canonical committed bundle:** `datasets/runs/llm_eval_camera_ready_20260424/` holds the frozen Table 1b + adapter/baseline/replay artifacts for submission. **Final engineering audit (freeze):** `datasets/runs/p6_final_audit_20260424/` from `python scripts/export_p6_final_audit_bundle.py --out-dir datasets/runs/p6_final_audit_20260424` (recompute-from-JSON checks, hashes, GPT-5.x forensics, replay frozen `replay_denials.json` vs full `trace.json` scan documented in `reproducibility_check.json`). **Scratch regeneration:** same filenames under `datasets/runs/llm_eval/` when using default `--out`. Artifacts: `red_team_results.json` (expanded red-team suite; run_manifest with timestamp_iso, evaluator_version, policy_version, prompt_template_hash; per-case attribution and denial_by_layer including `ponr_gate_only`; cross_model_summary when 2+ models; run_details for argument-level cases when n_runs>1); `confusable_deputy_results.json` (6 cases; attribution); `e2e_denial_trace.json`; with `--run-adapter`: `adapter_latency.json` (runs, tail_latency_p95_mean_ms; optional latency_decomposition when `--latency-decomposition`; optional denial_stats when `--denial-stats`); `baseline_comparison.json`, `baseline_comparison_args.json` (with `--run-baseline`); `baseline_benign.json` (with `--run-baseline --baseline-plan benign`); `denial_trace_stats.json` (with `--run-adapter --denial-stats`); optional `p6_adaptive_results.json` from `p6_adaptive_suite_run.py`. **Integrity gate:** `python scripts/verify_p6_camera_ready_bundle.py`.
- **Metrics:** red-team pass/fail; confusable deputy; jailbreak-style (in red_team_results.json); E2E denial trace; adapter tail latency; baseline 3-way (gated/weak/ungated) tool-level, args_unsafe, benign. Optional real-LLM: `--real-llm` with `--real-llm-provider auto` (default): `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` in `.env`; `gpt-*` / `claude-*` model ids; or **Prime Inference** (below). Results in `real_llm` or `real_llm_models[]`; `suite_mode` full vs core. OWASP: `docs/P6_OWASP_MAPPING.md`.
- **Options:** `--out DIR`; `--run-adapter`; `--adapter-scenarios toy_lab_v0,lab_profile_v0,warehouse_v0` (default: 3 scenarios); `--adapter-seeds` (default: 1..20); `--denial-stats` (with --run-adapter: denial_trace_stats.json); `--run-baseline` (gated vs weak vs ungated); `--baseline-plan benign|args_unsafe` (benign = utility/false-positive study; args_unsafe = safe_args ablation); `--latency-decomposition` (adapter_latency.json gains latency_decomposition); `--latency-threshold-ms N`; `--real-llm`; `--real-llm-provider auto|openai|anthropic|prime` (default auto); `--real-llm-models` / `--real-llm-model`; `--real-llm-runs N` (default 10); `--real-llm-suite full|core` (full = red + confusable + jailbreak in Table 1b loop). **Camera-ready reference run:** `--out datasets/runs/llm_eval_camera_ready_20260424 --real-llm --real-llm-runs 3 --real-llm-suite full` for Table 1b; verify success_criteria_met.trigger_met.
- **Prime Inference (P6):** OpenAI-compatible API at `https://api.pinference.ai/api/v1` ([Chat Completions](https://docs.primeintellect.ai/api-reference/inference-chat-completions)). Set **`PRIME_INTELLECT_API_KEY`** (or `PRIME_API_KEY`) in `.env`; API key must have **Inference** permission ([overview](https://docs.primeintellect.ai/inference/overview)). Optional **`PRIME_TEAM_ID`**: sent as header `X-Prime-Team-ID` for team billing. Use `--real-llm-provider prime` and model ids from `prime inference models` (example: `meta-llama/llama-3.1-70b-instruct`). The eval retries with exponential backoff on HTTP 429. Smoke: `--real-llm-runs 1` and one model before a full Table 1b run.
- **OpenAI GPT-5.x note (P6):** For `gpt-5*`, the client path uses Responses API first, falls back to `chat.completions`, retries without `temperature` if unsupported, and uses bounded timeouts. Keep these runs in separate `--out` directories and label as supplementary unless they are promoted into the canonical camera-ready denominator.
- **Tables/figures:** Red-team: `export_llm_redteam_table.py --out-dir datasets/runs/llm_eval_camera_ready_20260424`. Baseline: `export_p6_baseline_table.py` (use `--baseline-file baseline_comparison_args.json` or baseline_benign.json as needed). Artifact hashes: `export_p6_artifact_hashes.py --out-dir datasets/runs/llm_eval_camera_ready_20260424`. Reproducibility table: `export_p6_reproducibility_table.py`. Final audit bundle: `export_p6_final_audit_bundle.py --out-dir datasets/runs/p6_final_audit_20260424`. Layer attribution: `export_p6_layer_attribution.py`. Failure analysis: `export_p6_failure_analysis.py`. Cross-model heatmap: `export_p6_cross_model_heatmap.py`. Latency decomposition: `export_p6_latency_decomposition.py`. Firewall flow: `export_p6_firewall_flow.py`. Denial-trace case study: `export_p6_denial_trace_case_study.py --trace path`. **Optional experiments:** p6_concurrency_benchmark.py, p6_capture_ablation.py, p6_storage_benchmark.py, p6_cost_model.py, p6_policy_sweep.py, p6_replanning_benchmark.py, p6_adaptive_suite_run.py. See papers/P6_LLMPlanning/sat-cps2026/EXPERIMENTS_RUNBOOK.md.
- **Figure 1:** `python scripts/plot_llm_adapter_latency.py` (output `docs/figures/p6_adapter_latency.png`; requires adapter_latency.json from `--run-adapter`).
- **Integration test:** `tests/test_llm_p6.py` runs eval with `--run-adapter --adapter-scenarios toy_lab_v0 --adapter-seeds 7` and asserts both artifacts.

```bash
PYTHONPATH=impl/src python scripts/llm_redteam_eval.py [--out datasets/runs/llm_eval_camera_ready_20260424]
PYTHONPATH=impl/src python scripts/llm_redteam_eval.py --run-adapter --adapter-scenarios toy_lab_v0 --adapter-seeds 7
python scripts/plot_llm_adapter_latency.py [--latency datasets/runs/llm_eval_camera_ready_20260424/adapter_latency.json]
PYTHONPATH=impl/src python scripts/llm_redteam_eval.py --run-adapter --latency-threshold-ms 5000   # SLA check
# Prime Inference (after prime login / API key with Inference permission):
PYTHONPATH=impl/src python scripts/llm_redteam_eval.py --real-llm --real-llm-provider prime --real-llm-models meta-llama/llama-3.1-70b-instruct --real-llm-runs 1
# Prime top-4 matrix (stable ranking run):
PYTHONPATH=impl/src python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval_prime_matrix_top4_n3 --real-llm --real-llm-provider prime --real-llm-models x-ai/grok-4-fast,google/gemini-2.5-flash,openai/gpt-4.1-mini,qwen/qwen3-30b-a3b-instruct-2507 --real-llm-runs 3
```

Exit code 1 if any red-team case fails (expected_block not satisfied).

## P7 — Assurance (mapping + review)

- **Script:** `scripts/run_assurance_eval.py [--out DIR]`. Default output: `datasets/runs/assurance_eval/results.json`. Runs check_assurance_mapping and review on toy_lab_v0 and lab_profile_v0 (Table 2); materializes additional thin-slice runs so per_profile reviews are scenario-matched (lab on lab_profile_v0, warehouse on warehouse_v0, medical on traffic_v0 as a pipeline/proxy pairing—see `run_manifest` notes). Table 1 primary review is lab_profile_v0 (kernel PONR disposition_commit).
- **Output:** mapping_check (ok, ponr_coverage_ok), review (primary Table 1 row = lab_profile_v0), reviews (per scenario), per_profile (per pack on matched scenario), run_manifest (per_profile_scenario, table1_primary_scenario).
- **Check:** `scripts/check_assurance_mapping.py` (--inst, --profile-dir); schema + mapping completeness + PONR coverage.
- **Auditor walk-through:** `scripts/audit_bundle.py [--run-dir DIR] [--inst path] [--profile-dir path] [--scenario-id toy_lab_v0]` prints pass/fail for mapping completeness and PONR coverage (and optional run review); outputs JSON + human-readable. **One-command audit over release:** `scripts/audit_bundle.py --release datasets/releases/portfolio_v0.1` runs mapping + PONR; if the release dir contains evidence_bundle.json, review runs there too.
- **Part 11:** See `docs/PART11_AUDIT_TRAIL_ALIGNMENT.md` for evidence-bundle/trace mapping to Part 11-style audit trail (each requirement mapped to artifact path and field; machine-checkable). Non-goals: no certification claim; translation layer only. **Three profiles:** lab v0.1, warehouse v0.1, medical v0.1; results include per_profile (P7 DRAFT, kernel/assurance_pack/README.md, profiles/). Standards mapping table: `docs/P7_STANDARDS_MAPPING.md`. Kill criterion K7: no "template theater"; every mapping claim checkable by script or schema.
- **Review:** `scripts/review_assurance_run.py <run_dir> [--scenario-id <id>] [--review-mode schema_only|schema_plus_presence|full_review]`. Default `full_review`: scenario/trace alignment, PONR tasks, **all** evidence types per control, bundle+release SHA vs files. Weaker modes are **ablation baselines** for discrimination experiments. Failure codes: `docs/P7_REVIEW_FAILURE_CODES.md`. Scripted review is partial; no certification claim.
- **Robust matrix:** `scripts/run_assurance_robust_eval.py` (default seeds 1..20, 400 runs). `run_manifest.scenario_profile_alignment` documents scenario→pack pairing; see note for traffic_v0↔medical_v0.1.
- **Negative controls:** `scripts/run_assurance_negative_eval.py [--quick]` writes `datasets/runs/assurance_eval/negative_results.json` (`generation`, `aggregate`, `by_mode`, `by_family`, `by_scenario`, `by_perturbation`, per-row codes and latency). Use `--submission-mode` (or `--redact-paths`) for blind-review-safe manifests. `scripts/export_p7_negative_tables.py` emits CSVs under `papers/P7_StandardsMapping/`: Tables 4–6 (`p7_negative_family_summary.csv`, `p7_ablation_summary.csv`, `p7_failure_reason_breakdown.csv`) plus `p7_perturbation_reject_matrix.csv`, `p7_aggregate_lift_metrics.csv`, `p7_latency_by_mode.csv`, `p7_negative_by_scenario.csv`, `p7_boundary_case_summary.csv`, and provenance sidecars (`p7_submission_manifest_redacted.json`, `p7_generation_metadata.json`).
- **AIES 2026 bundle:** Use a dedicated output root `datasets/runs/assurance_eval_aies/`. Run `run_assurance_eval.py` and `run_assurance_negative_eval.py --submission-mode` into that root, materialize a representative `lab_profile_v0` run, then export bounded packet/tables/figure. Main-text artifacts are institutional baseline (`lab_profile_v0`) and portability (`warehouse_v0`); traffic/medical proxy artifacts are exported only under `proxy_stress_only/`. Use `export_bounded_review_packet.py --submission-mode` for path-redacted packet metadata.
- **Export:** `scripts/export_assurance_tables.py [--results path]` prints Table 1–2; Table 3 from `robust_results.json` when present. GSN-lite: `export_assurance_gsn.py`. Camera-ready Mermaid: `render_p7_mermaid_figures.py` (includes `docs/figures/p7_review_stages.mmd` — Figure 2 review-stage flow). Table index: `papers/P7_StandardsMapping/generated_tables.md`. Perturbation brief vs ids: `docs/P7_PERTURBATION_CHECKLIST.md`.
- **Integration tests:** `tests/test_assurance_p7.py`; `tests/test_assurance_negative_eval.py` (quick negative eval + export smoke + CSV↔JSON consistency checks for `by_mode`, `by_family`, and aggregate lift fields).

```bash
PYTHONPATH=impl/src python scripts/run_assurance_eval.py [--out datasets/runs/assurance_eval]
PYTHONPATH=impl/src python scripts/run_assurance_robust_eval.py [--out datasets/runs/assurance_eval]
PYTHONPATH=impl/src python scripts/run_assurance_negative_eval.py [--quick] [--submission-mode]
PYTHONPATH=impl/src python scripts/audit_bundle.py [--run-dir path/to/run] [--release datasets/releases/portfolio_v0.1] [--json-only]
PYTHONPATH=impl/src python scripts/export_assurance_tables.py
python scripts/export_p7_negative_tables.py --input datasets/runs/assurance_eval/negative_results.json [--submission-mode]
python scripts/export_assurance_gsn.py
# AIES packaging path:
PYTHONPATH=impl/src python scripts/run_assurance_eval.py --out datasets/runs/assurance_eval_aies
PYTHONPATH=impl/src python scripts/run_assurance_negative_eval.py --out datasets/runs/assurance_eval_aies --submission-mode
PYTHONPATH=impl/src python -c "from pathlib import Path; from labtrust_portfolio.thinslice import run_thin_slice; d=Path('datasets/runs/assurance_eval_aies/runs/lab_profile_v0_seed7'); d.mkdir(parents=True, exist_ok=True); run_thin_slice(d, seed=7, scenario_id='lab_profile_v0', drop_completion_prob=0.0)"
PYTHONPATH=impl/src python scripts/export_bounded_review_packet.py --run-dir datasets/runs/assurance_eval_aies/runs/lab_profile_v0_seed7 --out datasets/runs/assurance_eval_aies/bounded_review_packet --scenario-id lab_profile_v0 --submission-mode
python scripts/export_aies_assurance_tables.py --in datasets/runs/assurance_eval_aies --out datasets/runs/assurance_eval_aies/tables
python scripts/export_aies_review_packet_figure.py --in datasets/runs/assurance_eval_aies/bounded_review_packet --out datasets/runs/assurance_eval_aies/figures
```

## P8 — Meta-Coordination

- **Scenarios:** `regime_stress_v0` (default) and `regime_stress_v1` via `--scenario`; configurable `drop_completion_prob`.
- **Scripts:** `scripts/meta_eval.py`, `scripts/meta_collapse_sweep.py`, `scripts/verify_p8_meta_artifacts.py`, `scripts/export_meta_tables.py`, `scripts/plot_meta_collapse.py`
- **Output:** `--out DIR` (default `datasets/runs/meta_eval`); writes `comparison.json` with `schema_version`, fixed, meta_controller, optional naive_switch_baseline when `--run-naive`, `meta_non_worse_collapse`, `meta_strictly_reduces_collapse` (legacy alias `meta_reduces_collapse` = non-inferior counts), `collapse_paired_analysis` (McNemar, Wilson), `no_safety_regression`, `collapse_definition`, per_seed, `run_manifest` (includes `stress_selection_policy` when `--non-vacuous`), `success_criteria_met`, `excellence_metrics` (bootstrap `difference_ci95` labeled with `difference_ci95_method`; Student t CIs on per-arm means).
- **Run manifests:** comparison.json `run_manifest` (seeds, seed_count, scenario_id, fault_threshold, hysteresis, script, schema_version, non_vacuous, stress_selection_policy); collapse_sweep.json includes `schema_version` and matching scenario_id.
- **Args:** `--scenario regime_stress_v0|regime_stress_v1`, `--out`, `--seeds`, `--collapse-threshold` (default 2), `--drop-prob` (default 0.15), `--fault-threshold` (default 1; 0 = naive: switch on any fault), `--run-naive`, `--hysteresis N`, `--non-vacuous` (smallest drop_prob with any fixed-regime collapse in sweep; records policy in manifest), `--collapse-sweep-path`, `--fallback-adapter blackboard|centralized|retry_heavy`, `--stress-preset high|very_high`.
- **Collapse:** `tasks_completed < threshold` or `recovery_ok` false. Integration tests: `tests/test_meta_p8.py`, `tests/test_stats_p8_tools.py`.
- **Export:** `export_meta_tables.py` prints Table 1, interpretation blocks, optional Table 2. **Figure 1:** `plot_meta_collapse.py` plots mean tasks_completed with 95% t-intervals and collapse rate with Wilson 95% intervals.

**Publishable:** `run_paper_experiments.py --paper P8` runs per-scenario collapse_sweep + meta_eval `--non-vacuous` for **regime_stress_v0** (output `meta_eval/comparison.json`) and **regime_stress_v1** (output `meta_eval/scenario_regime_stress_v1/comparison.json`), then exports tables for both. Verify: `verify_p8_meta_artifacts.py --comparison ...` (use `--strict-publishable` for release gates: N>=20 and stress policy when non-vacuous). **CI vs publishable:** CI uses fewer seeds and does not claim draft tables; local publishable uses 20 seeds.

```bash
# Publishable (non-vacuous): per scenario, collapse sweep then meta_eval --non-vacuous
PYTHONPATH=impl/src python scripts/meta_collapse_sweep.py [--scenario regime_stress_v0] [--out datasets/runs/meta_eval] [--drop-probs 0.15,0.2,0.25,0.3] [--seeds 1,2,...,20]
PYTHONPATH=impl/src python scripts/meta_eval.py --scenario regime_stress_v0 --run-naive --fault-threshold 0 --non-vacuous [--out datasets/runs/meta_eval] [--seeds 1,2,...,20]
PYTHONPATH=impl/src python scripts/verify_p8_meta_artifacts.py --comparison datasets/runs/meta_eval/comparison.json --sweep datasets/runs/meta_eval/collapse_sweep.json
python scripts/export_meta_tables.py --comparison datasets/runs/meta_eval/comparison.json [--table2]
python scripts/plot_meta_collapse.py --sweep datasets/runs/meta_eval/collapse_sweep.json
```

## P0 — E1 corpus, E2 redaction, E3 replay link, E4 algorithm-independence

- **E1 (conformance corpus):** `scripts/build_p0_conformance_corpus.py --out datasets/runs/p0_conformance_corpus` builds challenge set (case_* dirs, corpus_manifest.json). `scripts/export_e1_corpus_table.py` produces Table 1. Conformance: `labtrust_portfolio check-conformance <run_dir>`; each run dir may have `conformance.json`.
- **E2:** `scripts/e2_redaction_demo.py --out datasets/runs/e2_redaction_demo` writes `trace_redacted.json` and `evidence_bundle_redacted.json`. `scripts/export_e2_admissibility_matrix.py` produces Table 2 (4-col verification-mode admissibility matrix).
- **E3:** `scripts/produce_p0_e3_release.py --runs N`; E3 multi-scenario: `scripts/replay_link_e3.py --scenarios toy_lab_v0,lab_profile_v0 --runs N`. Use `--standalone-verifier` to run verifier as separate process (`scripts/verify_maestro_from_trace.py`). Output: `datasets/runs/e3_summary.json`, `p0_e3_variance.json`; release: `datasets/releases/p0_e3_release`. Evidence bundle: `verification_mode` (public | evaluator | regulator). See `kernel/mads/VERIFICATION_MODES.v0.1.md`.
- **E4:** `scripts/run_p0_e4_controller_matrix.py --seeds 20 --scenarios toy_lab_v0,lab_profile_v0,rep_cps_scheduling_v0 --regimes baseline,moderate,stress,coordination_shock --out datasets/runs/p0_e4_controller_matrix.json` runs the controller matrix (publishable default). Use `datasets/runs/p0_e4_controller_pairs.jsonl` for controller-separating evidence and `datasets/runs/p0_e4_raw_failure_reasons.json` for raw-failure causal accounting; `scripts/export_p0_table3.py` consumes raw + normalized summaries and strong replay fields.
- **Focused divergence exports:** `scripts/export_p0_e4_controller_divergence_table.py` (coordination_shock + rep_cps_scheduling_v0 appendix table) and `scripts/export_p0_e4_claim_matrix.py` (claim-to-evidence guardrail). Semantic anomaly interpretation note: `docs/P0_E4_COORDINATION_SHOCK_NOTE.md`.
- **P0 tables/figures:** Table 1: build_p0_conformance_corpus, export_e1_corpus_table. Table 2: e2_redaction_demo, export_e2_admissibility_matrix. Table 3: run_p0_e4_controller_matrix, export_p0_table3 (strong replay preference from E4 raw baseline rows, then E3 strong replay). Figure 1: export_p0_assurance_pipeline. Figure 2: export_p0_tier_lattice. Figure 3: export_p0_redaction_figure. Per-seed E3: export_e3_table. plot_e3_latency. build_p0_conformance_summary → `datasets/releases/portfolio_v0.1/p0_conformance_summary.json`. See `papers/P0_MADS-CPS/DRAFT.md` Appendix.

```bash
PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/build_p0_conformance_corpus.py --out datasets/runs/p0_conformance_corpus
python scripts/export_e1_corpus_table.py --corpus datasets/runs/p0_conformance_corpus
PYTHONPATH=impl/src python scripts/e2_redaction_demo.py --out datasets/runs/e2_redaction_demo
python scripts/export_e2_admissibility_matrix.py
PYTHONPATH=impl/src python scripts/produce_p0_e3_release.py --runs 10
PYTHONPATH=impl/src python scripts/run_p0_e4_controller_matrix.py --seeds 10 --scenarios toy_lab_v0,lab_profile_v0 --regimes baseline,moderate,stress --out datasets/runs/p0_e4_controller_matrix.json
python scripts/export_p0_table3.py --e4 datasets/runs/p0_e4_raw_summary.json
python scripts/export_p0_assurance_pipeline.py
python scripts/export_p0_tier_lattice.py
python scripts/export_p0_redaction_figure.py
python scripts/plot_e3_latency.py
python scripts/build_p0_conformance_summary.py
```

## P4 — MAESTRO baselines and tables

- **Repro time:** `python scripts/repro_time_p4.py` records wall-clock for minimal repro (fault sweep + export); writes `datasets/runs/repro_manifest.json` (repro_wall_min). Use for "repro under 20 min" evidence.
- **Fault sweep:** `scripts/maestro_fault_sweep.py` writes `datasets/runs/maestro_fault_sweep/multi_sweep.json`. Sweep includes lab-real fault setting `calibration_invalid_01` (calibration_invalid_prob 0.1).
- **Anti-gaming:** `scripts/maestro_antigaming_eval.py` writes `datasets/runs/maestro_antigaming/antigaming_results.json` (always_deny, always_wait score poorly; `scoring_proof` documents legitimate_safe_min > always_wait > always_deny). See `bench/maestro/SCENARIO_SPEC.md` (Anti-gaming).
- **Adapter cost:** `bench/maestro/adapter_costs.json` (loc_estimate, hours_estimate per adapter); referenced in bench/maestro/README.md.
- **Baselines:** `scripts/maestro_baselines.py` runs Centralized, Blackboard, and RetryHeavy adapters; writes `bench/maestro/baseline_results.md` and `baseline_summary.json`. Fault-sweep reports include recovery metrics: `steps_to_completion_after_first_fault`, `tasks_completed_after_fault` (when faults occur).
- **Draft tables/figure:** `python scripts/export_maestro_tables.py` reads multi_sweep.json and baseline_summary.json and prints Table 1 (fault sweep) and Table 2 (baselines). Recovery proxy figure: `python scripts/plot_maestro_recovery.py` (tasks_completed vs fault setting).

```bash
PYTHONPATH=impl/src python scripts/maestro_fault_sweep.py [--scenarios toy_lab_v0,lab_profile_v0] [--seeds 5]
PYTHONPATH=impl/src python scripts/maestro_antigaming_eval.py [--out datasets/runs/maestro_antigaming]
```

## CI

The CI workflow runs the test job (including P1–P8 integration tests and meta-controller unit tests) and the conditional-evals job: P0 E1 (build_p0_conformance_corpus), P0 E3 (`produce_p0_e3_release.py --runs 5 --scenarios toy_lab_v0,lab_profile_v0 --no-release`), P0 E2 (`e2_redaction_demo.py`), replay_eval (corpus: all `*_trace.json` in bench/replay/corpus), maestro_fault_sweep (--seeds 5), maestro_baselines, contracts_eval, run_assurance_eval, rep_cps_eval (--delay-sweep 0,0.05,0.1), generate_multiscenario_runs, scaling_heldout_eval, llm_redteam_eval, meta_eval --run-naive --fault-threshold 0, meta_collapse_sweep (--drop-probs 0.15,0.2 --seeds 3). Results are written under `datasets/runs/` and `bench/maestro/` as above.
