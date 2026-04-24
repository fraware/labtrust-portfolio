# Robust GPT evaluation summary

ENGINEERING SIGN-OFF: GPT RESULTS NOT PAPER-READY

Blockers:
- API response/request IDs not stored in canonical JSON
- Full per-trial raw_output archive missing for most trials (evaluator stores run_details only for argument-level cases with n_runs>1)
- Stress suite not executed (cases defined only)
- prompt variant strict_json not executed
- prompt variant json_schema not executed
- prompt variant minimal_instruction not executed
- prompt variant verbose_instruction not executed
- prompt variant adversarial_context not executed
- prompt variant tool_return_injection not executed
- prompt variant benign_paraphrase not executed
- prompt variant unsafe_paraphrase not executed

See README.md for reproduction and limitations.
