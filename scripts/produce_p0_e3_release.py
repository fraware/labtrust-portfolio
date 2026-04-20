#!/usr/bin/env python3
"""
Produce E3 runs and release one to datasets/releases/p0_e3_release.
Runs replay_link_e3.py (default 20 seeds; --scenarios for multi-scenario), then release-dataset for first scenario seed_1.
Usage (from repo root):
  PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/produce_p0_e3_release.py
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Produce E3 runs and release")
    ap.add_argument("--runs", type=int, default=20, help="Number of seeds (default 20 for publishable; use 30 for sensitivity)")
    ap.add_argument(
        "--scenarios",
        type=str,
        default="toy_lab_v0,lab_profile_v0",
        help="Comma-separated scenario ids for E3 (minimal: toy_lab_v0; publishable: toy_lab_v0,lab_profile_v0 or more)",
    )
    ap.add_argument(
        "--no-release",
        action="store_true",
        help="Skip release step (only run E3 and write variance)",
    )
    args = ap.parse_args()
    do_release = not args.no_release
    scenario_ids = [s.strip() for s in args.scenarios.split(",") if s.strip()]
    if not scenario_ids:
        scenario_ids = ["toy_lab_v0"]

    env = os.environ.copy()
    env.setdefault("LABTRUST_KERNEL_DIR", str(REPO / "kernel"))
    env.setdefault("PYTHONPATH", str(REPO / "impl" / "src"))
    runs_dir = REPO / "datasets" / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    summary_path = runs_dir / "e3_summary.json"

    r = subprocess.run(
        [
            sys.executable,
            str(REPO / "scripts" / "replay_link_e3.py"),
            "--runs",
            str(args.runs),
            "--scenarios",
            ",".join(scenario_ids),
            "--out",
            str(summary_path),
        ],
        cwd=str(REPO),
        env=env,
    )
    if r.returncode != 0:
        return r.returncode

    if summary_path.exists():
        import json
        data = json.loads(summary_path.read_text(encoding="utf-8"))
        variance_path = runs_dir / "p0_e3_variance.json"
        per_scenario = data.get("per_scenario", [])
        if per_scenario:
            first = per_scenario[0]
            out = {
                "runs": data.get("runs", args.runs),
                "scenarios": data.get("scenarios", scenario_ids),
                "tasks_completed_mean": first.get("tasks_completed_mean"),
                "tasks_completed_stdev": first.get("tasks_completed_stdev"),
                "p95_latency_ms_mean": first.get("p95_latency_ms_mean"),
                "p95_latency_ms_stdev": first.get("p95_latency_ms_stdev"),
                "all_match": data.get("all_match"),
                "per_scenario": per_scenario,
            }
            if "tasks_completed_ci_95" in first:
                out["tasks_completed_ci_95"] = first["tasks_completed_ci_95"]
            if "p95_latency_ms_ci_95" in first:
                out["p95_latency_ms_ci_95"] = first["p95_latency_ms_ci_95"]
            if "p99_latency_ms" in first:
                out["p99_latency_ms"] = first["p99_latency_ms"]
        else:
            out = {
                "runs": data.get("runs", args.runs),
                "tasks_completed_mean": data.get("tasks_completed_mean"),
                "tasks_completed_stdev": data.get("tasks_completed_stdev"),
                "p95_latency_ms_mean": data.get("p95_latency_ms_mean"),
                "p95_latency_ms_stdev": data.get("p95_latency_ms_stdev"),
                "all_match": data.get("all_match"),
            }
            if "tasks_completed_ci_95" in data:
                out["tasks_completed_ci_95"] = data["tasks_completed_ci_95"]
            if "p95_latency_ms_ci_95" in data:
                out["p95_latency_ms_ci_95"] = data["p95_latency_ms_ci_95"]
            if "p99_latency_ms" in data:
                out["p99_latency_ms"] = data["p99_latency_ms"]
        if "run_manifest" in data:
            out["run_manifest"] = data["run_manifest"]
        variance_path.write_text(
            json.dumps(out, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Variance summary: {variance_path}")

    if not do_release:
        return 0
    run_dir = runs_dir / "e3" / scenario_ids[0] / "seed_1"
    if not (run_dir / "trace.json").exists():
        print(f"E3 run {run_dir} missing trace.json")
        return 1

    sys.path.insert(0, str(REPO / "impl" / "src"))
    from labtrust_portfolio.release import release_dataset

    releases_root = REPO / "datasets" / "releases"
    release_dir, manifest = release_dataset(run_dir, "p0_e3_release", releases_root)
    print(f"Released to {release_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
