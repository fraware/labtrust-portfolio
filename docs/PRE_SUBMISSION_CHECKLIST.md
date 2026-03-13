# Pre-submission checklist

Use this checklist for each paper immediately before submission (after Phase 3 is done). See [STATE_OF_THE_ART_CRITERIA.md](STATE_OF_THE_ART_CRITERIA.md#3-submission-readiness-phase-3--hostile-reviewer-checklist) for the Phase 3 items; [PAPER_GENERATION_WORKFLOW.md](PAPER_GENERATION_WORKFLOW.md) for regeneration and "Before actual submission."

## 1. Tag a release (optional but recommended)

To provide a citable artifact for reviewers and reproducibility:

1. **Ensure the repo state is clean:** All eval outputs and generated tables/figures you want frozen are committed (or note the exact commit in the supplement).
2. **Choose what to include in the tag:** At minimum: kernel schemas, scripts under `scripts/`, and a frozen dataset slice (e.g. `datasets/releases/` or the run dirs used for the paper's tables). For a single paper, e.g. P0: `kernel/`, `scripts/`, `impl/`, `datasets/releases/p0_e3_release/`, and `profiles/` if needed.
3. **Create an annotated tag:**  
   `git tag -a v0.1-p0-draft -m "P0 draft-complete; kernel + p0_e3_release; repro: see DRAFT.md"`  
   Use a naming scheme that identifies the paper and draft (e.g. `v0.1-p4-draft`, `v0.1-portfolio-draft`).
4. **Document the tag in the paper:** In the Reproducibility or Artifact section, state: "Artifact: clone repo, check out tag `v0.1-pX-draft`; repro commands at top of DRAFT.md."
5. **Push the tag:** `git push origin <tagname>` (when ready).

## 2. Final pass (mandatory)

Run through these for the paper you are submitting:

| Item | Check |
|------|--------|
| **Repro block** | At the top of DRAFT.md, every Table 1, Table 2, … and Figure 0, Figure 1 has an exact command (script name and args). Nothing is "optional" or "run X manually" without a script. Minimal run (under 20 min) is documented. |
| **Claim–evidence** | Every claim in `papers/Px_*/claims.yaml` has `artifact_paths` and at least one `table_id` or `figure_id`. No unsupported claims. |
| **Venue format** | Page limit, reference style (e.g. IEEE, ACM), author guidelines, and anonymization (if required) are satisfied. Shorten or adapt text/figures as needed. |
| **Run manifest** | For every table/figure that reports means or CIs, the draft or summary JSON states seeds, scenario, and fault settings. See [REPORTING_STANDARD.md](REPORTING_STANDARD.md). |

## 3. Publishable seeds

For any table or figure that will appear in the submitted PDF:

- Evals were run with 20 seeds (or the script's publishable default).
- Export/plot scripts were re-run and DRAFT.md numbers match the generated output.
- Run manifest is stated in the draft or in the summary JSON referenced by the draft.

Commands per paper: [PAPER_GENERATION_WORKFLOW.md — Quick reference](PAPER_GENERATION_WORKFLOW.md#quick-reference-commands-per-paper). Regenerate all artifacts for that paper with `python scripts/generate_paper_artifacts.py --paper Px`, then paste from `papers/Px_*/generated_tables.md` into DRAFT.md if needed.

## 4. After submission

- Update [PORTFOLIO_BOARD.md](../PORTFOLIO_BOARD.md): set the paper's Next action to "Submitted to &lt;venue&gt;" or similar.
- If you created a tag, keep it pushed so reviewers can use it.
