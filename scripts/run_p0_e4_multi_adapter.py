#!/usr/bin/env python3
"""
E4 (Algorithm-independence): Run at least two adapters (centralized, rep_cps) on the same
scenario(s); evaluate raw artifacts (no hidden alignment or evidence patching) and emit
the full P0 matrix bundle under datasets/runs/ (see run_p0_e4_controller_matrix.py).

This entry point runs baseline regime only and writes the legacy p0_e4_summary.json shape
for backward compatibility (strong replay rate is the primary replay_match_rate field).

Usage:
  PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/run_p0_e4_multi_adapter.py [--seeds N] [--scenarios A,B] [--out FILE]
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


def _matrix_paths(repo: Path) -> object:
    from labtrust_portfolio.p0_e4_matrix import MatrixPaths

    parent = repo / "datasets" / "runs"
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
        controller_matrix=parent / "p0_e4_controller_matrix.json",
        diagnostics=parent / "p0_e4_diagnostics.json",
    )


def main() -> int:
    import argparse

    from labtrust_portfolio.adapters import CentralizedAdapter, REPCPSAdapter, run_adapter
    from labtrust_portfolio.p0_e4_matrix import (
        legacy_e4_summary_from_matrix,
        legacy_summary_from_raw_summary_if_complete,
        raw_summary_has_non_baseline_regimes,
        run_controller_matrix,
    )

    ap = argparse.ArgumentParser(description="E4: Multi-adapter runs (baseline matrix + legacy summary)")
    ap.add_argument("--seeds", type=int, default=20, help="Number of seeds per adapter per scenario (default 20)")
    ap.add_argument(
        "--out",
        type=Path,
        default=REPO / "datasets" / "runs" / "p0_e4_summary.json",
        help="Legacy summary JSON (backward compatible shape)",
    )
    ap.add_argument(
        "--scenario",
        type=str,
        default=None,
        help="Single scenario id (overrides --scenarios if set)",
    )
    ap.add_argument(
        "--scenarios",
        type=str,
        default="toy_lab_v0,lab_profile_v0",
        help="Comma-separated scenario ids (publishable default: toy_lab_v0,lab_profile_v0)",
    )
    args = ap.parse_args()

    if args.scenario:
        scenario_ids = [args.scenario.strip()]
    else:
        scenario_ids = [s.strip() for s in args.scenarios.split(",") if s.strip()]
    if not scenario_ids:
        scenario_ids = ["toy_lab_v0"]
    seeds = list(range(1, args.seeds + 1))
    adapters = [
        ("centralized", CentralizedAdapter()),
        ("rep_cps", REPCPSAdapter()),
    ]
    commit = os.environ.get("GIT_SHA") or _git_head()
    raw_summary_path = REPO / "datasets" / "runs" / "p0_e4_raw_summary.json"
    summary = legacy_summary_from_raw_summary_if_complete(
        raw_summary_path,
        scenarios=scenario_ids,
        seeds=seeds,
        controllers=[a[0] for a in adapters],
        script_name="run_p0_e4_multi_adapter.py",
        git_sha=commit,
    )
    if summary is None:
        if raw_summary_has_non_baseline_regimes(raw_summary_path):
            print(
                "Refusing to overwrite multi-regime E4 artifacts from run_p0_e4_multi_adapter.py. "
                "Use scripts/run_p0_e4_controller_matrix.py for full matrix, or delete/regenerate "
                "datasets/runs/p0_e4_raw_summary.json if you intend to replace it with baseline-only.",
                file=sys.stderr,
            )
            return 2
        paths = _matrix_paths(REPO)
        paths.controller_matrix.parent.mkdir(parents=True, exist_ok=True)
        bundle = run_controller_matrix(
            repo_root=REPO,
            scenarios=scenario_ids,
            controllers=adapters,
            seeds=seeds,
            regimes=["baseline"],
            paths=paths,
            run_adapter_fn=run_adapter,
            git_sha=commit,
        )
        summary = legacy_e4_summary_from_matrix(
            bundle["raw_summary_rows"],
            scenarios=scenario_ids,
            seeds=seeds,
            controllers=[a[0] for a in adapters],
            script_name="run_p0_e4_multi_adapter.py",
            git_sha=commit,
        )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
