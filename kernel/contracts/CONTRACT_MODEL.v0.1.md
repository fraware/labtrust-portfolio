# Contract Model and Failure Classes (v0.1)

## Types and ownership

- **Typed state:** State is a key-value map with a declared type per key (e.g. device state, specimen state). Each key has an **owner** (writer identity or role) that is the only authority allowed to write that key unless a transition rule explicitly allows a handover.
- **Valid transitions:** A transition is valid if (1) the writer is the current owner for the affected key(s), or (2) the contract defines an admissible handover (e.g. lease release, coordinator reassignment). Valid transitions are listed in the contract (e.g. by name or by (state, event) -> new_state).
- **Time model:** Event time (when the event was logged), processing time (when the system processed it), actuation time (when the action took effect). Actuation-time transitions cannot precede the authorization event time.

## Failure classes

1. **Split-brain ownership:** Two writers believe they own the same key; both attempt to write. Detected when an event claims to write a key that is owned by another writer in state and no handover is defined.
2. **Stale write acceptance:** A write is accepted that is based on an outdated view of state (e.g. no lease check). Detected when event timestamp or sequence is before the last update for that key and the contract requires monotonicity.
3. **Unsafe last-write-wins under delay/reorder:** Messages are reordered; a later write (by wall clock) is applied after an earlier one, violating intended ordering. Detected when conflict_semantics require ordering and event order is violated.

The validator returns **verdict** (allow/deny) and **reason_codes** (e.g. SPLIT_BRAIN, STALE_WRITE, REORDER_VIOLATION).

## Conflict semantics

Contract specifies conflict_semantics: e.g. "last-write-wins" (with timestamp), "lease" (only owner within lease window), "OCC" (optimistic concurrency with version check). The validator enforces the chosen semantics.
