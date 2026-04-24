# Paper claims checklist (P6)

- **SUPPORTED** — The validator matches expected decisions on 25/25 released typed-step cases.
- **SUPPORTED** — The canonical real-LLM rows are 75/75 for gpt-4.1-mini and gpt-4.1.
- **SUPPORTED WITH SCOPE LIMITATION** — The supplementary latest-model rows are 73/75 for gpt-5.4 and 54/75 for gpt-5.4-pro.
- **SUPPORTED** — GPT-5.x rows are supplementary isolated compatibility runs.
- **SUPPORTED WITH SCOPE LIMITATION** — Mean task-level p95 adapter latency is 36.70 ms.
- **SUPPORTED WITH SCOPE LIMITATION** — Replay verification matches 60/60 denied steps in the frozen `replay_denials.json` summary; a fresh `trace.json` scan in this checkout finds additional denied-step records (see `reproducibility_check.json` `replay_fresh_trace_scan`).
- **SUPPORTED** — Tool-level baseline denials are 60/60/0.
- **SUPPORTED** — Argument-level baseline denials are 60/0/0.
- **SUPPORTED** — Benign baseline has zero gated false positives.
- **SUPPORTED** — Task-critical gated replacement has 20 denials and zero unsafe executions.
- **SUPPORTED WITH SCOPE LIMITATION** — Ungated task-critical replacement executes 20/20 unsafe steps.
- **SUPPORTED WITH SCOPE LIMITATION** — Denied steps are excluded from execution in the mock/thin-slice harness.
- **SUPPORTED WITH SCOPE LIMITATION** — The firewall provides a deterministic mediation boundary.
- **SUPPORTED WITH SCOPE LIMITATION** — The artifact supports replayable denial evidence.
- **UNSUPPORTED** — The artifact supports production deployment readiness.
- **UNSUPPORTED** — The artifact supports universal prompt-injection defense.
- **UNSUPPORTED** — The artifact supports complete CPS safety.
