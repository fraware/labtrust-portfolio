# NeurIPS 2026 — P5 submission bundle index

This folder is the **submission-facing index** for paper **P5_ScalingLaws** (evaluation protocol + empirical coordination-scaling benchmark). Normative claim tiers and reproduction steps live alongside it under `papers/P5_ScalingLaws/`.

## Core documents (parent directory)

| File | Purpose |
|------|---------|
| `../CLAIM_LOCK_NEURIPS2026.md` | Tier A–D claims; prohibited language |
| `../CLAIM_SOURCE_MAP.md` | Human-readable canonical paths + table mapping |
| `../claim_sources.yaml` | Machine-readable claim sources for CI checker |
| `../FINAL_REPRO_LOG.md` | Validation + P5 pipeline + hash instructions |
| `../generated_tables.md` | Regenerated Main Tables 1–4 + appendix |
| `../DRAFT.md` | Paper draft (must respect claim lock) |

## Optional LaTeX fragments

After regeneration, run (from repo root):

```bash
PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel \
python scripts/export_scaling_tables.py \
  --out papers/P5_ScalingLaws/generated_tables.md \
  --out-tex-dir papers/P5_ScalingLaws/neurips2026/tables_tex
```

Outputs:

- `tables_tex/main_tables_booktabs.tex` — Main Tables 1–4 with `booktabs` (`\usepackage{booktabs}` in the paper preamble).
- Parent `generated_tables.md` — markdown mirror for the draft and reviewers.

## Interpretation (reviewer one-liner)

Empirical coordination-scaling patterns on a **frozen 7,200-row** MAESTRO thin-slice grid; **scenario-heldout** trigger is **false** vs the admissible num-tasks bucket baseline; **family-heldout** trigger is **true**; recommendation and log-log **`scaling_fit`** are **exploratory** only.
