# Conditional triggers

Papers P2, P5, P6, and P8 are **conditional**: proceed only when their trigger criteria are met. This document records the trigger condition, “proceed when” criterion, and dependency order.

## P2 REP-CPS

- **Trigger:** Sensitivity sharing materially influences scheduling or actuation decisions in the target architecture (lab/warehouse/traffic), and therefore becomes safety/security relevant.
- **Trigger proof required:** REP-CPS improves robustness under compromise/delay **without throughput regression** on at least one **non-toy** lab scenario. Evidence in release: scenario id, centralized vs REP-CPS metrics, statement that trigger is met or not (if not, paper is "conditional / optional" only).
- **Current status:** Trigger is **not yet met** in the evaluated scenario: Table 1 shows identical tasks_completed_mean across REP-CPS, naive-in-loop, unsecured, and centralized. The paper is framed as a **profile-and-harness contribution**: typed, authenticated, rate-limited, safety-gated sensitivity-sharing profile with MAESTRO-compatible fault injection. Do not claim that sensitivity sharing materially influences actuation in the current scenario. Until a scenario where sensitivity sharing materially affects outcomes is added, the paper remains conditional/optional for the full trigger.
- **Proceed when:** You can show that REP-like protocols are in scope for the lab (or other) profile and that naive forms break under CPS constraints; or submit as profile paper with honest scope (profile + harness, reduced observed bias under compromise).
- **Dependency order:** After Contracts (P1) typed state and Replay/MAESTRO harnesses exist; REP-CPS is a profile inside the MADS envelope.

## P5 Scaling laws

- **Trigger:** MAESTRO provides **multi-scenario** datasets sufficient for out-of-sample validation. Otherwise the paper reads as overclaim.
- **Trigger proof required:** Beat **per-scenario baseline** out-of-sample, or reposition paper to "dataset analysis + negative results." Deliverable: heldout_results.json (or summary) explicitly states "beat_per_scenario_baseline" true/false; if false, draft states negative result and scope.
- **Proceed when:** MAESTRO runs exist across multiple scenario families and fault mixtures, and you can hold out a scenario family or fault mixture for validation.
- **Dependency order:** After P4 (MAESTRO) has multi-scenario coverage; consumes MAESTRO datasets and Replay traces.

## P6 LLM Planning

- **Trigger:** An LLM is in the control plane (planning/toolcalling), OR a typed-plan + validator firewall is needed as a general containment pattern.
- **Trigger proof required:** Firewall reduces unsafe attempts without collapsing task completion on at least one scenario family. Deliverable: evidence (unsafe blocked: red_team 8/8, confusable deputy 4/4, jailbreak-style 2/2); real-LLM Table 1b (5 runs/case, pass_rate, Wilson CI); adapter latency and 3-way baseline; tasks_completed non-zero; document in release and P6.
- **Proceed when:** You are building or evaluating an LLM-in-the-loop control plane and need containment and measurable robustness (not “elimination” of prompt injection).
- **Dependency order:** LLM planning is a module inside the MADS envelope; evaluated on MAESTRO scenarios.

## P8 Meta-coordination

- **Trigger:** Multiple coordination regimes are actually deployed (e.g. centralized, market, swarm, fallback), and mode-thrashing or collapse occurs under compound faults.
- **Trigger proof required:** Meta beats **best fixed regime** in at least one stress regime and **does not safety-regress** (no_safety_regression true). Deliverable: comparison.json (or summary) states trigger_met or equivalent; meta wins on collapse in at least one regime; safety invariant; if not met, paper remains conditional.
- **Proceed when:** You have at least two regimes and fault mixtures that cause regime stress; meta-controller can be compared to best fixed regime.
- **Dependency order:** After MAESTRO and Replay; safety constraints (PONRs from MADS) must remain invariant across regimes.

## Reference

See **PORTFOLIO_BOARD.md** section “Trigger criteria for conditional modules” for the canonical one-line triggers.
