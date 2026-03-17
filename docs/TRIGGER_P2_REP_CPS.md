# P2 REP-CPS: Trigger decision

**Trigger:** Proceed only if sensitivity sharing materially influences scheduling/actuation in the target architecture (lab/warehouse/traffic) and therefore becomes safety/security relevant.

**Current status:** Trigger is **not yet met** in the evaluated scenario: Table 1 shows identical tasks_completed_mean across REP-CPS, naive-in-loop, unsecured, and centralized. The paper is framed as a **profile-and-harness contribution**: REP-CPS is a safety-gated, typed, authenticated, rate-limited sensitivity-sharing profile with MAESTRO-compatible fault injection. Robust aggregation reduces observed compromise-induced bias relative to naive averaging in the evaluated harness; the contribution is the profile semantics and evaluation harness, not demonstrated operational benefit in this scenario. If a scenario where sensitivity sharing materially affects scheduling/actuation is added later, trigger proof can be updated.

**Implemented:** Profile spec (PROFILE_SPEC.v0.1.md), formal profile model in DRAFT, threat model, REP_CPS_PROFILE schema, reference aggregator, auth_hook, attack harness (compromised_updates), MAESTRO adapter, profile ablation (summary.json profile_ablation), rep_cps_eval.py. Dependencies (P1, P3, P4) are in place.

**Dependencies:** P1 (Contracts), P3 (Replay), P4 (MAESTRO) must be in place. REP-CPS reuses Contracts typed state and Replay/MAESTRO harnesses.
