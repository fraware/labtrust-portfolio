# Papers

Each paper folder contains an `AUTHORING_PACKET.md`, `README.md`, `DRAFT.md`, `claims.yaml` (claim table with evidence mapping: artifact_paths, table_ids, figure_ids; Figure 0 is the overview diagram), and optionally `PHASE3_PASSED.md` (date and checklist confirmation). **All nine papers (P0–P8) are at Draft stage**; Phase 3 (submission-readiness) passed 2025-03-11. All paper artifacts (DRAFT, claims, tables, figures) are polished for clarity, captions, and state-of-the-art alignment; see [docs/PAPER_ARTIFACT_STYLE.md](../docs/PAPER_ARTIFACT_STYLE.md) and [DRAFT_CONVERSION_CHECKLIST.md](../docs/DRAFT_CONVERSION_CHECKLIST.md) for standards. Next step: submission prep per [PRE_SUBMISSION_CHECKLIST.md](../docs/PRE_SUBMISSION_CHECKLIST.md) (tag release, final pass, venue format).

To move from Eval to Draft, a paper must satisfy the [Draft conversion checklist](../docs/DRAFT_CONVERSION_CHECKLIST.md); see [STATE_OF_THE_ART_CRITERIA.md](../docs/STATE_OF_THE_ART_CRITERIA.md#21-portfolio-wide-draft-conversion-checklist). Before submission, run the [Phase 3 checklist](../docs/STATE_OF_THE_ART_CRITERIA.md#3-submission-readiness-phase-3--hostile-reviewer-checklist). Evaluation scripts run per paper and write results under `datasets/runs/`; summary JSONs may include optional `excellence_metrics` (see [STANDARDS_OF_EXCELLENCE.md](../docs/STANDARDS_OF_EXCELLENCE.md)). Run `python scripts/export_excellence_summary.py` to print a one-line excellence summary per paper. After running all paper experiments (`run_paper_experiments.py`), see [datasets/runs/RUN_RESULTS_SUMMARY.md](../datasets/runs/RUN_RESULTS_SUMMARY.md) for a consolidated results summary. Conditional papers (P2, P5, P6, P8) document trigger proofs in [CONDITIONAL_TRIGGERS.md](../docs/CONDITIONAL_TRIGGERS.md); eval outputs include `success_criteria_met.trigger_met` where applicable. P1 trace-derivability: [P1_TRACE_DERIVABILITY.md](../docs/P1_TRACE_DERIVABILITY.md). P0 conformance summary: [P0_CONFORMANCE_SUMMARY_SPEC.md](../docs/P0_CONFORMANCE_SUMMARY_SPEC.md). P1–P8 have integration tests in `tests/` that run the eval script and assert on the produced artifact. Export and plot scripts generate tables and figures for draft inclusion; see [PAPER_GENERATION_WORKFLOW.md](../docs/PAPER_GENERATION_WORKFLOW.md) and [EVALS_RUNBOOK.md](../docs/EVALS_RUNBOOK.md).

Paper IDs:
- P0_MADS-CPS
- P1_Contracts
- P2_REP-CPS
- P3_Replay
- P4_CPS-MAESTRO
- P5_ScalingLaws
- P6_LLMPlanning
- P7_StandardsMapping
- P8_MetaCoordination
