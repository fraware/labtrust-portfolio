# Portfolio Board (source-of-truth)

This file is the canonical, repo-native portfolio board. Mirror to GitHub Projects if desired, but treat **this** as truth.

## Stages (exactly five)
- **Spec** — scoped, non-overlapping thesis + artifacts named in kernel; explicit kill criteria
- **MVP** — minimal runnable implementation; validates against kernel schemas
- **Eval** — credible experiments; repeated trials; variance reported; ablations if relevant
- **Draft** — paper draft is coherent; figures/tables reproducible from `datasets/`
- **Kill** — stop or merge: thesis weak, overlap too high, eval infeasible, or adoption dead-end

## Paper cards (IDs are stable)
| ID | Paper | Owner | Stage | Next action |
|---:|---|---|---|---|
| P0 | MADS-CPS (normative minimum bar) | TBD | Spec | Freeze scope; write “what is normative” section |
| P1 | Coordination Contracts | TBD | Spec | Contract schema + 2–3 failure classes |
| P2 | REP-CPS Profile | TBD | Spec | Threat model + profile draft |
| P3 | Deterministic Replay | TBD | MVP | Thin-slice replay equivalence + nondet detection |
| P4 | CPS-MAESTRO Benchmark | TBD | MVP | Scenario adapter + score report v0.1 |
| P5 | Scaling Laws (coordination tax) | TBD | Spec | Define task feature vector + data plan |
| P6 | LLM Planning (typed plans + validators) | TBD | Spec | Plan schema + validator harness |
| P7 | Standards Mapping (assurance pack) | TBD | Spec | Template mapping + one instantiation |
| P8 | Meta-Coordination (regime switching) | TBD | Spec | Switching criteria + safety conditions |

## Rules of coherence
1) Kernel schema IDs and versions are the only stable interfaces across papers.
2) MAESTRO + Replay are the default “release train”: every other paper either produces artifacts compatible with them or consumes their datasets.
3) Any paper that cannot define **kill criteria** is not ready to leave Spec.
