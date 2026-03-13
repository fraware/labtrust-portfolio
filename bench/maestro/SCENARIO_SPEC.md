# MAESTRO Scenario Spec and Fault Model (v0.1)

## Scenario format (YAML)

Each scenario file under `scenarios/*.yaml` has:

- **id:** Scenario identifier (e.g. toy_lab_v0, lab_profile_v0).
- **description:** Short human-readable description.
- **tasks:** List of `{name: string}` task definitions. Order defines default execution order for reference adapters.
- **faults:** List of fault definitions. Each has `name` and optional `param` (parameter name passed to harness).
- **family:** (Optional) Taxonomy family for grouping: `lab` (lab-profile scenarios), `warehouse`, `traffic`, or `regime_stress`. Used for filtering and reporting; if absent, treat as default.
- **resource_graph:** (Optional) Lab-realism model. See "Resource graph" below.
- **concurrency:** (Optional) Limits for station/instrument concurrency (e.g. max_concurrent_per_instrument, max_concurrent_per_station).
- **failure_dominance:** (Optional) Intended failure regime: `contention` (queue + branching + recovery) or `scale` (N agents). Lab-profile scenarios should use `contention` for ADePT-style credibility.

Scenarios align with the lab profile (`profiles/lab/v0.1/`) when they reference the same task names and fault classes (see fault_model.yaml). Resource graph and PONRs are defined in the profile or in the scenario; the scenario specifies the task and fault set for a run.

## Resource graph (lab realism)

When present, `resource_graph` models capacity-constrained resources and bottlenecks so that failures are dominated by contention and recovery, not by scale (N agents). This makes MAESTRO results believable for ADePT-style labs.

- **instruments:** List of `{id, capacity, states, warmup_required?}`. Instruments are capacity-constrained; `states` typically include `idle`, `running`, `calibration`, `warmup`, `cleaning`.
- **stations:** List of `{id, capacity, bottleneck}`. Stations act as bottlenecks when `bottleneck: true`; capacity limits concurrent usage.
- **queue_contention:** Boolean; when true, queue contention and retries are first-class (contention-induced failures and retry paths).
- **retry_policy:** Optional `{max_retries, backoff}` (e.g. exponential) for recovery semantics.
- **failure_dominance:** Optional string `contention` or `scale`; documents the intended failure regime for reporting.

## Fault model

Faults are injectable by the harness. Supported fault types (v0.1):

- **drop_completion:** With probability `drop_completion_prob`, the task does not complete (no task_end); a fault_injected event is emitted. Models tool failure or lost message.
- **delay:** Adds a random delay (e.g. scaled by `delay_p95_ms`) before the next event; optionally inject with `delay_fault_prob`. Emits fault_injected with fault "delay" then continues; models queue contention or network delay.
- **calibration_invalid:** Lab-real fault. With probability `calibration_invalid_prob`, a fault_injected event with fault "calibration_invalid" is emitted before task_end (instrument state invalid; task still completes). Models calibration drift or invalidation. When combined with resource_graph (instrument capacity 1, shared station bottleneck, cleaning/calibration states), fault injection stresses **contention and recovery**, not only drop/delay.

Fault parameters are scenario-specific (e.g. drop_completion_prob, delay_p95_ms, delay_fault_prob). The harness reads scenario YAML and fault config to decide when to inject. Fault sweeps can vary fault type (drop_completion vs delay) and probability.

## Scoring and report

Scoring is standardized: tasks_completed, task_latency_ms_p50/p95/p99, coordination_messages, fault_injected, fault_events, recovery_ok. The scoring library is in `impl` (maestro_report_from_trace); reports conform to MAESTRO_REPORT schema.

## Adapter interface

An adapter runs a scenario and returns (trace, maestro_report) as Python dicts (or writes to a run directory). Interface:

- **run(scenario_id, out_dir, seed, fault_config) -> (trace_dict, report_dict)**  
  or **run(scenario_id, out_dir, **kwargs) -> dict of paths**

At least two reference adapters implement this: centralized (current thin-slice) and blackboard (or event-sourced variant).

## Anti-gaming

Pathological strategies must not rank above legitimate operation. **always_deny** (reject every action) and **always_wait** (never advance) are measured via `scripts/maestro_antigaming_eval.py` and must score worse than legitimate strategies (safety-weighted: tasks_completed 0 or minimal). Results are written to `datasets/runs/maestro_antigaming/antigaming_results.json`. The benchmark penalizes uselessness so that pathological strategies do not rank as best.

**Scoring proof:** Safety-weighted scoring penalizes always_deny and always_wait (they score 0 and 1 tasks_completed; legitimate safe completion scores higher). Unsafe success (e.g. run completes but recovery_ok false or safety violation) is **not** rewarded: the report marks recovery_ok and fault_injected; a run that violates safety would score lower than a legitimate safe run. See antigaming_results.json `conclusion` and `strategies` for the explicit comparison.
