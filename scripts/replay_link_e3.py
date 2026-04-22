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

if "LABTRUST_KERNEL_DIR" not in os.environ:
    os.environ["LABTRUST_KERNEL_DIR"] = str(REPO_ROOT / "kernel")


E3_STRESS_FAULT_PARAMS = {
    "drop_completion_prob": 0.08,
    "delay_fault_prob": 0.08,
    "delay_p95_ms": 55.0,
    "reordered_event_fault_prob": 0.05,
}


def _run_replay_block(
    *,
    runs_dir: Path,
    run_parent: str,
    scenario_ids: list[str],
    n_runs: int,
    thin_slice_kwargs: dict,
    standalone_verifier: bool,
    verifier_script: Path,
    env: dict,
) -> tuple[list[dict], bool, bool]:
    """Returns (per_scenario, all_weak_match, all_strong_match)."""
    from labtrust_portfolio.maestro import maestro_report_from_trace
    from labtrust_portfolio.p0_e4_matrix import strong_replay_equivalent, weak_replay_match
    from labtrust_portfolio.thinslice import run_thin_slice

    per_scenario: list[dict] = []
    all_weak = True
    all_strong = True

    for scenario_id in scenario_ids:
        results = []
        for seed in range(1, n_runs + 1):
            run_dir = runs_dir / run_parent / scenario_id / f"seed_{seed}"
            run_dir.mkdir(parents=True, exist_ok=True)
            run_thin_slice(
                run_dir,
                seed=seed,
                scenario_id=scenario_id,
                **thin_slice_kwargs,
            )
            trace_path = run_dir / "trace.json"
            maestro_stored_path = run_dir / "maestro_report.json"
            trace = json.loads(trace_path.read_text(encoding="utf-8"))
            if standalone_verifier and verifier_script.exists():
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
                        recomputed = {
                            "metrics": {
                                "tasks_completed": 0,
                                "coordination_messages": 0,
                                "task_latency_ms_p95": 0.0,
                            }
                        }
                    else:
                        recomputed = json.loads(Path(out_path).read_text(encoding="utf-8"))
                finally:
                    Path(out_path).unlink(missing_ok=True)
            else:
                recomputed = maestro_report_from_trace(
                    trace["run_id"], trace["scenario_id"], trace
                )
            stored = json.loads(maestro_stored_path.read_text(encoding="utf-8"))
            weak = weak_replay_match(recomputed, stored)
            strong = strong_replay_equivalent(recomputed, stored, trace)
            results.append(
                {
                    "seed": seed,
                    "tasks_completed": recomputed["metrics"]["tasks_completed"],
                    "coordination_messages": recomputed["metrics"]["coordination_messages"],
                    "p95_latency_ms": recomputed["metrics"]["task_latency_ms_p95"],
                    "weak_replay_match": weak,
                    "strong_replay_match": strong,
                    "match": weak,
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
        scenario_weak = all(r["weak_replay_match"] for r in results)
        scenario_strong = all(r["strong_replay_match"] for r in results)
        if not scenario_weak:
            all_weak = False
        if not scenario_strong:
            all_strong = False
        per_scenario.append(
            {
                "scenario_id": scenario_id,
                "tasks_completed_mean": tc_mean,
                "tasks_completed_stdev": tc_stdev,
                "p95_latency_ms_mean": p95_mean,
                "p95_latency_ms_stdev": p95_stdev,
                "all_match": scenario_weak,
                "all_strong_match": scenario_strong,
                "tasks_completed_ci_95": list(tc_ci),
                "p95_latency_ms_ci_95": list(p95_ci),
                "p99_latency_ms": p99_latency,
                "per_run": results,
            }
        )
    return per_scenario, all_weak, all_strong


def _git_head() -> str | None:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if r.returncode == 0 and (r.stdout or "").strip():
            return r.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return None


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
    ap.add_argument(
        "--stress-appendix",
        action="store_true",
        help="Also run an optional faulted replay block under datasets/runs/e3_stress/ (appendix evidence)",
    )
    args = ap.parse_args()

    verifier_script = REPO_ROOT / "scripts" / "verify_maestro_from_trace.py"
    env = os.environ.copy()
    env.setdefault("LABTRUST_KERNEL_DIR", str(REPO_ROOT / "kernel"))
    env.setdefault("PYTHONPATH", str(REPO_ROOT / "impl" / "src"))

    scenario_ids = [s.strip() for s in args.scenarios.split(",") if s.strip()]
    if not scenario_ids:
        scenario_ids = ["toy_lab_v0"]

    runs_dir = Path(__file__).resolve().parents[1] / "datasets" / "runs"
    baseline_kwargs = {"drop_completion_prob": 0.0, "delay_fault_prob": 0.0}
    per_scenario, all_match_overall, all_strong_match_overall = _run_replay_block(
        runs_dir=runs_dir,
        run_parent="e3",
        scenario_ids=scenario_ids,
        n_runs=args.runs,
        thin_slice_kwargs=baseline_kwargs,
        standalone_verifier=bool(args.standalone_verifier),
        verifier_script=verifier_script,
        env=env,
    )

    stress_appendix = None
    if args.stress_appendix:
        sp, _, stress_strong = _run_replay_block(
            runs_dir=runs_dir,
            run_parent="e3_stress",
            scenario_ids=scenario_ids,
            n_runs=args.runs,
            thin_slice_kwargs=dict(E3_STRESS_FAULT_PARAMS),
            standalone_verifier=bool(args.standalone_verifier),
            verifier_script=verifier_script,
            env=env,
        )
        stress_appendix = {
            "fault_settings": dict(E3_STRESS_FAULT_PARAMS),
            "run_parent": "e3_stress",
            "per_scenario": sp,
            "all_strong_match": stress_strong,
        }

    run_manifest = {
        "seeds": list(range(1, args.runs + 1)),
        "scenario_ids": scenario_ids,
        "fault_settings": baseline_kwargs,
        "script": "replay_link_e3.py",
        "standalone_verifier": bool(args.standalone_verifier),
        "replay_match_definitions": {
            "weak": "tasks_completed and coordination_messages only",
            "strong": "full MAESTRO core (run_outcome, metrics, safety, coordination_efficiency, faults) plus PONR witness coverage when applicable",
        },
    }
    _ver = os.environ.get("GIT_SHA") or _git_head()
    if _ver:
        run_manifest["version"] = _ver
    # Excellence metrics (STANDARDS_OF_EXCELLENCE.md)
    first = per_scenario[0] if per_scenario else {}
    p95_ci = first.get("p95_latency_ms_ci_95", [0, 0])
    ci_width = float(p95_ci[1] - p95_ci[0]) if len(p95_ci) == 2 else 0.0
    conformance_pct = 100.0 if all_match_overall else (sum(1 for p in per_scenario if p["all_match"]) / len(per_scenario) * 100.0) if per_scenario else 0.0
    strong_pct = (
        100.0
        if all_strong_match_overall
        else (sum(1 for p in per_scenario if p.get("all_strong_match")) / len(per_scenario) * 100.0)
        if per_scenario
        else 0.0
    )
    excellence_metrics = {
        "e3_ci_width_p95_ms": round(ci_width, 4),
        "conformance_match_pct": round(conformance_pct, 1),
        "strong_replay_match_pct": round(strong_pct, 1),
        "n_scenarios": len(per_scenario),
        "n_runs_per_scenario": args.runs,
    }

    summary = {
        "runs": args.runs,
        "scenarios": scenario_ids,
        "all_match": all_match_overall,
        "all_strong_match": all_strong_match_overall,
        "all_match_per_scenario": [p["all_match"] for p in per_scenario],
        "all_strong_match_per_scenario": [p.get("all_strong_match") for p in per_scenario],
        "run_manifest": run_manifest,
        "per_scenario": per_scenario,
        "success_criteria_met": {"e3_all_match": all_match_overall, "e3_all_strong_match": all_strong_match_overall},
        "excellence_metrics": excellence_metrics,
    }
    if stress_appendix is not None:
        summary["stress_appendix"] = stress_appendix
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
