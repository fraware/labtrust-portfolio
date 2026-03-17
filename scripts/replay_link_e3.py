#!/usr/bin/env python3
"""
E3 (Replay link): Independent verifier recomputes MAESTRO metrics from TRACE.
Run with multiple seeds and report variance and 95% CIs.
Use --standalone-verifier to run the verifier as a separate process (scripts/verify_maestro_from_trace.py)
so that the producer and verifier are distinct code paths. Usage:
  PYTHONPATH=impl/src python scripts/replay_link_e3.py [--runs N] [--out FILE] [--standalone-verifier]
"""
from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

# t_{0.975, df} for 95% two-sided CI (df = n-1)
_T_975: dict[int, float] = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
    6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
    11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131,
    20: 2.086, 25: 2.060, 30: 2.042,
}


def _ci95(mean: float, stdev: float, n: int) -> tuple[float, float]:
    """95% CI for the mean (t-interval). Returns (lower, upper)."""
    if n <= 1 or stdev <= 0:
        return (mean, mean)
    df = n - 1
    t = _T_975.get(df, 2.0)  # fallback for large df
    half = t * (stdev / math.sqrt(n))
    return (mean - half, mean + half)

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "impl" / "src"))

import os
if "LABTRUST_KERNEL_DIR" not in os.environ:
    os.environ["LABTRUST_KERNEL_DIR"] = str(REPO_ROOT / "kernel")


