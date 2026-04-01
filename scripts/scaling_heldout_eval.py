#!/usr/bin/env python3
"""
P5 Scaling: held-out eval — leave-one-scenario-out (default) or leave-one-family-out.
Build table from multi-scenario runs; optional secondary targets (coordination tax proxies).
Writes datasets/runs/scaling_eval/heldout_results.json. Run generate_multiscenario_runs.py first.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "impl" / "src"))
if "LABTRUST_KERNEL_DIR" not in os.environ:
    os.environ["LABTRUST_KERNEL_DIR"] = str(REPO_ROOT / "kernel")

FEATURE_COLS_DEFAULT = ["num_tasks", "num_faults", "tool_density"]


def _response_val(row: Dict[str, Any], target: str) -> float:
    return float(row.get("response", {}).get(target, 0) or 0.0)


def regression_pi_coverage(
    train_rows: List[Dict[str, Any]],
    test_rows: List[Dict[str, Any]],
    target: str,
    feature_cols: Sequence[str],
    fit_linear_predictor: Any,
) -> Optional[float]:
    """
    Fraction of test points where actual lies in train-residual 95% interval
    (mean +/- 1.96 * train residual stdev). Exploratory calibration for C3.
    """
    pred_fn = fit_linear_predictor(train_rows, target, feature_cols=list(feature_cols))
    if pred_fn is None or len(test_rows) == 0:
        return None
    train_actuals = [_response_val(r, target) for r in train_rows]
    train_preds = [pred_fn(r) for r in train_rows]
    res = [a - p for a, p in zip(train_actuals, train_preds)]
    if len(res) < 2:
        return None
    sigma = statistics.pstdev(res)
    if sigma < 1e-15:
        return None
    test_actuals = [_response_val(r, target) for r in test_rows]
    test_preds = [pred_fn(r) for r in test_rows]
    covered = sum(
        1 for a, p in zip(test_actuals, test_preds)
        if abs(a - p) <= 1.96 * sigma
    )
    return covered / len(test_preds)


def eval_fold(
    train_rows: List[Dict[str, Any]],
    test_rows: List[Dict[str, Any]],
    rows_all: List[Dict[str, Any]],
    holdout_label: str,
    target: str,
    extract_features_from_scenario: Any,
    predict_baseline_mean: Any,
    predict_by_scenario: Any,
    predict_prior_model: Any,
    fit_linear_predictor: Any,
    fit_tree_stump_predictor: Any,
    feature_cols: Sequence[str],
) -> Dict[str, Any]:
    global_pred = predict_baseline_mean(train_rows, target)
    actuals = [_response_val(r, target) for r in test_rows]
    mae_global = (
        sum(abs(a - global_pred) for a in actuals) / len(actuals) if actuals else 0.0
    )
    per_scenario_preds = [
        predict_by_scenario(rows_all, r.get("scenario_id", ""), target)
        for r in test_rows
    ]
    mae_per_scenario = (
        sum(abs(a - p) for a, p in zip(actuals, per_scenario_preds)) / len(actuals)
        if actuals else 0.0
    )
    mae_feat_list: List[float] = []
    for r in test_rows:
        nt = r.get("_num_tasks", 0)
        same_nt = [x for x in train_rows if x.get("_num_tasks") == nt]
        if same_nt:
            fp = predict_baseline_mean(same_nt, target)
        else:
            fp = global_pred
        mae_feat_list.append(abs(_response_val(r, target) - fp))
    mae_feat = (
        sum(mae_feat_list) / len(mae_feat_list) if mae_feat_list else 0.0
    )
    if target == "tasks_completed":
        prior_preds = [predict_prior_model(r, target) for r in test_rows]
        mae_prior = (
            sum(abs(a - p) for a, p in zip(actuals, prior_preds)) / len(actuals)
            if actuals and prior_preds else None
        )
    else:
        mae_prior = None
    reg_predict = fit_linear_predictor(
        train_rows, target, feature_cols=list(feature_cols),
    )
    if reg_predict is not None:
        preds_reg = [reg_predict(r) for r in test_rows]
        mae_reg = (
            sum(abs(a - p) for a, p in zip(actuals, preds_reg)) / len(actuals)
            if actuals else None
        )
    else:
        mae_reg = None
    stump_predict = fit_tree_stump_predictor(train_rows, target, "num_tasks")
    if stump_predict is not None:
        preds_stump = [stump_predict(r) for r in test_rows]
        mae_stump = (
            sum(abs(a - p) for a, p in zip(actuals, preds_stump)) / len(actuals)
            if actuals and preds_stump else None
        )
    else:
        mae_stump = None
    test_collapse = [r.get("collapse", False) for r in test_rows if "collapse" in r]
    train_collapse = [r.get("collapse", False) for r in train_rows if "collapse" in r]
    test_collapse_rate = (
        sum(test_collapse) / len(test_collapse) if test_collapse else None
    )
    train_collapse_rate = (
        sum(train_collapse) / len(train_collapse) if train_collapse else None
    )
    pi_cov = regression_pi_coverage(
        train_rows, test_rows, target, feature_cols, fit_linear_predictor,
    )
    sid0 = test_rows[0].get("scenario_id", "") if test_rows else ""
    num_tasks_held = extract_features_from_scenario(sid0).get("num_tasks", 0)
    return {
        "held_out_scenario": holdout_label,
        "holdout_label": holdout_label,
        "train_n": len(train_rows),
        "test_n": len(test_rows),
        "global_baseline_pred": global_pred,
        "baseline_mae": mae_global,
        "per_scenario_baseline_pred": per_scenario_preds[0] if per_scenario_preds else None,
        "per_scenario_baseline_mae": mae_per_scenario,
        "num_tasks_held_out": num_tasks_held,
        "feat_baseline_mae": mae_feat,
        "prior_model_mae": mae_prior,
        "regression_mae": mae_reg,
        "stump_mae": mae_stump,
        "actuals_mean": sum(actuals) / len(actuals) if actuals else 0.0,
        "test_collapse_rate": test_collapse_rate,
        "train_collapse_rate": train_collapse_rate,
        "regression_pi_coverage_95": pi_cov,
    }


def build_folds(
    rows: List[Dict[str, Any]],
    holdout_mode: str,
    extract_features_from_scenario: Any,
) -> Tuple[str, List[Tuple[str, List[Dict[str, Any]], List[Dict[str, Any]]]]]:
    for r in rows:
        feats = extract_features_from_scenario(r.get("scenario_id", ""))
        r["_num_tasks"] = feats.get("num_tasks", 0)
    if holdout_mode == "scenario":
        ids = sorted({r.get("scenario_id") for r in rows if r.get("scenario_id")})
        folds = []
        for hid in ids:
            tr = [r for r in rows if r.get("scenario_id") != hid]
            te = [r for r in rows if r.get("scenario_id") == hid]
            if te:
                folds.append((hid, tr, te))
        return "scenario", folds
    if holdout_mode == "family":
        fams = sorted({r.get("scenario_family", "unknown") for r in rows})
        folds = []
        for fam in fams:
            tr = [r for r in rows if r.get("scenario_family") != fam]
            te = [r for r in rows if r.get("scenario_family") == fam]
            if te and tr:
                folds.append((fam, tr, te))
        return "family", folds
    raise ValueError(f"Unknown holdout_mode: {holdout_mode}")


def run_eval_for_target(
    rows: List[Dict[str, Any]],
    folds: List[Tuple[str, List[Dict[str, Any]], List[Dict[str, Any]]]],
    holdout_mode: str,
    target: str,
    extract_features_from_scenario: Any,
    predict_baseline_mean: Any,
    predict_by_scenario: Any,
    predict_prior_model: Any,
    fit_linear_predictor: Any,
    fit_tree_stump_predictor: Any,
    fit_scaling_exponent: Any,
    feature_cols: Sequence[str],
    scenario_ids: List[str],
) -> Dict[str, Any]:
    results = []
    for held_label, train_rows, test_rows in folds:
        results.append(
            eval_fold(
                train_rows,
                test_rows,
                rows,
                held_label,
                target,
                extract_features_from_scenario,
                predict_baseline_mean,
                predict_by_scenario,
                predict_prior_model,
                fit_linear_predictor,
                fit_tree_stump_predictor,
                feature_cols,
            )
        )
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
    overall_reg_mae = sum(reg_maes) / len(reg_maes) if reg_maes else None
    prior_maes = [r["prior_model_mae"] for r in results if r.get("prior_model_mae") is not None]
    overall_prior_mae = sum(prior_maes) / len(prior_maes) if prior_maes else None
    stump_maes = [r["stump_mae"] for r in results if r.get("stump_mae") is not None]
    overall_stump_mae = sum(stump_maes) / len(stump_maes) if stump_maes else None
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
    stdev_reg = (
        (sum((r["regression_mae"] - overall_reg_mae) ** 2 for r in results) / n_hold) ** 0.5
        if n_hold > 1 and overall_reg_mae is not None
        and all(r.get("regression_mae") is not None for r in results)
        else 0.0
    )
    ci_half = 1.96 * stdev_baseline / math.sqrt(n_hold) if n_hold else 0.0
    ci_half_feat = 1.96 * stdev_feat / math.sqrt(n_hold) if n_hold else 0.0
    ci_half_reg = (
        1.96 * stdev_reg / math.sqrt(n_hold)
        if n_hold and overall_reg_mae is not None else 0.0
    )
    scaling_fit = fit_scaling_exponent(rows, target, "num_tasks") if target else {}
    feature_ablation: List[Dict[str, Any]] = []
    for feat_set in [["num_tasks"], ["num_faults"], list(feature_cols)]:
        maes_ablation: List[float] = []
        for held_label, train_rows_ab, test_rows_ab in folds:
            if not test_rows_ab:
                continue
            pred_fn = fit_linear_predictor(train_rows_ab, target, feat_set)
            if pred_fn is None:
                continue
            actuals_ab = [_response_val(r, target) for r in test_rows_ab]
            preds_ab = [pred_fn(r) for r in test_rows_ab]
            mae_ab = sum(abs(a - p) for a, p in zip(actuals_ab, preds_ab)) / len(actuals_ab)
            maes_ablation.append(mae_ab)
        feature_ablation.append({
            "features": feat_set,
            "mae": round(sum(maes_ablation) / len(maes_ablation), 4) if maes_ablation else None,
        })
    pi_covs = [r["regression_pi_coverage_95"] for r in results if r.get("regression_pi_coverage_95") is not None]
    mean_pi_cov = sum(pi_covs) / len(pi_covs) if pi_covs else None
    held_labels = [r["holdout_label"] for r in results]
    train_n_total = sum(r["train_n"] for r in results)
    test_n_total = sum(r["test_n"] for r in results)
    summary_inner = {
        "target": target,
        "holdout_mode": holdout_mode,
        "held_out_results": results,
        "overall_baseline_mae": overall_mae,
        "overall_per_scenario_baseline_mae": overall_per_scenario_mae,
        "overall_feat_baseline_mae": overall_feat_mae,
        "overall_regression_mae": overall_reg_mae,
        "overall_prior_model_mae": overall_prior_mae,
        "overall_stump_mae": overall_stump_mae,
        "regression_skipped_reason": (
            "train_n < k or singular; see run_manifest.train_n_total"
            if overall_reg_mae is None else None
        ),
        "overall_collapse_rate": overall_collapse_rate,
        "overall_baseline_mae_ci95_lower": overall_mae - ci_half,
        "overall_baseline_mae_ci95_upper": overall_mae + ci_half,
        "overall_feat_baseline_mae_ci95_lower": overall_feat_mae - ci_half_feat,
        "overall_feat_baseline_mae_ci95_upper": overall_feat_mae + ci_half_feat,
        "overall_regression_mae_ci95_lower": (
            overall_reg_mae - ci_half_reg if overall_reg_mae is not None else None
        ),
        "overall_regression_mae_ci95_upper": (
            overall_reg_mae + ci_half_reg if overall_reg_mae is not None else None
        ),
        "mean_regression_pi_coverage_95": mean_pi_cov,
        "scaling_fit": scaling_fit if scaling_fit else None,
        "feature_ablation": feature_ablation,
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
    summary_inner["run_manifest"] = {
        "scenario_ids": scenario_ids,
        "held_out_labels": held_labels,
        "held_out_scenarios": held_labels,
        "train_n_total": train_n_total,
        "test_n_total": test_n_total,
        "script": "scaling_heldout_eval.py",
    }
    return summary_inner


def main() -> int:
    ap = argparse.ArgumentParser(description="P5: Held-out scenario / family evaluation")
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
        help="Primary response variable (default: tasks_completed)",
    )
    ap.add_argument(
        "--holdout-mode",
        choices=("scenario", "family"),
        default="scenario",
        help="Leave-one-scenario-out (default) or leave-one-taxonomy-family-out",
    )
    ap.add_argument(
        "--extra-targets",
        type=str,
        default="coordination_tax_proxy,error_amplification_proxy",
        help="Comma-separated extra response keys; use with --no-secondary to skip",
    )
    ap.add_argument(
        "--no-secondary",
        action="store_true",
        help="Do not evaluate secondary targets (coordination tax / error amplification proxies)",
    )
    args = ap.parse_args()

    from labtrust_portfolio.scaling import (
        build_dataset_from_runs,
        predict_baseline_mean,
        predict_by_scenario,
        predict_prior_model,
        extract_features_from_scenario,
        fit_linear_predictor,
        fit_tree_stump_predictor,
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
    try:
        holdout_mode, folds = build_folds(
            rows, args.holdout_mode, extract_features_from_scenario,
        )
    except ValueError as e:
        print(e)
        return 1
    if not folds:
        print("No folds: need more scenarios or families with train/test split.")
        return 1
    if len(folds) < 2 and args.holdout_mode == "scenario":
        print("Need at least 2 scenarios with data.")
        return 1
    if len(folds) < 2 and args.holdout_mode == "family":
        print("Need at least 2 scenario families with data (check scenario YAML family:).")
        return 1

    if args.no_secondary:
        extra_parts: List[str] = []
    else:
        extra_parts = [x.strip() for x in args.extra_targets.split(",") if x.strip()]

    summary = run_eval_for_target(
        rows,
        folds,
        holdout_mode,
        args.target,
        extract_features_from_scenario,
        predict_baseline_mean,
        predict_by_scenario,
        predict_prior_model,
        fit_linear_predictor,
        fit_tree_stump_predictor,
        fit_scaling_exponent,
        FEATURE_COLS_DEFAULT,
        scenario_ids,
    )
    summary["runs_dir"] = str(args.runs_dir)
    summary["total_rows"] = len(rows)
    summary["scenario_ids"] = scenario_ids
    summary["run_manifest"]["runs_dir"] = str(args.runs_dir)
    summary["run_manifest"]["holdout_mode"] = holdout_mode

    secondary: Dict[str, Any] = {}
    for et in extra_parts:
        if et == args.target:
            continue
        sec = run_eval_for_target(
            rows,
            folds,
            holdout_mode,
            et,
            extract_features_from_scenario,
            predict_baseline_mean,
            predict_by_scenario,
            predict_prior_model,
            fit_linear_predictor,
            fit_tree_stump_predictor,
            fit_scaling_exponent,
            FEATURE_COLS_DEFAULT,
            scenario_ids,
        )
        secondary[et] = {
            "overall_baseline_mae": sec["overall_baseline_mae"],
            "overall_regression_mae": sec["overall_regression_mae"],
            "overall_feat_baseline_mae": sec["overall_feat_baseline_mae"],
            "mean_regression_pi_coverage_95": sec.get("mean_regression_pi_coverage_95"),
            "scaling_fit": sec.get("scaling_fit"),
            "success_criteria_met": sec.get("success_criteria_met"),
        }
    if secondary:
        summary["secondary_targets"] = secondary

    overall_mae = summary["overall_baseline_mae"]
    overall_feat_mae = summary["overall_feat_baseline_mae"]
    results = summary["held_out_results"]

    ci_width = (
        summary["overall_baseline_mae_ci95_upper"] - summary["overall_baseline_mae_ci95_lower"]
    )
    out_of_sample_margin = (
        (overall_mae - overall_feat_mae)
        if overall_feat_mae is not None and overall_mae is not None else None
    )
    summary["excellence_metrics"] = {
        "out_of_sample_margin_vs_global_baseline": (
            round(out_of_sample_margin, 4) if out_of_sample_margin is not None else None
        ),
        "ci_width_95_baseline_mae": round(ci_width, 4),
        "beat_baseline_out_of_sample": summary["success_criteria_met"]["beat_baseline_out_of_sample"],
        "scenario_coverage": len(results),
    }
    if len(summary["held_out_results"]) >= 2:
        baseline_maes = [r["baseline_mae"] for r in summary["held_out_results"]]
        feat_maes = [r["feat_baseline_mae"] for r in summary["held_out_results"]]
        from labtrust_portfolio.stats import (
            bootstrap_ci_difference,
            effect_size_mean_diff,
            paired_t_test,
            power_paired_t_test,
        )
        diff_mean, _cohens_d = effect_size_mean_diff(baseline_maes, feat_maes)
        diff_ci95 = bootstrap_ci_difference(baseline_maes, feat_maes, seed=42)
        _t_stat, p_value, _df = paired_t_test(baseline_maes, feat_maes)
        power_post_hoc = power_paired_t_test(baseline_maes, feat_maes, alpha=0.05)
        diff_ci_width = (
            (diff_ci95[1] - diff_ci95[0])
            if not (math.isnan(diff_ci95[0]) or math.isnan(diff_ci95[1])) else None
        )
        summary["excellence_metrics"]["difference_mean"] = round(diff_mean, 4)
        summary["excellence_metrics"]["difference_ci95"] = [
            round(diff_ci95[0], 4),
            round(diff_ci95[1], 4),
        ]
        summary["excellence_metrics"]["difference_ci_width"] = (
            round(diff_ci_width, 4) if diff_ci_width is not None else None
        )
        summary["excellence_metrics"]["paired_t_p_value"] = (
            round(p_value, 4) if not math.isnan(p_value) else None
        )
        summary["excellence_metrics"]["power_post_hoc"] = (
            round(power_post_hoc, 4) if not math.isnan(power_post_hoc) else None
        )
        summary["excellence_metrics"]["alpha"] = 0.05

    args.out.mkdir(parents=True, exist_ok=True)
    out_file = args.out / "heldout_results.json"
    out_file.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
