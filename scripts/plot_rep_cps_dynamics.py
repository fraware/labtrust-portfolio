#!/usr/bin/env python3
"""
Plot P2 REP-CPS dynamic aggregation series from summary.json (dynamic_aggregation_series).
Output: docs/figures/p2_rep_cps_dynamics.png
Usage: python scripts/plot_rep_cps_dynamics.py [--summary path] [--out path]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_SUMMARY = REPO / "datasets" / "runs" / "rep_cps_eval" / "summary.json"
DEFAULT_OUT = REPO / "docs" / "figures" / "p2_rep_cps_dynamics.png"


def main() -> int:
    ap = argparse.ArgumentParser(description="Plot dynamic aggregation series (offline synthetic ticks)")
    ap.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY, help="summary.json path")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output PNG path")
    args = ap.parse_args()

    if not args.summary.exists():
        print(f"Error: {args.summary} not found.", file=sys.stderr)
        return 1
    data = json.loads(args.summary.read_text(encoding="utf-8"))
    dyn = data.get("dynamic_aggregation_series") or {}
    steps = dyn.get("steps") or []
    baseline = dyn.get("honest_only_trimmed_baseline")
    if not steps:
        print("Error: dynamic_aggregation_series.steps missing.", file=sys.stderr)
        return 1

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed.", file=sys.stderr)
        return 1

    ticks = [int(s.get("tick", i)) for i, s in enumerate(steps)]
    trim = [float(s.get("trimmed_mean", 0)) for s in steps]
    naive = [float(s.get("naive_mean", 0)) for s in steps]
    n_comp = [int(s.get("n_compromised", 0)) for s in steps]

    fig, ax = plt.subplots(figsize=(8.0, 4.5))
    ax.plot(ticks, trim, "o-", label="Trimmed mean", color="#1f77b4")
    ax.plot(ticks, naive, "s--", label="Naive mean", color="#ff7f0e")
    if baseline is not None:
        ax.axhline(float(baseline), color="#2ca02c", linestyle=":", linewidth=1.5, label="Honest-only trimmed baseline")
    ax2 = ax.twinx()
    ax2.plot(ticks, n_comp, "d:", color="#9467bd", alpha=0.8, label="n_compromised (harness)")
    ax2.set_ylabel("compromised count (series)", color="#9467bd")
    ax.set_xlabel("synthetic tick")
    ax.set_ylabel("aggregate load (offline)")
    ax.set_title("Offline temporal series: drift as compromised count grows (synthetic)")
    ax.legend(loc="upper left", fontsize=8)
    ax2.legend(loc="upper right", fontsize=8)
    fig.text(
        0.5,
        0.02,
        "Not a deployment trace; illustrates bias growth vs tick under the harness.",
        ha="center",
        fontsize=8,
        style="italic",
    )
    plt.tight_layout(rect=(0, 0.06, 1, 1))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(args.out, dpi=150)
    plt.close()
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
