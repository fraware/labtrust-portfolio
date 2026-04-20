# Paper generation workflow

This document spells out the repeatable, per-paper process to produce submission-ready drafts. It implements the plan in "Generate each paper": ensure eval artifacts exist, run export/plot scripts, fill or update DRAFT.md, and run the Phase 3 checklist.

**Current state:** All nine papers (P0–P8) are at Draft; Phase 3 passed (see each paper’s `PHASE3_PASSED.md`). Next: submission prep per [PRE_SUBMISSION_CHECKLIST.md](PRE_SUBMISSION_CHECKLIST.md). Eval summary JSONs may include optional `excellence_metrics`; run `python scripts/export_excellence_summary.py` to print a summary (see [STANDARDS_OF_EXCELLENCE.md](STANDARDS_OF_EXCELLENCE.md)).

**Phase 3 checklist:** [STATE_OF_THE_ART_CRITERIA.md](STATE_OF_THE_ART_CRITERIA.md#3-submission-readiness-phase-3--hostile-reviewer-checklist).

## Prerequisites (once per repo)

- **Environment:** `PYTHONPATH=impl/src`, `LABTRUST_KERNEL_DIR=kernel`. See [README.md](../README.md) for PowerShell/Bash.
- **Kernel:** `python scripts/validate_kernel.py` passes.
- **Reference scenario:** [bench/maestro/scenarios/lab_profile_v0.yaml](../bench/maestro/scenarios/lab_profile_v0.yaml) is the portfolio anchor.

## Dependency order

Generate **core papers (P0, P1, P3, P4, P7)** first, then **conditional papers (P2, P5, P6, P8)**.

## Per-paper steps (template)

For each paper Px:

1. **Ensure eval data exists** — Run the eval script(s) that produce inputs for this paper's tables and figures (typically 20 seeds for publishable; see [REPORTING_STANDARD.md](REPORTING_STANDARD.md)).
2. **Run export scripts (tables)** — Run each export script; capture stdout (markdown) and paste into DRAFT.md or use `scripts/generate_paper_artifacts.py --paper Px` to write to `papers/Px_*/generated_tables.md`.
3. **Run Figure 0 and Figure 1 scripts** — Run the `export_pX_*` diagram script (output `.mmd` in `docs/figures/`) and the `plot_*.py` script (output `.png`). For camera-ready, render Mermaid to PNG (e.g. `npx -p @mermaid-js/mermaid-cli mmdc -i file.mmd -o file.png`).
4. **Update DRAFT.md** — Replace placeholder table rows with actual output; ensure Figure 0/1 paths are correct; confirm Reproducibility block lists every script; for conditional papers, confirm Limitations state trigger and scope ([CONDITIONAL_TRIGGERS.md](CONDITIONAL_TRIGGERS.md)).
5. **Run Phase 3 checklist** — Verify all six items in [STATE_OF_THE_ART_CRITERIA.md](STATE_OF_THE_ART_CRITERIA.md) section 3.

## Paper-specific notes

| Paper | Eval data location | Tables from | Figure 0 script | Figure 1 script |
|-------|--------------------|------------|-----------------|-----------------|
| P0 | `p0_conformance_corpus/`, e2_redaction_demo, e3_summary.json, p0_e4_summary.json | `generate_paper_artifacts.py --paper P0` (runs E1–E4 exports) | export_p0_assurance_pipeline | export_p0_tier_lattice + plot_e3_latency |
| P1 | contracts_eval/eval.json, scale_test.json, scale_sweep.json (optional), transport_parity.json | export_contracts_corpus_table (Table 1, ablation-by-class, Table 3 / detection_metrics_by_class) | export_p1_contract_flow | plot_contracts_scale |
| P2 | rep_cps_eval/summary.json | export_rep_cps_tables.py (Tables 1–7 from summary.json) | export_p2_rep_profile_diagram | plot_rep_cps_summary, plot_rep_cps_gate_threshold, plot_rep_cps_dynamics, plot_rep_cps_latency |
| P3 | replay_eval/summary.json | export_replay_corpus_table.py --out-md papers/P3_Replay/generated_tables.md (Table 1 + Table 1b; overhead + baselines from same summary) | export_p3_paper_figures.py (or export_p3_replay_levels_diagram + export_p3_replay_levels_figure) | export_p3_paper_figures.py (overhead + localization + supplementary visuals); verify_p3_replay_summary.py |
| P4 | maestro_fault_sweep, baseline_summary, antigaming | export_maestro_tables | export_p4_maestro_flow | plot_maestro_recovery |
| P5 | scaling_eval/heldout_results.json | export_scaling_tables | export_p5_baseline_hierarchy | plot_scaling_mae |
| P6 | llm_eval/red_team_results (real_llm/real_llm_models, run_manifest, attribution, cross_model_summary), adapter_latency (optional latency_decomposition), baseline_comparison, baseline_comparison_args, baseline_benign, denial_trace_stats | export_llm_redteam_table (Table 1, Table 1b), export_p6_baseline_table (3-way; --baseline-file for args/benign), export_p6_artifact_hashes, export_p6_reproducibility_table, export_p6_layer_attribution, export_p6_failure_analysis, export_p6_cross_model_heatmap, export_p6_latency_decomposition | export_p6_firewall_flow | plot_llm_adapter_latency |
| P7 | assurance_eval/results.json | export_assurance_tables | export_p7_mapping_flow | export_assurance_gsn (Figure 1) |
| P8 | `meta_eval/comparison.json` (v0), optional `meta_eval/scenario_regime_stress_v1/comparison.json`; `collapse_sweep.json` per scenario dir | `export_meta_tables` (both comparisons after publishable run); `verify_p8_meta_artifacts` | `export_p8_meta_diagram` | `plot_meta_collapse` (t- and Wilson uncertainty) |

P2 tables are generated by `scripts/export_rep_cps_tables.py` from rep_cps_eval/summary.json. P3: Table 1 and Table 1b from `export_replay_corpus_table.py` (`--out-md papers/P3_Replay/generated_tables.md`); Tables 2–3 from `overhead_stats` and `baseline_overhead` in `replay_eval/summary.json` (documented in `papers/P3_Replay/generated_tables.md`); run `verify_p3_replay_summary.py` after regenerating the summary.

## Quick reference: commands per paper

All commands from repo root with `PYTHONPATH=impl/src` and `LABTRUST_KERNEL_DIR=kernel` set.

| Paper | Eval (run first) | Export tables | Figure 0 | Figure 1 |
|-------|------------------|---------------|----------|----------|
| P0 | `python scripts/build_p0_conformance_corpus.py --out datasets/runs/p0_conformance_corpus`; `python scripts/e2_redaction_demo.py --out datasets/runs/e2_redaction_demo`; `python scripts/produce_p0_e3_release.py --runs 20 --scenarios toy_lab_v0,lab_profile_v0 --standalone-verifier`; `python scripts/run_p0_e4_multi_adapter.py --seeds 20 --scenarios toy_lab_v0,lab_profile_v0 --out datasets/runs/p0_e4_summary.json` | `python scripts/generate_paper_artifacts.py --paper P0` | `python scripts/export_p0_assurance_pipeline.py` | `python scripts/export_p0_tier_lattice.py`; `python scripts/plot_e3_latency.py` |
| P1 | `python scripts/contracts_eval.py` [optional: `--baseline`, `--scale-test`, `--scale-sweep 1000,10000,100000`]; `python scripts/contracts_transport_parity.py` [optional: `--sequences ...`] | `python scripts/export_contracts_corpus_table.py` | `python scripts/export_p1_contract_flow.py` | `python scripts/plot_contracts_scale.py` |
| P2 | `python scripts/rep_cps_eval.py` (default 20 seeds; scenarios toy_lab_v0, lab_profile_v0, rep_cps_scheduling_v0) | `python scripts/export_rep_cps_tables.py --summary datasets/runs/rep_cps_eval/summary.json` | `python scripts/export_p2_rep_profile_diagram.py` (`--render-png|--render-svg|--render-pdf` optional) | `python scripts/plot_rep_cps_summary.py`, `python scripts/plot_rep_cps_gate_threshold.py`, `python scripts/plot_rep_cps_dynamics.py`, `python scripts/plot_rep_cps_latency.py` |
| P3 | `python scripts/replay_eval.py --out datasets/runs/replay_eval/summary.json --overhead-curve --overhead-runs 20 --thin-slice-seeds 42,43,44,45,46 --bootstrap-reps 500` | `python scripts/export_replay_corpus_table.py --out-md papers/P3_Replay/generated_tables.md`; Table 2–3 values from `summary.json` | `python scripts/export_p3_paper_figures.py` | `python scripts/export_p3_paper_figures.py`; `python scripts/verify_p3_replay_summary.py --strict-curve` |
| P4 | `python scripts/maestro_fault_sweep.py` (default 20 seeds); `python scripts/maestro_baselines.py`; `python scripts/maestro_antigaming_eval.py` | `python scripts/export_maestro_tables.py` | `python scripts/export_p4_maestro_flow.py` | `python scripts/plot_maestro_recovery.py` |
| P5 | `python scripts/generate_multiscenario_runs.py` (`--fault-mix`, `--profile all`, 12--20+ seeds); `python scripts/scaling_heldout_eval.py` (optional `--holdout-mode family` -> `scaling_eval_family/`); optional second family eval | `python scripts/export_scaling_tables.py` | `python scripts/export_p5_baseline_hierarchy.py` | `python scripts/plot_scaling_mae.py` |
| P6 | `python scripts/llm_redteam_eval.py` [optional: `--real-llm --real-llm-provider prime --real-llm-models x-ai/grok-4-fast,google/gemini-2.5-flash,openai/gpt-4.1-mini,qwen/qwen3-30b-a3b-instruct-2507 --real-llm-runs 3`, `--run-adapter`, `--run-baseline`, `--baseline-plan benign|args_unsafe`, `--latency-decomposition`] | `export_llm_redteam_table.py`; `export_p6_baseline_table.py` (3-way; --baseline-file for args/benign); `export_p6_artifact_hashes.py`, `export_p6_reproducibility_table.py`, `export_p6_layer_attribution.py`, `export_p6_failure_analysis.py`, `export_p6_cross_model_heatmap.py`, `export_p6_latency_decomposition.py` | `python scripts/export_p6_firewall_flow.py` | `python scripts/plot_llm_adapter_latency.py` |
| P7 | `python scripts/run_assurance_eval.py`; `python scripts/run_assurance_robust_eval.py` (default 20 seeds) | `python scripts/export_assurance_tables.py` (Table 3 from robust_results.json when present) | `python scripts/export_p7_mapping_flow.py`; optional `python scripts/render_p7_mermaid_figures.py` | `python scripts/export_assurance_gsn.py`; optional `render_p7_mermaid_figures.py` |
| P8 | **Publishable:** `python scripts/run_paper_experiments.py --paper P8` (v0 + v1, non-vacuous, `retry_heavy`). **Minimal:** `python scripts/meta_eval.py --run-naive --fault-threshold 0`. **Figure 1:** `python scripts/meta_collapse_sweep.py` then `plot_meta_collapse.py --sweep ...`. **Schema check:** `python scripts/verify_p8_meta_artifacts.py --comparison datasets/runs/meta_eval/comparison.json` (`--sweep`, `--strict-publishable` as needed). | `export_meta_tables.py` for `comparison.json` and for `scenario_regime_stress_v1/comparison.json` after publishable P8 | `python scripts/export_p8_meta_diagram.py` | `python scripts/plot_meta_collapse.py --sweep datasets/runs/meta_eval/collapse_sweep.json` |

## Automation

Use `python scripts/generate_paper_artifacts.py --paper Px` or `--paper all` to check eval outputs, run export and figure scripts, and write generated tables to `papers/Px_*/generated_tables.md`. See script help for options.

## Phase 3 verification

Before submission, for each paper run through the six items in [STATE_OF_THE_ART_CRITERIA.md](STATE_OF_THE_ART_CRITERIA.md) section 3 (Submission readiness):

1. Claim-evidence matrix complete (every claim in claims.yaml has artifact_paths and at least one table_id or figure_id).
2. Repro steps under 20 minutes (minimal run documented at top of DRAFT.md, executable with stated env).
3. Variance rules followed (run manifest and seed count stated; 20 seeds for publishable tables unless justified).
4. No redefinition of another paper's kernel (draft cites owning paper and kernel).
5. Overclaim check (no certification P7; no full hardware determinism P3; conditional papers state trigger/scope).
6. Repro block lists every script for every table and figure.

Optionally record completion (e.g. "Phase 3 passed" and date in paper README or board).

## Success criteria

- Every paper's DRAFT.md has no placeholder table rows; every table is filled or has a single command in the repro block that produces it.
- Every Figure 0 and Figure 1 is produced by the documented script and path.
- For each paper, Phase 3 checklist is satisfied (see [STATE_OF_THE_ART_CRITERIA.md](STATE_OF_THE_ART_CRITERIA.md) section 3).

## Before actual submission

See **[PRE_SUBMISSION_CHECKLIST.md](PRE_SUBMISSION_CHECKLIST.md)** for the full pre-submission checklist (tag a release, final pass, publishable seeds, post-submit).

1. **Tag a release (optional but recommended).** To provide a citable artifact: tag a release that includes kernel schemas, runnable scripts, and a frozen dataset slice (e.g. `datasets/releases/` or a specific run manifest). Example: `git tag -a v0.1-p0-draft -m "P0 draft-complete; kernel + p0_e3_release"`. Document the tag in the paper's Reproducibility section or supplement so reviewers can clone and check out that tag.
2. **Final pass.** Run through: (a) repro block—every table and figure has the exact command; (b) claim–evidence—every claim in claims.yaml has artifact_paths and table_id or figure_id; (c) venue-specific shortening and format (page limit, reference style, author guidelines).
3. **Publishable seeds.** For any table or figure in the submitted draft, ensure evals were run with 20 seeds (or the script's publishable default), export/plot scripts were re-run, and DRAFT.md numbers match. Run manifest (seeds, scenario, fault settings) should be stated in the draft or summary JSON.
