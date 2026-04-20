# P5 — When More Agents Hurt (coordination scaling)

P5 measures how **agent count** and **coordination regime** change MAESTRO thin-slice coordination load and throughput, and tests **leakage-aware** predictors under multiple held-out protocols.

## One command

`PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/run_paper_experiments.py --paper P5`

- **`--quick`:** small seed count, `core` scenarios, `--p5-lite` coordination grid (CI smoke).
- **Default (publishable):** 30 seeds, `real_world` scenarios, **all** `VALID_REGIMES` × **{1,2,4,8}** agents, fault labels **`no_drop`** and **`drop_005`** only (runtime bound), `--clean` on the multiscenario output directory.

## Artifacts (under `datasets/runs/` unless noted)

| Path | Role |
|------|------|
| `multiscenario_runs/` | Raw traces (7200 runs in publishable mode) |
| `scaling_eval/heldout_results.json` | Scenario LOO |
| `scaling_eval_family/heldout_results.json` | Family LOO |
| `scaling_eval_regime/heldout_results.json` | Regime LOO |
| `scaling_eval_agent_count/heldout_results.json` | Agent-count LOO |
| `scaling_eval_fault/heldout_results.json` | Fault-label LOO |
| `scaling_summary/regime_agent_summary.json` | Frozen regime × agent empirical summary (track with `git add -f` if needed) |
| `sensitivity_sweep/scaling_sensitivity.json` | Seed caps 10 / 20 / 30 |
| `scaling_recommend/recommendation_eval.json` | LOFO recommendation metrics |
| `papers/P5_ScalingLaws/generated_tables.md` | Script-exported tables |
| `papers/P5_ScalingLaws/regime_agent_summary.md` | Human-readable companion to the JSON summary |
| `docs/figures/p5_fig*.png` | Paper figures |

## Trigger semantics

`success_criteria_met.trigger_met` uses **admissible** baselines only (global mean, num-tasks bucket, regime train mean — not oracle per-scenario means).

**Strict protocol rule:** if any fold has `regression_mae = null`, that protocol’s `overall_regression_mae` is `null` and `trigger_met` is **false**.

Full spec: `docs/P5_SCALING_SPEC.md`. Authoring checklist: `papers/P5_ScalingLaws/AUTHORING_PACKET.md`.
