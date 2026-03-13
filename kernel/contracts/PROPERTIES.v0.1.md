# Contract Properties (v0.1)

This document states precise (informal) properties of the contract validator and state model. For machine-checked determinism of the validator, see the W2 wedge in `formal/lean/`.

## Lemma (single-writer + monotonic timestamps)

**Under the contract rules** (ownership, `_last_ts` monotonicity per key):

If every event for key K is from the **same writer** and event timestamps are **non-decreasing** per key (i.e. for each key, the sequence of events that touch that key has non-decreasing `ts`), then **no split-brain state is reachable**.

**Justification:** Split-brain is detected when an event claims to write a key that is already owned by a different writer in the current state. Under single-writer, the first event that writes K sets ownership to that writer; all subsequent events for K are from the same writer, so no second writer ever acquires K. Monotonic timestamps ensure that no stale_write or reorder_violation arises from out-of-order application; the validator denies any event with `ts <= _last_ts[key]` for that key, so state remains consistent with the order of accepted events.

## Detection completeness (conflict classes)

Under the following assumptions:

- **Assumptions:** (1) Every event carries `writer` (or actor id) and `ts` in the payload or at top level. (2) Keys are identified (e.g. `task_id` in payload). (3) State maintains `ownership` and `_last_ts` per key.

**Detection of conflict class split_brain** is complete: any event that writes a key already owned by a different writer is denied with reason code `split_brain`.

**Detection of conflict class stale_write** is complete: any event with `ts <= _last_ts[key]` for the key being written is denied with reason code `stale_write` (and optionally `reorder_violation`).

**Detection of conflict class reorder_violation** (unsafe LWW under reorder): any event that would violate monotonicity of accepted write times is denied; the validator rejects events with `ts <= _last_ts[key]`, so reordered delivery is detected when the later-ts event is applied before the earlier-ts one (the earlier application sets `_last_ts[key]`, so the later event is then stale).

These properties are aligned with the implementation in `impl/src/labtrust_portfolio/contracts.py` and the W2 formal model in `formal/lean/Labtrust/W2Contract.lean` (determinism: same state and event yield the same verdict).
