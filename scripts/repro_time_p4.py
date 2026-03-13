#!/usr/bin/env python3
"""
Record wall-clock time for P4 minimal repro (maestro_fault_sweep + export + plot).
Writes repro_wall_min to datasets/runs/repro_manifest.json (or --out path).
Usage: PYTHONPATH=impl/src python scripts/repro_time_p4.py [--out path]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser(description="P4 minimal repro wall-clock time")
    ap.add_argument(
        "--out",
        type=Path,
        default=REPO / "datasets" / "runs" / "repro_manifest.json",
        help="Write repro manifest JSON here",
    )
    ap.add_argument(
        "--seeds",
        type=int,
        default=3,
        help="Seeds for fault sweep (minimal for speed)",
    )
    args = ap.parse_args()

    env = os.environ.copy()
    env.setdefault("LABTRUST_KERNEL_DIR", str(REPO / "kernel"))
    env["PYTHONPATH"] = str(REPO / "impl" / "src")

    with tempfile.TemporaryDirectory() as td:
        out_dir = Path(td) / "maestro_fault_sweep"
        out_dir.mkdir(parents=True)
        t0 = time.perf_counter()
        r = subprocess.run(
            [
                sys.executable,
                str(REPO / "scripts" / "maestro_fault_sweep.py"),
                "--scenario", "toy_lab_v0",
                "--seeds", str(args.seeds),
                "--out", str(out_dir),
            ],
            cwd=str(REPO),
            env=env,
            capture_output=True,
            text=True,
            timeout=300,
        )
        if r.returncode != 0:
            print("maestro_fault_sweep failed:", r.stderr, file=sys.stderr)
            return 1
        r2 = subprocess.run(
            [
                sys.executable,
                str(REPO / "scripts" / "export_maestro_tables.py"),
                "--multi-sweep", str(out_dir / "multi_sweep.json"),
            ],
            cwd=str(REPO),
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        elapsed = time.perf_counter() - t0
        repro_wall_min = round(elapsed / 60.0, 2)
    manifest = {
        "paper": "P4",
        "repro_wall_min": repro_wall_min,
        "seeds": args.seeds,
        "script": "repro_time_p4.py",
        "note": "Minimal repro: maestro_fault_sweep (toy_lab_v0) + export_maestro_tables. For full repro use --seeds 10.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"P4 minimal repro: {repro_wall_min} min")
    return 0 if r2.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
