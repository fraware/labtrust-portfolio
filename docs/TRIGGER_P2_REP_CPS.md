# P2 REP-CPS: Trigger decision

**Trigger:** Proceed only if sensitivity sharing materially influences scheduling/actuation in the target architecture (lab/warehouse/traffic) and therefore becomes safety/security relevant.

**Decision: GO.** Sensitivity sharing is adopted as a coordination primitive in the target architecture (lab/warehouse/traffic); shared variables influence task assignment and scheduling. Implementing profile spec, threat model, REP_CPS_PROFILE, reference aggregator, attack harness, and MAESTRO adapter. Dependencies (P1, P3, P4) are in place.

**Dependencies:** P1 (Contracts), P3 (Replay), P4 (MAESTRO) must be in place. REP-CPS reuses Contracts typed state and Replay/MAESTRO harnesses.
