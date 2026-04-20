# P3 — Replay Levels and Nondeterminism Detection

P3 defines replay levels (L0/L1/L2) and nondeterminism detection for agentic CPS, framed for **AI security and CPS assurance**: L0 replay as a **machine-checkable assurance primitive** for control-plane evidence (contracts, localization, diagnostics, evidence bundles)—not generic debugging and not “hashing logs.”

The reference eval is `scripts/replay_eval.py`, which writes **`datasets/runs/replay_eval/summary.json`** with `schema_version: p3_replay_eval_v0.2` (full L0 overhead, baselines, multi-seed thin-slice family, **multi-point** `overhead_curve`, corpus outcomes with localization and **corpus_category**, **`corpus_space_summary`**, **`l1_twin_summary`** when `--l1-twin` including **`real_ingest_traces`** for a second L1 evaluation family).

## Read first

| File | Purpose |
|------|---------|
| [DRAFT.md](DRAFT.md) | Repro block, evaluation narrative, limitations (Markdown companion) |
| [DRAFT.tex](DRAFT.tex) | Submission LaTeX (numbers must match frozen `summary.json`) |
| [claims.yaml](claims.yaml) | Claim-to-evidence mapping |
| [generated_tables.md](generated_tables.md) | Exported tables from frozen summary |
| [AUTHORING_PACKET.md](AUTHORING_PACKET.md) | Scope, venues, experiment plan |
| [COMPILE.md](COMPILE.md) | LaTeX build (TeX Live / MiKTeX) |
| [l1_twin_evidence.md](l1_twin_evidence.md) | L1 cross-family (seeds + real_ingest) |
| [LOCALIZATION_FIGURE_SPEC.md](LOCALIZATION_FIGURE_SPEC.md) | First-divergence timeline figure |
| [PHASE3_PASSED.md](PHASE3_PASSED.md) | Submission checklist status |

## Canonical publishable pipeline

From repo root (`PYTHONPATH=impl/src`, `LABTRUST_KERNEL_DIR=kernel`):

```bash
python scripts/replay_eval.py \
  --out datasets/runs/replay_eval/summary.json \
  --overhead-curve --overhead-runs 20 \
  --thin-slice-seeds 42,43,44,45,46 \
  --bootstrap-reps 500 --l1-twin
python scripts/plot_replay_overhead.py
python scripts/export_replay_corpus_table.py --out-md papers/P3_Replay/generated_tables.md
PYTHONPATH=impl/src python scripts/export_p3_paper_figures.py
python scripts/verify_p3_replay_summary.py --strict-curve
```

**Scripts (detail):** `export_replay_corpus_table.py` (Table 1 + 1b + L1 sections); **`export_p3_paper_figures.py`** (camera-ready PNGs under `papers/P3_Replay/figures/`); `verify_p3_replay_summary.py` (schema + optional figure sidecar match; strict curve requires ≥2 overhead points).

**Cross-links:** [VISUALS_PER_PAPER.md](../../docs/VISUALS_PER_PAPER.md), [RESULTS_PER_PAPER.md](../../docs/RESULTS_PER_PAPER.md), [EVALS_RUNBOOK.md](../../docs/EVALS_RUNBOOK.md), [bench/replay/README.md](../../bench/replay/README.md), [P3_REAL_TRACE_INGESTION.md](../../docs/P3_REAL_TRACE_INGESTION.md), real-ingest note [bench/replay/corpus/REAL_BUCKET_TOY_LAB_SESSION.md](../../bench/replay/corpus/REAL_BUCKET_TOY_LAB_SESSION.md).

**Note:** [datasets/runs/RUN_RESULTS_SUMMARY.md](../../datasets/runs/RUN_RESULTS_SUMMARY.md) is a multi-paper snapshot when regenerated; **P3 numbers** come from `replay_eval/summary.json` and `generated_tables.md`, not from that file alone.

**CI:** `.github/workflows/ci.yml` runs a lighter replay_eval and a **`p3-paper-latex`** job; do not treat CI stdout as the publishable table source.
