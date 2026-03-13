# Typed Plan and LLM Containment Spec v0.1

## Plan schema

TYPED_PLAN: plan_id, steps (array). Each step: seq, tool (string), args (object), validators (array of validator names). Schema: `kernel/llm_runtime/TYPED_PLAN.v0.1.schema.json`. Plans are type-checked before execution; validators run per step (static, policy, gate integration).

## Validator stack

- **Static:** Schema validity (required fields, types).
- **Policy:** Per-step policy checks (e.g. tool allow-list, arg bounds). **v0.1 implements allow-list only;** argument sanity and PONR integration are future work.
- **Gate:** MADS admissibility (evidence, conformance) before actuation. Containment posture: validators block unsafe actions; we do not claim "elimination" of prompt injection.

## Deterministic toolcalling capture

Tool calls (tool name, args) must be captured deterministically so that replay and audit can reproduce what was requested. Wrapper records (timestamp, tool, args, validator_results) in trace or log.

## Tail-latency SLA (optional)

"Tail latency acceptable" is an optional, configurable criterion: e.g. `tail_latency_p95_mean_ms < threshold_ms`. The eval script supports `--latency-threshold-ms`; when set, it adds `latency_acceptable` to adapter_latency.json. Default: not enforced. Reported latency is thin-slice execution time (adapter run), not LLM inference time.

## Red-team suite

Aligned with OWASP LLM Top 10: prompt injection (via tool-fed content), unsafe tool use, jailbreak, etc. Each case has expected outcome (block or allow). Validators must block unsafe in red-team tests; tail latency may be checked via the optional SLA above.

## MAESTRO adapter

Adapter runs scenario; plan steps (or synthetic typed plan) are validated and optionally executed; trace includes plan_id and validator outcomes. Produces TRACE + MAESTRO_REPORT.
