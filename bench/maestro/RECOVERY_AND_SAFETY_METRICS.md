# MAESTRO recovery and safety metrics (v0.2)

This note defines the semantics of fields in `MAESTRO_REPORT.v0.2` produced from `TRACE.v0.1` by `impl/src/labtrust_portfolio/maestro.py` (`maestro_report_from_trace`). It is the normative interpretation for P4 manuscript claims.

## Time base

All `time_*_ms` metrics are derived from TRACE event timestamps `ts`, expressed in milliseconds relative to subtractions of epoch times also in `ts` units.

- **Thin-slice harness (`run_thin_slice`)**: `ts` is synthetic scenario time (seconds) advanced by the harness for inter-event spacing. It is **not** host wall-clock time unless a future adapter records wall time into `ts`.
- **Future real systems**: adapters should record a consistent clock in `ts` (for example monotonic control-loop time or wall UTC) and document the mapping in run metadata.

## Clock anchors

- **Run start reference `t0`**: timestamp of the first event in `trace["events"]`, or `0.0` if the event list is empty.
- **First fault**: first event with `type == "fault_injected"` whose payload `fault` is not used for scheduling-only gates, counted the same as all `fault_injected` entries in the trace for timing purposes.

### `time_to_first_fault_ms`

`(first_fault.ts - t0) * 1000`, or `null` if no `fault_injected` event exists.

### `time_to_recovery_ms`

`(first_recovery_succeeded.ts - first_fault.ts) * 1000`, or `null` if either the first fault or any `recovery_succeeded` event is missing. Non-negative when present.

**Recovery** means an explicit `recovery_succeeded` event emitted after a fault on the execution path (for example task completion after a drop with retries, or continuation after a modeled timeout stall). It is intentionally conservative: absence of the event implies recovery was not recorded, not that physical recovery was impossible.

### `time_to_safe_state_ms`

`(first_safe_state_reached.ts - t0) * 1000`, or `null` if no `safe_state_reached` event exists.

**Safe state** means the supervisor recorded `safe_state_reached` (harness: all planned tasks emitted `task_end` without an intervening safe shutdown). This is a **benchmark-level** predicate, not a certification of real-world safety.

## Safety

### `safety_violation` events

Each `safety_violation` event carries `payload.violation_type` and `payload.detail`. The report aggregates:

- `safety_violation_count`: number of such events.
- `safety_violation_types`: ordered list of `{type, detail}` objects (duplicates allowed for audit density).

### `unsafe_success_count` (run-level)

`1` if `planned_task_count` (from trace metadata, else inferred from completions) is met while `safety_violation_count > 0`, else `0`. This flags **completion under residual recorded violations** in the benchmark sense.

### Other safety counters

Derived by counting events of matching `type` (`ponr_violation`, `unsafe_task_completion`, `constraint_guard_trigger`, `deadline_miss`, `resource_conflict`, `invalid_action`, `blocked_action`) as implemented in `maestro_report_from_trace`.

## Coordination efficiency

Ratios use `max(1, tasks_completed)` in the denominator to avoid division by zero on pathological traces.

## `run_outcome` vocabulary

Closed set: `success_safe`, `success_unsafe`, `partial_safe`, `partial_unsafe`, `failed_safe_shutdown`, `failed_unsafe`. See `maestro.py::_classify_run_outcome` for the exact predicate tree (based on planned completion, safety signals, `recovery_ok`, and `safe_shutdown_initiated`).

## Thin-slice vs future adapters

Thin-slice emits a controlled subset of events to instantiate the schema. Real adapters should emit the same event types where possible so reports remain comparable; additional domain events may be added in future schema revisions with explicit versioning.
