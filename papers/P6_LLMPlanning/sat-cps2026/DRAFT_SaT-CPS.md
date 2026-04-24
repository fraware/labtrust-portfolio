# Secure CPS Tool Invocation via a Typed-Plan Firewall



**Venue: SaT-CPS 2026. Draft for ACM proceedings conversion. See SUBMISSION_STANDARD.md, ROLES.md, claims_satcps.yaml.**



---



## Abstract



(1) **CPS security problem.** Tool invocation in cyber-physical control planes is a trust boundary: planner output can request unsafe tools or arguments (e.g. path traversal), and execution without validation undermines safety and auditability. (2) **Mechanism.** We describe a runtime enforcement architecture for CPS tool invocation: typed plans, tool allow-listing, argument validation (`safe_args` + `ponr_gate`), and deterministic capture of proposed invocations. (3) **Synthetic result.** The validator blocks all released synthetic unsafe cases and admits the released safe cases (15 red-team, 6 confusable deputy, 4 jailbreak-style). (4) **Real-LLM result (OpenAI, camera-ready snapshot `llm_eval_camera_ready_20260424`).** With full-suite mode and N=3 runs per case, 25 cases per model (75 trials per model), gpt-4.1-mini and gpt-4.1 each achieve 75/75 (100.0%, 95% Wilson CI [95.1, 100.0]). Multi-model summaries and disagreement matrices are recorded in red_team_results.json. (5) **Optional cross-provider matrix.** A separate four-model run on Prime Inference is documented in EXPERIMENTS_RUNBOOK.md; denominators and models differ from the OpenAI run and must not be merged without relabeling. (6) **Adapter and latency.** The security layer adds bounded measured overhead; denial traces are recorded for replay and audit; optional latency decomposition (validation vs capture) is available in adapter_latency.json when --latency-decomposition is used. (7) **Baseline.** Tool-level benchmark: gated and weak both deny the injected disallowed tool; ungated allows. Argument-level benchmark (safe_args ablation): gated denies, weak and ungated allow. Benign suite: gated should admit safe steps while preserving the adversarial separation in the other baselines. (8) **Bounded claim.** We claim containment of the released unsafe cases and auditability; we do not claim elimination of prompt injection or full coverage of adversarial inputs.



---



## 1. Introduction



**Why CPS tool invocation is a security problem.** In CPS, the control plane often invokes tools (query status, submit results, or legacy interfaces). When a planner-- whether an LLM or a heuristic-- produces tool calls, those calls cross a trust boundary: unchecked execution of disallowed tools or malicious arguments (e.g. path traversal) can compromise safety and integrity. Runtime enforcement at this boundary is therefore a core concern for secure CPS architectures.



**Why ordinary LLM framing is insufficient for CPS.** Generic LLM safety benchmarks focus on prompt injection, jailbreaks, or output filtering in isolation. For CPS we need: (a) a clear trust boundary (planner output is untrusted until validated); (b) integration with trace and audit (deterministic capture, denial logs); (c) evaluation that includes both synthetic validator correctness and real-LLM stress tests; (d) explicit baselines that show the value of each validation layer (allow-list vs safe_args).



**What the typed-plan firewall is.** The typed-plan firewall sits at the actuation boundary: planner output is untrusted until the firewall admits it. Plans are typed (tool, args, validators); the firewall runs allow-list and argument checks (e.g. path traversal, dangerous patterns). Denied steps are not executed; they are captured for replay and audit. This is a runtime enforcement architecture for CPS tool invocation, not merely an LLM benchmark.



**What evidence is provided.** We report four evaluation blocks: (A) synthetic validator evidence (red-team, confusable deputy, jailbreak-style); (B) real-LLM stress test (model, pass rate, Wilson CI, and explicit failure-case analysis); (C) adapter latency and denial traces (bounded overhead, per-scenario denial counts); (D) baseline comparison (tool-level and argument-level: gated vs weak vs ungated).



**What is not claimed.** We do not claim elimination of prompt injection, full jailbreak coverage, or universal robustness. We claim containment of the released unsafe cases and auditability under the reported evaluation.



---



## 2. Threat model



**Assets.** CPS tool interfaces; operational state accessible via those tools; traces and denial logs; policy configuration (allow-list, validator stack).



**Adversarial leverage.** Prompt injection via planner input; tool-returned content that induces privilege-seeking behavior; malformed or privilege-seeking arguments (e.g. path traversal); confused-deputy dynamics; jailbreak-style instruction phrases in arguments.



**Trust assumptions.** The planner is untrusted at the actuation boundary. The validator and capture pipeline are trusted. The execution environment obeys firewall decisions (denied steps are not executed).



