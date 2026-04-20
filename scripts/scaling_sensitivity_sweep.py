#!/usr/bin/env python3
"""
P5: subsample sensitivity — run held-out eval at seed caps N=10, 20, 30 (or fewer if data sparse).
Writes datasets/runs/sensitivity_sweep/scaling_sensitivity.json (script-backed artifact).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List

REPO = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser(description="P5 scaling sensitivity vs max seed")
    ap.add_argument(
        "--runs-dir",
        type=Path,
        default=REPO / "datasets" / "runs" / "multiscenario_runs",
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=REPO / "datasets" / "runs" / "sensitivity_sweep",
    )
    ap.add_argument(
        "--caps",
        type=str,
        default="10,20,30",
        help="Comma-separated max seed values (inclusive)",
    )
    args = ap.parse_args()

    caps: List[int] = []
    for p in args.caps.split(","):
        p = p.strip()
        if p.isdigit():
            caps.append(int(p))
    if not caps:
        caps = [10, 20, 30]

    eval_script = REPO / "scripts" / "scaling_heldout_eval.py"
    env = {**{k: v for k, v in __import__("os").environ.items()}, "PYTHONPATH": str(REPO / "impl" / "src")}
    env.setdefault("LABTRUST_KERNEL_DIR", str(REPO / "kernel"))

    by_cap: Dict[str, Any] = {}
    for cap in sorted(set(caps)):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "eval"
            cmd = [
                sys.executable,
                str(eval_script),
                "--runs-dir",
                str(args.runs_dir),
                "--out",
                str(out),
                "--holdout-mode",
                "scenario",
                "--max-seed",
                str(cap),
            ]
            r = subprocess.run(cmd, cwd=str(REPO), env=env, capture_output=True, text=True, timeout=300)
            if r.returncode != 0:
                print(r.stderr or r.stdout, file=sys.stderr)
                return 1
            jpath = out / "heldout_results.json"
            by_cap[str(cap)] = json.loads(jpath.read_text(encoding="utf-8"))

    args.out_dir.mkdir(parents=True, exist_ok=True)
    out_file = args.out_dir / "scaling_sensitivity.json"
    payload = {
        "run_manifest": {
            "script": "scaling_sensitivity_sweep.py",
            "runs_dir": str(args.runs_dir),
            "caps": [str(c) for c in sorted(set(caps))],
            "holdout_mode": "scenario",
        },
        "by_max_seed": by_cap,
    }
    out_file.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
