# SaT-CPS 2026 submission standard (P6)

The paper will be judged on five axes. **No sentence survives unless it helps one of these five.**

1. **Venue fit:** The paper must clearly land in SaT-CPS topics: secure CPS architectures, access control, availability/recovery/auditing, formal security methods, medical CPS, and LLMs for trustworthy CPS.

2. **Security framing:** Reviewers should come away thinking "runtime enforcement architecture for CPS control-plane security," not "another LLM benchmarking paper."

3. **Empirical credibility:** Every claim must be backed by a table, figure, or artifact already measured. **Primary evidence:** Table 1 (15 red-team + 6 confusable deputy + 4 jailbreak-style synthetic suite), Figure 1 (decision path), Block C (adapter latency + denial trace case study), Block D (tool-level and argument-level baselines). **Canonical real-LLM (Table 1b):** OpenAI `gpt-4.1-mini` and `gpt-4.1`, `--real-llm-suite full`, report both case count and denominator from run_manifest. **Current camera-ready snapshot (`llm_eval_camera_ready_20260424`):** N=3 runs/case, 25 cases/model, each model 75/75 (100.0%, Wilson [95.1, 100.0]). **Optional:** Prime Inference four-model matrix (different N and denominator) only if clearly labeled as a separate run; see EXPERIMENTS_RUNBOOK.md. **Extended experiments** (concurrency, storage, adaptive suite, etc.) require the matching `p6_*.json` artifact before they appear in the main text.

4. **Failure honesty:** Report failure modes or boundary conditions explicitly for the run you cite (for example, argument-level cases, parse failures, or model-specific drift). Keep historical snapshots clearly labeled when discussing prior runs with different denominators.

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
- Appendix: ideally none, or at most a tiny claim-to-evidence map plus a reproducibility table (artifact hash, model_id, timestamp_iso, evaluator_version, policy_version, prompt_template_hash) from `export_p6_reproducibility_table.py`

Anything not essential to acceptance moves out: long reproduction blocks, internal process notes, raw JSON dumps, meta-discussion about caution. If artifact hashes are lengthy, use supplementary material and keep a one-row summary in the PDF.

## Related documents

- **ROLES.md** -- Four owners and lanes.
- **EXPERIMENTS_RUNBOOK.md** -- Commands and artifact locations; real-LLM run manually.
- **REVIEW_PROTOCOL.md** -- Three internal reviews before submission.
- **FINAL_CHECKLIST.md** -- Acceptance checklist.
