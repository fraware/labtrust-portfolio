#!/usr/bin/env python3
"""
Plot P4 recovery proxy: tasks_completed (or recovery_ok) vs fault setting from multi_sweep.
Serves as recovery curve (time-to-safe-state proxy). Usage:
  python scripts/plot_maestro_recovery.py [--multi-sweep path] [--out path]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_SWEEP = REPO / "datasets" / "runs" / "maestro_fault_sweep" / "multi_sweep.json"
DEFAULT_OUT = REPO / "docs" / "figures" / "p4_recovery_curve.png"


def main() -> int:
    ap = argparse.ArgumentParser(description="Plot P4 recovery proxy (tasks_completed vs fault setting)")
    ap.add_argument("--multi-sweep", type=Path, default=DEFAULT_SWEEP, help="multi_sweep.json path")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output PNG path")
    args = ap.parse_args()
    if not args.multi_sweep.exists():
        print(f"Error: {args.multi_sweep} not found. Run maestro_fault_sweep.py first.")
        return 1
    data = json.loads(args.multi_sweep.read_text(encoding="utf-8"))
    # Flatten: (scenario, setting) -> tasks_completed_mean
    points = []
    for combined in data.get("per_scenario", []):
        scenario = combined.get("scenario", "")
        for s in combined.get("sweep", []):
            setting = s.get("setting", "")
            tc = s.get("tasks_completed_mean", 0)
            points.append({"scenario": scenario, "setting": setting, "tasks_completed_mean": tc})
    if not points:
        print("No per_scenario/sweep data in multi_sweep.")
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    json.dump({"recovery_proxy": points}, args.out.with_suffix(".json").open("w"), indent=2)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        # Group by scenario, x = setting (string), y = tasks_completed_mean
        by_scenario = {}
        for p in points:
            s = p["scenario"]
            if s not in by_scenario:
                by_scenario[s] = []
            by_scenario[s].append((p["setting"], p["tasks_completed_mean"]))
        fig, ax = plt.subplots()
        for scenario, pairs in by_scenario.items():
            x = [str(p[0]) for p in pairs]
            y = [p[1] for p in pairs]
            ax.plot(x, y, "o-", label=scenario)
        ax.set_xlabel("Fault setting")
        ax.set_ylabel("tasks_completed (mean)")
        ax.set_title("P4 Recovery proxy: tasks_completed vs fault setting")
        ax.legend()
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(args.out, dpi=150)
        plt.close()
        print(f"Wrote {args.out}")
    except ImportError:
        print(f"matplotlib not installed. Wrote {args.out.with_suffix('.json')} for external plotting.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
