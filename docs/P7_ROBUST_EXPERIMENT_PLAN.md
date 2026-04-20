# P7 Robust Experiment Plan (State-of-the-Art Upgrade)

## Objective

Strengthen `P7_StandardsMapping` from a single worked example to a broad, mechanically checkable evidence package that supports claims under multi-domain and stressed conditions.

## Claim-to-Experiment Mapping

- `C1` (traceable structure): validate assurance-pack structure and mapping completeness with explicit schema and hazard-control-evidence checks.
- `C2` (mechanically checkable): run scripted review over a large matrix and quantify pass/failure rates, not only narrative examples.
- `C3` (worked example and replayability): extend worked examples beyond lab to domain-proxy scenarios (`warehouse_v0`, `traffic_v0`) and report aggregate replayability outcomes.

## Experiment Matrix

- **Scenarios:** `toy_lab_v0`, `lab_profile_v0`, `warehouse_v0`, `traffic_v0`
- **Profiles:** `lab_v0.1`, `warehouse_v0.1`, `medical_v0.1` (scenario-mapped)
- **Fault regimes:**
  - `nominal`
  - `delay_spike`
  - `drop_stress`
  - `calibration_noise`
  - `composite`
- **Seeds:** default `1..20` (portfolio submission bar for publishable tables; override with `--seeds` only with justification)

Total default runs: `4 scenarios x 5 regimes x 20 seeds = 400`.

## Metrics

- Mapping-level:
  - `mapping_check.ok`
  - `mapping_check.ponr_coverage_ok`
- Review-level:
  - `review_exit_ok`
  - `evidence_bundle_ok`
  - `trace_ok`
  - `ponr_coverage_ratio`
  - `control_coverage_ratio`
- Operational:
  - `task_latency_ms_p95` (from MAESTRO report)
- Real-world proxy:
  - pass-rate restricted to `warehouse_v0` and `traffic_v0`

## Success Criteria

- `mapping_check.ok = true`
- `evidence_bundle_ok_rate = 1.0`
- `trace_ok_rate = 1.0`
- `review_pass_rate >= 0.95` in full matrix
- `real_world_proxy.review_pass_rate >= 0.95`

## Execution

```bash
PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel \
  python scripts/run_assurance_eval.py --out datasets/runs/assurance_eval
PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel \
  python scripts/run_assurance_robust_eval.py --out datasets/runs/assurance_eval
# Default robust seeds are 1..20. Override only with an explicit methodological note.
python scripts/export_assurance_tables.py --results datasets/runs/assurance_eval/robust_results.json
```

Primary artifact outputs:

- `datasets/runs/assurance_eval/results.json`
- `datasets/runs/assurance_eval/robust_results.json`

## Reporting Guidance

- Use `results.json` for baseline submission tables.
- Use `robust_results.json` for robustness appendix and claim-strengthening discussion.
- Keep explicit non-claim text: this is a traceability and audit-support framework, not a certification claim.
