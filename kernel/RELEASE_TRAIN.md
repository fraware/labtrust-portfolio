# Release train contracts

The **release train** is the default evaluation and audit path for the portfolio. Two kernel artifacts are its stable contracts; backward-incompatible changes require a schema version bump.

## Contracts

- **TRACE** (`kernel/trace/TRACE.v0.1.schema.json`) — Execution trace format. Captures events, state hashes, and metadata so that replay and evaluation can reproduce control-plane behavior.
- **MAESTRO_REPORT** (`kernel/eval/MAESTRO_REPORT.v0.1.schema.json`) — Benchmark evaluation report. Standard metrics (latency percentiles, tasks completed, coordination messages, faults) so that runs are comparable across coordination architectures.

## Consumers

Papers that consume TRACE and/or MAESTRO_REPORT:

- **P0 (MADS-CPS):** Evidence admissibility; conformance checks; replay link (verifier recomputes MAESTRO from TRACE).
- **P3 (Replay):** Trace format and replay semantics; MAESTRO consumed from trace.
- **P4 (CPS-MAESTRO):** Owns the evaluation kernel and produces MAESTRO reports.
- **P5 (Scaling laws):** Consumes MAESTRO datasets for modeling.
- **P6 (LLM Planning):** Evaluated on MAESTRO scenarios.
- **P7 (Standards mapping):** Trace and report artifacts feed assurance packs.
- **P8 (Meta-coordination):** Evaluation on MAESTRO fault mixtures.

## Stability

- Do not change TRACE or MAESTRO_REPORT in a backward-incompatible way without bumping the schema version (e.g. `v0.1` → `v0.2`) and updating this document.
- The thin-slice pipeline and all dataset releases produce artifacts that validate against these schemas.
