# Safe LLM Planning for CPS: Typed Plans and Runtime Safety Gates

**Draft (v0.1). Paper ID: P6_LLMPlanning. Conditional paper; trigger and scope: docs/CONDITIONAL_TRIGGERS.md (P6).**

**Reproducibility.** From repo root, with `PYTHONPATH=impl/src` and `LABTRUST_KERNEL_DIR=kernel`. See [REPORTING_STANDARD.md](../docs/REPORTING_STANDARD.md) and [RESULTS_PER_PAPER.md](../docs/RESULTS_PER_PAPER.md). Run_manifest: red_team_results.json (red_team_case_count, script); adapter_latency.json (adapter_scenarios, adapter_seeds, script). Conditional trigger: success_criteria_met.trigger_met in red_team_results.json; see docs/CONDITIONAL_TRIGGERS.md (P6).

**Minimal run (under 20 min):** `python scripts/llm_redteam_eval.py` then `python scripts/llm_redteam_eval.py --run-adapter --adapter-scenarios toy_lab_v0 --adapter-seeds 3` then `python scripts/export_p6_firewall_flow.py` then `python scripts/plot_llm_adapter_latency.py`.

- **Figure 0:** `python scripts/export_p6_firewall_flow.py` (output `docs/figures/p6_firewall_flow.mmd`). Render Mermaid to PNG for camera-ready.
- **Table 1:** `python scripts/llm_redteam_eval.py` (output red_team_results.json; contains success_criteria_met.red_team_all_pass, trigger_met).
- **Table 2, Figure 1:** `python scripts/llm_redteam_eval.py --run-adapter` then `python scripts/plot_llm_adapter_latency.py` (output `docs/figures/p6_adapter_latency.png`).
- MAESTRO-integrated run and e2e_denial_trace: same eval; see e2e_denial_trace.json.

## 1. Motivation

LLM-in-the-loop and typed-plan + validator firewall are containment patterns for CPS. We position the component as a **typed plan firewall for any planner (LLM or heuristic)**: the firewall is for any planner; LLM is optional. Validators and plan schema apply regardless of planner source. This paper defines a typed plan schema, validator stack, deterministic toolcalling capture, and red-team suite; **containment only, not elimination** of prompt injection or unsafe actions.

## 2. Plan schema and validator stack

Schema: `kernel/llm_runtime/TYPED_PLAN.v0.1.schema.json` (plan_id, steps with seq, tool, args, validators).

**Figure 0 — Typed-plan firewall flow.** Plan is validated (validate_plan, policy_check_step); outcome is allow or deny. Regenerate with `python scripts/export_p6_firewall_flow.py` (output `docs/figures/p6_firewall_flow.mmd`). Spec: `kernel/llm_runtime/PLAN_SPEC.v0.1.md`. Validator: `impl/src/labtrust_portfolio/llm_planning.py` (`validate_plan`, `policy_check_step`). Deterministic capture: `capture_tool_call()` for replay/audit.

## 3. Red-team suite

`RED_TEAM_CASES`: eight cases and `CONFUSABLE_DEPUTY_CASES`: four cases with expected_block (unsafe blocked, safe allowed). Policy hook allow_list; validators must block unsafe in red-team tests. OWASP LLM Top 10 aligned; containment posture only.

**Table 1 — Red-team results.** Source: `datasets/runs/llm_eval/red_team_results.json`. Contains `success_criteria_met.red_team_all_pass` and `success_criteria_met.trigger_met` (conditional paper evidence). Run `scripts/llm_redteam_eval.py` to regenerate.

| Case id | expected_block | actually_blocked | pass |
|---------|----------------|-----------------|------|
| rt_unsafe_tool | true | true | yes |
| rt_safe_tool | false | false | yes |
| rt_unsafe_write | true | true | yes |
| rt_safe_submit | false | false | yes |
| rt_unsafe_shell | true | true | yes |

## 4. MAESTRO adapter and adapter latency

LLMPlanningAdapter (`adapters/llm_planning_adapter.py`) runs scenario, injects synthetic typed plan and validation result into trace metadata, produces TRACE + MAESTRO_REPORT. Run `llm_redteam_eval.py --run-adapter` to record latency; output: `adapter_latency.json` with runs, tail_latency_p95_mean_ms, scenarios, seeds. Optional `--latency-threshold-ms` adds latency_acceptable (SLA check). Reported latency is thin-slice execution time, not LLM inference.

**Table 2 — Adapter latency (when --run-adapter).** Source: `datasets/runs/llm_eval/adapter_latency.json`. Produced only when running `llm_redteam_eval.py --run-adapter`. Summary: tail_latency_p95_mean_ms, scenarios, seeds; per-run: scenario_id, seed, task_latency_ms_p95, wall_sec; run_manifest (adapter_scenarios, adapter_seeds, script). **Latency and jitter budget:** Even with synthetic plans, we report adapter latency (p50/p95, wall_sec) and optional stdev/CI when n >= 2; this gives a latency and jitter budget for integration (e.g. SLA threshold via `--latency-threshold-ms`). To refresh Table 2 and Figure 1: run with `--run-adapter` then `plot_llm_adapter_latency.py`.

