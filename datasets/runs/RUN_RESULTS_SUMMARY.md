# P4 MAESTRO publishable run summary

Canonical frozen copy: `datasets/releases/p4_publishable_v1/` (mirrors the evidence cited in `papers/P4_CPS-MAESTRO/claims.yaml`).

## Parameters

- **MAESTRO_REPORT schema**: v0.2 (`kernel/eval/MAESTRO_REPORT.v0.2.schema.json`)
- **Seeds per sweep cell**: 20 (seeds 1..20)
- **Scenarios in fault sweep**: `toy_lab_v0`, `lab_profile_v0`, `warehouse_v0`, `traffic_v0`, `regime_stress_v0`
- **Fault settings**: `no_drop`, `drop_005`, `drop_02`, `delay_01`, `drop_005_delay_01`, `calibration_invalid_01`, `recovery_stress_aux` (see `multi_sweep.json` `run_manifest`)
- **Baselines**: `Centralized`, `Blackboard`, `RetryHeavy`, `NoRecovery`, `ConservativeSafeShutdown` on `toy_lab_v0`, regimes `fault_free` and `drop_0_2` (drop_completion_prob=0.2)

## Primary artifacts

| Artifact | Path |
|----------|------|
| Fault sweep bundle | `datasets/runs/maestro_fault_sweep/multi_sweep.json` |
| Anti-gaming | `datasets/runs/maestro_antigaming/antigaming_results.json` |
| Baseline JSON | `bench/maestro/baseline_summary.json` |
| Baseline markdown | `bench/maestro/baseline_results.md` |
| Exported paper tables | `papers/P4_CPS-MAESTRO/generated_tables.md` |
| Recovery figure | `docs/figures/p4_recovery_curve.png` |
| Safety figure | `docs/figures/p4_safety_violations.png` |
| Efficiency figure | `docs/figures/p4_efficiency_messages.png` |
| Metric semantics | `bench/maestro/RECOVERY_AND_SAFETY_METRICS.md` |
| Scoring | `bench/maestro/SCORING.md` |

Regenerate: `PYTHONPATH=impl/src` then `python scripts/maestro_fault_sweep.py`, `python scripts/maestro_baselines.py`, `python scripts/maestro_antigaming_eval.py`, `python scripts/export_maestro_tables.py --out papers/P4_CPS-MAESTRO/generated_tables.md`, `python scripts/plot_maestro_recovery.py`.
