# Conditional Papers Evaluation Runbook

This runbook describes how to run the full evaluation pipelines for the conditional papers (P2, P5, P6, P8) and core evals (P0, P1, P3, P4, P7). Set `LABTRUST_KERNEL_DIR` to the repo `kernel/` directory (or rely on CI/default).

For interpretation of results and a plan for follow-up experiments across all papers, see [EVAL_RESULTS_INTERPRETATION.md](EVAL_RESULTS_INTERPRETATION.md). For reporting requirements (seeds, mean/stdev/p95/p99, CI, run manifest) on publishable tables, see [REPORTING_STANDARD.md](REPORTING_STANDARD.md). For moving a paper from Eval to Draft (claim table, evidence mapping, two tables + one figure, repro block), see [DRAFT_CONVERSION_CHECKLIST.md](DRAFT_CONVERSION_CHECKLIST.md) and [STATE_OF_THE_ART_CRITERIA.md](STATE_OF_THE_ART_CRITERIA.md#21-portfolio-wide-draft-conversion-checklist). Before submission, run the Phase 3 / hostile reviewer checklist in [STATE_OF_THE_ART_CRITERIA.md](STATE_OF_THE_ART_CRITERIA.md#3-submission-readiness-phase-3--hostile-reviewer-checklist). For the full peer-review visual set (Figure 0 overview diagram + tables + result figures per paper), see [VISUALS_PER_PAPER.md](VISUALS_PER_PAPER.md); overview diagrams are produced by `export_p0_assurance_pipeline.py` through `export_p8_meta_diagram.py` (output `.mmd` under `docs/figures/`). Integration tests (tests/test_contracts_p1.py, test_rep_cps_p2.py, test_replay_p3.py, test_maestro_p4.py, test_scaling_p5.py, test_llm_p6.py, test_assurance_p7.py, test_meta_p8.py) run the corresponding eval scripts and assert on output; P8 also includes unit tests for the meta-controller. Run with `python -m unittest discover -s tests` or `pytest tests`.

**CI vs publishable:** CI uses reduced seeds (e.g. 2–5) for speed. Publishable default is **20 seeds**; scripts default to 20. For any result table or figure used in a draft, use the default or regenerate with explicit seeds. Use `--seeds 10` for quick local runs; `--seeds 30` for sensitivity. Run manifest in each summary JSON records seeds and scenario. See [REPORTING_STANDARD.md](REPORTING_STANDARD.md).

**Excellence metrics:** Eval scripts write optional `excellence_metrics` to their summary JSONs (see [STANDARDS_OF_EXCELLENCE.md](STANDARDS_OF_EXCELLENCE.md)). To print a one-line excellence summary across all papers: `python scripts/export_excellence_summary.py` (or `--json` for machine output). Regenerate evals to populate excellence_metrics in JSONs that do not yet have them.

**Sensitivity (N=10, 20, 30):** To compare results across sample sizes, run the same eval at N=10, 20, 30 and compare `difference_mean`, `difference_ci95`, `difference_ci_width`, `paired_t_p_value` in the output JSONs. Or use `PYTHONPATH=impl/src python scripts/sensitivity_seed_sweep.py [--eval meta|rep_cps]` to run meta_eval (or rep_cps_eval) at N=10, 20, 30 and write `datasets/runs/sensitivity_sweep/sensitivity_summary.json` with one row per N. Use this to report "results stable at N=20, N=30" or "CI narrows with N."

**Camera-ready / key numbers:** For a presentable snapshot of P5, P6, P8 key results (MAE, trigger_met, red-team pass, no_safety_regression, etc.), see [RUN_RESULTS_SUMMARY.md](../datasets/runs/RUN_RESULTS_SUMMARY.md) (written by `run_paper_experiments.py`). To export a markdown "Key results" block from the latest run artifacts: `python scripts/export_key_results_p5_p6_p8.py` (reads heldout_results.json, comparison.json, red_team_results.json under `datasets/runs/`). Use the output to paste into drafts or verify numbers after a publishable run.

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

Per-paper runs: P0 (E3 multi-scenario + E2 redaction + export E3 table + build_p0_conformance_summary); P1 (corpus + scale-test with variance); P2 (delay sweep, two scenarios, 20 seeds); P3 (replay + overhead curve, --overhead-runs 20; optional --l1-twin); P4 (fault sweep 20 seeds, two scenarios + antigaming + baselines); P5 (multiscenario 20 seeds + --fault-mix, held-out eval, export scaling tables; trigger_met and excellence_metrics); P6 (red-team + confusable + adapter latency, two scenarios, five adapter seeds; optional --real-llm for Table 1b); P7 (assurance + three profiles + audit_bundle + export tables); P8 (collapse sweep then meta_eval --non-vacuous --fallback-adapter retry_heavy, 20 seeds; trigger_met and no_safety_regression). After a full run, see [datasets/runs/RUN_RESULTS_SUMMARY.md](../datasets/runs/RUN_RESULTS_SUMMARY.md) for a consolidated results summary. **P0 conformance summary:** `python scripts/build_p0_conformance_summary.py` writes `datasets/releases/portfolio_v0.1/p0_conformance_summary.json`. **P7 one-command audit:** `python scripts/audit_bundle.py --release datasets/releases/portfolio_v0.1` runs mapping + PONR and review if release dir contains evidence_bundle.json.

## Environment

```bash
export LABTRUST_KERNEL_DIR="$PWD/kernel"   # Linux/macOS
# PowerShell: $env:LABTRUST_KERNEL_DIR = "$PWD\kernel"
export PYTHONPATH="impl/src"
```

**Reproducibility:** Set **LABTRUST_FIXED_SEED** (integer) so stochastic steps (e.g. bootstrap in comparison stats) use a fixed seed; run_manifest still records the seeds used per run. Same seed list + same script + same LABTRUST_FIXED_SEED yields reproducible comparison stats. See [REPORTING_STANDARD.md](REPORTING_STANDARD.md).

## P1 — Contracts

- **Script:** `scripts/contracts_eval.py`
- **Output:** `datasets/runs/contracts_eval/eval.json` (corpus sequences, excellence_metrics: corpus_detection_rate_pct, overhead_p99_us, baseline_margin_denials); with `--scale-test`: `scale_test.json` (long-trace validator timing; use `--scale-test-runs 5` for mean/stdev of events_per_sec and time_per_write_us). Publishable run includes scale test (run_paper_experiments.py runs corpus eval then scale-test with 100k events and 5 runs).
- **Gatekeeper:** `allow_release(run_dir, check_contracts=True)` runs contract validator on trace; use for strict PONR gating. CLI: `labtrust_portfolio release-dataset --check-contracts <run_dir> <release_id>` denies release when any trace event is contract-denied; default (no flag) is conformance-only so thin-slice runs can release.
- **State machine:** `impl/.../instrument_state_machine.py`; contract `use_instrument_state_machine: true` aligns single-writer with idle/running transitions. See `bench/contracts/README.md`.
- **Lab profile integration:** One PONR transition (release) is gated: contract-invalid trace leads to gatekeeper denying release. See `tests/test_thinslice_e2e.TestThinSliceE2E.test_gatekeeper_denies_when_contract_invalid` and `docs/P1_TRACE_DERIVABILITY.md`.
- **Tables/figures:** Corpus table: `python scripts/export_contracts_corpus_table.py`. Scale throughput figure: `python scripts/plot_contracts_scale.py` (output `docs/figures/p1_scale_throughput.png`).

```bash
PYTHONPATH=impl/src python scripts/contracts_eval.py [--out datasets/runs/contracts_eval]
PYTHONPATH=impl/src python scripts/contracts_eval.py --scale-test [--scale-events 100000]
```

## P2 — REP-CPS

- **Bottleneck scenario:** `toy_lab_v0` (configurable via `--scenario`).
- **Script:** `scripts/rep_cps_eval.py`
- **Output:** `datasets/runs/rep_cps_eval/summary.json` (and per-run dirs under `rep_cps/`, `centralized/`). Also: `aggregation_variants` (method, bias, max_influence_per_compromised_agent), `sybil_sweep[]`, `safety_gate_denial.json`.
- **Metrics:** adapter comparison (tasks_completed), aggregation under compromise (bias robust vs naive); clipping and median_of_means variants; sybil stress test; safety-gate denial record. When `--aggregation-steps > 1`: convergence (steps_to_convergence, convergence_achieved_rate) in summary; Table 4 via `python scripts/export_rep_cps_convergence_table.py`.
- **Figure 1:** `python scripts/plot_rep_cps_summary.py` (output `docs/figures/p2_rep_cps_tasks.png`; tasks_completed by policy from summary.json). Required for peer-review; no optional figures.

```bash
# Publishable: default 20 seeds. Quick/CI: --seeds 2 or --seeds 5.
PYTHONPATH=impl/src python scripts/rep_cps_eval.py [--scenario toy_lab_v0] [--out datasets/runs/rep_cps_eval]
# Delay sweep + second scenario (publishable default 20 seeds):
PYTHONPATH=impl/src python scripts/rep_cps_eval.py --delay-sweep 0,0.05,0.1 --scenarios toy_lab_v0,lab_profile_v0
python scripts/export_rep_cps_convergence_table.py [--summary datasets/runs/rep_cps_eval/summary.json]
PYTHONPATH=impl/src python scripts/plot_rep_cps_summary.py
```

## P3 — Replay

- **Script:** `scripts/replay_eval.py`
- **Output:** `datasets/runs/replay_eval/summary.json` (or `--out` path). **Use a file path for `--out`** (e.g. `datasets/runs/replay_eval/summary.json`), not a directory; the script writes the summary JSON to that file. Includes `per_trace[]` with `root_cause_category` and **witness_slice** per divergence; top-level **witness_slices** (aggregate of all divergence witness slices); `overhead_stats`; with `--overhead-curve`: `overhead_curve[]` (event_count, p95_replay_ms).
- **L1:** L1 stub (L0 + twin config validation) and L1 twin (--l1-twin: deterministic re-run of control-plane state machine; l1_twin_ok, l1_twin_final_hash_match in summary). L2 aspirational with design subsection in REPLAY_LEVELS. Full corpus table: `python scripts/export_replay_corpus_table.py`. See `bench/replay/README.md` and `kernel/trace/REPLAY_LEVELS.v0.1.md`.
- **Figure:** `python scripts/plot_replay_overhead.py` (p95 replay ms vs event count from overhead_curve).

```bash
PYTHONPATH=impl/src python scripts/replay_eval.py --out datasets/runs/replay_eval/summary.json [--corpus-dir bench/replay/corpus] [--overhead-curve] [--overhead-runs 20]
```

## P5 — Scaling

- **Prerequisite:** Multi-scenario runs. Generate with `scripts/generate_multiscenario_runs.py`, then run held-out eval.
- **Output:** `datasets/runs/scaling_eval/heldout_results.json` (held_out_results, overall_baseline_mae, overall_per_scenario_baseline_mae, overall_feat_baseline_mae, overall_regression_mae, overall_collapse_rate, 95% CI for MAE, scaling_fit).
- **Metrics:** held-out MAE per scenario (global mean, per-scenario mean, num_tasks/features, regression, optional stump); collapse rate; exploratory scaling exponent. Use `scripts/export_scaling_tables.py` to print markdown tables for the draft. **Figure 1:** `python scripts/plot_scaling_mae.py` (output `docs/figures/p5_scaling_mae.png`; MAE by held-out scenario). **Publishable (state-of-the-art):** 20 seeds and `--fault-mix` so regression is typically fit and excellence_metrics (trigger_met, beat_per_scenario_baseline, difference_mean, paired_t_p_value) are populated; use `run_paper_experiments.py --paper P5`. **Sensitivity (N=10, 20, 30):** Run `sensitivity_seed_sweep.py --eval scaling --ns 10,20,30`; output `datasets/runs/sensitivity_sweep/scaling_sensitivity.json`. Optional stump baseline in heldout_results (overall_stump_mae).

```bash
PYTHONPATH=impl/src python scripts/generate_multiscenario_runs.py [--out datasets/runs/multiscenario_runs] [--fault-mix]
PYTHONPATH=impl/src python scripts/scaling_heldout_eval.py [--runs-dir datasets/runs/multiscenario_runs] [--out datasets/runs/scaling_eval]
python scripts/export_scaling_tables.py [--results datasets/runs/scaling_eval/heldout_results.json]
python scripts/plot_scaling_mae.py [--results datasets/runs/scaling_eval/heldout_results.json]
```

## P6 — LLM Planning

- **Script:** `scripts/llm_redteam_eval.py`
- **Output:** `datasets/runs/llm_eval/red_team_results.json`; `confusable_deputy_results.json` (adversarial args inducing privilege); `e2e_denial_trace.json` (blocked + safe recovery); with `--run-adapter`: `adapter_latency.json` (runs, tail_latency_p95_mean_ms, scenarios, seeds; optional latency_acceptable if `--latency-threshold-ms` set).
- **Metrics:** red-team pass/fail (8 cases); confusable deputy (4 cases); jailbreak-style cases (prompt-injection style args; results in red_team_results.json under `jailbreak_style`); E2E denial trace; optional tail latency from adapter runs (obtained with `--run-adapter`). Optional real-LLM: `--real-llm` when `.env` has OPENAI_API_KEY or ANTHROPIC_API_KEY; results merged into red_team_results.json. OWASP LLM Top 10 coverage: `docs/P6_OWASP_MAPPING.md`.
- **Options:** `--out DIR`; `--run-adapter`; `--adapter-scenarios toy_lab_v0,lab_profile_v0`; `--adapter-seeds 7,14,21,28,35` (publishable: multiple seeds for latency variance); `--latency-threshold-ms N`; `--real-llm` (optional; requires .env API keys; run manually for Table 1b). **Publishable:** `run_paper_experiments.py --paper P6` uses two scenarios and five adapter seeds; verify success_criteria_met.trigger_met in red_team_results.json.
- **Figure 1:** `python scripts/plot_llm_adapter_latency.py` (output `docs/figures/p6_adapter_latency.png`; requires adapter_latency.json from `--run-adapter`).
- **Integration test:** `tests/test_llm_p6.py` runs eval with `--run-adapter --adapter-scenarios toy_lab_v0 --adapter-seeds 7` and asserts both artifacts.

```bash
PYTHONPATH=impl/src python scripts/llm_redteam_eval.py [--out datasets/runs/llm_eval]
PYTHONPATH=impl/src python scripts/llm_redteam_eval.py --run-adapter --adapter-scenarios toy_lab_v0 --adapter-seeds 7
python scripts/plot_llm_adapter_latency.py [--latency datasets/runs/llm_eval/adapter_latency.json]
PYTHONPATH=impl/src python scripts/llm_redteam_eval.py --run-adapter --latency-threshold-ms 5000   # SLA check
```

Exit code 1 if any red-team case fails (expected_block not satisfied).

## P7 — Assurance (mapping + review)

- **Script:** `scripts/run_assurance_eval.py [--out DIR]`. Default output: `datasets/runs/assurance_eval/results.json`. Runs check_assurance_mapping and review on two scenarios (toy_lab_v0, lab_profile_v0) to exercise kernel PONR (lab has disposition_commit).
- **Output:** mapping_check (ok, ponr_coverage_ok), review (primary = toy_lab_v0), reviews (per scenario: evidence_bundle_ok, trace_ok, ponr_events, controls_covered, ponr_coverage, control_coverage_ratio, exit_ok).
- **Check:** `scripts/check_assurance_mapping.py` (--inst, --profile-dir); schema + mapping completeness + PONR coverage.
- **Auditor walk-through:** `scripts/audit_bundle.py [--run-dir DIR] [--inst path] [--profile-dir path] [--scenario-id toy_lab_v0]` prints pass/fail for mapping completeness and PONR coverage (and optional run review); outputs JSON + human-readable. **One-command audit over release:** `scripts/audit_bundle.py --release datasets/releases/portfolio_v0.1` runs mapping + PONR; if the release dir contains evidence_bundle.json, review runs there too.
- **Part 11:** See `docs/PART11_AUDIT_TRAIL_ALIGNMENT.md` for evidence-bundle/trace mapping to Part 11-style audit trail (each requirement mapped to artifact path and field; machine-checkable). Non-goals: no certification claim; translation layer only. **Three profiles:** lab v0.1, warehouse v0.1, medical v0.1; results include per_profile (P7 DRAFT, kernel/assurance_pack/README.md, profiles/). Standards mapping table: `docs/P7_STANDARDS_MAPPING.md`. Kill criterion K7: no "template theater"; every mapping claim checkable by script or schema.
- **Review:** `scripts/review_assurance_run.py <run_dir> [--scenario-id toy_lab_v0]`; PONR coverage requires --scenario-id from the known list (SCENARIO_PONR_TASK_NAMES); no heuristic when scenario unknown. Scripted review is partial.
- **Export:** `scripts/export_assurance_tables.py [--results path]` prints Table 1 and Table 2 (per-scenario) for draft. GSN-lite graph: `python scripts/export_assurance_gsn.py` (Mermaid from assurance_pack_instantiation.json).
- **Integration test:** tests/test_assurance_p7.py runs run_assurance_eval --out <temp>, asserts results and export script; TestAuditBundle runs audit_bundle (mapping + PONR; optional run-dir review).

```bash
PYTHONPATH=impl/src python scripts/run_assurance_eval.py [--out datasets/runs/assurance_eval]
PYTHONPATH=impl/src python scripts/audit_bundle.py [--run-dir path/to/run] [--release datasets/releases/portfolio_v0.1] [--json-only]
PYTHONPATH=impl/src python scripts/export_assurance_tables.py
python scripts/export_assurance_gsn.py
```

## P8 — Meta-Coordination

- **Scenario:** `regime_stress_v0` with configurable `drop_completion_prob`.
- **Script:** `scripts/meta_eval.py`
- **Output:** `--out DIR` (default `datasets/runs/meta_eval`); writes `comparison.json` (fixed, meta_controller, optional naive_switch_baseline when `--run-naive`, meta_reduces_collapse, no_safety_regression, collapse_definition, per_seed, run_manifest, success_criteria_met.trigger_met, excellence_metrics).
- **Run manifests:** comparison.json includes run_manifest (seeds, scenario_id, fault_threshold, script); collapse_sweep.json (from meta_collapse_sweep.py) includes run_manifest (seeds, drop_probs, scenario_id, script).
- **Args:** `--out`, `--seeds`, `--collapse-threshold` (default 2), `--drop-prob` (default 0.15), `--fault-threshold` (default 1; 0 = naive: switch on any fault), `--run-naive` (also run meta with fault_threshold=0 as naive baseline), `--hysteresis N` (thrash control; require N consecutive fault observations before switch; default 1), `--non-vacuous` (run or read collapse_sweep, use smallest drop_prob where collapse_count > 0; exit with message if none found), `--collapse-sweep-path` (path to collapse_sweep.json when using --non-vacuous), `--fallback-adapter blackboard|centralized|retry_heavy` (when set, meta run uses fallback adapter when switch is decided; two coordination paths). `--stress-preset very_high` (higher drop_prob) or scenario `regime_stress_v1.yaml` for second stress scenario.
- **Collapse:** `tasks_completed < threshold` or `recovery_ok` false (from report.faults); per-seed results include `recovery_ok` when present. Integration test: `tests/test_meta_p8.py` runs meta_eval with `--out <temp>`, `--run-naive`, `--fault-threshold 0` and asserts comparison.json (no_safety_regression, meta_reduces_collapse, regime_switch_count_total >= 1), then runs `export_meta_tables.py`. Unit tests: `TestMetaController` cover `decide_switch` and `regime_switch_event`. A stress test runs with `--collapse-threshold 4` to exercise collapse metrics when tasks_completed < 4.
- **Export:** `scripts/export_meta_tables.py --comparison datasets/runs/meta_eval/comparison.json [--table2]` prints markdown Table 1 (fixed vs meta vs naive) and Table 2 (per-seed). **Figure 1:** Run `meta_collapse_sweep.py` first to produce collapse_sweep.json, then `python scripts/plot_meta_collapse.py --sweep datasets/runs/meta_eval/collapse_sweep.json` (output `docs/figures/p8_meta_collapse.png`). Optional stress: run with `--drop-prob 0.25` or `0.3` or `--collapse-threshold 4` to observe collapse; run `meta_collapse_sweep.py` with `--drop-probs 0.15,0.2,0.25,0.3` (and `--seeds 1,...,10`) to get collapse_sweep.json. Thrash control: `--hysteresis N`; naive-switch baseline uses fault_threshold=0.

**Publishable (state-of-the-art / non-vacuous):** `run_paper_experiments.py --paper P8` runs collapse_sweep (20 seeds) then meta_eval --non-vacuous --fallback-adapter retry_heavy so Table 1 uses a drop_prob where collapse_count > 0 and two real regimes are compared. Verify comparison.json has success_criteria_met.trigger_met and no_safety_regression true. Manual order: (1) `meta_collapse_sweep.py` (20 seeds, --drop-probs 0.15,0.2,0.25,0.3), (2) `meta_eval.py --run-naive --fault-threshold 0 --non-vacuous --fallback-adapter retry_heavy`, (3) `export_meta_tables.py`, (4) `plot_meta_collapse.py`. If no drop_prob in the sweep has collapse, present Table 1 as methodology and auditability only. CI can omit --non-vacuous for speed.

```bash
# Publishable (non-vacuous): collapse sweep then meta_eval --non-vacuous
PYTHONPATH=impl/src python scripts/meta_collapse_sweep.py [--out datasets/runs/meta_eval] [--drop-probs 0.15,0.2,0.25,0.3] [--seeds 1,2,...,20]
PYTHONPATH=impl/src python scripts/meta_eval.py --run-naive --fault-threshold 0 --non-vacuous [--out datasets/runs/meta_eval] [--seeds 1,2,...,20]
python scripts/export_meta_tables.py --comparison datasets/runs/meta_eval/comparison.json [--table2]
python scripts/plot_meta_collapse.py --sweep datasets/runs/meta_eval/collapse_sweep.json
```

## P0 — E1 conformance, E3 variance, E2 redaction

- **E1:** Each run (thin-slice or adapter) may write `conformance.json` under the run dir (tier, pass, reasons). CLI: `labtrust_portfolio check-conformance <run_dir>` also writes conformance.json. E1 result location: `<run_dir>/conformance.json`.

## P0 — E3 variance and E2 redaction

- **E3 script:** `scripts/produce_p0_e3_release.py`; E3 multi-scenario: `scripts/replay_link_e3.py --scenarios toy_lab_v0,lab_profile_v0 --runs N`.
- **E3 output:** `datasets/runs/e3_summary.json`, `datasets/runs/p0_e3_variance.json`; with multi-scenario, summary includes `per_scenario[]` and run dirs under `datasets/runs/e3/<scenario_id>/seed_<n>`. With release: `datasets/releases/p0_e3_release`. Evidence bundle schema requires `verification_mode` (public | evaluator | regulator). See `kernel/mads/VERIFICATION_MODES.v0.1.md`.
- **E2 script:** `scripts/e2_redaction_demo.py` — runs thin-slice once, redacts trace, writes `trace_redacted.json` and `evidence_bundle_redacted.json` (verification_mode, redaction_manifest) to output dir. The redacted trace is for audit only (payloads replaced by refs); it is not replayed, and the bundle has replay_ok false. CI runs this; redacted artifacts live at `datasets/runs/e2_redaction_demo/`.
- **P0 tables/figures:** `export_e3_table.py` (full table), `export_e3_table.py --compact` (per-scenario variance + CI), `export_e2_admissibility_matrix.py` (E2 admissibility matrix), `plot_e3_latency.py` (E3 p95 latency by scenario). Conformance summary: `build_p0_conformance_summary.py` → `datasets/releases/portfolio_v0.1/p0_conformance_summary.json` (see `docs/P0_CONFORMANCE_SUMMARY_SPEC.md`).

```bash
PYTHONPATH=impl/src python scripts/produce_p0_e3_release.py --runs 10
PYTHONPATH=impl/src python scripts/e2_redaction_demo.py --out datasets/runs/e2_redaction_demo
python scripts/export_e3_table.py
python scripts/export_e3_table.py --compact
python scripts/export_e2_admissibility_matrix.py
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

The CI workflow runs the test job (including P1–P8 integration tests and meta-controller unit tests) and the conditional-evals job: P0 E3 (`produce_p0_e3_release.py --runs 5 --scenarios toy_lab_v0,lab_profile_v0 --no-release`), P0 E2 (`e2_redaction_demo.py`), replay_eval (corpus: all `*_trace.json` in bench/replay/corpus), maestro_fault_sweep (--seeds 5), maestro_baselines, contracts_eval, run_assurance_eval, rep_cps_eval (--delay-sweep 0,0.05,0.1), generate_multiscenario_runs, scaling_heldout_eval, llm_redteam_eval, meta_eval --run-naive --fault-threshold 0, meta_collapse_sweep (--drop-probs 0.15,0.2 --seeds 3). Results are written under `datasets/runs/` and `bench/maestro/` as above.
