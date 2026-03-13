#!/usr/bin/env python3
"""
Sensitivity seed sweep: run a key eval (meta_eval or rep_cps_eval) at N=10, 20, 30
and record difference_mean, difference_ci95, difference_ci_width, paired_t_p_value per N.
Writes datasets/runs/sensitivity_sweep/sensitivity_summary.json.
Usage:
  PYTHONPATH=impl/src python scripts/sensitivity_seed_sweep.py [--eval meta|rep_cps] [--out DIR]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _seeds_list(n: int) -> str:
    return ",".join(str(i) for i in range(1, n + 1))


def run_meta_eval(seeds: str, out_dir: Path) -> dict | None:
    env = os.environ.copy()
    env.setdefault("LABTRUST_KERNEL_DIR", str(REPO / "kernel"))
    env["PYTHONPATH"] = str(REPO / "impl" / "src")
    run_dir = out_dir / "meta_eval" / f"n_{len(seeds.split(','))}"
    run_dir.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        [
            sys.executable,
            str(REPO / "scripts" / "meta_eval.py"),
            "--seeds", seeds,
            "--out", str(run_dir),
        ],
        cwd=str(REPO),
        env=env,
        capture_output=True,
        text=True,
        timeout=600,
    )
    if r.returncode != 0:
        return None
    comp_path = run_dir / "comparison.json"
    if not comp_path.exists():
        return None
    data = json.loads(comp_path.read_text(encoding="utf-8"))
    em = data.get("excellence_metrics", {})
    return {
        "n": len(seeds.split(",")),
        "difference_mean": em.get("difference_mean"),
        "difference_ci95": em.get("difference_ci95"),
        "difference_ci_width": em.get("difference_ci_width"),
        "paired_t_p_value": em.get("paired_t_p_value"),
        "power_post_hoc": em.get("power_post_hoc"),
    }


def run_scaling_sweep(n: int, out_dir: Path) -> dict | None:
    """Run generate_multiscenario_runs with n seeds, then scaling_heldout_eval; return metrics."""
    env = os.environ.copy()
    env.setdefault("LABTRUST_KERNEL_DIR", str(REPO / "kernel"))
    env["PYTHONPATH"] = str(REPO / "impl" / "src")
    runs_subdir = out_dir / "scaling" / f"n_{n}"
    runs_subdir.mkdir(parents=True, exist_ok=True)
    r1 = subprocess.run(
        [
            sys.executable,
            str(REPO / "scripts" / "generate_multiscenario_runs.py"),
            "--seeds", str(n),
            "--out", str(runs_subdir),
            "--fault-mix",
        ],
        cwd=str(REPO),
        env=env,
        capture_output=True,
        text=True,
        timeout=900,
    )
    if r1.returncode != 0:
        return None
    eval_out = runs_subdir / "eval"
    eval_out.mkdir(parents=True, exist_ok=True)
    r2 = subprocess.run(
        [
            sys.executable,
            str(REPO / "scripts" / "scaling_heldout_eval.py"),
            "--runs-dir", str(runs_subdir),
            "--out", str(eval_out),
        ],
        cwd=str(REPO),
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if r2.returncode != 0:
        return None
    results_path = eval_out / "heldout_results.json"
    if not results_path.exists():
        return None
    data = json.loads(results_path.read_text(encoding="utf-8"))
    scaling_fit = data.get("scaling_fit") or {}
    return {
        "n": n,
        "overall_baseline_mae": data.get("overall_baseline_mae"),
        "overall_regression_mae": data.get("overall_regression_mae"),
        "overall_feat_baseline_mae": data.get("overall_feat_baseline_mae"),
        "scaling_exponent": scaling_fit.get("scaling_exponent"),
        "scaling_r_squared": scaling_fit.get("scaling_r2"),
        "ci_width_95_baseline_mae": data.get("excellence_metrics", {}).get("ci_width_95_baseline_mae"),
    }


def run_rep_cps_eval(seeds: str, out_dir: Path) -> dict | None:
    env = os.environ.copy()
    env.setdefault("LABTRUST_KERNEL_DIR", str(REPO / "kernel"))
    env["PYTHONPATH"] = str(REPO / "impl" / "src")
    run_dir = out_dir / "rep_cps_eval" / f"n_{len(seeds.split(','))}"
    run_dir.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        [
            sys.executable,
            str(REPO / "scripts" / "rep_cps_eval.py"),
            "--seeds", seeds,
            "--scenarios", "toy_lab_v0",
            "--delay-sweep", "0.05",
            "--out", str(run_dir),
        ],
        cwd=str(REPO),
        env=env,
        capture_output=True,
        text=True,
        timeout=600,
    )
    if r.returncode != 0:
        return None
    summary_path = run_dir / "summary.json"
    if not summary_path.exists():
        return None
    data = json.loads(summary_path.read_text(encoding="utf-8"))
    em = data.get("excellence_metrics", {})
    return {
        "n": len(seeds.split(",")),
        "difference_mean": em.get("difference_mean"),
        "difference_ci95": em.get("difference_ci95"),
        "difference_ci_width": em.get("difference_ci_width"),
        "paired_t_p_value": em.get("paired_t_p_value"),
        "power_post_hoc": em.get("power_post_hoc"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Sensitivity seed sweep: run eval at N=10,20,30")
    ap.add_argument(
        "--eval",
        choices=("meta", "rep_cps", "scaling"),
        default="meta",
        help="Eval to run (meta_eval, rep_cps_eval, or scaling)",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=REPO / "datasets" / "runs" / "sensitivity_sweep",
        help="Output directory for sweep results",
    )
    ap.add_argument(
        "--ns",
        type=str,
        default="10,20,30",
        help="Comma-separated sample sizes (default 10,20,30)",
    )
    args = ap.parse_args()
    ns = [int(x.strip()) for x in args.ns.split(",") if x.strip()]
    if args.eval == "scaling":
        results = []
        for n in ns:
            row = run_scaling_sweep(n, args.out)
            if row:
                results.append(row)
            else:
                results.append({"n": n, "error": "run failed or missing output"})
        args.out.mkdir(parents=True, exist_ok=True)
        summary = {"eval": "scaling", "script": "sensitivity_seed_sweep.py", "sweep": results}
        out_file = args.out / "scaling_sensitivity.json"
        out_file.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2))
        return 0 if all("error" not in r for r in results) else 1
    runner = run_meta_eval if args.eval == "meta" else run_rep_cps_eval
    results = []
    for n in ns:
        seeds = _seeds_list(n)
        row = runner(seeds, args.out)
        if row:
            results.append(row)
        else:
            results.append({"n": n, "error": "run failed or missing output"})
    summary = {
        "eval": args.eval,
        "script": "sensitivity_seed_sweep.py",
        "sweep": results,
    }
    args.out.mkdir(parents=True, exist_ok=True)
    out_file = args.out / "sensitivity_summary.json"
    out_file.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if all("error" not in r for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
