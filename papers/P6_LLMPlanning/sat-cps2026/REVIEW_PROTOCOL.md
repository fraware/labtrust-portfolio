# SaT-CPS 2026 P6 -- Internal review protocol

No final submission until all three reviews pass.

## Review 1 -- Hostile security reviewer

**Question:** What claims can I falsify in 30 seconds?

**Checks:**
- Overclaiming (elimination, full coverage, guarantee)
- Weak or vague threat model
- Missing security framing (paper reads like an LLM benchmark)
- Unjustified generalization beyond the released suite

**Pass criterion:** Claims are bounded to containment and auditability; threat model is explicit; **path-traversal and denylist-key** real-LLM failures (0/5 in reported OpenAI run) are reported as first-class; OpenAI vs Prime (or other) real-LLM runs are not conflated; no banned words (sufficient, comprehensive, guarantee, eliminate, state-of-the-art, unqualified robust).

---

## Review 2 -- Systems reviewer

**Question:** What mechanism is proposed and what evidence makes it credible?

**Checks:**
- Clarity of architecture (typed-plan firewall, allow-list, safe_args, capture); Figure 1 (decision path) present
- Four evaluation blocks (A--D) clearly tied to claims; Block C includes case study (denial trace)
- Baselines (tool-level and argument-level) honestly framed
- Latency and denial interpretation consistent with artifacts (adapter_latency.json, denial_trace_stats.json, trace metadata denied_steps)

**Pass criterion:** A reader can state the mechanism and point to a table or figure for each main claim; baseline section states what it does and does not prove; optional benign baseline and latency decomposition are described only if cited; experiment roadmap 0--12 extras appear only with matching artifacts.

---

## Review 3 -- ACM production reviewer

**Question:** Will this compile, fit, and pass formatting?

**Checks:**
- Template: acmart sigconf; no manual margin or font overrides
- Page count within 10 pages (including references)
- Author block and affiliations present as required by workshop CFP
- References in .bib; figure readability (PDF/PNG acceptable)
- Only ACM-approved packages

**Pass criterion:** PDF compiles cleanly; page budget respected; author block and CCS/keywords present; figures legible.

---

## Sign-off

| Review | Reviewer | Pass (Y/N) | Date |
|--------|----------|------------|------|
| 1 -- Security | | | |
| 2 -- Systems | | | |
| 3 -- ACM production | | | |

Submission authorized only when all three are Pass.

See SUBMISSION_STANDARD.md and FINAL_CHECKLIST.md.
