#!/usr/bin/env python3
"""
Plot P3 replay overhead: p95 replay time (ms) vs event count from replay_eval overhead_curve.
Usage: python scripts/plot_replay_overhead.py [--summary path] [--out path]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_SUMMARY = REPO / "datasets" / "runs" / "replay_eval" / "summary.json"
DEFAULT_OUT = REPO / "docs" / "figures" / "p3_replay_overhead.png"


def main() -> int:
    ap = argparse.ArgumentParser(description="Plot P3 replay p95 vs event count")
    ap.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY, help="replay_eval summary.json")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output PNG path")
    args = ap.parse_args()
    if not args.summary.exists():
        print(f"Error: {args.summary} not found. Run replay_eval.py --overhead-curve first.")
        return 1
    data = json.loads(args.summary.read_text(encoding="utf-8"))
    curve = data.get("overhead_curve", [])
    if not curve:
        print("Error: no overhead_curve in summary. Run with --overhead-curve.")
        return 1
    data_path = args.out.with_suffix(".json")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    json.dump({"overhead_curve": curve}, data_path.open("w"), indent=2)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        x = [e["event_count"] for e in curve]
        y = [e["p95_replay_ms"] for e in curve]
        yerr = None
        if curve and all(
            "p95_replay_ci95_lower_ms" in e and "p95_replay_ci95_upper_ms" in e
            for e in curve
        ):
            lo = [e["p95_replay_ms"] - e["p95_replay_ci95_lower_ms"] for e in curve]
            hi = [e["p95_replay_ci95_upper_ms"] - e["p95_replay_ms"] for e in curve]
            yerr = [lo, hi]
        fig, ax = plt.subplots()
        if yerr is not None:
            ax.errorbar(x, y, yerr=yerr, fmt="o-", capsize=3, elinewidth=1)
        else:
            ax.plot(x, y, "o-")
        ax.set_xlabel("Event count (trace size)")
        ax.set_ylabel("Replay p95 (ms)")
        ax.set_title("P3 Replay: p95 time vs trace size")
        plt.tight_layout()
        plt.savefig(args.out, dpi=150)
        plt.close()
        print(f"Wrote {args.out}")
    except ImportError:
        print(f"matplotlib not installed. Wrote {data_path} for external plotting.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
