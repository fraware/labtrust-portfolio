#!/usr/bin/env python3
"""
Plot P2 REP-CPS gate-threshold sweep from summary.json (gate_threshold_sweep_results).
Output: docs/figures/p2_rep_cps_gate_threshold.png
Usage: python scripts/plot_rep_cps_gate_threshold.py [--summary path] [--out path]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_SUMMARY = REPO / "datasets" / "runs" / "rep_cps_eval" / "summary.json"
DEFAULT_OUT = REPO / "docs" / "figures" / "p2_rep_cps_gate_threshold.png"


def main() -> int:
    ap = argparse.ArgumentParser(description="Plot gate-threshold sweep for REP-CPS")
    ap.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY, help="summary.json path")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output PNG path")
    args = ap.parse_args()

    if not args.summary.exists():
        print(f"Error: {args.summary} not found.", file=sys.stderr)
        return 1
    data = json.loads(args.summary.read_text(encoding="utf-8"))
    rows = data.get("gate_threshold_sweep_results") or []
    if not rows:
        print("Error: gate_threshold_sweep_results missing. Re-run rep_cps_eval.py with "
              "--gate-threshold-sweep 1.5,2.0,2.5 and rep_cps_scheduling_v0 in scenarios.",
              file=sys.stderr)
        return 1

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed.", file=sys.stderr)
        return 1

    thresholds = [float(r["safety_gate_max_load"]) for r in rows]
    rep_t = [float(r.get("rep_cps_tasks_mean", 0)) for r in rows]
    naive_t = [float(r.get("naive_in_loop_tasks_mean", 0)) for r in rows]
    unsec_t = [float(r.get("unsecured_tasks_mean", 0)) for r in rows]
    rep_deny = [float(r.get("rep_cps_gate_deny_rate", 0)) for r in rows]
    unsec_deny = [float(r.get("unsecured_gate_deny_rate", 0)) for r in rows]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.2))
    ax1.plot(thresholds, rep_t, "o-", label="REP-CPS", color="#1f77b4")
    ax1.plot(thresholds, naive_t, "s--", label="Naive-in-loop", color="#ff7f0e")
    ax1.plot(thresholds, unsec_t, "^:", label="Unsecured", color="#d62728")
    ax1.set_xlabel("safety_gate_max_load (threshold)")
    ax1.set_ylabel("tasks_completed (mean)")
    ax1.set_title("Tasks vs gate threshold (scheduling scenario)")
    ax1.legend(loc="best", fontsize=8)
    ax1.grid(True, alpha=0.3)

    ax2.plot(thresholds, rep_deny, "o-", label="REP-CPS deny rate", color="#1f77b4")
    ax2.plot(thresholds, unsec_deny, "s--", label="Unsecured deny rate", color="#d62728")
    ax2.set_xlabel("safety_gate_max_load (threshold)")
    ax2.set_ylabel("gate deny rate")
    ax2.set_ylim(-0.05, 1.05)
    ax2.set_title("Observed gate denial rate vs threshold")
    ax2.legend(loc="best", fontsize=8)
    ax2.grid(True, alpha=0.3)

    fig.suptitle("P2 REP-CPS: gate-threshold sensitivity (rep_cps_scheduling_v0)", fontsize=11)
    plt.tight_layout()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(args.out, dpi=150)
    plt.close()
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
