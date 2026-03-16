# Paper Artifact Polish Standards

This document defines portfolio-wide standards so all paper artifacts (DRAFTs, claims, tables, figures, READMEs) are consistent, clear, and state-of-the-art aligned. Use it together with [DRAFT_CONVERSION_CHECKLIST.md](DRAFT_CONVERSION_CHECKLIST.md) and [STATE_OF_THE_ART_CRITERIA.md](STATE_OF_THE_ART_CRITERIA.md).

## Repro block

- **Order:** List commands in this order: Figure 0, Table 1, Table 2, Figure 1, then any extra tables or figures.
- **Env:** State once at the top: "From repo root, with `PYTHONPATH=impl/src` and `LABTRUST_KERNEL_DIR=kernel`."
- **Minimal vs publishable:** Define both when relevant:
  - **Minimal run:** Fewer seeds (e.g. 3), one scenario; target under 20 min for repro.
  - **Publishable run:** Default 20 seeds, multi-scenario where applicable; document in run_manifest.
- **Per item:** Each table and figure has one line: script name and (if needed) input/output path or release id.

## Table captions

Format: **Table N — Short title.** One sentence describing what the table shows (e.g. "Fault sweep: tasks_completed mean/stdev and p95 latency (ms) by scenario and setting; N seeds per cell."). Include units (ms, %, seeds) in the caption or column headers.

## Figure captions

Format: **Figure N — Short title.** One sentence interpreting the figure (e.g. "Recovery proxy: tasks_completed drops under higher drop probability; multi-scenario overlay."). Do not use a generic "Figure 1" as the figure title in the plot itself; use a short descriptive title.

## Terminology

- Use **run_manifest** when referring to seeds, scenario, or fault settings (e.g. "run_manifest records seed_count and scenario_id").
- Use **excellence_metrics** when citing comparison stats (difference_mean, difference_ci95, power_post_hoc, etc.).
- Link to [REPORTING_STANDARD.md](REPORTING_STANDARD.md) and [RESULTS_PER_PAPER.md](RESULTS_PER_PAPER.md) once per draft (e.g. in Reproducibility or Limitations).

## Figure style (plots)

- **Axis labels:** Include units (e.g. "tasks_completed (mean)", "Fault setting", "Latency (ms)").
- **Legend:** When multiple series (e.g. scenarios), include a legend.
- **Title:** Use a short descriptive title in the plot, not the default "Figure 1".
- **DPI:** 150 for draft; 300 for camera-ready. This repo standard is 150 unless a paper overrides.
- **Layout:** Avoid overlapping labels; use rotation (e.g. xticks) and tight_layout as needed so the figure is readable when pasted into the draft.

## Overview diagrams (Figure 0, Mermaid)

- **Node labels:** Clear and unambiguous; avoid abbreviations unless explained in the draft.
- **DRAFT:** Include one sentence describing what Figure 0 shows (pipeline, levels, or architecture).
- Scripts output `.mmd` to `docs/figures/`; render to PNG for camera-ready via Mermaid CLI or editor.

## References

- **P1 (Contracts), P2 (REP-CPS), P4 (MAESTRO):** Replace [1], [2] in the DRAFT References section with actual citations before submission (e.g. consistency/coordination or state-machine literature for P1; Byzantine aggregation / CPS coordination for P2; multi-agent or coordination benchmark and CPS/robotics testbed for P4).
- **P5 (Scaling):** Replace [1], [2] in the DRAFT References section with actual citations (e.g. multi-agent/coordination overhead, RL reward scaling) before submission.
- Draft conversion: [DRAFT_CONVERSION_CHECKLIST.md](DRAFT_CONVERSION_CHECKLIST.md).
- Visual inventory: [VISUALS_PER_PAPER.md](VISUALS_PER_PAPER.md).
- Result locations and how to read: [RESULTS_PER_PAPER.md](RESULTS_PER_PAPER.md).
