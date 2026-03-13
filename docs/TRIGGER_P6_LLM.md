# P6 LLM Planning: Trigger decision

**Trigger:** Proceed only if (a) an LLM is in the control plane (planning/toolcalling), or (b) a typed-plan + validator firewall is needed as a general containment pattern.

**Decision: GO.** Typed-plan + validator firewall is adopted as the general containment pattern for the portfolio; LLM-in-the-loop is in scope for future lab targets. Proceeding with TYPED_PLAN schema, validator library, deterministic toolcalling wrapper, red-team suite, and MAESTRO adapter.

**Dependencies:** MADS envelope; MAESTRO scenarios for evaluation.
