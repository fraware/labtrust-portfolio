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

Faults are injectable by the harness. **Core** fault types (YAML + thin-slice):

- **drop_completion**, **delay**, **calibration_invalid** (see parameters on `run_thin_slice`).

**Extended** injectors (thin-slice harness; surfaced in `recovery_stress_aux` sweep rows and/or lab-heavy paths) include at least: **timeout**, **partial_result**, **reordered_event**, **resource_contention_spike**, **invalid_action_injection**, **agent_nonresponse** (worker stall), **duplicate_completion**, **conflicting_action**, **constraint_guard_trigger** (lab disposition), **sensor_stale** / stale reads, **deadline_miss** (synthetic). Lab-profile runs additionally model disposition / PONR-adjacent risk via explicit `ponr_violation` and `unsafe_task_completion` markers when guards fire.

Fault parameters are scenario-specific and sweep-specific. See `datasets/runs/maestro_fault_sweep/multi_sweep.json` `run_manifest.fault_params` for the frozen publishable grid.

## Scoring and report

Scoring is standardized in **MAESTRO_REPORT v0.2**: throughput, latency tails, coordination efficiency, recovery timing, explicit safety counters, `run_outcome`, and structured `safety_violation_types`. Implemented in `impl/src/labtrust_portfolio/maestro.py` (`maestro_report_from_trace`). Semantics: `bench/maestro/RECOVERY_AND_SAFETY_METRICS.md`. Composite ranking / anti-gaming: `bench/maestro/SCORING.md`.

## Adapter interface

An adapter runs a scenario and returns (trace, maestro_report) as Python dicts (or writes to a run directory). Interface:

- **run(scenario_id, out_dir, seed, fault_config) -> (trace_dict, report_dict)**  
  or **run(scenario_id, out_dir, **kwargs) -> dict of paths**

At least two reference adapters implement this: centralized (current thin-slice) and blackboard (or event-sourced variant).

## Anti-gaming

Pathological strategies must not rank above legitimate operation. **always_deny** (reject every action) and **always_wait** (never advance) are measured via `scripts/maestro_antigaming_eval.py` and must score worse than legitimate strategies (safety-weighted: tasks_completed 0 or minimal). Results are written to `datasets/runs/maestro_antigaming/antigaming_results.json`. The benchmark penalizes uselessness so that pathological strategies do not rank as best.

**Scoring proof:** Safety-weighted scoring penalizes always_deny and always_wait (they score 0 and 1 tasks_completed; legitimate safe completion scores higher). Unsafe success (e.g. run completes but recovery_ok false or safety violation) is **not** rewarded: the report marks recovery_ok and fault_injected; a run that violates safety would score lower than a legitimate safe run. See antigaming_results.json `conclusion` and `strategies` for the explicit comparison.
