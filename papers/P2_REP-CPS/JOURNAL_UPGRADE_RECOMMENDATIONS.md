# P2 REP-CPS Journal Upgrade Recommendations

This document is a recommendation suite for strengthening the latest TeX draft of `REP-CPS: A Safety-Gated Profile for Authenticated Sensitivity Sharing in Cyber-Physical Coordination` for peer-reviewed journal submission.

The goal is not to make the paper sound larger than the evidence supports. The goal is to make it more interesting, more differentiated, and more publication-ready while preserving the current honest scope.

## Executive assessment

The current draft has a strong honesty profile, a clear systems instinct, and a credible artifact story. Its main weakness is not clarity. Its main weakness is perceived significance.

Right now, a skeptical reviewer can summarize the paper as:

- "This is a well-engineered profile and harness."
- "The authors show reduced bias in the aggregate."
- "But the main task-level metric often does not change."

That is a solid workshop or artifact-strength contribution, but it is not yet maximally compelling as a journal paper unless the manuscript does more than report bounded behavior. To become more interesting, the paper should do one or more of the following:

1. Make a stronger scientific object explicit.
2. Show a sharper trigger scenario where protocol discipline changes downstream outcomes.
3. Elevate the contribution from "profile + harness" to "design methodology + assurance case + reproducible evaluation pattern."
4. Produce a richer explanation of when sensitivity sharing matters, when it does not, and why.

The best path is not to abandon the current framing. The best path is to upgrade it from a careful negative/conditional paper into a high-value journal paper about disciplined informational control in CPS.

## Core diagnosis

### What is already good

- The paper is unusually honest about what is and is not demonstrated.
- The profile is concrete rather than vague: typing, freshness, rate limits, provenance, auth hooks, robust aggregation family, safety gate.
- The artifact already supports more than the draft currently exploits: `rep_cps_scheduling_v0`, `per_scenario`, `excellence_metrics`, threat micro-evidence, latency, ablation, resilience envelope.
- The "informational-only until gated" semantics is a real conceptual contribution if the paper leans into it harder.

### What currently limits journal interest

- The central empirical headline is still defensive: "bounded behavior without task-level improvement."
- The draft reads as if it is trying to preempt reviewer attacks rather than define a memorable positive idea.
- The contribution list is operationally correct, but it does not yet crystallize a reusable design pattern for the field.
- The evaluation is strong on robustness slices but still underexploits "when does this actually matter?" as the main scientific question.
- The discussion and future work imply a more interesting paper than the current results section fully delivers.

## Recommended strategic repositioning

The paper becomes substantially more interesting if you reposition it around one primary thesis.

### Recommended primary thesis

`Sensitivity sharing is a hidden control surface in CPS, and therefore must be treated as a profiled, safety-gated informational subsystem rather than as ordinary telemetry.`

This is stronger and more memorable than:

- "we define a profile"
- "we reduce bias under compromise"
- "we built a harness"

Those are still contributions, but they should support the thesis rather than act as the thesis.

### Better journal framing

The paper should read as answering this question:

`How should CPS designers safely admit, aggregate, and operationalize decentralized informational signals that are not commands but can still affect mission behavior?`

That question is journal-worthy because it sits between:

- distributed robustness,
- runtime assurance,
- systems architecture,
- and safety-critical integration.

### Positioning statement to make explicit

The paper is not about inventing a better estimator. It is about identifying and formalizing a neglected systems object: `decision-relevant informational state`.

That phrase, or a close variant, should appear prominently.

## Highest-impact recommendations

## 1. Make the paper about an under-theorized systems object

Add a short subsection in the introduction or problem setting titled:

`Decision-relevant informational state`

Define it as signals that:

- are not commands,
- are not purely passive logs,
- can influence scheduling, admission, triage, or actuation,
- and therefore deserve explicit admissibility and safety semantics.

Why this helps:

- It makes the paper conceptually richer.
- It gives reviewers a reason to cite the paper even if they do not adopt REP-CPS exactly.
- It lifts the work above "one more robust aggregation profile."

