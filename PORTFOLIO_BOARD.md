# Portfolio Board (source-of-truth)

This file is the canonical, repo-native portfolio board. Mirror to GitHub Projects if desired, but treat **this** as truth.

**Current state:** All nine papers (P0–P8) are at **Draft** stage. Phase 3 (submission-readiness) checklist passed 2025-03-11 for each; see `papers/Px_*/PHASE3_PASSED.md`. Next step for each: submission prep (tag release, final pass, venue format) per [docs/PRE_SUBMISSION_CHECKLIST.md](docs/PRE_SUBMISSION_CHECKLIST.md). Eval summary JSONs include optional `excellence_metrics`; run `python scripts/export_excellence_summary.py` to print a summary. Strengthened experiments and known limitations: [docs/EXPERIMENTS_AND_LIMITATIONS.md](docs/EXPERIMENTS_AND_LIMITATIONS.md); plan: [docs/PLAN_STRENGTHEN_EXPERIMENTS.md](docs/PLAN_STRENGTHEN_EXPERIMENTS.md).

## Stages (exactly five)
- **Spec** — scoped, non-overlapping thesis + artifacts named in kernel; explicit kill criteria
- **MVP** — minimal runnable implementation; validates against kernel schemas
- **Eval** — credible experiments; repeated trials; variance reported; ablations if relevant
- **Draft** — paper draft is coherent; figures/tables reproducible from `datasets/`. Gate: see [Draft conversion checklist](docs/STATE_OF_THE_ART_CRITERIA.md#21-portfolio-wide-draft-conversion-checklist) (claim table, evidence mapping, two tables + one figure, limitations, repro block at top).
- **Kill** — stop or merge: thesis weak, overlap too high, eval infeasible, or adoption dead-end

## Paper cards (IDs are stable)

Tags:
- **core-kernel**: minimum kernel for ADePT-style unmanned labs
- **conditional**: only worth building if trigger criteria are met

Paper owners are TBD unless set in the board.

| ID | Paper | Tag | Owner | Stage | Next action |
|---:|---|---|---|---|---|
| P0 | MADS-CPS (normative minimum bar) | core-kernel | TBD | Draft | Phase 3 passed (2025-03-11). Submission prep; venue adaptation. |
| P1 | Coordination Contracts | core-kernel | TBD | Draft | Phase 3 passed (2025-03-11). Submission prep; venue adaptation. |
| P2 | REP-CPS Profile | conditional | TBD | Draft | Phase 3 passed (2025-03-11). Submission prep; venue adaptation. |
| P3 | Replay levels + nondeterminism detection | core-kernel | TBD | Draft | Phase 3 passed (2025-03-11). Submission prep; venue adaptation. |
| P4 | CPS-MAESTRO Benchmark | core-kernel | TBD | Draft | Phase 3 passed (2025-03-11). Submission prep; venue adaptation. |
| P5 | Scaling Laws (coordination tax) | conditional | TBD | Draft | Phase 3 passed (2025-03-11). Submission prep; venue adaptation. |
| P6 | LLM Planning (typed plans + validators) | conditional | TBD | Draft | Phase 3 passed (2025-03-11). Submission prep; venue adaptation. |
| P7 | Standards Mapping (assurance pack) | core-kernel | TBD | Draft | Phase 3 passed (2025-03-11). Submission prep; venue adaptation. |
| P8 | Meta-Coordination (regime switching) | conditional | TBD | Draft | Phase 3 passed (2025-03-11). Submission prep; venue adaptation. |

## Trigger criteria for conditional modules
- **P2 REP-CPS**: only if sensitivity sharing materially influences scheduling/actuation under partial/compromised information.
- **P5 Scaling laws**: only if MAESTRO datasets cover multiple scenario families and beat trivial baselines out-of-sample.
- **P6 LLM planning**: only if an LLM is in the control plane OR if typed-plan firewalls/validators are needed as a general containment pattern.
- **P8 Meta-coordination**: only if multiple coordination regimes are deployed and mode-thrashing/collapse appears under fault mixtures.

## Reference organism
One canonical scenario is the portfolio anchor: **lab_profile_v0** (`bench/maestro/scenarios/lab_profile_v0.yaml`). Every paper touches it at least once (instantiation or eval). Primary scaling anchor: resource graphs, campaign concurrency, heterogeneity, fault recovery (not "thousand agents" by default).

## Rules of coherence
1) Kernel schema IDs and versions are the only stable interfaces across papers.
2) MAESTRO + Replay are the default “release train”: every other paper either produces artifacts compatible with them or consumes their datasets.
3) Any paper that cannot define **kill criteria** is not ready to leave Spec.
4) Do not claim “public openness” as a requirement; default is **restricted auditability** with redaction hooks.
5) Do not claim “full determinism on hardware”; claim **replay levels + nondeterminism detection**.

**Submission readiness:** Before marking a paper Draft-complete or submitting, run the Phase 3 / hostile reviewer checklist in [docs/STATE_OF_THE_ART_CRITERIA.md](docs/STATE_OF_THE_ART_CRITERIA.md) section 3 (claim-evidence matrix, repro under 20 min, variance rules, no kernel redefinition, overclaim check, repro block lists every script).

Cross-cutting docs: [docs/INTEGRATION_CONTRACTS.md](docs/INTEGRATION_CONTRACTS.md), [docs/CONDITIONAL_TRIGGERS.md](docs/CONDITIONAL_TRIGGERS.md), [docs/VALIDATING_A_RUN.md](docs/VALIDATING_A_RUN.md), [docs/STATE_OF_THE_ART_CRITERIA.md](docs/STATE_OF_THE_ART_CRITERIA.md), [docs/DRAFT_CONVERSION_CHECKLIST.md](docs/DRAFT_CONVERSION_CHECKLIST.md), [docs/PAPER_BY_PAPER_NEXT_STEPS_PLAN.md](docs/PAPER_BY_PAPER_NEXT_STEPS_PLAN.md) (implementation roadmap), [docs/EVALS_RUNBOOK.md](docs/EVALS_RUNBOOK.md), [docs/EVAL_RESULTS_INTERPRETATION.md](docs/EVAL_RESULTS_INTERPRETATION.md). **Before submit:** [docs/PRE_SUBMISSION_CHECKLIST.md](docs/PRE_SUBMISSION_CHECKLIST.md) (tag release, final pass, venue format). **Excellence tier:** [docs/STANDARDS_OF_EXCELLENCE.md](docs/STANDARDS_OF_EXCELLENCE.md) (optional metrics per paper and portfolio-wide).

