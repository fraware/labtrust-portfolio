#!/usr/bin/env python3
"""
P5 Scaling: held-out scenario eval. Build table from multi-scenario runs, hold out
one scenario, train baseline on rest, evaluate (MAE). Writes to
datasets/runs/scaling_eval/. Run generate_multiscenario_runs.py first.
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


def main() -> int:
    ap = argparse.ArgumentParser(description="P5: Held-out scenario evaluation")
    ap.add_argument(
        "--runs-dir",
        type=Path,
        default=REPO_ROOT / "datasets" / "runs" / "multiscenario_runs",
        help="Runs dir (trace.json + maestro_report.json per run)",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "datasets" / "runs" / "scaling_eval",
        help="Output directory for eval results",
    )
    ap.add_argument(
        "--target",
        type=str,
        default="tasks_completed",
        help="Response variable to predict (default: tasks_completed)",
    )
    args = ap.parse_args()

    from labtrust_portfolio.scaling import (
        build_dataset_from_runs,
        predict_baseline_mean,
        predict_by_scenario,
        extract_features_from_scenario,
        fit_linear_predictor,
        fit_scaling_exponent,
    )

    if not args.runs_dir.exists():
        print(f"Runs dir not found: {args.runs_dir}")
        print("Run: PYTHONPATH=impl/src python scripts/generate_multiscenario_runs.py")
        return 1

    rows = build_dataset_from_runs(args.runs_dir)
    if not rows:
        print("No rows. Ensure runs dir has run subdirs with trace.json and maestro_report.json")
        return 1

    scenario_ids = sorted({r.get("scenario_id") for r in rows if r.get("scenario_id")})
    if len(scenario_ids) < 2:
        print("Need at least 2 scenario families. Generate more runs.")
        return 1

    for r in rows:
        feats = extract_features_from_scenario(r.get("scenario_id", ""))
        r["_num_tasks"] = feats.get("num_tasks", 0)
    target = args.target
    results = []
    for held_out_id in scenario_ids:
        train_rows = [r for r in rows if r.get("scenario_id") != held_out_id]
        test_rows = [r for r in rows if r.get("scenario_id") == held_out_id]
        if not test_rows:
            continue
        global_pred = predict_baseline_mean(train_rows, target)
        actuals = [r.get("response", {}).get(target, 0) for r in test_rows]
        mae_global = (
            sum(abs(a - global_pred) for a in actuals) / len(actuals) if actuals else 0.0
        )
        per_scenario_pred = predict_by_scenario(rows, held_out_id, target)
        mae_per_scenario = (
            sum(abs(a - per_scenario_pred) for a in actuals) / len(actuals)
            if actuals else 0.0
        )
        num_tasks_held = extract_features_from_scenario(held_out_id).get("num_tasks", 0)
        same_num_tasks = [r for r in train_rows if r.get("_num_tasks") == num_tasks_held]
        if same_num_tasks:
            feat_pred = predict_baseline_mean(same_num_tasks, target)
        else:
            feat_pred = global_pred
        mae_feat = (
            sum(abs(a - feat_pred) for a in actuals) / len(actuals) if actuals else 0.0
        )
        reg_predict = fit_linear_predictor(
            train_rows, target,
            feature_cols=["num_tasks", "num_faults", "tool_density"],
        )
        if reg_predict is not None:
            preds_reg = [
                reg_predict(r) for r in test_rows
            ]
            mae_reg = (
                sum(abs(a - p) for a, p in zip(actuals, preds_reg)) / len(actuals)
                if actuals and preds_reg else None
            )
        else:
            mae_reg = None
        test_collapse = [
            r.get("collapse", False) for r in test_rows
            if "collapse" in r
        ]
        train_collapse = [
            r.get("collapse", False) for r in train_rows
            if "collapse" in r
        ]
        test_collapse_rate = (
            sum(test_collapse) / len(test_collapse)
            if test_collapse else None
        )
        train_collapse_rate = (
            sum(train_collapse) / len(train_collapse)
            if train_collapse else None
        )
        results.append({
            "held_out_scenario": held_out_id,
            "train_n": len(train_rows),
            "test_n": len(test_rows),
            "global_baseline_pred": global_pred,
            "baseline_mae": mae_global,
            "per_scenario_baseline_pred": per_scenario_pred,
            "per_scenario_baseline_mae": mae_per_scenario,
            "num_tasks_held_out": num_tasks_held,
            "feat_baseline_pred": feat_pred,
            "feat_baseline_mae": mae_feat,
            "regression_mae": mae_reg,
            "actuals_mean": sum(actuals) / len(actuals) if actuals else 0.0,
            "test_collapse_rate": test_collapse_rate,
            "train_collapse_rate": train_collapse_rate,
        })

    overall_mae = (
        sum(r["baseline_mae"] for r in results) / len(results) if results else 0.0
    )
    overall_per_scenario_mae = (
        sum(r["per_scenario_baseline_mae"] for r in results) / len(results)
        if results else 0.0
    )
    overall_feat_mae = (
        sum(r["feat_baseline_mae"] for r in results) / len(results) if results else 0.0
    )
    reg_maes = [r["regression_mae"] for r in results if r.get("regression_mae") is not None]
    overall_reg_mae = (
        sum(reg_maes) / len(reg_maes) if reg_maes else None
    )
    collapse_rates = [
        r["test_collapse_rate"] for r in results
        if r.get("test_collapse_rate") is not None
    ]
    overall_collapse_rate = (
        sum(collapse_rates) / len(collapse_rates) if collapse_rates else None
    )
    n_hold = len(results)
    stdev_baseline = (
        (sum((r["baseline_mae"] - overall_mae) ** 2 for r in results) / n_hold) ** 0.5
        if n_hold > 1 else 0.0
    )
    stdev_feat = (
        (sum((r["feat_baseline_mae"] - overall_feat_mae) ** 2 for r in results) / n_hold)
        ** 0.5 if n_hold > 1 else 0.0
    )
    ci_half = 1.96 * stdev_baseline / math.sqrt(n_hold) if n_hold else 0.0
    ci_half_feat = 1.96 * stdev_feat / math.sqrt(n_hold) if n_hold else 0.0
    scaling_fit = fit_scaling_exponent(rows, target, "num_tasks")
    held_out_scenarios = [r["held_out_scenario"] for r in results]
    train_n_total = sum(r["train_n"] for r in results)
    test_n_total = sum(r["test_n"] for r in results)
    summary = {
        "runs_dir": str(args.runs_dir),
        "target": target,
        "total_rows": len(rows),
        "scenario_ids": scenario_ids,
        "run_manifest": {
            "runs_dir": str(args.runs_dir),
            "scenario_ids": scenario_ids,
            "held_out_scenarios": held_out_scenarios,
            "train_n_total": train_n_total,
            "test_n_total": test_n_total,
            "script": "scaling_heldout_eval.py",
        },
        "held_out_results": results,
        "overall_baseline_mae": overall_mae,
        "overall_per_scenario_baseline_mae": overall_per_scenario_mae,
        "overall_feat_baseline_mae": overall_feat_mae,
        "overall_regression_mae": overall_reg_mae,
        "overall_collapse_rate": overall_collapse_rate,
        "overall_baseline_mae_ci95_lower": overall_mae - ci_half,
        "overall_baseline_mae_ci95_upper": overall_mae + ci_half,
        "overall_feat_baseline_mae_ci95_lower": overall_feat_mae - ci_half_feat,
        "overall_feat_baseline_mae_ci95_upper": overall_feat_mae + ci_half_feat,
        "scaling_fit": scaling_fit if scaling_fit else None,
        "success_criteria_met": {
            "beat_baseline_out_of_sample": (
                overall_reg_mae is not None and overall_reg_mae <= overall_mae
            ) or (overall_feat_mae <= overall_mae),
            "beat_per_scenario_baseline": overall_per_scenario_mae is not None,
            "trigger_met": (
                (overall_reg_mae is not None and overall_reg_mae <= overall_mae)
                or (overall_feat_mae <= overall_mae)
            ),
        },
    }
    # Excellence metrics (STANDARDS_OF_EXCELLENCE.md) + comparison stats (REPORTING_STANDARD)
    ci_width = (summary["overall_baseline_mae_ci95_upper"] - summary["overall_baseline_mae_ci95_lower"]) if "overall_baseline_mae_ci95_upper" in summary else None
    out_of_sample_margin = (overall_mae - overall_feat_mae) if overall_feat_mae is not None and overall_mae is not None else None
    summary["excellence_metrics"] = {
        "out_of_sample_margin_vs_global_baseline": round(out_of_sample_margin, 4) if out_of_sample_margin is not None else None,
        "ci_width_95_baseline_mae": round(ci_width, 4) if ci_width is not None else None,
        "beat_baseline_out_of_sample": summary["success_criteria_met"]["beat_baseline_out_of_sample"],
        "scenario_coverage": len(results),
    }
    if len(results) >= 2:
        baseline_maes = [r["baseline_mae"] for r in results]
        feat_maes = [r["feat_baseline_mae"] for r in results]
        from labtrust_portfolio.stats import (
            bootstrap_ci_difference,
            effect_size_mean_diff,
            paired_t_test,
            power_paired_t_test,
        )
        diff_mean, cohens_d = effect_size_mean_diff(baseline_maes, feat_maes)
        diff_ci95 = bootstrap_ci_difference(baseline_maes, feat_maes, seed=42)
        t_stat, p_value, _ = paired_t_test(baseline_maes, feat_maes)
        power_post_hoc = power_paired_t_test(baseline_maes, feat_maes, alpha=0.05)
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
    args.out.mkdir(parents=True, exist_ok=True)
    out_file = args.out / "heldout_results.json"
    out_file.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
