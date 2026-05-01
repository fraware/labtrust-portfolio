# P5 vs P4 boundary (MAESTRO overlap)

Both P4 and P5 run on MAESTRO scenarios. To avoid paper-slicing concerns, keep contributions disjoint:

## P4 — benchmark / fault-injection artifact

- Scenario definitions and fault sweeps used as a **benchmark harness**.
- Adapter baselines, anti-gaming score, recovery-oriented metrics after faults.

## P5 — evaluation protocol and coordination-scaling study

- **7,200-row** coordination-scaling grid (six scenario ids × five regimes × four agent counts × two fault labels × 30 seeds).
- Held-out prediction protocols with **admissible vs oracle** baseline discipline.
- **Protocol-specific triggers** (`trigger_met` differs by leave-one-out mode).
- Title-grounding **1→8 agent deltas** from `regime_agent_summary.json`.

P5 should **not** restate P4’s anti-gaming narrative as its core novelty. When both papers appear in the same portfolio, cite P4 only as **shared infrastructure context** if needed.