Suggested one-sentence formulation:

`We argue that decentralized sensitivity variables are neither control commands nor harmless telemetry; they form decision-relevant informational state whose admission and downstream effect must be governed explicitly.`

## 2. Promote the scheduling-dependent scenario from supporting evidence to centerpiece evidence

The repo already contains `rep_cps_scheduling_v0` and `scheduling_dependent_eval`. The current TeX draft still sounds like the trigger is broadly unmet. That is no longer the strongest available framing.

Recommended refinement:

- Say that the trigger is not met in the two baseline parity scenarios.
- Then say it is partially met in the scheduling-dependent scenario, where aggregate quality changes downstream scheduling behavior under spoof stress.

This must be described carefully, but it gives the paper a much stronger narrative:

- non-scheduling scenarios show profile discipline without throughput penalty,
- scheduling scenario shows when the informational path actually matters,
- together they reveal the boundary between "harmless telemetry" and "decision-relevant informational state."

Why this helps:

- It turns the paper from a mostly negative result into a scoped positive result.
- It makes the conditional framing more sophisticated rather than weaker.
- It creates a stronger "when it matters" contribution.

## 3. Add explicit research questions and answer them

Journal papers benefit from explicit RQs. The current draft has claims, but not clear research questions.

Recommended RQs:

- `RQ1:` Can a profiled sensitivity-sharing path bound compromised influence without imposing material overhead?
- `RQ2:` Which profile controls matter most: authentication, freshness, rate limiting, robust aggregation, or safety gating?
- `RQ3:` Under what architectural conditions does sensitivity sharing become task-relevant rather than merely informational?
- `RQ4:` How should such a protocol be evaluated so that negative and conditional outcomes remain scientifically useful?

Then answer each RQ directly in the discussion or conclusion.

Why this helps:

- It gives reviewers a cleaner structure.
- It makes the paper feel more like a mature journal article than a polished artifact report.

## 4. Add a "when it matters / when it does not" section

This paper can be more interesting than a standard positive-results paper if it explicitly theorizes boundary conditions.

Add a section or subsection:

`When sensitivity sharing changes outcomes`

Include a compact table with columns like:

- Architecture condition
- Does scheduler/admission read aggregate?
- Expected effect of compromised informational state
- What REP-CPS can and cannot improve

Example rows:

- Aggregate not consumed by scheduler: parity expected.
- Aggregate consumed only through gate: denial behavior matters more than throughput.
- Aggregate consumed for scheduling/admission: task divergence possible and meaningful.

Why this helps:

- It converts an apparent weakness into a generalizable insight.
- It gives the paper pedagogical value for system designers.

## 5. Add a stronger figure zero

The paper needs a visually memorable systems figure before the tables.

Recommended Figure 0:

`Informational path to gated operational effect`

Flow:

- local agent state
- typed sensitivity update
- admissibility surface
- aggregation family
- informational state
- safety gate
- downstream scheduler/admission/action

Also mark attack points:

- spoofing,
- replay,
- burst influence,
- compromised values.

Why this helps:

- It makes the contribution legible at a glance.
- It differentiates the work from pure aggregation papers.

## Experimental upgrades that would materially increase interest

## 6. Strengthen the main positive empirical story around `rep_cps_scheduling_v0`

The strongest next-step experiment is not another generic robustness sweep. It is a better causal story around the scheduling scenario.

Add a dedicated subsection:

`Scheduling-dependent evaluation`

Show:

- REP-CPS robust in-loop results,
- naive in-loop results,
- unsecured results,
- centralized baseline,
- gate pass/deny rates,
- resulting task completion or task denial outcomes,
- per-scenario statistics only for `rep_cps_scheduling_v0`.

If possible, add:

- confidence intervals,
- paired comparisons,
- effect size between REP-CPS and naive-in-loop on the scheduling scenario.

Why this helps:

- Reviewers want the operational consequence, not only the aggregate distortion.
- This is the single best path from "careful systems profile" to "compelling scoped systems result."

## 7. Add a threshold-sweep or gate-sensitivity experiment

