# P1 — Coordination Contracts

**Coordination Contracts: Typed State, Ownership, and Valid Transitions Above Messaging for Cyber-Physical Systems.**

P1 defines a minimal contract layer (typed state, ownership, valid transitions, temporal semantics) that makes coordination pathologies explicit as invalid state transitions and allows a trace-derived validator to detect and deny them before application. Validation is executable from event traces plus declared configuration alone (no privileged hidden state), with bounded per-write overhead.

- **Draft and claims:** [DRAFT.md](DRAFT.md), [claims.yaml](claims.yaml).
- **Outline and scope:** [AUTHORING_PACKET.md](AUTHORING_PACKET.md).
- **Tables and figures:** [VISUALS_PER_PAPER.md](../docs/VISUALS_PER_PAPER.md), [RESULTS_PER_PAPER.md](../docs/RESULTS_PER_PAPER.md).
- **Corpus:** 51+ sequences (tiered benchmark: micro, meso, stress/adversarial). Benchmark spec: [bench/contracts/BENCHMARK_SPEC.v0.1.md](../../bench/contracts/BENCHMARK_SPEC.v0.1.md).
- **Reproducibility:** Minimal and publishable run instructions are in **Appendix A** of the draft; scripts and run manifests are documented there and in the artifact.
- **LADS and transport parity:** Mock LADS demo: `scripts/contracts_mock_lads_run.py`. Transport-invariance parity: `scripts/contracts_transport_parity.py` writes `transport_parity.json` (same canonical sequence, event-log vs LADS-shaped; parity_ok). The contract surface is transport-agnostic by construction; the paper illustrates with a reference store and LADS-shaped event mapping and does not claim full cross-transport deployment.
- **Run with other papers:** `python scripts/run_paper_experiments.py --paper P1`.
- **Key results:** Corpus detection (51+ sequences, exact per-event verdict match), policy comparison and ablation (contract, timestamp-only, ownership-only, accept-all), ablation_by_class, detection metrics (TP/FP/FN, precision, recall, F1), event-level latency percentiles with bootstrap CI95, resource_and_cost, scale_test and optional scale_sweep; see Section 9 of the draft and eval.json (datasets/runs/contracts_eval) after running the pipeline.
