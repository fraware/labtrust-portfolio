#!/usr/bin/env python3
"""
Build P0 conformance summary aggregating conformance over all released P0 runs.
Writes datasets/releases/portfolio_v0.1/p0_conformance_summary.json.
Usage (from repo root):
  PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/build_p0_conformance_summary.py
  [--out datasets/releases/portfolio_v0.1/p0_conformance_summary.json]
  [--runs-dir datasets/runs]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _find_p0_run_dirs(runs_dir: Path) -> list[Path]:
    """Discover P0 run dirs: e3/<scenario>/seed_<n>, e2_redaction_demo, and any run with trace + evidence_bundle."""
    found: list[Path] = []
    if not runs_dir.exists():
        return found
    # E3 layout: e3/<scenario>/seed_<n>/
    e3 = runs_dir / "e3"
    if e3.is_dir():
        for scenario_dir in e3.iterdir():
            if scenario_dir.is_dir():
                for seed_dir in scenario_dir.iterdir():
                    if seed_dir.is_dir() and (seed_dir / "trace.json").exists():
                        found.append(seed_dir)
    # E2 redaction demo (single run dir)
    e2 = runs_dir / "e2_redaction_demo"
    if e2.is_dir() and (e2 / "trace.json").exists():
        found.append(e2)
    return sorted(found, key=lambda p: (str(p),))


def main() -> int:
    ap = argparse.ArgumentParser(description="Build P0 conformance summary")
    ap.add_argument(
        "--out",
        type=Path,
        default=REPO / "datasets" / "releases" / "portfolio_v0.1" / "p0_conformance_summary.json",
        help="Output path for p0_conformance_summary.json",
    )
    ap.add_argument(
        "--runs-dir",
        type=Path,
        default=REPO / "datasets" / "runs",
        help="Root dir to scan for P0 run dirs (e3/*, e2_redaction_demo)",
    )
    args = ap.parse_args()

    sys.path.insert(0, str(REPO / "impl" / "src"))
    if "LABTRUST_KERNEL_DIR" not in os.environ:
        os.environ["LABTRUST_KERNEL_DIR"] = str(REPO / "kernel")

    from labtrust_portfolio.conformance import check_conformance

    run_dirs = _find_p0_run_dirs(args.runs_dir)
    runs: list[dict] = []
    for run_dir in run_dirs:
        if "e3" in str(run_dir) and run_dir.parent.parent.name == "e3":
            run_id = f"e3_{run_dir.parent.name}_{run_dir.name}"
        else:
            run_id = run_dir.name
        try:
            result = check_conformance(run_dir)
            runs.append({
                "run_id": run_id,
                "run_dir": str(run_dir.relative_to(REPO)) if REPO in run_dir.parents else str(run_dir),
                "tier": result.tier,
                "pass": result.passed,
                "reasons": result.failures,
            })
        except Exception as e:
            runs.append({
                "run_id": run_id,
                "run_dir": str(run_dir.relative_to(REPO)) if REPO in run_dir.parents else str(run_dir),
                "tier": 0,
                "pass": False,
                "reasons": [str(e)],
            })

    summary = {
        "version": "0.1",
        "source": "p0_conformance_summary",
        "runs_count": len(runs),
        "runs": runs,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.out} ({len(runs)} runs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
