# P1 TeX Draft Recommendations

This memo reviews `papers/P1_Contracts/DRAFT.tex` against the current repository artifact state and proposes changes that would make the paper stronger for peer-review publication.

## 1. Immediate factual corrections

These should be fixed before any stylistic or conceptual revision.

- The draft says the benchmark has `51` sequences. The current artifact run in `datasets/runs/contracts_eval/eval.json` reports `54` sequences.
- The abstract and results say `TP=34, FP=0, FN=0`. The current artifact reports `TP=37, FP=0, FN=0`.
- The abstract says median latency is about `21 us`. The current artifact reports event-level `median=5.0 us`, `p95=12.7 us`, `p99=63.9 us`, with bootstrap CIs.
- The draft compares only four policies, but the checked-in evaluation now includes `occ_only`, `lease_only`, `lock_only`, and `naive_lww` in addition to the original baselines.
- The appendix full-corpus table is stale. It omits the new sequences `concurrent_controller_race`, `cross_key_interleaved_race`, and `delayed_release_reassignment`.
- The transport-parity text should match the actual checked-in artifact. The current `transport_parity.json` shows parity across four canonical sequences and `parity_ok_all=true`.

## 2. Highest-value content upgrades

These are the changes most likely to improve reviewer interest rather than merely fix consistency.

### A. Reframe the paper around a sharper problem

The current draft is correct, but still reads like a clean artifact report. To feel more journal-worthy, it should foreground a sharper thesis:

- Move from "validator over traces" to "a reusable coordination-admission layer for shared CPS state."
- State clearly that the novelty is not ownership checking or timestamp checking individually, but the combination of:
  - keyed authority,
  - temporal admissibility,
  - reason-coded denials,
  - trace-derivability,
  - transport-boundary portability.
- Add one short motivating vignette in the introduction that feels operationally real:
  - controller A releases a unit,
  - controller B acts on stale authority,
  - transport succeeds,
  - coordination still fails,
  - contract boundary denies the write.

### B. Make the comparator story more serious

Reviewers will likely object that the baselines are too weak unless the paper anticipates that objection explicitly.

- Expand the policy comparison section so it discusses all current comparator families:
  - `timestamp_only`,
  - `ownership_only`,
  - `occ_only`,
  - `lease_only`,
  - `lock_only`,
  - `naive_lww`.
- Say directly that some comparators are intentionally reference proxies because the corpus event model does not encode full lease windows, lock acquisition, or OCC read-set semantics.
- Turn that limitation into a strength by emphasizing what the paper is isolating:
  - which semantic ingredients are necessary at the coordination boundary,
  - not whether a full industrial transaction manager was reimplemented.

### C. Upgrade the results from "all green" to "diagnostic evidence"

Perfect scores can look suspiciously easy unless the paper shows how and where weaker approaches fail.

- Add a class-level results table based on `detection_metrics_by_class`.
- Add a concise comparator-decomposition table showing:
  - split-brain is where timestamp/OCC/lease proxies fail,
  - stale/reorder is where ownership/lock proxies fail,
  - unknown-key is where generic accept/temporal-only baselines fail.
- Add one paragraph interpreting why `full_contract` wins structurally, not just numerically.

## 3. Upgrades that make the paper more interesting

These are the recommendations that most increase novelty perception.

### A. Emphasize "coordination validity" as a missing systems layer

Right now the paper reads partly as a validation mechanism. It becomes more interesting if it argues for a missing systems abstraction.

- Introduce the phrase "coordination validity layer" or "coordination-admission layer" and use it consistently.
- Explain that transport decides delivery, storage decides persistence, but coordination contracts decide admissibility of shared-state mutation.
- Tie this explicitly to CPS orchestration, laboratory automation, or multi-controller systems rather than leaving it as a generic distributed-systems claim.

### B. Lean harder into replayability and auditability

This is one of the strongest differentiators and should feel central.

- Add a short subsection or paragraph on why trace-derivability matters in regulated or safety-relevant workflows:
  - post hoc audit,
  - incident reconstruction,
  - reproducible debugging,
  - evidence for assurance cases.
