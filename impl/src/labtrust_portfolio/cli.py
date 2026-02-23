from __future__ import annotations

import argparse
from pathlib import Path
from .thinslice import run_thin_slice

def main() -> int:
    ap = argparse.ArgumentParser(prog="labtrust_portfolio")
    sub = ap.add_subparsers(dest="cmd", required=True)

    ts = sub.add_parser("run-thinslice", help="Run the thin-slice TRACE→MAESTRO→Replay→Evidence pipeline")
    ts.add_argument("--out-dir", type=Path, required=True)
    ts.add_argument("--seed", type=int, default=7)
    ts.add_argument("--delay-p95-ms", type=float, default=50.0)
    ts.add_argument("--drop-completion-prob", type=float, default=0.02)

    args = ap.parse_args()
    if args.cmd == "run-thinslice":
        out = run_thin_slice(args.out_dir, seed=args.seed, delay_p95_ms=args.delay_p95_ms, drop_completion_prob=args.drop_completion_prob)
        for k, p in out.items():
            print(f"{k}: {p}")
        return 0

    return 1
