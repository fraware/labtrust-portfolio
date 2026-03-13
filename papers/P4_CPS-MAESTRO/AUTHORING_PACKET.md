# CPS-MAESTRO: Benchmark + Fault Injection Suite for CPS-Grade Agent Coordination

**Paper ID:** P4_CPS-MAESTRO  
**Tag:** core-kernel  
**Board path:** MVP → Eval → Draft  
**Kernel ownership:** evaluation kernel (scenario specs, fault models, scoring, report format)

## 1) One-line question
How do we make CPS coordination **measurable and comparable** under tail latency, faults, recovery behavior, and operational cost—especially for autonomous labs?

## 2) Scope anchors (ADePT-aligned realism)
- Autonomous labs are not primarily “thousand-agent” problems; they are **heterogeneous device + robot + station** systems with recovery and drift.
- MAESTRO must model: drift/calibration invalidation, insertion failures, queue contention, partial observability, and recovery sequences.

## 3) Claims
- **C1:** Standard scenarios + fault models + scoring produce stable, comparable measurements across coordination architectures.
- **C2:** Variance is first-class: repeated runs and tail reporting are mandatory.
- **C3:** Adapter interface makes adoption tractable across centralized/blackboard/hybrid stacks.
- **C4:** The suite is usable by third parties: docs + CI + reference baselines.

## 4) Outline
1. Motivation: why coordination benchmarking fails (variance, hidden assumptions, missing faults)
2. Scenario spec (lab/warehouse/traffic micro-world)
3. Fault injection model (network/tool/agent/world)
4. Scoring and reporting (p95/p99, MTTR, coordination tax, safety violations)
5. Adapter interface + reference implementations
6. Reproducibility protocol and dataset format
7. Baseline results + ablations

## 5) Experiment plan
- Scenarios (minimum):
  - lab profile micro-world (resource graph + PONRs + recovery),
  - warehouse micro-world,
  - traffic micro-intersection.
- Fault sweeps:
  - drift/calibration invalidation,
  - tool timeouts/partial results,
  - queue contention,
  - delay/drop/reorder,
  - compromised agent behavior.
- Metrics:
  - p95/p99 latency, throughput, success, safety violations, MTTR,
  - coordination messages per completed task,
  - operational overhead proxies.
- Baselines:
  - centralized scheduler,
  - blackboard/event-sourced,
  - market allocation,
  - swarm fallback.

## 6) Artifact checklist
- scenario definitions + fault injection harness
- `kernel/eval/MAESTRO_REPORT.v0.1.schema.json`
- scoring library + standardized JSON reports
- adapter interface + 2–4 reference adapters
- dataset release scripts + reproducibility README

## 7) Kill criteria
- **K1:** results are unstable run-to-run due to underspecification.
- **K2:** adapters become bespoke and expensive for each method.
- **K3:** If scoring is gameable without improving real robustness/safety, revise scoring.
- **K4:** If MAESTRO can be "won" by pathological strategies (always_deny, always_wait, or unsafe success), revise **scoring** until it cannot; document in SCENARIO_SPEC and anti-gaming section. Scoring is safety-weighted so unsafe success does not yield high scores.

## 8) Target venues
- ICRA/IROS/RSS (benchmark + CPS relevance)
- DSN (dependability benchmarking)
- arXiv first (cs.RO, cs.SE)

## 9) Integration contract
- MAESTRO is the **release train** producing datasets used by scaling laws and validating LLM/REP/meta modules.
- Must emit traces compatible with Replay and evidence bundles compatible with MADS.

