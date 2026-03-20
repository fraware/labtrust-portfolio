## Reproducibility: result-to-artifact mapping

Every result in the paper maps to one exact artifact. Table hash is SHA256 of the artifact file.

| Table | Artifact | model_id | timestamp | seed | prompt_template_hash | evaluator_version | policy_version | artifact_hash |
|-------|----------|----------|-----------|------|----------------------|-------------------|----------------|---------------|
| Table 1 / 1b | red_team_results.json | - | 2026-03-18T14:29:32+00:00 | - | - | llm_redteam_eval.v1 | typed_plan.0.1 | 9009d1589affc06f... |
| Table 1 | confusable_deputy_results.json | - | 2026-03-18T14:29:32+00:00 | - | - | llm_redteam_eval.v1 | typed_plan.0.1 | 28ae63fe2aacb2d2... |
| Table 2 | adapter_latency.json | - | - | 1,2,3,4,5... | - | - | - | 62ddc331a32cbc21... |
| Case study | e2e_denial_trace.json | - | - | - | - | - | - | f0a97b99f0b9513e... |
| Table (tool-level) | baseline_comparison.json | - | - | 1,2,3,4,5... | - | - | - | 4d178dfe4357aa2f... |
| Table (argument-level) | baseline_comparison_args.json | - | - | 1,2,3,4,5... | - | - | - | 8efa0c888e8fd1e9... |
| Table 2 | denial_trace_stats.json | - | - | 1,2,3,4,5... | - | - | - | abe67d52e1a23872... |
