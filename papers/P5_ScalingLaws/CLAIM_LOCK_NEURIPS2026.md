# P5 claim lock — NeurIPS 2026 (E&D / evaluation protocol)

This document tiers claims so the submission stays defensible as a **reproducible evaluation protocol and empirical benchmark study**, not as a universal CPS scaling law or a deployment-ready predictor.

## Tier A — headline claims

Allowed in abstract, introduction, results, and conclusion.

- The P5 freeze contains a **7,200-run** grid.
- The grid spans: **six** `real_world` scenario identifiers; **five** coordination regimes; agent counts **{1, 2, 4, 8}**; fault labels **`no_drop`** and **`drop_005`**; **30** random seeds.
- **Coordination tax** (proxy: coordination messages / max(1, tasks completed)) rises sharply as agent count increases (see regime × agent summary and Main Table 1).
- **Throughput** (`tasks_completed`) is often flat or degraded despite more agents (same sources).
- **Scenario-heldout** prediction for `tasks_completed` does **not** beat the strongest admissible **train-only num-tasks bucket** baseline under the main protocol (`trigger_met` is **false**).
- **Family-heldout** prediction **does** trigger (`trigger_met` **true**).
- Under scenario-heldout, the **coordination-tax proxy** is **much more predictable than throughput (`tasks_completed`) or latency-derived error amplification** in the sense of admissible regression MAE and **`trigger_met`** (Main Table 4): tax meets the admissible trigger while **`tasks_completed` does not**; tax regression MAE is far below **error amplification**. Do **not** claim coordination-tax MAE is lower than **`tasks_completed`** MAE without normalizing targets (different scales).
- **Recommendation / regime-selection** artifacts are **exploratory** and **not deployment-ready**.

**Documentation alignment:** `trigger_met` is **protocol-specific** (e.g. leave-one-family-out can be true while leave-one-scenario-out is false because regression fails against the num-tasks bucket baseline).

## Tier B — supporting claims

Allowed in methods and appendix.

- Regression uses a **fixed P5 feature vector**; the predictor is **ridge-stabilized linear regression** when the default vector is long enough (see `impl/src/labtrust_portfolio/scaling.py`).
- Multiple holdout protocols: leave-one-scenario-out, leave-one-family-out, leave-one-regime-out, leave-one-agent-count-out, leave-one-fault-setting-out.
- **Oracle** baselines are reported separately and **never** define trigger semantics.
- **Sensitivity** over seed caps is reported.
- **`scaling_fit`** (log-log exponent / R²) is **exploratory** only.

Strict nulling: if any fold cannot fit regression, protocol-level `overall_regression_mae` is null, `trigger_met` is false, and exports should show N/A with a recorded skip reason (see `scaling_heldout_eval.py`).

## Tier C — exploratory claims

Allowed only in appendix or text explicitly marked **exploratory**.

- Recommendation / regret metrics; regime-selection accuracy; collapse prediction; scaling exponent / log-log fit; error-amplification proxy; any claim grounded primarily in **oracle** per-scenario means.

## Tier D — prohibited claims

Do **not** claim:

- “We establish CPS scaling laws.”
- “The model predicts held-out scenarios robustly.”
- “The recommender selects optimal regimes.”
- “More agents always hurt.”
- “The results generalize to physical plants.”
- “The MAESTRO thin-slice timing is plant MTTR.”
- “Collapse probability is robustly estimated.”
- “Oracle baselines are valid baselines” (for go/no-go).

**Preferred phrasing:** empirical coordination-scaling patterns; thin-slice MAESTRO grid; admissible train-only baseline; scenario-heldout trigger fails; family-heldout trigger succeeds; exploratory recommender; controlled synthetic environment.

## Paper posture (one paragraph)

The strongest defensible statement is: **In a controlled MAESTRO thin-slice grid, coordination tax rises sharply with agent count while throughput often saturates or degrades; however, these empirical regularities do not automatically yield strong held-out prediction under strict admissible baselines.** The failed scenario-heldout trigger is a **methodological core**, not an embarrassment.
