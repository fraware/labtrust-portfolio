# P2 REP-CPS: Trigger decision

**Trigger:** Proceed only if sensitivity sharing materially influences scheduling/actuation in the target architecture (lab/warehouse/traffic) and therefore becomes safety/security relevant.

**Current status (scoped):** **Partially demonstrated in-eval:** Scenario **rep_cps_scheduling_v0** links **safety-gate outcome** to thin-slice scheduling (withhold `task_end` when gate denies). Under **duplicate-sender spoof** stress, **naive in-loop mean** typically exceeds the gate threshold and yields **zero** completions; **REP-CPS (trimmed mean)** stays below threshold and preserves completions—see `summary.json` **`scheduling_dependent_eval`**. On **toy_lab_v0** and **lab_profile_v0**, the scheduler does not consume REP aggregate, so **tasks_completed** remains parity with centralized. **Full operational trigger** (real lab scheduler, warehouse/traffic, live messaging) is **not** claimed.

**Implemented:** Profile spec, REP_CPS_PROFILE schema, `rep_cps.py` (`aggregate`, `auth_hook`, `compromised_updates`, `sensitivity_spoof_duplicate_sender_update`), **rep_cps_scheduling_v0.yaml**, thinslice `rep_cps_safety_gate_ok` + `scheduling_denied_rep_cps_gate`, REPCPSAdapter (aggregation-first path for scheduling scenarios), CentralizedAdapter (gate forced open for scheduling baseline), **rep_cps_eval.py** (default third scenario, `freshness_replay_evidence`, `sybil_vs_spoofing_evidence`, `messaging_sim`, `dynamic_aggregation_series`, scoped `success_criteria_met`), export/plot scripts, tests. Publishable default: 20 seeds, **toy_lab_v0, lab_profile_v0, rep_cps_scheduling_v0**, delay sweep.

**Dependencies:** P1 (Contracts), P3 (Replay), P4 (MAESTRO) must be in place. REP-CPS reuses Contracts typed state and Replay/MAESTRO harnesses.
