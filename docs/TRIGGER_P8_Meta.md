# P8 Meta-Coordination: Trigger decision

**Trigger:** Proceed only if multiple coordination regimes are actually deployed (centralized, market, swarm, fallback) and mode-thrashing/collapse occurs under compound faults.

**Decision: GO.** Multiple coordination regimes (centralized, blackboard) exist in P4; compound faults and scenario stress justify meta-controller behavior. Proceeding with meta-controller spec, switching criteria, MAESTRO scenarios for regime stress, and trace events for mode changes.

**Dependencies:** P4 (MAESTRO), P3 (Replay), P0 (MADS PONRs invariant across regimes).