**Security properties sought.** No unsafe step (disallowed tool or unsafe arguments in the released suite) reaches execution in the reported setting; all denied actions are captured for replay and audit; runtime overhead remains low enough for the target CPS context.



**Non-goals.** Proving semantic correctness of whole plans; complete jailbreak coverage; universal robustness; elimination of prompt injection.



| Threat | Entry point | Security property | Mitigation | Out of scope |

|--------|-------------|--------------------|------------|--------------|

| Disallowed tool | Planner output | No unsafe step executed | allow_list | Semantic plan correctness |

| Path traversal in args | Planner output | No unsafe step executed | safe_args check | Full input sanitization |

| Jailbreak-style phrases in args | Planner output | No unsafe step executed | safe_args (pattern check) | General prompt injection |

| Confused deputy (elevation in args) | Planner output | No unsafe step executed | safe_args / policy | Cross-component trust |

| Unaudited execution | Adapter | Denials replayable/auditable | Deterministic capture | Full forensics |



---



## 3. System overview



Typed plans: schema with steps (seq, tool, args, validators). Validator stack: allow_list (tool allow-listing), safe_args (path traversal, dangerous patterns, jailbreak-style phrases). validate_plan_step runs the configured validators; policy_check_step provides allow-list-only (weak) mode. Denied steps are recorded in trace metadata; capture_tool_call supports replay. Integration with MAESTRO: LLMPlanningAdapter runs scenarios, injects plan and validation outcome into trace, reports denials and tasks_completed. See Figure 1 (decision path: planner output -> typed step -> allow-list -> safe_args -> capture -> allow/deny) and kernel/llm_runtime/PLAN_SPEC.v0.1.md.



---



## 4. Evaluation



**Research questions.** (Q1) Does the validator correctly separate safe and unsafe cases on the synthetic suite? (Q2) Does that separation persist when an LLM must realize the unsafe argument forms under repeated prompting? (Q3) Can the enforcement layer be embedded with bounded overhead and replayable denial traces? (Q4) What does each validation layer contribute (tool vs argument)? (Q5) Do measured safe cases remain admissible? **Statistical treatment.** Pass rates use 95% Wilson score intervals; latency uses mean, stdev, and 95% CI for the mean; baselines report denial counts and task completion. **Artifact integrity.** Every result maps to one exact artifact; run export_p6_artifact_hashes.py and export_p6_reproducibility_table.py for the appendix reproducibility table (model_id, timestamp, seed, prompt_template_hash, evaluator_version, policy_version, artifact_hash).



### Block A --  Synthetic validator evidence



Synthetic evidence isolates validator correctness from model-generation variability. The full synthetic table (15 red-team, 6 confusable deputy, 4 jailbreak-style) is the primary validator evidence: all unsafe cases blocked, all safe cases admitted. Source: red_team_results.json, confusable_deputy_results.json; export_llm_redteam_table.py.



### Block B --  Real-LLM stress test



The validator correctly blocks the canonical unsafe step; the real-LLM experiment tests whether models reliably emit unsafe argument forms under repeated prompting.



**Canonical OpenAI run (Table 1b, camera-ready snapshot).** Reported: full-suite mode, 3 runs per case, 25 cases per model (75 trials per model). Models gpt-4.1-mini and gpt-4.1 each score 75/75 (100.0%, 95% Wilson CI [95.1, 100.0]). Command: `llm_redteam_eval.py --out datasets/runs/llm_eval_camera_ready_20260424 --real-llm --real-llm-models gpt-4.1-mini,gpt-4.1 --real-llm-runs 3 --real-llm-suite full`. Output: red_team_results.json (real_llm_models[], cross_model_summary when multiple models).



**Optional Prime Inference four-model matrix.** Reported (2026-03-18): 3 runs per case, 13 cases/model (39 trials/model). x-ai/grok-4-fast 39/39 (100.0%, Wilson [91.0, 100.0]); google/gemini-2.5-flash, openai/gpt-4.1-mini, qwen/qwen3-30b-a3b-instruct-2507 each 33/39 (84.6%, [70.3, 92.8]). Disagreement matrix isolates two argument-level cases. Use a **separate** output directory (e.g. llm_eval_prime_matrix_top4_n3) so OpenAI N=5 runs are not overwritten. See EXPERIMENTS_RUNBOOK.md.



**Failure case as first-class result.** Any future argument-level misses or parse failures must be reported explicitly with denominator and suite mode. Repeated-run real-LLM evaluation is necessary to assess containment; argument-level cases are exactly where real systems need tighter controls. Keep failure reporting first-class when runs are refreshed.



