#!/usr/bin/env python3
"""
P5: leave-one-family-out regime recommendation — compare risk-adjusted pick vs hindsight-best regime
per (scenario_id, seed, fault_setting, agent_count) group. Writes recommendation_eval.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "impl" / "src"))


def p5_group_key(r: Dict[str, Any]) -> Tuple[Any, ...]:
    return (
        str(r.get("scenario_id", "")),
        int(r.get("seed", 0) or 0),
        str(r.get("fault_setting_label", "")),
        int(r.get("agent_count", 1) or 1),
    )


def observed_best_regime(pool: List[Dict[str, Any]]) -> Tuple[str | None, float]:
    best_r: str | None = None
    best_tc = -1.0
    for r in pool:
        tc = float(r.get("response", {}).get("tasks_completed", 0) or 0.0)
        reg = str(r.get("coordination_regime", ""))
        if tc > best_tc:
            best_tc = tc
            best_r = reg
    return best_r, best_tc


def main() -> int:
    ap = argparse.ArgumentParser(description="P5 regime recommendation LOFO eval")
    ap.add_argument(
        "--runs-dir",
        type=Path,
        default=REPO / "datasets" / "runs" / "multiscenario_runs",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=REPO / "datasets" / "runs" / "scaling_recommend" / "recommendation_eval.json",
    )
    args = ap.parse_args()

    from labtrust_portfolio.scaling import (
        DEFAULT_FEATURE_COLS_P5,
        build_dataset_from_runs,
        build_scaling_holdout_folds,
        extract_features_from_scenario,
        fit_linear_predictor,
        regime_recommendation_bundle,
    )

    if not args.runs_dir.exists():
        print(f"Runs dir not found: {args.runs_dir}", file=sys.stderr)
        return 1
    rows = build_dataset_from_runs(args.runs_dir)
    if not rows:
        print("No rows", file=sys.stderr)
        return 1

    groups: Dict[Tuple[Any, ...], List[Dict[str, Any]]] = {}
    for r in rows:
        groups.setdefault(p5_group_key(r), []).append(r)

    holdout_mode, folds = build_scaling_holdout_folds(
        rows, "family", extract_features_from_scenario,
    )
    if not folds:
        print("No LOFO folds (need 2+ families)", file=sys.stderr)
        return 1

    match = 0
    total = 0
    regrets: List[float] = []
    brier_terms: List[float] = []

    feats = list(DEFAULT_FEATURE_COLS_P5)
    for _held, train_rows, test_rows in folds:
        pred_tc = fit_linear_predictor(train_rows, "tasks_completed", feats)
        pred_cp = fit_linear_predictor(train_rows, "collapse_probability", feats)
        pred_col = pred_cp
        for r in test_rows:
            k = p5_group_key(r)
            pool = groups.get(k, [])
            regset = {str(x.get("coordination_regime")) for x in pool}
            if len(regset) < 2:
                continue
            br, btc = observed_best_regime(pool)
            if br is None:
                continue
            ac = int(r.get("agent_count", 1) or 1)
            bundle = regime_recommendation_bundle(
                train_rows,
                r,
                agent_count=ac,
                fitted_tasks_predictor=pred_tc,
                fitted_collapse_predictor=pred_cp,
            )
            rec = bundle.get("recommended_regime")
            total += 1
            if rec == br:
                match += 1
            tc_at_rec = None
            for x in pool:
                if str(x.get("coordination_regime")) == str(rec):
                    tc_at_rec = float(x.get("response", {}).get("tasks_completed", 0) or 0.0)
                    break
            if tc_at_rec is not None:
                regrets.append(max(0.0, btc - tc_at_rec))
            if pred_col is not None:
                p_hat = float(pred_col(r))
                p_hat = max(0.0, min(1.0, p_hat))
                y = 1.0 if r.get("collapse") else 0.0
                brier_terms.append((p_hat - y) ** 2)

    out: Dict[str, Any] = {
        "run_manifest": {
            "script": "scaling_recommend_eval.py",
            "runs_dir": str(args.runs_dir),
            "holdout_mode": holdout_mode,
            "n_folds": len(folds),
        },
        "regime_selection_accuracy": (match / total) if total else None,
        "n_decisions": total,
        "mean_regret_tasks_completed": (
            float(sum(regrets) / len(regrets)) if regrets else None
        ),
        "regret_p95": None,
        "brier_collapse_on_test_rows": (
            float(sum(brier_terms) / len(brier_terms)) if brier_terms else None
        ),
    }
    if regrets:
        sr = sorted(regrets)
        out["regret_p95"] = float(sr[int(0.95 * (len(sr) - 1))])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
