# CPS-MAESTRO: Standardized Evaluation of Thousand-Agent CPS Coordination Under Faults, Tail Latency, and Cost

**Paper ID:** P4_CPS-MAESTRO  
**Stage target (board):** Spec → MVP → Eval → Draft  
**Kernel dependency:** must reference kernel schemas by version; breaking changes require version bump.

## 1) Thesis (one paragraph)
Make coordination measurable and comparable via a benchmark suite with fault injection, scenario adapters, scoring, and variance-aware reporting, optimized for CPS constraints and auditable outputs.

## 2) Claims (citable, falsifiable)
- Without a shared evaluation substrate, coordination claims remain incomparable; MAESTRO supplies a practical yardstick.
- Tail latency, recovery curves, and coordination tax are first-class metrics for CPS, not afterthoughts.
- Variance and repeated trials are required; single-run demos are scientifically weak for agentic CPS.

## 3) Outline (high-level)
1. Problem framing and scope boundary (what this paper is / is not)
2. Core object (spec / protocol / trace / benchmark / model) and formal definitions
3. Implementation surface (schemas, validators, harness)
4. Evaluation plan (what evidence would convince a skeptic)
5. Limitations and explicit non-goals
6. Relationship to the portfolio (how it plugs into MADS-CPS / MAESTRO / Replay)

## 4) Experiment plan (minimum credible)
- Repeated trials (N≥30) for each architecture in 1–2 scenarios; report p50/p95/p99 + variance + MTTR.
- Ablations: fault injection on/off; safety gate on/off; measure coordination tax deltas.

## 5) Artifact checklist (must ship)
- Scenario spec format (bench/maestro/scenarios/*.yaml) + adapters interface
- Scoring/report schema (kernel/eval/MAESTRO_REPORT.v0.1.schema.json → expand)
- Fault injection harness (drop/delay/Byzantine tool output baselines)
- Reference baselines: centralized scheduler vs blackboard vs hybrid (incremental).

## 6) Kill criteria (stop early if true)
- If scenarios are too bespoke and cannot be adapted to other systems, benchmark won’t be adopted.
- If metrics are unstable or easy to game, MAESTRO becomes noise.
- If harness is too heavy to run, adoption collapses—must stay ‘thin’ and modular.

## 7) Target venues (initial)
arXiv (cs.RO, cs.AI, cs.SE); benchmarking/evaluation workshops; later robotics systems venue.

## 8) Integration contract (portfolio coherence)
- Output artifacts must validate against kernel schemas (or propose a versioned extension).
- All evaluations must be reproducible from `datasets/` with a release manifest and evidence bundle.
- Do not duplicate scope owned by other papers; cite and depend on them.
