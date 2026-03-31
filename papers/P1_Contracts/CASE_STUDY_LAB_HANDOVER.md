# Case Study: Laboratory Functional Unit Handover

## System context
- Domain: laboratory functional unit orchestration.
- Shared resource: `centrifuge_slot_3`.
- Writers/controllers: `controller_a` and `controller_b`.
- Boundary event model: timestamped candidate writes with keyed ownership metadata.

## Failure scenario
`controller_a` finishes a run and releases ownership. A delayed message causes `controller_b` to issue a new start before release is reconstructed in replay state, then a stale completion arrives from `controller_a`.

## What delivery correctness says
All events are delivered successfully and checksummed correctly. Delivery-level correctness therefore reports no transport failure.

## Strong baseline behavior (B5 practical heuristic)
- Detects the obvious owner mismatch.
- Misses one timing-sensitive invalidity when handover metadata appears present but timestamp regression still violates coordination semantics.

## Full contract behavior
- Denies the early `controller_b` start with `split_brain`.
- Denies the stale completion with `stale_write` and `reorder_violation`.
- Preserves replay state on denials and emits deterministic reason-coded verdicts.

## Replay excerpt
```json
{
  "initial_state": {
    "ownership": {"centrifuge_slot_3": "controller_a"},
    "_last_ts": {"centrifuge_slot_3": 4112.0}
  },
  "events": [
    {"type":"task_end","ts":4112.4,"actor":{"id":"controller_a"},"payload":{"task_id":"centrifuge_slot_3","writer":"controller_a"}},
    {"type":"task_start","ts":4112.5,"actor":{"id":"controller_b"},"payload":{"task_id":"centrifuge_slot_3","writer":"controller_b"}},
    {"type":"task_end","ts":4112.2,"actor":{"id":"controller_a"},"payload":{"task_id":"centrifuge_slot_3","writer":"controller_a"}}
  ],
  "contract_verdicts": ["allow","deny","deny"],
  "reason_codes": [[],["split_brain"],["stale_write","reorder_violation"]]
}
```

## Before/after outcome
| Mode | Outcome |
| --- | --- |
| Delivery correctness only | All writes accepted; invalid owner write not blocked |
| Strong baseline (B5) | Denies ownership mismatch, allows one timing-sensitive invalid write |
| Full contract | Denies both invalid writes with explicit reason codes |

## Why this abstraction exists
This scenario shows that transport success does not imply coordination validity, and that reason-coded replay provides actionable operational diagnosis rather than only pass/fail signaling.
