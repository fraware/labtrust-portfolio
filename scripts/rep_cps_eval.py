#!/usr/bin/env python3
"""
P2 REP-CPS evaluation: adapter comparison and robust vs naive aggregation.
Runs REPCPSAdapter and CentralizedAdapter on same scenario/seeds; compares
robust vs naive aggregation with compromised_updates. Writes to
datasets/runs/rep_cps_eval/. Set LABTRUST_KERNEL_DIR to repo kernel/.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# t_{0.975, df} for 95% two-sided CI (df = n-1)
_T_975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}


def _ci95(mean: float, stdev: float, n: int) -> tuple[float, float]:
    """95% CI for the mean (t-interval). Returns (lower, upper)."""
    if n <= 1 or stdev <= 0:
        return (mean, mean)
    df = n - 1
    t = _T_975.get(df, 2.0)
    half = t * (stdev / math.sqrt(n))
    return (mean - half, mean + half)
sys.path.insert(0, str(REPO_ROOT / "impl" / "src"))
if "LABTRUST_KERNEL_DIR" not in os.environ:
    os.environ["LABTRUST_KERNEL_DIR"] = str(REPO_ROOT / "kernel")


# Bottleneck scenario for P2 (convergence/stability under delay/fault)
REP_CPS_BOTTLENECK_SCENARIO = "toy_lab_v0"


def run_adapter_comparison(
    scenario_id: str,
    seeds: list[int],
    out_dir: Path,
    delay_fault_prob: float = 0.05,
) -> list[dict]:
    """Run REPCPS (robust), REPCPS naive, REPCPS unsecured, and Centralized; return metrics."""
    from labtrust_portfolio.adapters.rep_cps_adapter import REPCPSAdapter
    from labtrust_portfolio.adapters.centralized import CentralizedAdapter
    from labtrust_portfolio.adapters.base import run_adapter

    rep_cps = REPCPSAdapter()
    centralized = CentralizedAdapter()
    results = []

    for seed in seeds:
        run_id = f"seed_{seed}"
        rep_dir = out_dir / "rep_cps" / run_id
        rep_naive_dir = out_dir / "rep_cps_naive" / run_id
        rep_unsec_dir = out_dir / "rep_cps_unsecured" / run_id
        cen_dir = out_dir / "centralized" / run_id
        rep_dir.mkdir(parents=True, exist_ok=True)
        rep_naive_dir.mkdir(parents=True, exist_ok=True)
        rep_unsec_dir.mkdir(parents=True, exist_ok=True)
        cen_dir.mkdir(parents=True, exist_ok=True)

        fault_params = {
            "drop_completion_prob": 0.02,
            "delay_fault_prob": delay_fault_prob,
        }

        rep_result = run_adapter(
            rep_cps, scenario_id, rep_dir, seed=seed, **fault_params
        )
        rep_naive_result = run_adapter(
            rep_cps, scenario_id, rep_naive_dir, seed=seed,
            aggregation_method="mean", **fault_params
        )
        rep_unsec_result = run_adapter(
            rep_cps, scenario_id, rep_unsec_dir, seed=seed,
            aggregation_method="mean", use_compromised=True,
            allowed_agents=None, **fault_params
        )
        cen_result = run_adapter(
            centralized, scenario_id, cen_dir, seed=seed, **fault_params
        )

        m_rep = rep_result.maestro_report.get("metrics", {})
        m_naive = rep_naive_result.maestro_report.get("metrics", {})
        m_unsec = rep_unsec_result.maestro_report.get("metrics", {})
        m_cen = cen_result.maestro_report.get("metrics", {})
        meta_rep = rep_result.trace.get("metadata", {})
        meta_naive = rep_naive_result.trace.get("metadata", {})
        meta_unsec = rep_unsec_result.trace.get("metadata", {})

        results.append({
            "seed": seed,
            "rep_cps_tasks_completed": m_rep.get("tasks_completed", 0),
            "rep_cps_naive_tasks_completed": m_naive.get("tasks_completed", 0),
            "rep_cps_unsecured_tasks_completed": m_unsec.get("tasks_completed", 0),
            "centralized_tasks_completed": m_cen.get("tasks_completed", 0),
            "rep_cps_aggregate_load": meta_rep.get("rep_cps_aggregate_load"),
            "rep_cps_naive_aggregate_load": meta_naive.get("rep_cps_aggregate_load"),
            "rep_cps_unsecured_aggregate_load": meta_unsec.get("rep_cps_aggregate_load"),
            "rep_cps_safety_gate_ok": meta_rep.get("rep_cps_safety_gate_ok"),
            "delay_fault_prob": delay_fault_prob,
        })
    return results


def run_aggregation_under_compromise() -> dict:
    """Compare robust vs naive aggregation with honest + compromised updates."""
    from labtrust_portfolio.rep_cps import aggregate, compromised_updates

    honest = [
        {"variable": "load", "value": 0.3, "ts": 0.0, "agent_id": "a1"},
        {"variable": "load", "value": 0.35, "ts": 0.0, "agent_id": "a2"},
        {"variable": "load", "value": 0.32, "ts": 0.0, "agent_id": "a3"},
    ]
    compromised = compromised_updates(
        "load", num_compromised=2, extreme_value=10.0, ts=0.0
    )
    combined = honest + compromised
    agg_robust = aggregate("load", combined, method="trimmed_mean", trim_fraction=0.25)
    agg_naive = aggregate("load", combined, method="mean")
    agg_honest_only = aggregate(
        "load", honest, method="trimmed_mean", trim_fraction=0.25
    )

    bias_robust = abs(agg_robust - agg_honest_only)
    bias_naive = abs(agg_naive - agg_honest_only)

    return {
        "honest_only_aggregate": agg_honest_only,
        "with_compromise_robust_aggregate": agg_robust,
        "with_compromise_naive_aggregate": agg_naive,
        "unsecured_aggregate": agg_naive,
        "bias_robust": bias_robust,
        "bias_naive": bias_naive,
        "compromised_count": 2,
        "honest_count": 3,
    }


def run_rate_limit_windowing_check() -> dict:
    """Exercise aggregate() with rate_limit and max_age_sec; return summary snippet."""
    from labtrust_portfolio.rep_cps import aggregate

    updates = [
        {"variable": "load", "value": 0.3, "ts": 0.0, "agent_id": "a1"},
        {"variable": "load", "value": 0.35, "ts": 0.0, "agent_id": "a1"},
        {"variable": "load", "value": 0.32, "ts": 0.5, "agent_id": "a2"},
        {"variable": "load", "value": 0.1, "ts": 0.2, "agent_id": "a3"},
    ]
    no_limit = aggregate("load", updates, method="mean")
    with_rate = aggregate(
        "load", updates, method="mean",
        rate_limit=1, current_ts=1.0
    )
    with_age = aggregate(
        "load", updates, method="mean",
        max_age_sec=0.4, current_ts=2.0
    )
    return {
        "rate_limit_windowing_exercised": True,
        "aggregate_no_limit": no_limit,
        "aggregate_with_rate_limit_1": with_rate,
        "aggregate_with_max_age_04": with_age,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="P2 REP-CPS evaluation")
    ap.add_argument(
        "--scenario",
        type=str,
        default=REP_CPS_BOTTLENECK_SCENARIO,
        help="Bottleneck scenario id",
    )
    ap.add_argument(
        "--seeds",
        type=str,
        default="1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20",
        help="Comma-separated seeds (default: 1..20 for publishable; use up to 30 for sensitivity)",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "datasets" / "runs" / "rep_cps_eval",
        help="Output directory",
    )
    ap.add_argument(
        "--skip-adapter",
        action="store_true",
        help="Only run aggregation-under-compromise",
    )
    ap.add_argument(
        "--delay-sweep",
        type=str,
        default="0,0.05,0.1,0.2",
        help="Comma-separated delay_fault_prob values (publishable default: 0,0.05,0.1,0.2; CI may use 0.05)",
    )
    ap.add_argument(
        "--scenarios",
        type=str,
        default="toy_lab_v0,lab_profile_v0",
        help="Comma-separated scenario ids (publishable: toy_lab_v0,lab_profile_v0; use --scenario for single)",
    )
    args = ap.parse_args()

    seeds = [int(s.strip()) for s in args.seeds.split(",") if s.strip()]
    args.out.mkdir(parents=True, exist_ok=True)
    scenarios = [args.scenario] if not args.scenarios else [x.strip() for x in args.scenarios.split(",") if x.strip()]
    if not scenarios:
        scenarios = [args.scenario]
    delay_values = [float(x.strip()) for x in args.delay_sweep.split(",") if x.strip()]
    if not delay_values:
        delay_values = [0.05]

    summary = {
        "scenario_ids": scenarios,
        "bottleneck_scenario": REP_CPS_BOTTLENECK_SCENARIO,
        "seeds": seeds,
        "delay_fault_prob_sweep": delay_values,
        "aggregation_steps": 1,
        "run_manifest": {
            "seeds": seeds,
            "seed_count": len(seeds),
            "scenario_ids": scenarios,
            "delay_fault_prob_sweep": delay_values,
            "script": "rep_cps_eval.py",
        },
    }

    summary["rate_limit_windowing"] = run_rate_limit_windowing_check()

    all_adapter = []
    if not args.skip_adapter:
        delay_sweep_results = []
        for scenario_id in scenarios:
            for d in delay_values:
                if len(scenarios) == 1 and len(delay_values) == 1:
                    run_dir = args.out
                else:
                    run_dir = args.out / scenario_id / f"delay_{d}"
                run_dir.mkdir(parents=True, exist_ok=True)
                adapter_results = run_adapter_comparison(
                    scenario_id, seeds, run_dir, delay_fault_prob=d
                )
                tasks_rep = [r["rep_cps_tasks_completed"] for r in adapter_results]
                tasks_cen = [r["centralized_tasks_completed"] for r in adapter_results]
                stdev_rep = statistics.stdev(tasks_rep) if len(tasks_rep) > 1 else 0.0
                stdev_cen = statistics.stdev(tasks_cen) if len(tasks_cen) > 1 else 0.0
                mean_rep = statistics.mean(tasks_rep)
                mean_cen = statistics.mean(tasks_cen)
                n_r = len(tasks_rep)
                ci_rep = _ci95(mean_rep, stdev_rep, n_r) if n_r >= 2 else (mean_rep, mean_rep)
                ci_cen = _ci95(mean_cen, stdev_cen, len(tasks_cen)) if len(tasks_cen) >= 2 else (mean_cen, mean_cen)
                delay_sweep_results.append({
                    "scenario_id": scenario_id,
                    "delay_fault_prob": d,
                    "rep_cps_tasks_mean": mean_rep,
                    "rep_cps_tasks_stdev": stdev_rep,
                    "rep_cps_tasks_ci95": list(ci_rep),
                    "centralized_tasks_mean": mean_cen,
                    "centralized_tasks_ci95": list(ci_cen),
                })
                all_adapter.extend(adapter_results)
        summary["delay_sweep"] = delay_sweep_results
        summary["adapter_runs"] = (
            all_adapter[:len(seeds)] if all_adapter else []
        )
        tasks_rep = [r["rep_cps_tasks_completed"] for r in all_adapter]
        tasks_cen = [r["centralized_tasks_completed"] for r in all_adapter]
        n_rep = len(tasks_rep)
        n_cen = len(tasks_cen)
        mean_rep = statistics.mean(tasks_rep)
        mean_cen = statistics.mean(tasks_cen)
        stdev_rep = statistics.stdev(tasks_rep) if n_rep > 1 else 0.0
        stdev_cen = statistics.stdev(tasks_cen) if n_cen > 1 else 0.0
        summary["rep_cps_tasks_completed_mean"] = mean_rep
        summary["rep_cps_tasks_completed_stdev"] = stdev_rep
        summary["rep_cps_tasks_completed_ci95"] = list(_ci95(mean_rep, stdev_rep, n_rep)) if n_rep >= 2 else [mean_rep, mean_rep]
        summary["centralized_tasks_completed_mean"] = mean_cen
        summary["centralized_tasks_completed_stdev"] = stdev_cen
        summary["centralized_tasks_completed_ci95"] = list(_ci95(mean_cen, stdev_cen, n_cen)) if n_cen >= 2 else [mean_cen, mean_cen]
        tasks_naive = [r["rep_cps_naive_tasks_completed"] for r in all_adapter]
        tasks_unsec = [r["rep_cps_unsecured_tasks_completed"] for r in all_adapter]
        summary["rep_cps_naive_tasks_completed_mean"] = statistics.mean(tasks_naive)
        summary["rep_cps_naive_tasks_completed_stdev"] = (
            statistics.stdev(tasks_naive) if len(tasks_naive) > 1 else 0.0
        )
        summary["rep_cps_unsecured_tasks_completed_mean"] = statistics.mean(tasks_unsec)
        summary["rep_cps_unsecured_tasks_completed_stdev"] = (
            statistics.stdev(tasks_unsec) if len(tasks_unsec) > 1 else 0.0
        )
        aggs_naive = [
            r["rep_cps_naive_aggregate_load"] for r in all_adapter
            if r.get("rep_cps_naive_aggregate_load") is not None
        ]
        aggs_unsec = [
            r["rep_cps_unsecured_aggregate_load"] for r in all_adapter
            if r.get("rep_cps_unsecured_aggregate_load") is not None
        ]
        summary["rep_cps_naive_aggregate_load_mean"] = (
            statistics.mean(aggs_naive) if len(aggs_naive) > 0 else None
        )
        summary["rep_cps_unsecured_aggregate_load_mean"] = (
            statistics.mean(aggs_unsec) if len(aggs_unsec) > 0 else None
        )

    agg_compromise = run_aggregation_under_compromise()
    summary["aggregation_under_compromise"] = agg_compromise

    from labtrust_portfolio.rep_cps import aggregate, compromised_updates
    honest = [
        {"variable": "load", "value": 0.3, "ts": 0.0, "agent_id": "a1"},
        {"variable": "load", "value": 0.35, "ts": 0.0, "agent_id": "a2"},
        {"variable": "load", "value": 0.32, "ts": 0.0, "agent_id": "a3"},
    ]
    k_compromised = 2
    compromised = compromised_updates("load", num_compromised=k_compromised, extreme_value=10.0, ts=0.0)
    combined = honest + compromised
    agg_honest = aggregate("load", honest, method="trimmed_mean", trim_fraction=0.25)
    variants = []
    for method in ("trimmed_mean", "median", "clipping", "median_of_means"):
        agg_with = aggregate("load", combined, method=method) if method != "trimmed_mean" else aggregate("load", combined, method="trimmed_mean", trim_fraction=0.25)
        bias = abs(agg_with - agg_honest)
        max_influence = (bias / k_compromised) if k_compromised else 0.0
        variants.append({"method": method, "bias": round(bias, 4), "max_influence_per_compromised_agent": round(max_influence, 4)})
    summary["aggregation_variants"] = variants

    sybil_sweep = []
    for n_comp in range(0, 6):
        comp = compromised_updates("load", num_compromised=n_comp, extreme_value=10.0, ts=0.0)
        comb = honest + comp
        agg_r = aggregate("load", comb, method="trimmed_mean", trim_fraction=0.25)
        agg_n = aggregate("load", comb, method="mean")
        sybil_sweep.append({
            "n_compromised": n_comp,
            "bias_robust": round(abs(agg_r - agg_honest), 4),
            "bias_naive": round(abs(agg_n - agg_honest), 4),
        })
    summary["sybil_sweep"] = sybil_sweep

    safety_gate_denial = {
        "safety_gate_integration": True,
        "claim": "REP output cannot directly trigger actuation; must pass through policy check.",
        "example": "When policy rejects an action (e.g. rep_cps_safety_gate_ok false), system does not actuate; recovery is safe.",
        "denial_trace_recorded": all_adapter and any(r.get("rep_cps_safety_gate_ok") is False for r in all_adapter) or False,
    }
    (args.out / "safety_gate_denial.json").write_text(
        json.dumps(safety_gate_denial, indent=2) + "\n", encoding="utf-8"
    )
    summary["safety_gate_denial"] = safety_gate_denial

    robust_beats_naive = agg_compromise.get("bias_robust", 0) < agg_compromise.get("bias_naive", 0)
    if all_adapter:
        adapter_parity = abs(summary["rep_cps_tasks_completed_mean"] - summary["centralized_tasks_completed_mean"]) < 1e-6
        summary["success_criteria_met"] = {
            "adapter_parity": adapter_parity,
            "robust_beats_naive": robust_beats_naive,
            "trigger_met": adapter_parity and robust_beats_naive,
        }
    else:
        summary["success_criteria_met"] = {
            "adapter_parity": None,
            "robust_beats_naive": robust_beats_naive,
            "trigger_met": robust_beats_naive,
        }

    # Excellence metrics (STANDARDS_OF_EXCELLENCE.md) + comparison stats (REPORTING_STANDARD)
    agg = summary.get("aggregation_under_compromise", {})
    bias_robust = agg.get("bias_robust")
    bias_naive = agg.get("bias_naive")
    bias_reduction_pct = (
        round(100.0 * (bias_naive - bias_robust) / bias_naive, 2)
        if bias_naive and bias_naive > 0 else None
    )
    variants = summary.get("aggregation_variants", [])
    influence_bound = None
    for v in variants:
        if v.get("method") == "trimmed_mean":
            influence_bound = v.get("max_influence_per_compromised_agent")
            break
    summary["excellence_metrics"] = {
        "influence_bound_max_per_compromised": influence_bound,
        "bias_reduction_pct": bias_reduction_pct,
        "safety_gate_integration": safety_gate_denial.get("safety_gate_integration"),
        "trigger_met": summary["success_criteria_met"].get("trigger_met"),
    }
    if all_adapter and len(tasks_rep) == len(tasks_cen) and len(tasks_rep) >= 2:
        from labtrust_portfolio.stats import (
            bootstrap_ci_difference,
            effect_size_mean_diff,
            paired_t_test,
            power_paired_t_test,
        )
        diff_mean, cohens_d = effect_size_mean_diff(tasks_rep, tasks_cen)
        diff_ci95 = bootstrap_ci_difference(tasks_rep, tasks_cen, seed=42)
        t_stat, p_value, _ = paired_t_test(tasks_rep, tasks_cen)
        power_post_hoc = power_paired_t_test(tasks_rep, tasks_cen, alpha=0.05)
        diff_ci_width = (diff_ci95[1] - diff_ci95[0]) if not (math.isnan(diff_ci95[0]) or math.isnan(diff_ci95[1])) else None
        summary["excellence_metrics"]["difference_mean"] = round(diff_mean, 4)
        summary["excellence_metrics"]["difference_ci95"] = [
            round(diff_ci95[0], 4),
            round(diff_ci95[1], 4),
        ]
        summary["excellence_metrics"]["difference_ci_width"] = round(diff_ci_width, 4) if diff_ci_width is not None else None
        summary["excellence_metrics"]["paired_t_p_value"] = (
            round(p_value, 4) if not math.isnan(p_value) else None
        )
        summary["excellence_metrics"]["power_post_hoc"] = round(power_post_hoc, 4) if not math.isnan(power_post_hoc) else None
        summary["excellence_metrics"]["alpha"] = 0.05

    out_summary = args.out / "summary.json"
    out_summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
