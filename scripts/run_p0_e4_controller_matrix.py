#!/usr/bin/env python3
"""
P0 E4 controller matrix: raw vs normalized conformance, weak/strong replay, multi-regime stress.

Writes (default under datasets/runs/):
  p0_e4_per_seed.jsonl, p0_e4_raw_summary.json, p0_e4_normalized_summary.json,
  p0_e4_normalization_diff.json, p0_e4_controller_matrix.json, p0_e4_diagnostics.json,
  p0_e4_controller_pairs.jsonl, p0_e4_raw_failure_reasons.json

Usage:
  PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel \\
    python scripts/run_p0_e4_controller_matrix.py \\
      --seeds 30 \\
      --scenarios toy_lab_v0,lab_profile_v0,rep_cps_scheduling_v0 \\
      --regimes baseline,moderate,stress,coordination_shock \\
      --out datasets/runs/p0_e4_controller_matrix.json
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "impl" / "src"))
if "LABTRUST_KERNEL_DIR" not in os.environ:
    os.environ["LABTRUST_KERNEL_DIR"] = str(REPO / "kernel")


def _git_head() -> str | None:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(REPO),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return None


def _paths_for_out(repo: Path, out: Path) -> object:
    from labtrust_portfolio.p0_e4_matrix import MatrixPaths

    parent = out.resolve().parent
    root = parent / "p0_e4_matrix"
    return MatrixPaths(
        repo_root=repo,
        runs_parent=parent,
        raw_runs_root=root / "raw",
        norm_runs_root=root / "normalized",
        per_seed_jsonl=parent / "p0_e4_per_seed.jsonl",
        raw_summary=parent / "p0_e4_raw_summary.json",
        normalized_summary=parent / "p0_e4_normalized_summary.json",
        normalization_diff=parent / "p0_e4_normalization_diff.json",
        controller_matrix=out,
        diagnostics=parent / "p0_e4_diagnostics.json",
        controller_pairs_jsonl=parent / "p0_e4_controller_pairs.jsonl",
        raw_failure_reasons=parent / "p0_e4_raw_failure_reasons.json",
    )


def main() -> int:
    import argparse

    from labtrust_portfolio.adapters import CentralizedAdapter, REPCPSAdapter, run_adapter
    from labtrust_portfolio.p0_e4_matrix import REGIME_FAULT_PARAMS, run_controller_matrix

    ap = argparse.ArgumentParser(description="P0 E4 controller matrix (raw + normalized + diagnostics)")
    ap.add_argument("--seeds", type=int, default=20, help="Number of seeds (1..N)")
    ap.add_argument(
        "--scenarios",
        type=str,
        default="toy_lab_v0,lab_profile_v0,rep_cps_scheduling_v0",
        help="Comma-separated scenario ids",
    )
    ap.add_argument(
        "--regimes",
        type=str,
        default="baseline,moderate,stress,coordination_shock",
        help=f"Comma-separated regimes (known: {', '.join(sorted(REGIME_FAULT_PARAMS))})",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=REPO / "datasets" / "runs" / "p0_e4_controller_matrix.json",
        help="Primary matrix JSON output path (siblings written next to it)",
    )
    args = ap.parse_args()

    scenario_ids = [s.strip() for s in args.scenarios.split(",") if s.strip()]
    if not scenario_ids:
        scenario_ids = ["toy_lab_v0"]
    regimes = [r.strip() for r in args.regimes.split(",") if r.strip()]
    if not regimes:
        regimes = ["baseline"]
    for r in regimes:
        if r not in REGIME_FAULT_PARAMS:
            print(f"Unknown regime {r!r}; known: {sorted(REGIME_FAULT_PARAMS)}", file=sys.stderr)
            return 2

    seeds = list(range(1, args.seeds + 1))
    controllers = [
        ("centralized", CentralizedAdapter()),
        ("rep_cps", REPCPSAdapter()),
    ]
    paths = _paths_for_out(REPO, args.out)
    args.out.parent.mkdir(parents=True, exist_ok=True)

    commit = os.environ.get("GIT_SHA") or _git_head()
    bundle = run_controller_matrix(
        repo_root=REPO,
        scenarios=scenario_ids,
        controllers=controllers,
        seeds=seeds,
        regimes=regimes,
        paths=paths,
        run_adapter_fn=run_adapter,
        git_sha=commit,
    )
    print(json.dumps({"wrote": str(args.out), "keys": list(bundle.keys())}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
