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
Prompt injection is structurally different from SQL injection; treat LLMs as potentially “confusable deputies” and design for containment and residual risk, not perfect mitigation. citeturn0search1turn0search2

## 3) Claims
- **C1:** Typed plan outputs + validators produce a testable interface that blocks unsafe tool use and unsafe PONR proposals.
- **C2:** Deterministic toolcalling capture + bounded retries makes behavior replayable and auditable.
- **C3:** A CPS-specific red-team suite (prompt injection, malformed toolcalls, excessive agency) is required and sufficient to exercise key failure modes.
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
- Metrics: red-team pass (8 cases), confusable deputy (4), jailbreak-style (2); real-LLM: 5 runs per case, pass_rate_pct, 95% Wilson CI, latency mean ± stdev; adapter tail_latency_p95 mean/stdev/CI; denial-trace stats (runs_with_denial, tasks_completed_mean per scenario).
- Baselines: 3-way (gated = full validator; weak = allow-list only; ungated = no validation); tool-level (execute_system) and argument-level (--baseline-plan args_unsafe: path traversal in allow-listed tool); same scenarios/seeds.
- Real-LLM: `--real-llm --real-llm-model gpt-4o-mini --real-llm-runs 5`; prompt hardening for path-traversal case (rt_allowed_tool_disallowed_args).
- Stressors: prompt injection via tool-fed content; partial tool results; path traversal in args; time pressure.

## 6) Artifact checklist
- `kernel/llm_runtime/TYPED_PLAN.v0.1.schema.json`
- validator library + policy hooks (allow_list, safe_args)
- deterministic toolcalling wrapper (capture_tool_call)
- red-team suite (8 cases) + confusable deputy (4) + jailbreak-style (2); expected_block per case
- MAESTRO adapter (LLMPlanningAdapter; validation_mode gated/weak/ungated) + 3-way baseline results (tool-level: baseline_comparison.json; argument-level: baseline_comparison_args.json)
- Real-LLM: red_team_results.json real_llm (n_runs_per_case, pass_rate_pct, Wilson CI, latency stats); export_llm_redteam_table.py (Table 1b)
- Appendix A: export_p6_artifact_hashes.py (SHA256 hashes)

## 7) Kill criteria
- **K1:** validators fail to reliably block unsafe actions in red-team tests.
- **K2:** deterministic capture is too brittle across providers to support replay.
- **K3:** tail latency becomes operationally infeasible.

## 8) Target venues
- robotics systems + security workshops; arXiv first (cs.RO, cs.CR)

## 9) Integration contract
- Must treat LLM planning as a module inside MADS envelope.
- Must not claim elimination of prompt injection; claim containment + measurable robustness.

