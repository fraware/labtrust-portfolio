# Robust GPT evaluation summary

ENGINEERING SIGN-OFF: GPT RESULTS NOT PAPER-READY

Blockers:
- API response/request IDs not present on stored trials (independence audit is partial)
- Full per-trial raw_output archive incomplete (cross-model aligned stored-raw trials=6, model n_runs_total reference=75)
- Stress suite not executed in this JSON (no rs_* case rows)
- prompt variant strict_json not executed (no case rows)
- prompt variant json_schema not executed (no case rows)
- prompt variant minimal_instruction not executed (no case rows)
- prompt variant verbose_instruction not executed (no case rows)
- prompt variant adversarial_context not executed (no case rows)
- prompt variant tool_return_injection not executed (no case rows)
- prompt variant benign_paraphrase not executed (no case rows)
- prompt variant unsafe_paraphrase not executed (no case rows)

See README.md for reproduction and limitations.
