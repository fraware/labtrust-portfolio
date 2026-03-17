# SaT-CPS 2026 P6 -- Final acceptance checklist

Paper is ready for submission only when all items are true.

- [ ] **Title** sounds like a CPS security paper (e.g. secure or auditable runtime enforcement for tool invocation).
- [ ] **Abstract** contains main numbers (9/9 synthetic; real-LLM: gpt-4.1-mini 55/65, gpt-4.1 55/65; Wilson CI [73.9, 91.4]) and the main failures (path-traversal 0/5 and denylist-key 0/5 for both models).
- [ ] **Introduction** defines the trust boundary early (planner output untrusted until firewall admits it).
- [ ] **Threat model** has explicit assets, adversarial leverage, trust assumptions, and non-goals (and table).
- [ ] **Synthetic suite** is clearly primary validator evidence (Block A): 9 red-team, 4 confusable deputy, 2 jailbreak-style.
- [ ] **Real-LLM section** includes denominator, CI, and failure-case analysis (Block B): gpt-4.1-mini 55/65 (84.6%), gpt-4.1 55/65 (84.6%); path-traversal 0/5 and denylist-key 0/5 both reported.
- [ ] **Block C** includes adapter latency and the denial-trace case study (e.g. execute_system denied, captured for audit).
- [ ] **Figure 1** is the decision path (planner output -> allow-list -> safe_args -> capture -> allow/deny); regenerate with export_p6_firewall_flow.py.
- [ ] **Baseline section** explicitly states what it does and does not prove (tool-level and argument-level) (Block D).
- [ ] **Discussion** says "containment" and never "elimination"; no banned words.
- [ ] **Paper** is in ACM proceedings format and within the 10-page cap.
- [ ] **Author names and affiliations** are present as requested by the workshop CFP.

After submission, run Review 1--3 from REVIEW_PROTOCOL.md and record sign-off.

See SUBMISSION_STANDARD.md (five axes, page budget) and EXPERIMENTS_RUNBOOK.md (artifacts).

