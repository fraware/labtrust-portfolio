# Strong Baseline Definitions (P1)

## B1: Versioned OCC Boundary
- State: per-key `version`, per-key `last_seen_version`.
- Admission rule: allow only if `read_version == current_version` and timestamp is non-regressive.
- Deny conditions: version mismatch, stale timestamp.

## B2: Lease with Expiry/Renewal
- State: per-key `{owner,start,expiry}` lease record.
- Admission rule: owner can renew; non-owner can write only after expiry and explicit handover.
- Deny conditions: write by non-owner before expiry, expired lease without renewal.

## B3: Lock/Mutex Lifecycle
- State: per-key lock owner with acquire/release behavior.
- Admission rule: lock owner writes are allowed; lock is acquired when empty and released on end.
- Deny conditions: write without lock ownership.

## B4: State-Machine-Only Guard
- State: per-key local machine state (`idle`/`running`).
- Admission rule: only valid local transitions (`idle->task_start`, `running->task_end`).
- Deny conditions: illegal transition; no multi-writer authority checks.

## B5: Practical Engineering Heuristic
- State: ownership map, monotonic timestamp map, optional handover token.
- Admission rule: owner write with monotonic time; ownership transfer only with matching handover token.
- Deny conditions: stale timestamp, owner mismatch without valid handover metadata.

## Reporting contract
For each baseline report:
- sequence exact-match rate
- event-level TP/FP/FN and precision/recall/F1
- per-class misses
- false denials on valid traces
- mean runtime overhead
