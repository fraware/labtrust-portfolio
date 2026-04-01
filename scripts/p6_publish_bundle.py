#!/usr/bin/env python3
"""
P6 one-shot publish bundle: core paper experiments (run_paper_experiments --paper P6),
optional concurrency/replanning stress scripts, and table exports for llm_eval artifacts.

Usage (repo root, PowerShell):
  $env:PYTHONPATH="impl\\src"; $env:LABTRUST_KERNEL_DIR="$PWD\\kernel"
  python scripts/p6_publish_bundle.py
  python scripts/p6_publish_bundle.py --quick --skip-optional-benchmarks
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUNS = REPO / "datasets" / "runs" / "llm_eval"


def _env() -> dict:
    e = os.environ.copy()
    e.setdefault("LABTRUST_KERNEL_DIR", str(REPO / "kernel"))
    e.setdefault("PYTHONPATH", str(REPO / "impl" / "src"))
    return e


def _run(cmd: list[str], desc: str) -> bool:
    print(f"\n=== {desc} ===", flush=True)
    r = subprocess.run(cmd, cwd=str(REPO), env=_env())
    if r.returncode != 0:
        print(f"FAILED: {desc}", file=sys.stderr)
        return False
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description="P6 extended eval + exports")
    ap.add_argument("--quick", action="store_true", help="Pass --quick to run_paper_experiments")
    ap.add_argument(
        "--skip-optional-benchmarks",
        action="store_true",
        help="Skip concurrency and replanning micro-benchmarks (faster)",
    )
    args = ap.parse_args()

    base = [sys.executable, str(REPO / "scripts" / "run_paper_experiments.py"), "--paper", "P6"]
    if args.quick:
        base.append("--quick")
    if not _run(base, "run_paper_experiments P6"):
        return 1

    if not args.skip_optional_benchmarks and not args.quick:
        if not _run(
            [sys.executable, str(REPO / "scripts" / "p6_concurrency_benchmark.py"), "--out-dir", str(RUNS)],
            "p6_concurrency_benchmark",
        ):
            return 1
        if not _run(
            [sys.executable, str(REPO / "scripts" / "p6_replanning_benchmark.py"), "--out-dir", str(RUNS)],
            "p6_replanning_benchmark",
        ):
            return 1

    exports = [
        [sys.executable, str(REPO / "scripts" / "export_llm_redteam_table.py"), "--out-dir", str(RUNS), "--out", str(REPO / "papers" / "P6_LLMPlanning" / "exported_tables.md")],
        [sys.executable, str(REPO / "scripts" / "export_p6_baseline_table.py"), "--out-dir", str(RUNS)],
        [sys.executable, str(REPO / "scripts" / "export_p6_layer_attribution.py")],
    ]
    for cmd in exports:
        if not _run(cmd, " ".join(cmd[-2:])):
            return 1
    print("\nP6 publish bundle completed.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
