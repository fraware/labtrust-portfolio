# Pre-submission checklist

Use this checklist for each paper immediately before submission (after Phase 3 is done). See [STATE_OF_THE_ART_CRITERIA.md](STATE_OF_THE_ART_CRITERIA.md#3-submission-readiness-phase-3--hostile-reviewer-checklist) for the Phase 3 items; [PAPER_GENERATION_WORKFLOW.md](PAPER_GENERATION_WORKFLOW.md) for regeneration and "Before actual submission."

## 1. Tag a release (optional but recommended)

To provide a citable artifact for reviewers and reproducibility:

1. **Ensure the repo state is clean:** All eval outputs and generated tables/figures you want frozen are committed (or note the exact commit in the supplement).
2. **Choose what to include in the tag:** At minimum: kernel schemas, scripts under `scripts/`, and a frozen dataset slice (e.g. `datasets/releases/` or the run dirs used for the paper's tables). For a single paper, e.g. P0: `kernel/`, `scripts/`, `impl/`, `datasets/releases/p0_e3_release/`, and `profiles/` if needed.
3. **Create an annotated tag:**  
   `git tag -a v0.1-p0-draft -m "P0 draft-complete; kernel + p0_e3_release; repro: see DRAFT.md"`  
   Use a naming scheme that identifies the paper and draft (e.g. `v0.1-p4-draft`, `v0.1-portfolio-draft`).
4. **Document the tag in the paper:** In the Reproducibility or Artifact section, state: "Artifact: clone repo, check out tag `v0.1-pX-draft`; repro commands at top of DRAFT.md."
5. **Push the tag:** `git push origin <tagname>` (when ready).

## 2. Final pass (mandatory)

Run through these for the paper you are submitting:

| Item | Check |
|------|--------|
| **Repro block** | At the top of DRAFT.md, every Table 1, Table 2, … and Figure 0, Figure 1 has an exact command (script name and args). Nothing is "optional" or "run X manually" without a script. Minimal run (under 20 min) is documented. |
| **Claim–evidence** | Every claim in `papers/Px_*/claims.yaml` has `artifact_paths` and at least one `table_id` or `figure_id`. No unsupported claims. |
| **Venue format** | Page limit, reference style (e.g. IEEE, ACM), author guidelines, and anonymization (if required) are satisfied. Shorten or adapt text/figures as needed. |
| **Run manifest** | For every table/figure that reports means or CIs, the draft or summary JSON states seeds, scenario, and fault settings. See [REPORTING_STANDARD.md](REPORTING_STANDARD.md). |

## 3. Publishable seeds

For any table or figure that will appear in the submitted PDF:

- Evals were run with 20 seeds (or the script's publishable default).
- Export/plot scripts were re-run and DRAFT.md numbers match the generated output.
- Run manifest is stated in the draft or in the summary JSON referenced by the draft.
- **Key results (P5, P6, P8):** DRAFTs include a Key results subsection; verify numbers match [RUN_RESULTS_SUMMARY.md](../datasets/runs/RUN_RESULTS_SUMMARY.md) or re-run `python scripts/export_key_results_p5_p6_p8.py` after the publishable pipeline.

**Core papers (P1, P2, P3, P4, P7):**

- **P1:** Verify eval.json has all_detection_ok true (or success_criteria_met equivalent) and run_manifest for the run used for Table 1 and Table 2; state in draft if needed.
- **P2 trigger:** In the evaluated scenario, sensitivity sharing does not materially change tasks_completed; the paper is framed as a profile-and-harness contribution. State in the draft that the trigger is not yet met and that the contribution is the safety-gated profile and MAESTRO-compatible harness. Verify summary.json has profile_ablation, resilience_envelope, latency_cost, safety_gate_denial (denial_trace_recorded, safety_gate_campaign), and excellence_metrics (bias_reduction_pct, adapter_parity). Tables/figures: export_rep_cps_tables.py (Tables 1–7), plot_rep_cps_latency.py (Figure 2). See [CONDITIONAL_TRIGGERS.md](CONDITIONAL_TRIGGERS.md).
- **P3:** Verify `replay_eval/summary.json` has `schema_version: p3_replay_eval_v0.2`, `fidelity_pass`, `success_criteria_met.corpus_expected_outcomes_met`, `run_manifest` (thin_slice_seeds, overhead_runs, bootstrap_reps), and that tables/figures were regenerated from that run; run `python scripts/verify_p3_replay_summary.py --strict-curve` if Figure 1 depends on `overhead_curve`.
- **P4:** Verify multi_sweep.json run_manifest (seeds, scenarios) for the run used for Table 1; use 20 seeds and two scenarios for publishable tables.
- **P7:** Verify results.json mapping_check_ok and ponr_coverage_ok for the run used for tables; draft must state no certification claim and that review is scripted and partial.
- **P5 regression:** If Table 2 regression row is N/A, draft must state so and avoid claiming regression beats baseline.
- **P5 trigger:** Verify heldout_results.json has beat_per_scenario_baseline and trigger_met true for the run used for tables; state in the draft that the conditional trigger is met (or that the paper is negative/dataset analysis). See [CONDITIONAL_TRIGGERS.md](CONDITIONAL_TRIGGERS.md).
- **P6 evidence:** If submitting without real-LLM, abstract or limitations must state "results from synthetic plans only"; if submitting with real-LLM, Table 1b must appear (pass_rate_pct, 95% Wilson CI, n_runs_per_case) and run_manifest must record model_id and n_runs_per_case. Baseline table: 3-way (gated/weak/ungated) from export_p6_baseline_table.py.
- **P6 trigger:** Verify red_team_results.json has trigger_met true for the run used for tables; state in the draft that the trigger is met (or that the paper is conditional/optional). See [CONDITIONAL_TRIGGERS.md](CONDITIONAL_TRIGGERS.md).
- **P8 non-vacuous:** Tables must be from a run with `meta_eval --non-vacuous` (so fixed-regime collapse appears in the sweep and `run_manifest.stress_selection_policy` is populated), or the draft must state methodology/auditability-only scope and must not imply strict collapse reduction.
- **P8 semantics:** `meta_reduces_collapse` is an alias for **non-inferiority** on counts (`meta_non_worse_collapse`: meta collapse_count <= fixed). **Strict** improvement is `meta_strictly_reduces_collapse`; paired binary inference is in `collapse_paired_analysis` and `excellence_metrics` (McNemar, Wilson). Regenerate v1 tables from `datasets/runs/meta_eval/scenario_regime_stress_v1/comparison.json` when citing dual-scenario evidence.
- **P8 trigger:** Verify `comparison.json` has `trigger_met` and `no_safety_regression` true; run `python scripts/verify_p8_meta_artifacts.py --comparison <path> [--strict-publishable]` for release gates. See [CONDITIONAL_TRIGGERS.md](CONDITIONAL_TRIGGERS.md).

### Conditional papers (P2, P5, P6, P8)

Before submission, for each conditional paper ensure the following and state in the draft accordingly. Canonical trigger wording: [CONDITIONAL_TRIGGERS.md](CONDITIONAL_TRIGGERS.md).

| Paper | Checks |
|-------|--------|
| **P2** | Trigger not met in evaluated scenario. State in draft that the contribution is the safety-gated profile and harness; summary has profile_ablation, resilience_envelope, latency_cost, safety_gate_denial (denial_trace_recorded, safety_gate_campaign), bias_reduction_pct, adapter_parity. Tables: export_rep_cps_tables.py; Figure 2: plot_rep_cps_latency.py. See [CONDITIONAL_TRIGGERS.md](CONDITIONAL_TRIGGERS.md). |
| **P5** | Trigger: `heldout_results.json` has `beat_per_scenario_baseline` and `trigger_met` true for the run used for tables. Regression row: if N/A, state in draft and do not claim regression beats baseline. |
| **P6** | Trigger: `red_team_results.json` has `trigger_met` true. Evidence: if synthetic-only, state in abstract/limitations; if real-LLM, Table 1b (pass_rate, Wilson CI) in draft, run_manifest model_id and n_runs_per_case; baseline 3-way table. |
| **P8** | Non-vacuous: Table 1 from `meta_eval --non-vacuous` with documented `stress_selection_policy`, or label methodology/auditability only. Dual-scenario publishable: `run_paper_experiments.py --paper P8` (v0 + v1). Trigger: `trigger_met` and `no_safety_regression`; verify with `verify_p8_meta_artifacts.py`. Do not headline “reduces collapse” when evidence is tie-only without stating non-inferiority. |

Commands per paper: [PAPER_GENERATION_WORKFLOW.md — Quick reference](PAPER_GENERATION_WORKFLOW.md#quick-reference-commands-per-paper). Regenerate all artifacts for that paper with `python scripts/generate_paper_artifacts.py --paper Px`, then paste from `papers/Px_*/generated_tables.md` into DRAFT.md if needed.

## 4. After submission

- Update [PORTFOLIO_BOARD.md](../PORTFOLIO_BOARD.md): set the paper's Next action to "Submitted to &lt;venue&gt;" or similar.
- If you created a tag, keep it pushed so reviewers can use it.
