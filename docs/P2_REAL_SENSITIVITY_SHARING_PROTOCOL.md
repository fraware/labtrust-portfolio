# P2 Real sensitivity-sharing integration protocol

This document describes how to plug a **real sensitivity-sharing setting** (live shared state from sensors or coordination middleware) into the same REP-CPS `aggregate()` and validator. When a real feed is available, a script can read from it and produce one summary JSON (bias/influence with and without REP-CPS).

## Required event shape

Each update from the live feed must provide (at minimum):

- **variable** (str): Variable name (e.g. `"load"`).
- **value** (float): Numeric value.
- **ts** (float): Timestamp (seconds or ms; consistent with other updates).
- **agent_id** (str): Identity of the reporting agent (for auth_hook and provenance).

Optional: `rate_limit`, `max_age_sec` for windowing (see `impl/src/labtrust_portfolio/rep_cps.py`).

## How to plug in a live feed

1. **Produce a list of updates** in the shape above (e.g. from a message queue, REST poll, or OPC UA subscription).
2. **Filter** with `auth_hook(update, allowed_agents=...)` if using an allow-list.
3. **Call** `aggregate("variable_name", updates, method="trimmed_mean", trim_fraction=0.25)` (or `method="mean"` for naive baseline).
4. **Compare** aggregate output with and without REP-CPS (e.g. robust vs naive, or with/without auth filter) to compute bias and influence.

## Running the same validator

The REP-CPS safety gate does not actuate directly; MADS tier (e.g. Tier 2) is required before actuation. For validation:

- Run the adapter (REPCPSAdapter) with the same scenario/seeds and record `rep_cps_aggregate_load`, `rep_cps_safety_gate_ok`.
- For a **real feed** path: build an adapter or script that (1) reads N updates from the live source, (2) runs `aggregate()` and optionally multi-step aggregation with `aggregation_epsilon`, (3) writes one summary JSON with bias_robust, bias_naive, and (when applicable) steps_to_convergence.

## Deliverable when real feed exists

When a real sensitivity-sharing feed is available:

1. Implement a script that reads from that feed (e.g. `scripts/rep_cps_live_feed_run.py`), produces updates in the required shape, and calls `aggregate()` (and optionally the same multi-step loop as REPCPSAdapter).
2. Write one summary JSON (e.g. `datasets/runs/rep_cps_live/feed_summary.json`) with run_manifest, bias/influence metrics with and without REP-CPS.
3. Add a short subsection in P2 DRAFT and one table row citing the run.
