# SaT-CPS 2026 P6 -- Four owners (no shared ownership)

Each lane has a single owner with authority. No shared ownership.

| Owner | Lane | Authority |
|-------|------|------------|
| **A. Security-story** | Title, abstract, introduction, threat model, related-work framing, claims wording, conclusion | All narrative and security positioning |
| **B. Evaluation** | What goes in main paper vs appendix; which experiments to run; numbers and tables | Block A--D structure; Table 1 (15 red-team + 6 confusable + 4 jailbreak-style), Table 1b (real-LLM), Table 2; Figure 1 (decision path), Figure 2 (adapter latency); case study (denial trace) |
| **C. Artifact/reproducibility** | Commands, hashes, figure generation, release tag, evidence traceability | EXPERIMENTS_RUNBOOK.md; export_llm_redteam_table.py, export_p6_baseline_table.py (incl. baseline_comparison_args.json, baseline_benign.json), export_p6_firewall_flow.py, plot_llm_adapter_latency.py, export_p6_denial_trace_case_study.py, export_p6_artifact_hashes.py, export_p6_reproducibility_table.py, export_p6_final_audit_bundle.py (p6_final_audit_20260424), export_p6_layer_attribution.py, export_p6_failure_analysis.py, export_p6_cross_model_heatmap.py, export_p6_latency_decomposition.py; optional p6_concurrency_benchmark.py through p6_adaptive_suite_run.py |
| **D. ACM/compliance** | acmart, page budget, author block, CCS concepts, keywords, package compliance, PDF hygiene | LaTeX template, compilation, formatting |

Assign owners by name or role; placeholder until assigned.

See SUBMISSION_STANDARD.md for the five axes and FINAL_CHECKLIST.md for sign-off.
