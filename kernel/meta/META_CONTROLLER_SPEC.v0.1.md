# Meta-Controller Spec v0.1

## Model

- **State:** current_regime (e.g. "centralized", "blackboard", "fallback"), fault_count, latency_p95.
- **Actions:** switch_regime(to_regime). Meta-controller observes metrics and decides when to switch.
- **Switching criteria:** Thresholds (e.g. fault_count > N, latency_p95 > M ms) or stability window; switch only when criteria met and safety conditions hold.

## Switch criterion (v0.1)

The reference implementation (`impl/src/labtrust_portfolio/meta_controller.py`, `decide_switch`) uses a **threshold-based rule** with **hysteresis only on fault-based switching**:

1. **Revert (no hysteresis):** If currently in fallback and `fault_count <= 0` and `latency_p95_ms < 0.5 * latency_threshold_ms`, switch back to centralized.
2. **Fault-based switch to fallback:** If `fault_count >= hysteresis_consecutive` and `fault_count > fault_threshold`, switch to fallback (thrash control: require consecutive fault observations).
3. **Latency-based switch to fallback:** If `latency_p95_ms > latency_threshold_ms`, switch to fallback (no hysteresis; high latency alone can trigger fallback).

So revert and latency-based switch work even when `fault_count` is zero; hysteresis applies only to fault-count–driven switching. Regret-based or safety-bound-based switching (e.g. formal safety certificates) are out of scope for v0.1 and documented as future work.

## Collapse (v0.1)

**Current proxy:** Collapse is defined as `tasks_completed < collapse_threshold` (configurable; default 2 in meta_eval). A run is counted as collapsed when the MAESTRO report has tasks_completed below that threshold. This is a proxy for "run did not meet minimum progress"; it is not tied to a specific failure event or recovery timeout in the trace schema. **Future work:** Tie collapse to a concrete failure event type or recovery-timeout field in the trace (e.g. when the trace schema supports it); document in kernel.

## Safety conditions

PONRs (from MADS) are invariant across regimes: no regime change may violate PONR admissibility. Before switching: verify evidence and conformance for current run; gate actuation per MADS.

## Auditability

Every regime change is logged: trace event type `regime_switch` with payload `from_regime`, `to_regime`, `reason` (e.g. "fault_threshold"). Replay can reconstruct regime history.

## Trace events

Event type `regime_switch`. Payload: `from_regime` (string), `to_regime` (string), `reason` (string). Actor: meta-controller. Enables audit and replay of mode changes.
