#!/usr/bin/env python3
"""Plot P1 scale throughput vs event count.

Default behavior reads existing scale_sweep.json/scale_test.json.
Use --rerun to execute contracts_eval --scale-test for each point.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO / "docs" / "figures" / "p1_scale_throughput.png"


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Plot P1 scale throughput vs event count"
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help="Output PNG path (or JSON if matplotlib missing)",
    )
    ap.add_argument(
        "--scale-events",
        type=str,
        default="1000,10000,50000,100000",
        help="Comma-separated event counts for sweep",
    )
    ap.add_argument(
        "--rerun",
        action="store_true",
        help="Re-run contracts_eval --scale-test for each scale point",
    )
    args = ap.parse_args()
    env = os.environ.copy()
    env.setdefault("LABTRUST_KERNEL_DIR", str(REPO / "kernel"))
    env.setdefault("PYTHONPATH", str(REPO / "impl" / "src"))
    out_dir = REPO / "datasets" / "runs" / "contracts_eval"
    out_dir.mkdir(parents=True, exist_ok=True)
    counts = [int(x.strip()) for x in args.scale_events.split(",") if x.strip()]
    points = []
    sweep_path = out_dir / "scale_sweep.json"
    scale_path = out_dir / "scale_test.json"
    if (not args.rerun) and sweep_path.exists():
        d = json.loads(sweep_path.read_text(encoding="utf-8"))
        for row in d.get("sweep_results", []):
            points.append(
                {
                    "events": row.get("total_events", 0),
                    "events_per_sec": row.get("events_per_sec", 0),
                }
            )
    elif (not args.rerun) and scale_path.exists():
        d = json.loads(scale_path.read_text(encoding="utf-8"))
        points.append(
            {
                "events": d.get("total_events", 0),
                "events_per_sec": d.get("events_per_sec", 0),
            }
        )
    else:
        for n in counts:
            r = subprocess.run(
                [
                    sys.executable,
                    str(REPO / "scripts" / "contracts_eval.py"),
                    "--out",
                    str(out_dir),
                    "--scale-test",
                    "--scale-events",
                    str(n),
                ],
                cwd=str(REPO),
                env=env,
                capture_output=True,
                text=True,
            )
            if r.returncode != 0:
                continue
            if scale_path.exists():
                d = json.loads(scale_path.read_text(encoding="utf-8"))
                points.append({
                    "events": d.get("total_events", n * 2),
                    "events_per_sec": d.get("events_per_sec", 0),
                })
    if not points:
        print(
            "No scale data available; run contracts_eval.py --scale-test "
            "(or use --rerun)."
        )
        return 1
    data_path = args.out.with_suffix(".json")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    json.dump({"throughput_sweep": points}, data_path.open("w"), indent=2)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        x = [p["events"] for p in points]
        y = [p["events_per_sec"] for p in points]
        fig, ax = plt.subplots()
        ax.plot(x, y, "o-")
        ax.set_xlabel("Total events")
        ax.set_ylabel("Events/sec")
        ax.set_title(
            "P1 Contract validator scale: throughput vs event count"
        )
        plt.tight_layout()
        plt.savefig(args.out, dpi=150)
        plt.close()
        print(f"Wrote {args.out}")
    except ImportError:
        print(
            f"matplotlib not installed. Wrote {data_path} for "
            "external plotting."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