- If possible, include one concrete "deny with reason codes" example in the main text.

### C. Add one formal-strength paragraph

The paper already has a good skeleton for formal reasoning. It would benefit from one step more formal confidence.

- Add a proposition about admitted-prefix invariants:
  - ownership consistency is preserved,
  - last accepted timestamp remains monotone per key.
- Then state clearly which parts are machine-checked today and which remain proof sketches.
- This gives the paper a stronger semantics profile without overclaiming theorem-prover completeness.

## 4. Recommended manuscript structure changes

These changes would improve readability and reviewer reception.

### A. Tighten the abstract

The abstract should do four things faster:

- open with the problem,
- name the core abstraction,
- state the strongest artifact-backed result,
- state scope limits clearly.

A stronger abstract would:

- update all numbers to the current artifact,
- mention the benchmark is `54` sequences,
- mention perfect exact-match verdict agreement,
- mention the decisive comparator margin,
- mention bounded event-level latency with percentile reporting,
- avoid older stale metrics.

### B. Make contributions more concrete

The current contributions are solid, but a journal version should make them more evidence-coupled.

Recommended contribution wording:

- a contract semantics for keyed coordination validity,
- a trace-derived validator and enforcing store,
- a reproducible benchmark with adversarial families and comparator decomposition,
- a transport-boundary mapping and parity demonstration.

### C. Rebuild the results section around questions

Instead of listing outcomes, structure the section as four reviewer-facing questions:

- Does the contract match ground truth on the corpus?
- Which failure classes require both authority and time semantics?
- How weak are simpler policies?
- What does the transport-boundary mapping actually demonstrate?

That structure will make the paper feel less like an artifact dump and more like an argument.

## 5. Tables and figures to add or revise

The current TeX draft is still too sparse visually for a journal submission.

- Keep the validation-flow figure, but make it look like a systems architecture figure rather than a placeholder.
- Replace the current summary table with current metrics from `eval.json`.
- Add a comparator table with all policy families now present in the repo.
- Add a class-level detection table derived from `detection_metrics_by_class`.
- Add a transport-parity mini-table:
  - sequence,
  - event count,
  - parity ok.
- If you run the async stress artifact before submission, add one robustness table summarizing stress profiles and detection retention.

## 6. What to say more carefully

These are likely reviewer pressure points.

- Do not imply that transport parity means real cross-transport deployment equivalence.
- Do not imply that perfect benchmark scores mean field correctness.
- Do not describe `occ_only`, `lease_only`, or `lock_only` as full implementations if they are proxies.
- Do not use the latency number without clarifying it is event-level, trace-driven, and single-process.

## 7. Strong journal-facing narrative angle

If you want the paper to feel more interesting, the strongest narrative is this:

"Coordination Contracts are not another middleware feature. They are a portable semantics layer that makes shared-state mutation auditable, replayable, and denyable under explicit authority and temporal rules."

That framing is stronger than:

"We built a validator that catches some bad writes."

## 8. Concrete next edits I recommend

If you want the fastest path to a stronger submission, do these next:

1. Update `DRAFT.tex` to the current artifact numbers and sequence count.
2. Replace the four-policy comparison with the full comparator suite now in the repo.
3. Add a class-level results table from `detection_metrics_by_class`.
4. Add one motivating real-world CPS handover vignette in the introduction.
5. Add one proposition on admitted-prefix invariants and explicitly connect it to trace-derivability.
6. Tighten the transport claim to "boundary semantic parity," not live transport equivalence.
7. If you plan a stronger submission push, run and include the async stress artifact before finalizing the draft.

## 9. Suggested paper posture

For peer review, the paper should present itself as:

- a systems semantics paper with executable artifact support,
- a coordination-boundary abstraction for CPS,
- a benchmark-backed argument about what simpler policies miss,
- a conservative, auditable contribution with explicit limits.

That posture is both stronger and safer than trying to oversell it as a general distributed-consistency solution.
