# Safe LLM Planning for CPS: Typed Plans, Deterministic Toolcalling, and Runtime Safety Gates

**Paper ID:** P6_LLMPlanning  
**Tag:** conditional  
**Board path:** Spec → MVP → Eval → Draft  
**Kernel ownership:** LLM runtime kernel (typed plan schema + validator interface + toolcalling capture)

## 1) Trigger condition
Proceed only if:
- an LLM is in the control plane (planning/toolcalling), OR
- a typed-plan + validator firewall is needed as a general containment pattern.

## 2) Scope anchor (security realism)
Prompt injection is structurally different from SQL injection; treat LLMs as potentially confusable deputies and design for containment and residual risk, not perfect mitigation.

## 3) Claims
- **C1:** Typed plan outputs + validators produce a testable interface that blocks unsafe tool use and unsafe PONR proposals.
- **C2:** Deterministic toolcalling capture + bounded retries makes behavior replayable and auditable.
- **C3:** A CPS-oriented suite (15 red-team, 6 confusable deputy, 4 jailbreak-style + adaptive cases) exercises key failure modes aligned with OWASP LLM Top 10 mapping.
- **C4:** Under MAESTRO faults, the pattern reduces safety violations without unacceptable tail latency.

## 4) Outline
1. Why LLM-agent demos fail CPS constraints
2. Plan schema and type system
3. Validator stack: static checks, policy checks, gate integration
4. Deterministic toolcalling capture and replay integration
5. Red-team suite aligned with OWASP LLM Top 10 categories
6. Evaluation on MAESTRO scenarios
7. Deployment guidance: least privilege, safe refusal, residual risk posture

## 5) Experiment plan
- Scenarios: 3 MAESTRO scenarios (toy_lab_v0, lab_profile_v0, warehouse_v0), 20 seeds per scenario (publishable).
- Metrics: red-team pass (15 cases), confusable deputy (6), jailbreak-style (4); adaptive suite pass; real-LLM: default 10 runs per case, full-suite mode (`--real-llm-suite full`), pass_rate_pct, 95% Wilson CI, latency mean ± stdev; adapter tail_latency_p95 mean/stdev/CI; denial-trace stats (runs_with_denial, tasks_completed_mean per scenario); run_manifest (timestamp_iso, evaluator_version, policy_version, prompt_template_hash, suite_mode); layer attribution; optional baseline benign and latency_decomposition.
- Baselines: 3-way (gated = full validator; weak = allow-list only; ungated = no validation); tool-level (execute_system) and argument-level (--baseline-plan args_unsafe: path traversal in allow-listed tool); same scenarios/seeds.
- Real-LLM (canonical): `--real-llm --real-llm-models gpt-4.1-mini,gpt-4.1 --real-llm-runs 10 --real-llm-suite full` (OpenAI). Optional: `--real-llm-provider prime` and separate `--out` for multi-provider matrices (see sat-cps2026/EXPERIMENTS_RUNBOOK.md).
- Stressors: prompt injection via tool-fed content; partial tool results; path traversal in args; time pressure.

## 6) Artifact checklist
- `kernel/llm_runtime/TYPED_PLAN.v0.1.schema.json`
- validator library + policy hooks (allow_list, safe_args, ponr_gate, privilege heuristic)
- deterministic toolcalling wrapper (capture_tool_call)
- red-team suite (15 cases) + confusable deputy (6) + jailbreak-style (4) + adaptive suite; expected_block per case
- MAESTRO adapter (LLMPlanningAdapter; validation_mode gated/weak/ungated) + baseline results (tool-level: baseline_comparison.json; argument-level: baseline_comparison_args.json; benign: baseline_benign.json)
- Real-LLM: red_team_results.json real_llm / real_llm_models (n_runs_per_case, pass_rate_pct, Wilson CI, latency stats, cross_model_summary); export_llm_redteam_table.py (Table 1b)
- Appendix / integrity: export_p6_artifact_hashes.py, export_p6_reproducibility_table.py; optional export_p6_layer_attribution.py, export_p6_failure_analysis.py, export_p6_cross_model_heatmap.py, export_p6_latency_decomposition.py
- SaT-CPS 2026 venue pack: sat-cps2026/README.md, FINAL_CHECKLIST.md, claims_satcps.yaml, main.tex

## 7) Kill criteria
- **K1:** validators fail to reliably block unsafe actions in red-team tests.
- **K2:** deterministic capture is too brittle across providers to support replay.
- **K3:** tail latency becomes operationally infeasible.

## 8) Target venues
- robotics systems + security workshops; arXiv first (cs.RO, cs.CR)

## 9) Integration contract
- Must treat LLM planning as a module inside MADS envelope.
- Must not claim elimination of prompt injection; claim containment + measurable robustness.