Right now the gate is important architecturally, but the paper could show much more about it empirically.

Recommended experiment:

- sweep the gate threshold over a reasonable range,
- report pass/deny curves for REP-CPS, naive, and unsecured,
- measure how threshold choice changes downstream behavior.

This creates an important journal-level result:

`The impact of protocol discipline is not binary; it depends on where the operational gate is set relative to attack-induced distortion.`

Suggested outputs:

- ROC-like gate sensitivity curve,
- denial rate versus threshold,
- task completion versus threshold for scheduling scenario,
- threshold region where naive fails but REP-CPS passes.

Why this helps:

- It makes the gate a first-class systems mechanism rather than an architectural comment.

## 8. Add temporal behavior as a primary result, not an optional artifact note

The draft currently downplays multi-step behavior. That is understandable, but journals often value temporal behavior more than one-shot snapshots.

Recommended addition:

- promote `dynamic_aggregation_series` into the main results,
- show recovery/stability after a compromised burst,
- compare settling or drift of robust versus naive aggregation over multiple steps.

Questions to answer:

- How long does distortion persist?
- Does rate limiting shorten recovery?
- Does freshness protect against repeated stale influence?

Possible metrics:

- max deviation over time,
- time-to-return within epsilon of honest aggregate,
- cumulative distortion area under curve,
- gate-denial duration.

Why this helps:

- CPS reviewers care about dynamics, not just point estimates.
- It makes the work feel more "cyber-physical" and less "static message processing."

## 9. Add comparator families that make the baseline suite feel harder to beat

The current baselines are good but still somewhat easy for a reviewer to dismiss as insufficiently strong.

Recommended additional comparators:

- median,
- winsorized mean,
- clipped mean,
- exponentially weighted moving average with admissibility,
- simple anomaly-rejection heuristic baseline,
- thresholded "last known good" baseline.

Important note:

You do not need all of these in the final journal version. Even two stronger comparator classes would help.

Why this helps:

- It makes the evaluation feel less tailored.
- It shifts the question from "does robust beat naive?" to "which discipline package is most defensible for CPS?"

## 10. Add a deployment-oriented stress study

To improve journal appeal, add one section that asks:

`What happens when communication and operational faults coexist?`

Recommended matrix:

- delay sweep,
- optional drop sweep,
- spoofing or compromised updates,
- scheduler dependence on aggregate,
- gate threshold variants.

Then present:

- per-scenario outcomes,
- per-fault outcomes,
- most failure-inducing combinations,
- most protective profile components.

Why this helps:

- It creates a more realistic systems narrative.
- It shows the paper is not just about one fault family.

## Manuscript-level recommendations

## 11. Rewrite the abstract to carry a stronger positive hook

The current abstract is honest but too defensive too early.

Better abstract arc:

1. Sensitivity sharing is a hidden control surface.
2. REP-CPS defines a disciplined profile for it.
3. The profile couples admissibility, aggregation, and gate semantics.
4. Evaluation identifies when sensitivity sharing is operationally inert and when it becomes decision-relevant.
5. Results: reduced distortion, bounded overhead, gate-mediated denial, scoped scheduling effect.
6. Contribution: a reusable design and evaluation methodology for informational control surfaces in CPS.

Do not remove the limitation statement. Move it later in the abstract after the positive contribution is clear.

## 12. Tighten the contribution list

The current contribution list is correct but too implementation-shaped.

A stronger journal version would read more like:

1. A conceptualization of `decision-relevant informational state` in CPS.
2. A deployment profile that couples admissibility, bounded aggregation, and gate-mediated semantics.
3. A reproducible evaluation methodology distinguishing offline robustness, in-loop bounded behavior, and scheduling-dependent operational effect.
4. Evidence that profile controls interact non-trivially, with rate limits and authentication materially affecting robustness beyond estimator choice alone.

Then implementation details can appear underneath each contribution.

## 13. Add a threat-to-control-to-evidence table

This should appear in the main paper, not only in supplementary documentation.

Recommended columns:

