# When More Agents Hurt: Predicting Coordination Tax and Error Amplification in Cyber-Physical Workflows

**Paper ID:** P5_ScalingLaws  
**Stage target (board):** Spec → MVP → Eval → Draft  
**Kernel dependency:** must reference kernel schemas by version; breaking changes require version bump.

## 1) Thesis (one paragraph)
Empirically model coordination overhead and error amplification in CPS, using task-feature predictors (decomposability, sequential depth, tool density, physical coupling, deadline tightness) to guide architecture selection.

## 2) Claims (citable, falsifiable)
- Coordination tax is predictable from measurable task features; architecture choice can be made decision-usable.
- Error amplification and recovery probability degrade nonlinearly with scale and coupling; ignoring this yields ‘safe but unusable’ systems.
- Scaling analysis must be tied to reproducible benchmark data (MAESTRO) and replayable traces.

## 3) Outline (high-level)
1. Problem framing and scope boundary (what this paper is / is not)
2. Core object (spec / protocol / trace / benchmark / model) and formal definitions
3. Implementation surface (schemas, validators, harness)
4. Evaluation plan (what evidence would convince a skeptic)
5. Limitations and explicit non-goals
6. Relationship to the portfolio (how it plugs into MADS-CPS / MAESTRO / Replay)

## 4) Experiment plan (minimum credible)
- Generate runs across multiple scenarios and agent counts; fit models; evaluate on held-out scenarios.
- Compare architecture A/B/C selection predicted vs observed outcomes; quantify regret.

## 5) Artifact checklist (must ship)
- Task feature schema (new kernel schema in v0.2, or paper-local appendix initially)
- Dataset builder consuming MAESTRO runs to produce feature→outcome table
- Baseline predictive models (GLM/GBDT) + ablation scripts
- Published run manifests for reproducibility.

## 6) Kill criteria (stop early if true)
- If task features do not predict outcomes beyond trivial baselines, contribution weak.
- If dataset size is insufficient for stable inference, delay paper until MAESTRO matures.
- If results are too scenario-specific, re-scope to a narrower claim.

## 7) Target venues (initial)
arXiv (cs.RO, cs.AI, cs.LG); ML-for-systems / robotics evaluation workshops.

## 8) Integration contract (portfolio coherence)
- Output artifacts must validate against kernel schemas (or propose a versioned extension).
- All evaluations must be reproducible from `datasets/` with a release manifest and evidence bundle.
- Do not duplicate scope owned by other papers; cite and depend on them.
