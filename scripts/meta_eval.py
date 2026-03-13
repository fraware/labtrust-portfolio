#!/usr/bin/env python3
"""
P8 Meta-Coordination: comparison eval. Run regime_stress_v0 with high fault;
compare CentralizedAdapter (fixed) vs MetaAdapter. Collapse = tasks_completed
below threshold. Writes datasets/runs/meta_eval/comparison.json.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "impl" / "src"))
if "LABTRUST_KERNEL_DIR" not in os.environ:
    os.environ["LABTRUST_KERNEL_DIR"] = str(REPO_ROOT / "kernel")

# Regime-stress scenario and fault level for eval
META_EVAL_SCENARIO = "regime_stress_v0"
# Collapse proxy: tasks_completed below this (no safety claim)
DEFAULT_COLLAPSE_THRESHOLD = 2


def main() -> int:
    ap = argparse.ArgumentParser(description="P8: Meta-controller vs fixed regime comparison")
    ap.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "datasets" / "runs" / "meta_eval",
        help="Output directory for comparison results",
    )
    ap.add_argument(
        "--seeds",
        type=str,
        default="1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20",
        help="Comma-separated seeds; default 20 for publishable; use 30 for sensitivity; CI may use fewer (e.g. 1,2,3)",
    )
    ap.add_argument(
        "--collapse-threshold",
        type=int,
        default=DEFAULT_COLLAPSE_THRESHOLD,
        help="tasks_completed below this => collapse",
    )
    ap.add_argument(
        "--drop-prob",
        type=float,
        default=0.15,
        help="drop_completion_prob for stress (default: 0.15). For non-vacuous collapse run meta_collapse_sweep first and use a value where collapse_count > 0.",
    )
    ap.add_argument(
        "--stress-preset",
        type=str,
        choices=("", "high", "very_high"),
        default="",
        help="If 'high', override --drop-prob to 0.25; if 'very_high', to 0.35 (optional second stress level)",
    )
    ap.add_argument(
        "--fault-threshold",
        type=int,
        default=1,
        help="Switch when fault_count > this (0 = naive: switch on any fault)",
    )
    ap.add_argument(
        "--run-naive",
        action="store_true",
        help="Also run meta with fault_threshold=0 (naive switching baseline)",
    )
    ap.add_argument(
        "--hysteresis",
        type=int,
        default=1,
        help="Require N consecutive fault observations before switch (thrash control; default 1)",
    )
    ap.add_argument(
        "--non-vacuous",
        action="store_true",
        help="Run or read collapse_sweep, use smallest drop_prob where collapse_count > 0; exit with message if none found",
    )
    ap.add_argument(
        "--collapse-sweep-path",
        type=Path,
        default=None,
        help="Path to collapse_sweep.json (used with --non-vacuous); default: <out>/collapse_sweep.json",
    )
    ap.add_argument(
        "--fallback-adapter",
        type=str,
        choices=("", "blackboard", "centralized", "retry_heavy"),
        default="",
        help="When set, meta run uses fallback adapter when switch is decided (two coordination paths). Use retry_heavy for architecturally distinct regimes (Centralized vs RetryHeavy).",
    )
    args = ap.parse_args()
    if args.stress_preset == "high":
        args.drop_prob = 0.25
    elif args.stress_preset == "very_high":
        args.drop_prob = 0.35

    if args.non_vacuous:
        import subprocess
        from collections import defaultdict
        sweep_path = args.collapse_sweep_path or (args.out / "collapse_sweep.json")
        if not sweep_path.exists():
            cmd = [
                sys.executable,
                str(REPO_ROOT / "scripts" / "meta_collapse_sweep.py"),
                "--out", str(args.out),
            ]
            r = subprocess.run(cmd, cwd=str(REPO_ROOT), env=os.environ, timeout=600)
            if r.returncode != 0:
                print("meta_collapse_sweep.py failed; cannot determine non-vacuous drop_prob", file=sys.stderr)
                return 1
            sweep_path = args.out / "collapse_sweep.json"
        data = json.loads(sweep_path.read_text(encoding="utf-8"))
        per_run = data.get("per_run", [])
        # Per drop_prob: count collapsed
        by_drop = defaultdict(lambda: {"count": 0, "collapsed": 0})
        for r in per_run:
            dp = r["drop_prob"]
            by_drop[dp]["count"] += 1
            if r.get("collapsed", False):
                by_drop[dp]["collapsed"] += 1
        chosen = None
        for dp in sorted(by_drop.keys()):
            if by_drop[dp]["collapsed"] > 0:
                chosen = dp
                break
        if chosen is None:
            print(
                "Non-vacuous: no drop_prob in sweep had collapse_count > 0. "
                "Table 1 should be presented as methodology and auditability only. Exiting.",
                file=sys.stderr,
            )
            return 1
        args.drop_prob = chosen
        print(f"Non-vacuous: using drop_prob={chosen} (collapse_count > 0 in sweep)", file=sys.stderr)

    from labtrust_portfolio.adapters.centralized import CentralizedAdapter
    from labtrust_portfolio.adapters.meta_adapter import MetaAdapter
    from labtrust_portfolio.adapters.base import run_adapter

    fallback_adapter = None
    if getattr(args, "fallback_adapter", ""):
        if args.fallback_adapter == "blackboard":
            from labtrust_portfolio.adapters.blackboard import BlackboardAdapter
            fallback_adapter = BlackboardAdapter()
        elif args.fallback_adapter == "centralized":
            fallback_adapter = CentralizedAdapter()
        elif args.fallback_adapter == "retry_heavy":
            from labtrust_portfolio.adapters.retry_heavy import RetryHeavyAdapter
            fallback_adapter = RetryHeavyAdapter()

    seeds = [int(s.strip()) for s in args.seeds.split(",") if s.strip()]
    scenario_id = META_EVAL_SCENARIO
    fault_params = {
        "drop_completion_prob": args.drop_prob,
        "delay_fault_prob": 0.0,
        "fault_threshold": args.fault_threshold,
        "hysteresis_consecutive": args.hysteresis,
    }
    threshold = args.collapse_threshold

    args.out.mkdir(parents=True, exist_ok=True)
    fixed_results = []
    meta_results = []
    naive_results = [] if args.run_naive else None

    centralized = CentralizedAdapter()
    meta = MetaAdapter()

    for seed in seeds:
        fix_dir = args.out / "fixed" / f"seed_{seed}"
        meta_dir = args.out / "meta" / f"seed_{seed}"
        fix_dir.mkdir(parents=True, exist_ok=True)
        meta_dir.mkdir(parents=True, exist_ok=True)

        fix_res = run_adapter(
            centralized, scenario_id, fix_dir, seed=seed, **fault_params
        )
        meta_kw = {**fault_params}
        if fallback_adapter is not None:
            meta_kw["fallback_adapter"] = fallback_adapter
        meta_res = run_adapter(
            meta, scenario_id, meta_dir, seed=seed, **meta_kw
        )

        m_fix = fix_res.maestro_report.get("metrics", {})
        m_meta = meta_res.maestro_report.get("metrics", {})
        fix_tasks = m_fix.get("tasks_completed", 0)
        meta_tasks = m_meta.get("tasks_completed", 0)
        meta_switches = meta_res.trace.get("metadata", {}).get("regime_switch_count", 0)
        fallback_tasks = meta_res.trace.get("metadata", {}).get("fallback_tasks_completed")
        # Optional collapse dimension: recovery_ok false (from report.faults)
        fix_recovery_ok = fix_res.maestro_report.get("faults", {}).get("recovery_ok", True)
        meta_recovery_ok = meta_res.maestro_report.get("faults", {}).get("recovery_ok", True)
        fix_collapse = (fix_tasks < threshold) or (fix_recovery_ok is False)
        meta_collapse = (meta_tasks < threshold) or (meta_recovery_ok is False)

        fixed_results.append({
            "seed": seed,
            "tasks_completed": fix_tasks,
            "collapse": fix_collapse,
            "recovery_ok": fix_recovery_ok,
        })
        meta_results.append({
            "seed": seed,
            "tasks_completed": meta_tasks,
            "regime_switch_count": meta_switches,
            "collapse": meta_collapse,
            "recovery_ok": meta_recovery_ok,
            "fallback_tasks_completed": fallback_tasks,
        })

        if args.run_naive:
            naive_params = {**fault_params, "fault_threshold": 0}
            naive_dir = args.out / "naive" / f"seed_{seed}"
            naive_dir.mkdir(parents=True, exist_ok=True)
            naive_res = run_adapter(
                meta, scenario_id, naive_dir, seed=seed, **naive_params
            )
            n_tasks = naive_res.maestro_report.get("metrics", {}).get(
                "tasks_completed", 0
            )
            n_switches = naive_res.trace.get("metadata", {}).get(
                "regime_switch_count", 0
            )
            n_recovery_ok = naive_res.maestro_report.get("faults", {}).get("recovery_ok", True)
            n_collapse = (n_tasks < threshold) or (n_recovery_ok is False)
            naive_results.append({
                "seed": seed,
                "tasks_completed": n_tasks,
                "regime_switch_count": n_switches,
                "collapse": n_collapse,
                "recovery_ok": n_recovery_ok,
            })

    import math
    import statistics

    fixed_collapses = sum(1 for r in fixed_results if r["collapse"])
    meta_collapses = sum(1 for r in meta_results if r["collapse"])
    fixed_tasks_mean = sum(r["tasks_completed"] for r in fixed_results) / len(fixed_results)
    meta_tasks_mean = sum(r["tasks_completed"] for r in meta_results) / len(meta_results)
    n_seeds = len(fixed_results)
    fixed_tc_list = [r["tasks_completed"] for r in fixed_results]
    meta_tc_list = [r["tasks_completed"] for r in meta_results]
    fixed_stdev = statistics.stdev(fixed_tc_list) if n_seeds > 1 else 0.0
    meta_stdev = statistics.stdev(meta_tc_list) if n_seeds > 1 else 0.0
    _T_975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}
    def _ci95(mean, stdev, n):
        if n <= 1 or stdev <= 0:
            return [mean, mean]
        t = _T_975.get(n - 1, 2.0)
        half = t * (stdev / math.sqrt(n))
        return [mean - half, mean + half]
    fixed_ci95 = _ci95(fixed_tasks_mean, fixed_stdev, n_seeds) if n_seeds >= 2 else [fixed_tasks_mean, fixed_tasks_mean]
    meta_ci95 = _ci95(meta_tasks_mean, meta_stdev, n_seeds) if n_seeds >= 2 else [meta_tasks_mean, meta_tasks_mean]

    collapse_def = f"tasks_completed < {threshold} or recovery_ok false"
    comparison = {
        "scenario_id": scenario_id,
        "drop_completion_prob": args.drop_prob,
        "fault_threshold": args.fault_threshold,
        "seeds": seeds,
        "collapse_definition": collapse_def,
        "collapse_threshold": threshold,
        "run_manifest": {
            "seeds": seeds,
            "seed_count": len(seeds),
            "scenario_id": scenario_id,
            "drop_completion_prob": args.drop_prob,
            "collapse_threshold": threshold,
            "fault_threshold": args.fault_threshold,
            "script": "meta_eval.py",
            "non_vacuous": getattr(args, "non_vacuous", False),
            "fallback_adapter": getattr(args, "fallback_adapter", "") or None,
        },
        "fixed": {
            "tasks_completed_mean": fixed_tasks_mean,
            "tasks_completed_stdev": fixed_stdev,
            "tasks_completed_ci95": fixed_ci95,
            "collapse_count": fixed_collapses,
            "per_seed": fixed_results,
        },
        "meta_controller": {
            "tasks_completed_mean": meta_tasks_mean,
            "tasks_completed_stdev": meta_stdev,
            "tasks_completed_ci95": meta_ci95,
            "collapse_count": meta_collapses,
            "per_seed": meta_results,
        },
        "meta_reduces_collapse": meta_collapses <= fixed_collapses,
        "no_safety_regression": meta_tasks_mean >= fixed_tasks_mean * 0.9,
        "fallback_tasks_completed_mean": (
            statistics.mean([r["fallback_tasks_completed"] for r in meta_results if r.get("fallback_tasks_completed") is not None])
            if any(r.get("fallback_tasks_completed") is not None for r in meta_results) else None
        ),
        "success_criteria_met": {
            "no_safety_regression": meta_tasks_mean >= fixed_tasks_mean * 0.9,
            "meta_reduces_collapse": meta_collapses <= fixed_collapses,
            "trigger_met": (
                meta_tasks_mean >= fixed_tasks_mean * 0.9 and meta_collapses <= fixed_collapses
            ),
        },
    }
    # Excellence metrics (STANDARDS_OF_EXCELLENCE.md) + comparison stats (REPORTING_STANDARD)
    from labtrust_portfolio.stats import (
        bootstrap_ci_difference,
        effect_size_mean_diff,
        paired_t_test,
        power_paired_t_test,
    )
    diff_mean, cohens_d = effect_size_mean_diff(meta_tc_list, fixed_tc_list)
    diff_ci95 = bootstrap_ci_difference(meta_tc_list, fixed_tc_list, seed=42)
    t_stat, p_value, dof = paired_t_test(meta_tc_list, fixed_tc_list)
    power_post_hoc = power_paired_t_test(meta_tc_list, fixed_tc_list, alpha=0.05)
    difference_ci_width = (diff_ci95[1] - diff_ci95[0]) if not (math.isnan(diff_ci95[0]) or math.isnan(diff_ci95[1])) else None
    collapse_reduction = fixed_collapses - meta_collapses if fixed_collapses >= meta_collapses else 0
    meta_switch_total = sum(r.get("regime_switch_count", 0) for r in meta_results)
    comparison["excellence_metrics"] = {
        "difference_mean": round(diff_mean, 4),
        "difference_ci95": [round(diff_ci95[0], 4), round(diff_ci95[1], 4)],
        "difference_ci_width": round(difference_ci_width, 4) if difference_ci_width is not None else None,
        "paired_t_p_value": round(p_value, 4) if not math.isnan(p_value) else None,
        "alpha": 0.05,
        "power_post_hoc": round(power_post_hoc, 4) if not math.isnan(power_post_hoc) else None,
        "cohens_d": round(cohens_d, 4) if not math.isnan(cohens_d) else None,
        "collapse_reduction_vs_fixed": collapse_reduction,
        "no_safety_regression": comparison["no_safety_regression"],
        "switch_audit_trail_total": meta_switch_total,
        "trigger_met": comparison["success_criteria_met"]["trigger_met"],
    }
    if naive_results is not None:
        naive_tasks_mean = (
            sum(r["tasks_completed"] for r in naive_results) / len(naive_results)
        )
        naive_switches = sum(r["regime_switch_count"] for r in naive_results)
        naive_tc_list = [r["tasks_completed"] for r in naive_results]
        naive_stdev = statistics.stdev(naive_tc_list) if len(naive_results) > 1 else 0.0
        naive_ci95 = _ci95(naive_tasks_mean, naive_stdev, len(naive_results)) if len(naive_results) >= 2 else [naive_tasks_mean, naive_tasks_mean]
        comparison["naive_switch_baseline"] = {
            "fault_threshold": 0,
            "tasks_completed_mean": naive_tasks_mean,
            "tasks_completed_stdev": naive_stdev,
            "tasks_completed_ci95": naive_ci95,
            "regime_switch_count_total": naive_switches,
            "per_seed": naive_results,
        }
    out_file = args.out / "comparison.json"
    out_file.write_text(json.dumps(comparison, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(comparison, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
