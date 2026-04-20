# MAESTRO Benchmark Release v0.1

This file defines the canonical scenario set for the MAESTRO benchmark release v0.1.

**Scenario set:** toy_lab_v0, lab_profile_v0, warehouse_v0, traffic_v0, regime_stress_v0.

These five scenarios form the v0.1 benchmark set. **Framing (P4):** lab scenarios (`toy_lab_v0`, `lab_profile_v0`, `regime_stress_v0`) carry the strongest lab-first semantics; `warehouse_v0` and `traffic_v0` are small auxiliary micro-scenarios for cross-domain smoke, not full-domain CPS benchmarks. For held-out evaluation and train/val/test usage, see P5 (scaling_heldout_eval), which uses a leave-one-scenario-out protocol.

The machine-readable list is in `benchmark_scenarios.v0.1.json`.
