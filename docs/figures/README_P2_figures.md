# P2 REP-CPS figure pipeline

Figures for `papers/P2_REP-CPS/DRAFT.tex` are generated from `datasets/runs/rep_cps_eval/summary.json` after a publishable `rep_cps_eval.py` run.

## Prerequisites

- `PYTHONPATH=impl/src`, `LABTRUST_KERNEL_DIR` pointing at `kernel/`
- Matplotlib for PNG plots
- Optional: `@mermaid-js/mermaid-cli` (`mmdc` on PATH) for Figure 0 PNG/SVG/PDF from Mermaid

## Commands (from repo root)

1. Evaluation (20 seeds, three scenarios, gate sweep):

   `python scripts/rep_cps_eval.py --scenarios toy_lab_v0,lab_profile_v0,rep_cps_scheduling_v0 --delay-sweep 0,0.05,0.1,0.2 --drop-sweep 0.02 --gate-threshold-sweep 1.5,2.0,2.5`

2. Tables: `python scripts/export_rep_cps_tables.py`

3. Figure 0 Mermaid: `python scripts/export_p2_rep_profile_diagram.py`

4. Figure 0 camera-ready renders (optional):
   - `python scripts/export_p2_rep_profile_diagram.py --render-png`
   - `python scripts/export_p2_rep_profile_diagram.py --render-svg`
   - `python scripts/export_p2_rep_profile_diagram.py --render-pdf`

5. Task figures: `python scripts/plot_rep_cps_summary.py`

6. Gate figure: `python scripts/plot_rep_cps_gate_threshold.py`

7. Dynamics figure: `python scripts/plot_rep_cps_dynamics.py`

8. Latency figure: `python scripts/plot_rep_cps_latency.py`

Outputs default to `docs/figures/`:

| File | Script |
|------|--------|
| `p2_rep_profile_diagram.mmd` | `export_p2_rep_profile_diagram.py` |
| `p2_rep_profile_diagram.png` | `--render-png` with `mmdc` |
| `p2_rep_profile_diagram.svg` | `--render-svg` with `mmdc` |
| `p2_rep_profile_diagram.pdf` | `--render-pdf` with `mmdc` |
| `p2_rep_cps_tasks.png` | `plot_rep_cps_summary.py` |
| `p2_rep_cps_tasks_per_scenario.png` | `plot_rep_cps_summary.py` |
| `p2_rep_cps_gate_threshold.png` | `plot_rep_cps_gate_threshold.py` |
| `p2_rep_cps_dynamics.png` | `plot_rep_cps_dynamics.py` |
| `p2_rep_cps_latency.png` | `plot_rep_cps_latency.py` |
