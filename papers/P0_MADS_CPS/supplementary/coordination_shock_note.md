# P0 E4 coordination_shock note

This note explains the `coordination_shock` + `rep_cps_scheduling_v0` row where `rep_cps` can show:

- `tasks_completed = 0`
- `task_latency_ms_p95 = 0.0`
- `run_outcome = partial_safe`
- while raw conformance and strong replay remain high.

## Why raw conformance can still pass

Raw conformance checks evidence admissibility and integrity predicates: schema validity, hash integrity, replay consistency, and PONR coverage where applicable. It does **not** require positive throughput. A run can be machine-checkable and policy-safe while being operationally nonproductive.

In this regime, a controller may choose (or be forced into) a safe policy path that completes no tasks under heavy coordination stress. That outcome can still satisfy artifact-level conformance if the emitted artifacts are valid and internally consistent.

## Why strong replay can still be 1.0

Strong replay checks whether the stored MAESTRO core slice matches recomputation from trace, plus PONR witness coverage when required. If both producer and verifier agree on the same nonproductive safe outcome, strong replay is expected to pass.

In short: replay checks **consistency of evidence**, not productivity.

## Zero-latency semantics in this row

In this pipeline, `task_latency_ms_p95` is interpreted over completed tasks. When `tasks_completed == 0`, the exported p95 is `0.0` as the empty-completion sentinel.

This is treated as intentional semantics, not a hidden fallback bug, and is guarded by `tests/test_p0_e4_zero_latency_semantics.py`.

## Is `partial_safe` intended here?

Yes. Under `coordination_shock`, `partial_safe` can be an intended safe-fail behavior: the controller avoids unsafe progression under severe perturbation and compromised/contended coordination conditions.

## How to classify this outcome

For manuscript wording, classify this row as:

- **assurance-valid, safe-nonproductive degradation**

rather than a pure controller malfunction. It demonstrates that admissibility can hold while operational productivity diverges across controllers.

## One-sentence paper wording

Under `coordination_shock` in `rep_cps_scheduling_v0`, `rep_cps` exhibits an assurance-valid safe-nonproductive outcome (`partial_safe`, zero completed tasks) whose artifacts remain raw-conformant and strongly replay-equivalent, showing divergence in productivity without loss of evidence-layer admissibility.