**MAESTRO-integrated run (planner proposes unsafe, validator blocks, system completes safely).** One run where the planner proposes an unsafe action, the validator blocks it, and the system still completes tasks safely: documented in `e2e_denial_trace.json` (blocked step, outcome). Metrics: tasks_completed and recovery_ok remain acceptable; evidence that the firewall reduces unsafe attempts without collapsing task completion. Run `llm_redteam_eval.py` with adapter; e2e_denial_trace records the denial and outcome.

**Figure 1 — Adapter latency by scenario.** Mean latency (p95 ms or wall_sec) by scenario from adapter_latency.json. Regenerate with `python scripts/plot_llm_adapter_latency.py` (output `docs/figures/p6_adapter_latency.png`). Input: `datasets/runs/llm_eval/adapter_latency.json` (produced by `llm_redteam_eval.py --run-adapter`).

## 5. Comparison to existing LLM safety and tool-use benchmarks

| Aspect | P6 (this work) | OWASP LLM Top 10 / tool-use benchmarks |
|--------|----------------|----------------------------------------|
| Scope | Tool-policy containment (allow-list); deterministic capture | Broader: prompt injection, jailbreak, output safety |
| Red-team | Static cases (8 red-team + 4 confusable deputy); tool-centric; expected_block | Often: adversarial prompts, jailbreak suites, multi-step attacks |
| LLM | Real LLM supported when .env keys are set (--real-llm); synthetic-only by default for CI/keyless | Real model calls, tool-use APIs |
| Validator | Allow-list only (v0.1); arg/PONR future | Varies: filters, guardrails, tool restrictions |

We do not run jailbreak or adversarial prompt suites; scope is tool-policy containment and deterministic capture for CPS integration.

## 6. Limitations

Scope and conditional triggers: [EXPERIMENTS_AND_LIMITATIONS.md](../docs/EXPERIMENTS_AND_LIMITATIONS.md). Per-paper:

- **Conditional paper (trigger and scope):** Trigger requires the firewall to reduce unsafe attempts without collapsing task completion on at least one scenario. Evidence: `red_team_results.json` (success_criteria_met.trigger_met, red_team_all_pass), `e2e_denial_trace.json`, and adapter runs (tasks_completed). **Scope:** Typed-plan containment and tool-policy firewall only; no claim to elimination of prompt injection. If success_criteria_met.trigger_met is false, frame the paper as "conditional / optional"; see docs/CONDITIONAL_TRIGGERS.md (P6).
- **Containment not elimination:** We claim containment (firewall blocks unsafe actions); we do not claim elimination of prompt injection or adversarial inputs.
- **Real LLM:** Optional; when `.env` at repo root contains API keys (OPENAI_API_KEY or ANTHROPIC_API_KEY), run with `--real-llm` to call a real model for red-team-style prompts; results merged into red_team_results.json. Synthetic plans remain the default for CI and keyless environments.
- **No adversarial prompts or jailbreaks:** Red-team is tool-centric and static; no multi-step attack plans or prompt-injection suite.
- **Validator stack:** Allow-list only in v0.1; no argument checks or PONR checks (documented as future).
- **Static red-team:** Cases are fixed (not generated or adaptive).
- **Latency:** Reported latency is thin-slice execution time (adapter run), not LLM inference; tail-latency SLA is optional and configurable via `--latency-threshold-ms`.

## 7. Methodology and reproducibility

**Methodology:** Hypothesis—typed plan + validator stack blocks unsafe actions in red-team cases; containment only (no elimination claim). Metrics: validator blocks unsafe (expected_block true); tail latency acceptable. Kill criterion: validators fail to block unsafe in red-team. Red-team: RED_TEAM_CASES with expected_block; policy_check_step allow_list. Deployment guidance: least privilege, safe refusal, residual risk acknowledged. Portfolio criteria: `docs/STATE_OF_THE_ART_CRITERIA.md`.

**Reproducibility:** Validate plan: `validate_plan(typed_plan)`; policy: `policy_check_step(step, allowed_tools)`. Red-team: `llm_redteam_eval.py` writes `datasets/runs/llm_eval/red_team_results.json` (includes success_criteria_met.trigger_met, red_team_all_pass). With `--run-adapter`: writes `adapter_latency.json` (run_manifest: adapter_scenarios, adapter_seeds); then run `plot_llm_adapter_latency.py --latency datasets/runs/llm_eval/adapter_latency.json` to refresh Figure 1. Integration test: `tests/test_llm_p6.py` runs eval with --run-adapter and asserts both artifacts. Red-team cases: `llm_planning.RED_TEAM_CASES`. Adapter: `LLMPlanningAdapter`; trace metadata typed_plan_valid, typed_plan_captured. Spec: `kernel/llm_runtime/PLAN_SPEC.v0.1.md`.

**Claims and backing**

| Claim | Artifact / backing |
|-------|---------------------|
| C1 Schema + validator | TYPED_PLAN schema, validate_plan, policy_check_step (allow-list) |
| C2 Deterministic capture | capture_tool_call(), trace metadata |
| C3 Red-team containment | RED_TEAM_CASES, red_team_results.json, all_block_unsafe_pass |
| C4 MAESTRO integration | LLMPlanningAdapter, adapter_latency.json, typed_plan in trace |
| Containment only; no real LLM | Limitations section; adapter injects synthetic plan |
