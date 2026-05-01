# P5 coordination-tax proxy

The headline empirical pattern in P5 is rising **coordination load** as agent count increases. The paper uses a lightweight trace-derived quantity:

\[
\text{coordination\_tax\_proxy} = \frac{\text{coordination\_messages}}{\max(1,\ \text{tasks\_completed})}.
\]

## Why this is a proxy (not a universal cost)

- It is **not** a universal monetary, energy, or network cost metric.
- It is **meaningful in MAESTRO trace semantics**: message traffic scaled by completed work summarizes how much coordination chatter accompanies each finished task in the thin-slice harness.
- Some regimes **mechanically** induce more messages per task as agents multiply (e.g. broadcast-style chatter), even when throughput is flat.
- It must be read **together with** `tasks_completed`, latency summaries, and optional secondary proxies (e.g. error amplification).
- It measures **message load per completed task inside the MAESTRO trace**, not a physical plant resource.

## Paper sentence

We call this a proxy because it measures message load per completed task inside the MAESTRO trace semantics, not a universal cost or energy measure.