def main() -> int:
    ap = argparse.ArgumentParser(description="E3: Recompute MAESTRO from TRACE, report variance")
    ap.add_argument("--runs", type=int, default=20, help="Number of thin-slice runs (seeds 1..N); default 20 for publishable")
    ap.add_argument("--out", type=Path, default=None, help="Write summary JSON here")
    ap.add_argument(
        "--scenarios",
        type=str,
        default="toy_lab_v0",
        help="Comma-separated scenario ids (e.g. toy_lab_v0,lab_profile_v0)",
    )
    ap.add_argument(
        "--standalone-verifier",
        action="store_true",
        help="Run verifier as separate process (verify_maestro_from_trace.py) for independent replay link",
    )
    args = ap.parse_args()

    from labtrust_portfolio.thinslice import run_thin_slice
    from labtrust_portfolio.maestro import maestro_report_from_trace

    verifier_script = REPO_ROOT / "scripts" / "verify_maestro_from_trace.py"
    env = os.environ.copy()
    env.setdefault("LABTRUST_KERNEL_DIR", str(REPO_ROOT / "kernel"))
    env.setdefault("PYTHONPATH", str(REPO_ROOT / "impl" / "src"))

    scenario_ids = [s.strip() for s in args.scenarios.split(",") if s.strip()]
    if not scenario_ids:
        scenario_ids = ["toy_lab_v0"]

    runs_dir = Path(__file__).resolve().parents[1] / "datasets" / "runs"
    per_scenario = []
    all_match_overall = True

    for scenario_id in scenario_ids:
        results = []
        for seed in range(1, args.runs + 1):
            run_dir = runs_dir / "e3" / scenario_id / f"seed_{seed}"
            run_dir.mkdir(parents=True, exist_ok=True)
            run_thin_slice(
                run_dir,
                seed=seed,
                drop_completion_prob=0.0,
                scenario_id=scenario_id,
                delay_fault_prob=0.0,
            )
            trace_path = run_dir / "trace.json"
            maestro_stored_path = run_dir / "maestro_report.json"
            trace = json.loads(trace_path.read_text(encoding="utf-8"))
            if args.standalone_verifier and verifier_script.exists():
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".json", delete=False
                ) as f:
                    out_path = f.name
                try:
                    r = subprocess.run(
                        [
                            sys.executable,
                            str(verifier_script),
                            str(trace_path),
                            out_path,
                        ],
                        capture_output=True,
                        cwd=str(REPO_ROOT),
                        env=env,
                    )
                    if r.returncode != 0:
                        recomputed = {"metrics": {"tasks_completed": 0, "coordination_messages": 0, "task_latency_ms_p95": 0.0}}
                    else:
                        recomputed = json.loads(Path(out_path).read_text(encoding="utf-8"))
                finally:
                    Path(out_path).unlink(missing_ok=True)
            else:
                recomputed = maestro_report_from_trace(
                    trace["run_id"], trace["scenario_id"], trace
                )
            stored = json.loads(maestro_stored_path.read_text(encoding="utf-8"))
            match = (
                recomputed["metrics"]["tasks_completed"]
                == stored["metrics"]["tasks_completed"]
                and recomputed["metrics"]["coordination_messages"]
                == stored["metrics"]["coordination_messages"]
            )
            results.append(
                {
                    "seed": seed,
                    "tasks_completed": recomputed["metrics"]["tasks_completed"],
                    "coordination_messages": recomputed["metrics"]["coordination_messages"],
                    "p95_latency_ms": recomputed["metrics"]["task_latency_ms_p95"],
                    "match": match,
                }
            )

        tasks = [r["tasks_completed"] for r in results]
        p95s = [r["p95_latency_ms"] for r in results]
        n = len(tasks)
        tc_mean = statistics.mean(tasks)
        tc_stdev = statistics.stdev(tasks) if n > 1 else 0.0
        p95_mean = statistics.mean(p95s)
        p95_stdev = statistics.stdev(p95s) if n > 1 else 0.0
        tc_ci = _ci95(tc_mean, tc_stdev, n)
        p95_ci = _ci95(p95_mean, p95_stdev, n)
        p99_idx = min(int(0.99 * len(p95s)), len(p95s) - 1) if p95s else -1
        p99_latency = sorted(p95s)[p99_idx] if p99_idx >= 0 else 0.0
        scenario_match = all(r["match"] for r in results)
        if not scenario_match:
            all_match_overall = False
        per_scenario.append({
            "scenario_id": scenario_id,
            "tasks_completed_mean": tc_mean,
            "tasks_completed_stdev": tc_stdev,
            "p95_latency_ms_mean": p95_mean,
            "p95_latency_ms_stdev": p95_stdev,
            "all_match": scenario_match,
            "tasks_completed_ci_95": list(tc_ci),
            "p95_latency_ms_ci_95": list(p95_ci),
            "p99_latency_ms": p99_latency,
            "per_run": results,
        })

    run_manifest = {
        "seeds": list(range(1, args.runs + 1)),
        "scenario_ids": scenario_ids,
        "fault_settings": {"drop_completion_prob": 0.0, "delay_fault_prob": 0.0},
        "script": "replay_link_e3.py",
    }
    if os.environ.get("GIT_SHA"):
        run_manifest["version"] = os.environ.get("GIT_SHA")
    # Excellence metrics (STANDARDS_OF_EXCELLENCE.md)
    first = per_scenario[0] if per_scenario else {}
    p95_ci = first.get("p95_latency_ms_ci_95", [0, 0])
    ci_width = float(p95_ci[1] - p95_ci[0]) if len(p95_ci) == 2 else 0.0
    conformance_pct = 100.0 if all_match_overall else (sum(1 for p in per_scenario if p["all_match"]) / len(per_scenario) * 100.0) if per_scenario else 0.0
    excellence_metrics = {
        "e3_ci_width_p95_ms": round(ci_width, 4),
        "conformance_match_pct": round(conformance_pct, 1),
        "n_scenarios": len(per_scenario),
        "n_runs_per_scenario": args.runs,
    }

    summary = {
        "runs": args.runs,
        "scenarios": scenario_ids,
        "all_match": all_match_overall,
        "all_match_per_scenario": [p["all_match"] for p in per_scenario],
        "run_manifest": run_manifest,
        "per_scenario": per_scenario,
        "success_criteria_met": {"e3_all_match": all_match_overall},
        "excellence_metrics": excellence_metrics,
    }
    if len(per_scenario) == 1:
        p = per_scenario[0]
        summary["tasks_completed_mean"] = p["tasks_completed_mean"]
        summary["tasks_completed_stdev"] = p["tasks_completed_stdev"]
        summary["p95_latency_ms_mean"] = p["p95_latency_ms_mean"]
        summary["p95_latency_ms_stdev"] = p["p95_latency_ms_stdev"]
        summary["tasks_completed_ci_95"] = p["tasks_completed_ci_95"]
        summary["p95_latency_ms_ci_95"] = p["p95_latency_ms_ci_95"]
        summary["p99_latency_ms"] = p["p99_latency_ms"]
        summary["per_run"] = p["per_run"]
    print("E3 Replay link summary:")
    print(json.dumps(summary, indent=2))
    if args.out:
        args.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return 0 if summary["all_match"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