- Threat
- Control in profile
- How exercised in artifact
- Metric / table / figure
- Residual limitation

Example threats:

- spoofing,
- sybil-style multiplicity,
- stale/replayed updates,
- burst influence,
- compromised extreme values,
- unsafe downstream dependence.

Why this helps:

- It makes the paper look systematic.
- It reduces reviewer friction.
- It visually demonstrates construct validity.

## 14. Add a design principles subsection

Journal readers often remember design principles better than mechanisms.

Recommended principles:

- `P1: Informational state is not harmless if it can shape action.`
- `P2: Admission controls are part of semantics, not preprocessing.`
- `P3: Aggregation robustness is insufficient without provenance and rate control.`
- `P4: Operational effect must be mediated explicitly.`
- `P5: Evaluation must distinguish informational robustness from mission impact.`

Why this helps:

- It turns the paper into something other researchers can reuse.

## 15. Make the limitations section more analytically valuable

The limitations section is already honest, but it can do more scholarly work.

Instead of only listing weaknesses, structure it as:

- what the evidence establishes,
- what it does not establish,
- what experiment or deployment step would close each gap.

That makes the paper look like a disciplined research program rather than a scoped prototype.

## Title and framing recommendations

## 16. Consider a title that emphasizes the broader idea

The current title is good but can be made more journal-memorable.

Possible alternatives:

- `REP-CPS: Safety-Gated Sensitivity Sharing as a Profiled Informational Control Surface in Cyber-Physical Systems`
- `Profiling Decision-Relevant Informational State in Cyber-Physical Coordination: The REP-CPS Approach`
- `Safety-Gated Sensitivity Sharing for Cyber-Physical Coordination: A Profile and Evaluation Methodology`

If you want to stay conservative, keep the current title but change the subtitle language throughout the paper to emphasize informational control surfaces.

## 17. Add explicit novelty bullets near the end of related work

End the related work section with three bullets:

- Not a new estimator.
- Not a new runtime assurance theorem.
- New in the composition of admissibility, bounded aggregation, and explicit gated semantics for decision-relevant informational state.

This is already latent in the draft. Make it explicit and crisp.

## Recommended new sections or subsections

If you are willing to expand the manuscript, add the following:

### A. Decision-relevant informational state

Purpose:

- define the conceptual object,
- motivate why telemetry-like signals can become safety-relevant.

### B. Architectural conditions for operational effect

Purpose:

- explain why some scenarios show parity and others show divergence,
- make the conditionality scientifically informative.

### C. Threat-to-control-to-evidence matrix

Purpose:

- unify the threat model and empirical evidence.

### D. Scheduling-dependent evaluation

Purpose:

- make the strongest operational slice easy to find.

### E. Deployment guidance

Purpose:

- tell practitioners when REP-CPS is appropriate,
- what assumptions must hold,
- which controls are non-negotiable.

## Recommended new tables and figures

## Tables

### Table A. Threat-control-evidence matrix

This should become a centerpiece table.

### Table B. Per-scenario summary

Separate:

- `toy_lab_v0`
- `lab_profile_v0`
- `rep_cps_scheduling_v0`

Show:

- tasks completed,
- aggregate load,
- gate denials,
- key comparison stats.

### Table C. Profile-control importance

Use the ablation to explicitly rank which controls matter most.

Possible columns:

- Control removed
- Aggregate distortion
- Gate impact
- Operational implication

### Table D. Comparator table

If additional aggregators are tested, summarize robustness and overhead.

## Figures

### Figure 0. Informational path and gate semantics

Architectural overview with attack points.

### Figure 3. Scheduling-dependent effect

Show the operational slice where naive and robust differ.

### Figure 4. Gate threshold sensitivity

If implemented, this could become one of the paper's most publishable figures.

### Figure 5. Dynamic aggregation and recovery

Time series under burst or stale/replay conditions.

## Journal-specific recommendations

## 18. Make the paper useful even to readers who do not adopt REP-CPS

A strong journal paper leaves behind something portable.

The most portable outputs here are:

