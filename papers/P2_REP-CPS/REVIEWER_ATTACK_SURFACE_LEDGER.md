# P2 REP-CPS — Reviewer attack surface ledger

Maps each reviewer challenge to the mitigation path (manuscript vs experiment vs both). Baseline: `DRAFT.md`, `claims.yaml`, `rep_cps_eval.py`, `summary.json`, `generated_tables.md`.

| Attack / weakness | Mitigation | Location |
|-------------------|------------|----------|
| Why sensitivity sharing if tasks are equal? | Necessity vignette + explicit conditional sentence in abstract; **trigger scenario** `rep_cps_scheduling_v0` where gate-closed policies yield zero scheduling completions vs robust REP | DRAFT §1, Abstract; `bench/maestro/scenarios/rep_cps_scheduling_v0.yaml`; adapter + thinslice |
| Novelty collapses to hygiene | Subsection: novelty is assurance **profile** (composition + informational semantics + gate + harness), not a new estimator; Related Work fences | DRAFT Related Work + Discussion |
| Synthetic harness only | Limitations + threat→evidence table; optional **messaging_sim** and explicit out-of-scope rows; future work | DRAFT §3, Limitations; `summary.json` `messaging_sim` |
| Offline vs in-loop confusion | Dedicated **Two evaluation modes** paragraph; Results cross-ref before Table 1/2 | DRAFT §5 |
| Threat model broader than evidence | Split: exercised / partial / out of scope; claim-to-threat alignment | DRAFT §3; `claims.yaml`; `summary.json` `threat_evidence` |
| Deployable vague | Operational definition paragraph tied to C1 and Table 5 | DRAFT; claims |
| Rate limit underplayed | Narrative + C2 evidence to Table 6; ablation | DRAFT Results |
| Safety-gate value | Paragraph: throughput unchanged elsewhere but gate blocks unsafe effective control; campaign table | DRAFT §5 |
| Robust aggregation delta modest | Frame as directional + envelope + ablation; no overclaim | DRAFT Discussion |
| Construct validity (hand-crafted harness) | Honest scope + MAESTRO alignment + threat_evidence rows | DRAFT; eval |

## Success criteria (eval)

- `adapter_parity`: REP-CPS vs Centralized **mean tasks_completed** match on runs where `scenario_id` is not a `rep_cps_scheduling_dependent` scenario (toy_lab_v0, lab_profile_v0).
- `scheduling_trigger_outcome`: On `rep_cps_scheduling_v0`, mean REP tasks exceeds mean naive-in-loop tasks (spoofed-update stress).
- Conditional **full** trigger (material influence on all scenarios): still not claimed unless extended; see `docs/CONDITIONAL_TRIGGERS.md`.
