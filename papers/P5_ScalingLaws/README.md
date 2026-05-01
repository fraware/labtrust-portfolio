# P5 — When More Agents Hurt (coordination scaling & held-out evaluation)

P5 measures **empirical coordination-scaling patterns** across agent count and coordination regime in MAESTRO thin-slice runs, and tests **leakage-aware** predictors under multiple held-out protocols. **We do not establish a general scaling law**; log-log `scaling_fit` and recommendation metrics are **exploratory**.

Normative claim tiers: **`CLAIM_LOCK_NEURIPS2026.md`**. Submission bundle index: **`neurips2026/README.md`**.

## P5 reviewer quick path

This paper studies coordination-scaling and held-out prediction over a frozen MAESTRO thin-slice grid.

Headline evidence:

- **7,200** runs
- Six **`real_world`** scenario identifiers
- Five coordination regimes
- Agent counts **1, 2, 4, 8**
- Fault labels **`no_drop`** and **`drop_005`**
- **30** seeds

Canonical reproduction:

```bash
PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel \
  python scripts/run_paper_experiments.py --paper P5
```

Main artifacts:

- `datasets/runs/scaling_eval/heldout_results.json`
- `datasets/runs/scaling_eval_family/heldout_results.json`
- `datasets/runs/scaling_summary/regime_agent_summary.json`
- `datasets/runs/sensitivity_sweep/scaling_sensitivity.json`
- `papers/P5_ScalingLaws/generated_tables.md`

Important interpretation:

- Scenario-heldout **`trigger_met` is false** vs the admissible num-tasks bucket baseline (mixed / negative result is central).
- Family-heldout **`trigger_met` is true**.
- Recommendation artifacts are **exploratory** (`claim_status` in `recommendation_eval.json`); **not deployment-ready** architecture selection.
- **`scaling_fit`** is **exploratory** (scaling-law-style diagnostic).
- **No physical deployment** or plant MTTR claim.

Claim-source gate: `python scripts/check_p5_claim_sources.py`

## One command

`PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/run_paper_experiments.py --paper P5`

- **`--quick`:** small seed count, `core` scenarios, `--p5-lite` coordination grid (CI smoke).
- **Default (publishable):** 30 seeds, `real_world` scenarios (six ids; no `toy_lab_v0`), **all** `VALID_REGIMES` × **{1,2,4,8}** agents, fault labels **`no_drop`** and **`drop_005`** only (runtime bound), `--clean` on the multiscenario output directory.

After a full run, headline metrics and the Git commit recorded in each `heldout_results.json` `run_manifest.commit` must match `DRAFT.md`, `AUTHORING_PACKET.md`, and the HTML comment atop `generated_tables.md` (regenerate tables with `export_scaling_tables.py` so the comment updates).

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
| `scaling_recommend/recommendation_eval.json` | LOFO recommendation metrics + `claim_status` |
| `papers/P5_ScalingLaws/generated_tables.md` | Script-exported Main Tables 1–4 + appendix |
| `papers/P5_ScalingLaws/p5_artifact_hashes.txt` | Repo-relative SHA256 manifest for `datasets/runs/` (depth ≤2); refresh via `scripts/hash_p5_artifacts.py` |
| `papers/P5_ScalingLaws/regime_agent_summary.md` | Human-readable companion to the JSON summary |
| `papers/P5_ScalingLaws/CLAIM_LOCK_NEURIPS2026.md` | Tiered claims for submission |
| `papers/P5_ScalingLaws/CLAIM_SOURCE_MAP.md` | Path → table mapping |
| `papers/P5_ScalingLaws/FINAL_REPRO_LOG.md` | Reproduction checklist |
| `docs/figures/p5_fig*.png` | Paper figures |

## Trigger semantics

`success_criteria_met.trigger_met` uses **admissible** baselines only (global mean, num-tasks bucket, regime train mean — not oracle per-scenario means).

**Strict protocol rule:** if any fold has `regression_mae = null`, that protocol’s `overall_regression_mae` is `null` and `trigger_met` is **false**.

Full spec: `docs/P5_SCALING_SPEC.md`. Baseline discipline: `docs/P5_BASELINE_DISCIPLINE.md`. Coordination-tax proxy: `docs/P5_COORDINATION_TAX_PROXY.md`. Authoring checklist: `papers/P5_ScalingLaws/AUTHORING_PACKET.md`.