- a conceptual vocabulary,
- a design checklist,
- an evaluation methodology,
- and a threat-to-control reasoning pattern.

Add a boxed checklist or compact list:

`Checklist for deploying sensitivity sharing in CPS`

Possible items:

- typed variable semantics,
- sender identity assumptions,
- freshness policy,
- rate limit policy,
- admissible aggregator family,
- gate semantics,
- traceability requirements,
- threshold calibration method,
- negative-case testing.

## 19. Add a reproducibility and auditability paragraph that sounds journal-grade

The artifact story is already good. Present it not only as code availability but as auditability infrastructure.

Frame it as:

- fixed manifest,
- machine-readable outputs,
- claim-to-evidence mapping,
- scenario-level disaggregation,
- statistical comparison block,
- denial traces for unsafe operational dependence.

This reads stronger in journals than a generic "code is available" paragraph.

## 20. Explicitly separate three evidence layers

One of the cleanest upgrades would be to organize evidence into:

- `Layer 1: Offline robustness of aggregate estimation`
- `Layer 2: In-loop bounded behavior and safety gating`
- `Layer 3: Scheduling-dependent operational effect`

This provides a much better intellectual architecture for the results section.

## Concrete rewrite recommendations by section

## Introduction

Change the opening emphasis from "naive deployment is unsafe" to:

`CPS increasingly relies on informational signals that are not commands but still shape operational decisions.`

Then show why this creates a neglected assurance problem.

## Scope and conditional trigger

Refine the language so it does not undersell `rep_cps_scheduling_v0`.

Better structure:

- broad trigger is not universally met,
- scoped trigger is partially met in scheduling-dependent evaluation,
- therefore the paper provides both bounded general evidence and a scoped operational demonstration.

## Problem setting

Add one paragraph explaining why informational state differs from both control commands and passive monitoring.

## Profile model

Add a short "design rationale" paragraph after each formal subsection:

- why typing matters,
- why rate control is semantic rather than merely defensive,
- why gating is external to the estimator.

## Results

Reorganize into:

1. `Offline robustness`
2. `Which controls matter`
3. `In-loop bounded behavior`
4. `Scheduling-dependent operational effect`
5. `Overhead and deployment implications`

This will read as a scientific progression rather than a list of artifact outputs.

## Discussion

End with a stronger takeaway:

`The paper's broader claim is that informational coordination channels in CPS must be treated as governed interfaces, not informal side channels.`

## A prioritized implementation plan

If the goal is to maximize journal strength efficiently, the best order is:

### Tier 1: Must do

- Reframe around decision-relevant informational state.
- Promote `rep_cps_scheduling_v0` and `scheduling_dependent_eval`.
- Add explicit RQs.
- Add per-scenario table in the main paper.
- Add a threat-control-evidence table.
- Rework the abstract and introduction so the positive thesis appears before the limitations.

### Tier 2: Strongly recommended

- Add gate threshold sensitivity study.
- Promote dynamic/multi-step behavior into the main results.
- Add 1-2 stronger comparator baselines beyond naive mean.
- Add Figure 0 for the architecture and attack points.

### Tier 3: Excellent if feasible

- Add a live messaging or OPC UA-aligned integration slice.
- Add a deployment checklist subsection.
- Add a formal proposition about bounded influence under explicit identity and rate assumptions.
- Add a practitioner-oriented case study vignette.

## Suggested paper archetype

If you want the paper to feel more journal-ready, write it as a hybrid of three archetypes:

- a systems architecture paper,
- a runtime assurance integration paper,
- and an empirical methodology paper.

Do not write it primarily as a robust aggregation paper. That is the least distinctive framing available to you.

## Bottom line

The paper becomes substantially more interesting if it is presented not as:

`Here is a profile that behaves better under compromise.`

but as:

`Here is how CPS should govern decision-relevant informational state, how that governance can be evaluated reproducibly, and when it actually changes downstream behavior.`

That framing is already latent in the repo and in the current artifact set. The strongest upgrade is to make the manuscript fully reflect it.
