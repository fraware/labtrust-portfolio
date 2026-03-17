# SaT-CPS 2026 submission standard (P6)

The paper will be judged on five axes. **No sentence survives unless it helps one of these five.**

1. **Venue fit:** The paper must clearly land in SaT-CPS topics: secure CPS architectures, access control, availability/recovery/auditing, formal security methods, medical CPS, and LLMs for trustworthy CPS.

2. **Security framing:** Reviewers should come away thinking "runtime enforcement architecture for CPS control-plane security," not "another LLM benchmarking paper."

3. **Empirical credibility:** Every claim must be backed by a table, figure, or artifact already measured. Primary evidence: Table 1 (9 red-team + 4 confusable deputy + jailbreak-style), Figure 1 (decision path), Block C case study (denial trace), baselines.

4. **Failure honesty:** The path-traversal real-LLM failure (0/5 for gpt-4.1-mini and gpt-4.1) is an asset, not a weakness to hide.

5. **Format discipline:** ACM proceedings style, named authors, 10-page cap respected.

## Banned words

Unless explicitly justified, do not use: **sufficient**, **comprehensive**, **guarantee**, **eliminate**, **state-of-the-art**, or **robust** (without a scoped object). One pass over the draft to remove or replace them before submission.

## Page budget (10 pages total including references)

- Title/abstract: 0.5 page
- Introduction: 1 page
- Related work: 0.75 page
- System overview: 1 page
- Threat model + experimental design: 1 page
- Results: 2.5--3 pages
- Discussion + limitations: 1 page
- Conclusion: 0.25 page
- References: remainder
- Appendix: ideally none, or at most a tiny claim-to-evidence map

Anything not essential to acceptance moves out: long reproduction blocks, internal process notes, extended artifact hash tables, meta-discussion about caution. Compress early.

## Related documents

- **ROLES.md** -- Four owners and lanes.
- **EXPERIMENTS_RUNBOOK.md** -- Commands and artifact locations; real-LLM run manually.
- **REVIEW_PROTOCOL.md** -- Three internal reviews before submission.
- **FINAL_CHECKLIST.md** -- Acceptance checklist.
