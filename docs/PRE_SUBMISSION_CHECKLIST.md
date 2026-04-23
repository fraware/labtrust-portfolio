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

- **P1:** Verify eval.json has `success_criteria_met.all_detection_ok` true and `run_manifest` (script_version, corpus_fingerprint, corpus_sequence_count) for the run used for tables; confirm `detection_metrics_by_class`, `excellence_metrics` (per_class_ci95, split_brain_detection_advantage), and full `ablation` keys (occ_only, lease_only, lock_only, naive_lww) if the draft cites them; regenerate `transport_parity.json` (parity_ok_all, per_sequence[], parity_confidence) if the draft cites boundary parity; optional `stress_results.json` if async stress is cited; `papers/P1_Contracts/generated_tables.md` and `papers/P1_Contracts/generated_appendix_corpus.tex` match export output; Figure 0 submission asset exists at `papers/P1_Contracts/figures/contracts_flow.pdf`; claim map and lock checklist are consistent (`papers/P1_Contracts/claims.yaml`, `papers/P1_Contracts/SUBMISSION_LOCK.md`).
- **P2 trigger (scoped):** State that **toy_lab_v0 / lab_profile_v0** runs show scoped adapter parity (scheduler does not consume REP aggregate) and that **rep_cps_scheduling_v0** demonstrates **task-level** gate effect (`scheduling_dependent_eval`). Contribution remains profile + harness; real schedulers/buses are out of scope. Verify summary.json includes profile_ablation, resilience_envelope, latency_cost, safety_gate_denial, per_scenario (aggregated metrics per scenario_id), excellence_metrics (comparison statistics on non-scheduling scenarios), freshness_replay_evidence, sybil_vs_spoofing_evidence, messaging_sim, dynamic_aggregation_series, offline_comparator_baselines, and scheduling_dependent_eval (when scheduling scenario is in run_manifest.scenario_ids). Verify run_manifest includes delay_fault_prob_sweep and optionally drop_completion_prob_sweep. Tables/figures: export_rep_cps_tables.py (includes per-scenario summary, comparison statistics, messaging_sim and dynamic_aggregation_series tables), plot_rep_cps_summary.py, plot_rep_cps_gate_threshold.py, plot_rep_cps_dynamics.py, plot_rep_cps_latency.py, and export_p2_rep_profile_diagram.py (Figure 0 source + optional camera-ready renders). See [CONDITIONAL_TRIGGERS.md](CONDITIONAL_TRIGGERS.md), [papers/P2_REP-CPS/REVIEWER_REBUTTAL_MATRIX.md](../papers/P2_REP-CPS/REVIEWER_REBUTTAL_MATRIX.md).
- **P3:** Verify `replay_eval/summary.json` has `schema_version: p3_replay_eval_v0.2`, `fidelity_pass`, `success_criteria_met.corpus_expected_outcomes_met`, `corpus_space_summary`, `per_trace[]` with **`corpus_category`** (synthetic_trap, field_proxy, real_ingest, synthetic_pass), `run_manifest` (thin_slice_seeds, overhead_runs, bootstrap_reps), and that tables/figures were regenerated from that run; with `--l1-twin`, verify **`l1_twin_summary`** (multi-seed aggregate) is present; regenerate Table 1 / Table 1b via `python scripts/export_replay_corpus_table.py --out-md papers/P3_Replay/generated_tables.md`; run `python scripts/verify_p3_replay_summary.py --strict-curve` if Figure 1 depends on `overhead_curve`.
- **P4:** Verify multi_sweep.json run_manifest (seeds, scenarios) for the run used for Table 1; use 20 seeds and two scenarios for publishable tables.
- **P7:** Verify `results.json` has `mapping_check.ok` and `mapping_check.ponr_coverage_ok` for the run used for Tables 1–2; verify `robust_results.json` for Table 3 if cited; verify **`negative_results.json`** and **`papers/P7_StandardsMapping/p7_*.csv`** match Tables 4–6 and supplement claims (`p7_perturbation_reject_matrix.csv`, `p7_aggregate_lift_metrics.csv`, `p7_latency_by_mode.csv`, `p7_negative_by_scenario.csv`, `p7_boundary_case_summary.csv`, `p7_submission_manifest_redacted.json`, `p7_generation_metadata.json`); run `tests/test_assurance_negative_eval.py` to assert CSV↔JSON consistency for `by_mode`, `by_family`, and aggregate lift fields. Draft must state no certification claim, that review is scripted and partial, and that Table 6 code counts may sum to > n_invalid when multiple codes appear on one rejection. For blind review, generate P7 negative artifacts with `--submission-mode` (or `--redact-paths`). See [P7_REVIEW_CHECKLIST.md](P7_REVIEW_CHECKLIST.md), [P7_PERTURBATION_CHECKLIST.md](P7_PERTURBATION_CHECKLIST.md).
- **P7/AIES packaging:** Verify `datasets/runs/assurance_eval_aies/` is fully regenerated and internally consistent (`baseline_summary.json`, `institutional_positive_summary.json`, `negative_summary.json`, `bounded_review_packet/`, `tables/`, `figures/`, `RUN_MANIFEST.json`). Confirm institutional main-text focus: baseline row from `lab_profile_v0`, portability row from `warehouse_v0`, and traffic/medical only under `proxy_stress_only/`. Confirm bounded packet is exported with `--submission-mode` and packet manifest shows `path_redaction: submission_mode`. Run `tests/test_assurance_aies_exports.py`.
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
| **P2** | Scoped trigger: toy/lab parity vs scheduling scenario task divergence (`scheduling_dependent_eval`). Contribution is profile + harness; state limitations. Summary: profile_ablation, resilience_envelope, latency_cost, safety_gate_denial, per_scenario, excellence_metrics (comparison statistics), freshness_replay_evidence, sybil_vs_spoofing_evidence, messaging_sim, dynamic_aggregation_series, offline_comparator_baselines. Tables: export_rep_cps_tables.py (includes per-scenario summary, comparison statistics, messaging_sim and dynamic_aggregation_series blocks); figures: plot_rep_cps_summary.py, plot_rep_cps_gate_threshold.py, plot_rep_cps_dynamics.py, plot_rep_cps_latency.py, and Figure 0 from export_p2_rep_profile_diagram.py. See [CONDITIONAL_TRIGGERS.md](CONDITIONAL_TRIGGERS.md). |
| **P5** | Trigger: `heldout_results.json` has `beat_per_scenario_baseline` and `trigger_met` true for the run used for tables. Regression row: if N/A, state in draft and do not claim regression beats baseline. |
| **P6** | Trigger: `red_team_results.json` has `trigger_met` true. Evidence: if synthetic-only, state in abstract/limitations; if real-LLM, Table 1b (pass_rate, Wilson CI) in draft, run_manifest model_id and n_runs_per_case; baseline 3-way table. |
| **P8** | Non-vacuous: Table 1 from `meta_eval --non-vacuous` with documented `stress_selection_policy`, or label methodology/auditability only. Dual-scenario publishable: `run_paper_experiments.py --paper P8` (v0 + v1). Trigger: `trigger_met` and `no_safety_regression`; verify with `verify_p8_meta_artifacts.py`. Do not headline “reduces collapse” when evidence is tie-only without stating non-inferiority. |

Commands per paper: [PAPER_GENERATION_WORKFLOW.md — Quick reference](PAPER_GENERATION_WORKFLOW.md#quick-reference-commands-per-paper). Regenerate all artifacts for that paper with `python scripts/generate_paper_artifacts.py --paper Px`, then paste from `papers/Px_*/generated_tables.md` into DRAFT.md if needed.

## 4. After submission

- Update [PORTFOLIO_BOARD.md](../PORTFOLIO_BOARD.md): set the paper's Next action to "Submitted to &lt;venue&gt;" or similar.
- If you created a tag, keep it pushed so reviewers can use it.
