# P1 Trace-derivability: contract predicates from trace alone

All contract predicates used by the coordination contract validator are computed from **trace alone** (event sequence, timestamps, task_id, actor, payload fields). No privileged or hidden state is required beyond what is logged in the trace and declared in the contract config.

## Predicate → trace field mapping

| Predicate / check | Trace fields used | Description |
|-------------------|-------------------|-------------|
| **single_writer_per_task (split_brain)** | `event.type`, `event.payload.task_id`, `event.actor.id` (or `payload.writer`), state `ownership[key]` | State `ownership` is derived by replaying the trace: for each task_id we record the writer from the first task_start/task_end. A later event with the same task_id and a different writer → split_brain. |
| **timestamp_ordering (stale_write / reorder)** | `event.ts`, `event.payload.task_id`, state `_last_ts[key]` | State `_last_ts` is derived from the trace: we update last_ts[key] = event.ts when we apply the event. If event.ts < _last_ts[key] → reorder_violation / stale_write. |
| **instrument_state_machine** (optional) | `event.type`, `event.payload.task_id`, state `_instrument_state` | When contract has `use_instrument_state_machine: true`, we apply the event to a lab instrument state (idle → running → idle). State is derived by replaying events through `instrument_state_machine.apply_instrument_event`. |

## State derived from trace

- **ownership**: map task_id → writer; updated on each task_start / task_end from `event.actor.id` or `event.payload.writer`.
- **_last_ts**: map task_id → last timestamp seen; updated from `event.ts` when event is applied.
- **_instrument_state**: when enabled, per-key instrument state (idle/running/etc.) from `instrument_state_machine.apply_instrument_event`.

All of these are computed by a single pass over the trace; no external or privileged state is required. The contract config (e.g. `use_instrument_state_machine`) is declared and can be shipped with the trace or release.

## Kill criterion K1

If a contract predicate required **privileged hidden state** not derivable from trace + declared config, the design would lose portability and auditability. This document is the single source of truth: every check in `contracts.validate` and `instrument_state_machine` uses only trace fields and derived state above.
