# P3 — Replay Levels and Nondeterminism Detection

P3 defines replay levels (L0/L1/L2) and nondeterminism detection for agentic CPS. The reference eval is `scripts/replay_eval.py`, which writes `datasets/runs/replay_eval/summary.json` with `schema_version: p3_replay_eval_v0.2` (full L0 overhead, baselines, multi-seed thin-slice family, corpus outcomes, optional overhead curve and bootstrap CIs).

**Read first:** [DRAFT.md](DRAFT.md) (repro block, evaluation, limitations), [claims.yaml](claims.yaml), [generated_tables.md](generated_tables.md).

**Scripts:** `export_replay_corpus_table.py` (Table 1), tables 2–3 from summary JSON fields, `export_p3_replay_levels_diagram.py` (Figure 0), `plot_replay_overhead.py` (Figure 1), `verify_p3_replay_summary.py` (schema and optional figure consistency).

**Cross-links:** [VISUALS_PER_PAPER.md](../docs/VISUALS_PER_PAPER.md), [RESULTS_PER_PAPER.md](../docs/RESULTS_PER_PAPER.md) (P3 section), [EVALS_RUNBOOK.md](../docs/EVALS_RUNBOOK.md), [bench/replay/README.md](../../bench/replay/README.md), [P3_REAL_TRACE_INGESTION.md](../docs/P3_REAL_TRACE_INGESTION.md). Outline: [AUTHORING_PACKET.md](AUTHORING_PACKET.md).

**Run:** `python scripts/run_paper_experiments.py --paper P3` (or full flags in DRAFT.md). **Note:** [datasets/runs/RUN_RESULTS_SUMMARY.md](../../datasets/runs/RUN_RESULTS_SUMMARY.md) is the P5/P6/P8 consolidated snapshot; P3 numbers come from `replay_eval/summary.json` and generated tables, not from that file.