### Block C --  Adapter latency and denial traces



3 scenarios, 20 seeds each (60 runs); mean p95 latency, stdev, 95% CI; total denied unsafe steps (60/60 in reported run); per-scenario denial counts; tasks completed. Message: this security layer adds bounded measured overhead while preserving task completion in the reported denial-injection setting. Source: adapter_latency.json, denial_trace_stats.json.



**Case study: denial trace.** In a representative run, the planner proposed step { tool: execute_system, args: { cmd: "rm -rf" } }. Allow-list check: tool not in allow_list -> Deny. The step was captured for audit; no execution occurred. Regenerate snippet from a baseline trace: `python scripts/export_p6_denial_trace_case_study.py --trace datasets/runs/llm_eval/baseline_runs/gated/toy_lab_v0/seed_1/trace.json`.

**Latency decomposition and layer attribution.** With --latency-decomposition, adapter_latency.json includes per-component timings (validation_ms, capture_total_ms) with p50/p95/p99. Layer attribution (denial by allow_list_only, safe_args_only, both, admitted) is in red_team_results.json and confusable_deputy_results.json per case; export_p6_layer_attribution.py produces the stacked-bar table. Argument-level failure analysis (exact unsafe vs omitted vs safe substitution, etc.) is produced by export_p6_failure_analysis.py from real-LLM run_details.



### Block D --  Baseline comparison (honest framing)



**Tool-level benchmark (existing).** The injected unsafe step is execute_system (disallowed tool). Gated and weak both deny (rejection at allow-list layer); ungated allows. This baseline shows the value of having a gate at all; it does not isolate the marginal contribution of safe_args. Reported: 60 runs; gated 60 denials, weak 60, ungated 0; tasks_completed_mean 3.95 (all modes).



**Argument-level benchmark (safe_args ablation).** With an allow-listed tool and unsafe arguments (path traversal), gated denies (safe_args blocks), weak allows (allow-list only), ungated allows. This demonstrates the incremental value of argument-level validation. Reported: 60 runs; gated 60 denials, weak 0, ungated 0; tasks_completed_mean 3.95. Source: baseline_comparison.json (tool-level), baseline_comparison_args.json (argument-level); export_p6_baseline_table.py [--baseline-file baseline_comparison_args.json].

**Utility-security tradeoff.** Benign suite (--baseline-plan benign) runs gated/weak/ungated on all-safe steps; baseline_benign.json reports benign_acceptance_rate and false_positive_count per mode. Gated should preserve benign acceptance (no over-denial) while improving unsafe denial in the adversarial baselines.



---



## 5. Discussion and limitations



Containment, not elimination: the firewall blocks the released unsafe cases; we do not claim elimination of prompt injection or full coverage. Validator v0.2 covers allow_list and safe_args; PONR and broader checks are future work. Real-LLM pass rate is model- and prompt-dependent; synthetic table remains primary validator evidence. Residual risk from novel attack vectors remains.



---



## 6. Conclusion



We presented a runtime enforcement architecture for CPS tool invocation: typed-plan firewall with allow-listing and argument validation, deterministic capture for audit, and a released evaluation suite (synthetic, real-LLM, adapter latency, tool-level and argument-level baselines). The firewall blocks the released unsafe cases and admits the released safe cases; denial-injection experiments show bounded overhead and the incremental value of argument-level validation. We report the real-LLM path-traversal failure case as a first-class result. Claims are limited to containment and auditability under the reported evaluation.



---



## References and figures



- **Figure 1 (decision path):** Regenerate with `python scripts/export_p6_firewall_flow.py`; output docs/figures/p6_firewall_flow.mmd (Mermaid). Render to PDF/PNG for ACM. Path: planner output -> typed step -> allow-list -> safe_args -> capture -> allow/deny.

- **Figure 2 (adapter latency):** plot_llm_adapter_latency.py from adapter_latency.json; include only if compact and clearly answers overhead.

- **Reproduction:** See EXPERIMENTS_RUNBOOK.md in this folder for the experiment roadmap (0--12), one-shot commands, artifact locations, OpenAI real-LLM (canonical Table 1b), optional Prime multi-model run, benign baseline, latency decomposition, and export scripts (export_llm_redteam_table.py, export_p6_reproducibility_table.py, export_p6_layer_attribution.py, export_p6_failure_analysis.py, export_p6_cross_model_heatmap.py, export_p6_latency_decomposition.py). Appendix A in papers/P6_LLMPlanning/DRAFT.md lists the core reproduction chain and artifact hashes.



