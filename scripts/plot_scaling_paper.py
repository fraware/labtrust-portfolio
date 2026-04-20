#!/usr/bin/env python3
"""
P5 paper figures from frozen JSON + runs dir (Figure 0 pipeline schematic is optional text;
Figures 1–5 from artifacts). Writes under docs/figures/p5_*.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, DefaultDict, Dict, List

REPO = Path(__file__).resolve().parents[1]
FIG = REPO / "docs" / "figures"


def _load(p: Path) -> Dict[str, Any]:
    return json.loads(p.read_text(encoding="utf-8"))


def _rows_from_runs(runs_dir: Path) -> List[Dict[str, Any]]:
    sys.path.insert(0, str(REPO / "impl" / "src"))
    from labtrust_portfolio.scaling import build_dataset_from_runs

    if not runs_dir.exists():
        return []
    return build_dataset_from_runs(runs_dir)


def main() -> int:
    ap = argparse.ArgumentParser(description="P5 scaling paper plots")
    ap.add_argument("--heldout-main", type=Path, required=True)
    ap.add_argument("--heldout-family", type=Path)
    ap.add_argument("--heldout-regime", type=Path)
    ap.add_argument("--recommend", type=Path)
    ap.add_argument("--sensitivity", type=Path)
    ap.add_argument("--runs-dir", type=Path, required=True)
    args = ap.parse_args()

    FIG.mkdir(parents=True, exist_ok=True)
    rows = _rows_from_runs(args.runs_dir)

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed; skipping PNG generation.")
        return 0

    # Figure 1: MAE by holdout label (main)
    if args.heldout_main.exists():
        d = _load(args.heldout_main)
        res = d.get("held_out_results", [])
        labels = [r.get("holdout_label", "?") for r in res]
        base = [float(r.get("baseline_mae", 0) or 0) for r in res]
        reg = [float(r.get("regression_mae") or 0.0) for r in res]
        x = range(len(labels))
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.bar([i - 0.2 for i in x], base, 0.4, label="Global mean MAE")
        ax.bar([i + 0.2 for i in x], reg, 0.4, label="Regression MAE")
        ax.set_xticks(list(x))
        ax.set_xticklabels(labels, rotation=30, ha="right")
        ax.set_ylabel("MAE")
        ax.set_title("P5 Fig 1 — Held-out MAE (main protocol)")
        ax.legend()
        fig.tight_layout()
        fig.savefig(FIG / "p5_fig1_mae_holdout.png", dpi=150)
        plt.close(fig)

    # Figure 2–3: agent_count vs tasks_completed / collapse by regime
    if rows:
        by_reg_ac: DefaultDict[str, DefaultDict[int, List[float]]] = defaultdict(
            lambda: defaultdict(list),
        )
        coll_by: DefaultDict[str, DefaultDict[int, List[float]]] = defaultdict(
            lambda: defaultdict(list),
        )
        for r in rows:
            reg = str(r.get("coordination_regime", "centralized"))
            ac = int(r.get("agent_count", 1) or 1)
            by_reg_ac[reg][ac].append(
                float(r.get("response", {}).get("tasks_completed", 0) or 0),
            )
            coll_by[reg][ac].append(1.0 if r.get("collapse") else 0.0)

        def _mean(xs: List[float]) -> float:
            return sum(xs) / len(xs) if xs else 0.0

        fig, ax = plt.subplots(figsize=(8, 5))
        for reg in sorted(by_reg_ac.keys()):
            xs = sorted(by_reg_ac[reg].keys())
            ys = [_mean(by_reg_ac[reg][x]) for x in xs]
            ax.plot(xs, ys, marker="o", label=reg)
        ax.set_xlabel("agent_count")
        ax.set_ylabel("mean tasks_completed")
        ax.set_title("P5 Fig 2 — Throughput vs agent count by regime")
        ax.legend()
        fig.tight_layout()
        fig.savefig(FIG / "p5_fig2_tasks_vs_agents.png", dpi=150)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(8, 5))
        for reg in sorted(coll_by.keys()):
            xs = sorted(coll_by[reg].keys())
            ys = [_mean(coll_by[reg][x]) for x in xs]
            ax.plot(xs, ys, marker="s", label=reg)
        ax.set_xlabel("agent_count")
        ax.set_ylabel("empirical collapse rate")
        ax.set_title("P5 Fig 3 — Collapse vs agent count by regime")
        ax.legend()
        fig.tight_layout()
        fig.savefig(FIG / "p5_fig3_collapse_vs_agents.png", dpi=150)
        plt.close(fig)

    # Figure 4: phase-style — mean coordination_tax_proxy vs agent_count
    if rows:
        tax: DefaultDict[str, DefaultDict[int, List[float]]] = defaultdict(
            lambda: defaultdict(list),
        )
        for r in rows:
            reg = str(r.get("coordination_regime", "centralized"))
            ac = int(r.get("agent_count", 1) or 1)
            tax[reg][ac].append(float(r.get("coordination_tax_proxy", 0) or 0))
        fig, ax = plt.subplots(figsize=(8, 5))
        for reg in sorted(tax.keys()):
            xs = sorted(tax[reg].keys())
            ys = [sum(tax[reg][x]) / len(tax[reg][x]) for x in xs]
            ax.plot(xs, ys, marker="^", label=reg)
        ax.set_xlabel("agent_count")
        ax.set_ylabel("mean coordination_tax_proxy")
        ax.set_title("P5 Fig 4 — Coordination tax vs agents (phase map proxy)")
        ax.legend()
        fig.tight_layout()
        fig.savefig(FIG / "p5_fig4_tax_phase.png", dpi=150)
        plt.close(fig)

    # Figure 5: sensitivity — regression MAE vs cap
    if args.sensitivity and args.sensitivity.exists():
        d = _load(args.sensitivity)
        caps = sorted(int(k) for k in d.get("by_max_seed", {}).keys())
        ys = []
        for c in caps:
            block = d["by_max_seed"].get(str(c), {})
            v = block.get("overall_regression_mae")
            ys.append(float(v) if v is not None else math.nan)
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(caps, ys, marker="o")
        ax.set_xlabel("max seed (inclusive)")
        ax.set_ylabel("overall regression MAE")
        ax.set_title("P5 Fig 5 — Sensitivity vs seed cap")
        fig.tight_layout()
        fig.savefig(FIG / "p5_fig5_sensitivity.png", dpi=150)
        plt.close(fig)

    # Figure 0: pipeline schematic (stages)
    fig, ax = plt.subplots(figsize=(8, 2))
    stages = ["Runs", "Traces", "Features", "LOFO", "Recs"]
    ax.bar(list(range(len(stages))), [1] * len(stages), color="#4472c4")
    ax.set_xticks(list(range(len(stages))))
    ax.set_xticklabels(stages, rotation=15, ha="right")
    ax.set_ylabel("relative stage weight (schematic)")
    ax.set_title("P5 Fig 0 — Evaluation pipeline (schematic)")
    fig.tight_layout()
    fig.savefig(FIG / "p5_fig0_pipeline.png", dpi=150)
    plt.close(fig)

    print(f"P5 figures written under {FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
