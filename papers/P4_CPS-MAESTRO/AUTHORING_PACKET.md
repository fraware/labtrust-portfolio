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

## 5) Experiment plan (implemented vs aspirational)
- **Implemented scenarios:** lab-first `toy_lab_v0`, `lab_profile_v0` (resource graph + disposition risk path); auxiliary `warehouse_v0`, `traffic_v0`; `regime_stress_v0` (and `regime_stress_v1` exists for P8 cross-links).
- **Implemented fault sweeps:** drop/delay/calibration_invalid grid plus `recovery_stress_aux` (timeout, partial_result, invalid_action, agent_nonresponse, sensor_stale, resource spikes, etc.) documented in `SCENARIO_SPEC.md` and `multi_sweep.json` `run_manifest`.
- **Implemented metrics:** MAESTRO_REPORT v0.2 fields per `RECOVERY_AND_SAFETY_METRICS.md` (recovery times, safety structure, coordination efficiency, `run_outcome`).
- **Implemented baselines:** Centralized, Blackboard (parameterization), RetryHeavy, NoRecovery, ConservativeSafeShutdown with fault-free and `drop_0_2` regimes.
- **Not claimed here:** market allocation, swarm fallback, compromised-agent red-team beyond scripted fault injectors, real OPC-UA plant loops.

## 6) Artifact checklist
- scenario definitions + fault injection harness
- `kernel/eval/MAESTRO_REPORT.v0.2.schema.json` (publishable); v0.1 retained for legacy
- scoring library + standardized JSON reports
- adapter interface + 2–4 reference adapters
- dataset release scripts + reproducibility README
- frozen rerun bundle in `datasets/releases/p4_publishable_v1/` with 20-seed evidence (refreshed 2026-04-20)

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

