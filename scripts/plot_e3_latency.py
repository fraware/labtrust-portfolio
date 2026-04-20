#!/usr/bin/env python3
"""
Plot E3 p95 latency distribution per scenario from e3_summary.json.
Output: docs/figures/p0_e3_latency.png (or --out path).
Usage: PYTHONPATH=impl/src python scripts/plot_e3_latency.py [--summary path] [--out path]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_SUMMARY = REPO / "datasets" / "runs" / "e3_summary.json"
DEFAULT_OUT = REPO / "docs" / "figures" / "p0_e3_latency.png"


def main() -> int:
    ap = argparse.ArgumentParser(description="Plot E3 p95 latency per scenario")
    ap.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY, help="e3_summary.json path")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output PNG path")
    args = ap.parse_args()

    if not args.summary.exists():
        print(f"Error: {args.summary} not found. Run produce_p0_e3_release.py or replay_link_e3.py first.")
        return 1

    data = json.loads(args.summary.read_text(encoding="utf-8"))
    per_scenario = data.get("per_scenario", [])
    if not per_scenario:
        # Single-scenario format: per_run at top level
        per_run = data.get("per_run", [])
        if per_run:
            per_scenario = [{
                "scenario_id": data.get("scenarios", ["toy_lab_v0"])[0] if data.get("scenarios") else "toy_lab_v0",
                "per_run": per_run,
            }]
    if not per_scenario:
        print("Error: no per_scenario or per_run in summary.")
        return 1

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        # Write data for external plotting
        out_data = []
        for block in per_scenario:
            p95s = []
            for r in block.get("per_run", []):
                p = r.get("p95_latency_ms")
                if isinstance(p, (int, float)):
                    p95s.append(float(p))
            out_data.append({"scenario_id": block.get("scenario_id", ""), "p95_latency_ms": p95s})
        args.out.parent.mkdir(parents=True, exist_ok=True)
        json_path = args.out.with_suffix(".json")
        json_path.write_text(json.dumps(out_data, indent=2) + "\n", encoding="utf-8")
        print(f"matplotlib not installed. Wrote {json_path} for external plotting.")
        return 0

    fig, ax = plt.subplots()
    scenarios = []
    values = []
    for block in per_scenario:
        sid = block.get("scenario_id", "?")
        p95s = []
        for r in block.get("per_run", []):
            p = r.get("p95_latency_ms")
            if isinstance(p, (int, float)):
                p95s.append(float(p))
        if p95s:
            scenarios.append(sid)
            values.append(p95s)
    if not scenarios:
        print("Error: no p95_latency_ms values in summary.")
        return 1
    ax.boxplot(values, tick_labels=scenarios)
    ax.set_ylabel("p95 latency (ms)")
    ax.set_xlabel("Scenario")
    ax.set_title("E3 p95 latency distribution per scenario")
    plt.tight_layout()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(args.out, dpi=150)
    plt.close()
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
