#!/usr/bin/env python3
"""
Export P5 Scaling tables from frozen JSON artifacts (script-generated for the draft).
Usage (from repo root):
  PYTHONPATH=impl/src python scripts/export_scaling_tables.py
  python scripts/export_scaling_tables.py --results ... --out papers/P5_ScalingLaws/generated_tables.md
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS = (
    REPO / "datasets" / "runs" / "scaling_eval" / "heldout_results.json"
)


def _fmt(x: float | int | str | None) -> str:
    if x is None:
        return "-"
    if isinstance(x, (int, float)):
        return f"{x:.2f}" if isinstance(x, float) else str(x)
    return str(x)


def _fmt4(x: float | int | str | None) -> str:
    """Four decimals for small scores (e.g. Brier) so tables do not round to zero."""
    if x is None:
        return "-"
    if isinstance(x, float):
        return f"{x:.4f}"
    return _fmt(x)


def _load(p: Path | None) -> dict | None:
    if p is None or not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def table1_main(data: dict) -> list[str]:
    h1 = (
        "| Held-out | train_n | test_n | global_mae | oracle_ps_mae | "
        "adm_train_ps_mae | regime_train_mae | feat_mae | reg_mae | mean_actual |"
    )
    h2 = (
        "|----------|--------|--------|------------|---------------|------------------|"
        "------------------|---------|---------|-------------|"
    )
    lines = ["# Table 1 — Main OOS prediction (per fold)", "", h1, h2]
    for r in data.get("held_out_results", []):
        lines.append(
            f"| {r.get('holdout_label', '')} | {r.get('train_n', '')} | "
            f"{r.get('test_n', '')} | {_fmt(r.get('baseline_mae'))} | "
            f"{_fmt(r.get('oracle_per_scenario_baseline_mae'))} | "
            f"{_fmt(r.get('admissible_per_scenario_train_mae'))} | "
            f"{_fmt(r.get('regime_train_mean_baseline_mae'))} | "
            f"{_fmt(r.get('feat_baseline_mae'))} | "
            f"{_fmt(r.get('regression_mae'))} | {_fmt(r.get('actuals_mean'))} |"
        )
    lines.append("")
    return lines


def table2_baselines(data: dict) -> list[str]:
    adm = data.get("admissible_baselines") or {}
    ora = data.get("oracle_baselines") or {}
    lines = [
        "# Table 2 — Baseline hierarchy (admissible vs oracle)",
        "",
        "| Class | Baseline | MAE | CI95 lower | CI95 upper |",
        "|-------|----------|-----|------------|------------|",
    ]
    mae_b = data.get("overall_baseline_mae")
    lo_b = data.get("overall_baseline_mae_ci95_lower")
    hi_b = data.get("overall_baseline_mae_ci95_upper")
    lines.append(f"| Admissible | Global mean | {_fmt(mae_b)} | {_fmt(lo_b)} | {_fmt(hi_b)} |")
    mae_ad = adm.get("per_scenario_train_only_mae")
    lines.append(f"| Admissible | Per-scenario train-only | {_fmt(mae_ad)} | - | - |")
    mae_rf = adm.get("regime_train_mean_mae")
    lines.append(f"| Admissible | Regime train mean | {_fmt(mae_rf)} | - | - |")
    mae_ag = adm.get("agent_count_train_mean_mae")
    lines.append(f"| Admissible | Agent-count train mean | {_fmt(mae_ag)} | - | - |")
    mae_f = data.get("overall_feat_baseline_mae")
    lo_f = data.get("overall_feat_baseline_mae_ci95_lower")
    hi_f = data.get("overall_feat_baseline_mae_ci95_upper")
    lines.append(f"| Admissible | Num-tasks bucket | {_fmt(mae_f)} | {_fmt(lo_f)} | {_fmt(hi_f)} |")
    mae_r = data.get("overall_regression_mae")
    lo_r = data.get("overall_regression_mae_ci95_lower")
    hi_r = data.get("overall_regression_mae_ci95_upper")
    if mae_r is not None:
        lines.append(
            f"| Admissible | Regression (P5 features) | {_fmt(mae_r)} | {_fmt(lo_r)} | {_fmt(hi_r)} |"
        )
    mae_o = ora.get("per_scenario_mean_including_test_mae")
    lines.append(f"| Oracle | Per-scenario (includes test) | {_fmt(mae_o)} | - | - |")
    lines.append("")
    sc = data.get("success_criteria_met") or {}
    lines.append("**Trigger (admissible):** `trigger_met` = " + str(sc.get("trigger_met")) + "")
    lines.append("")
    return lines


def table3_recommend(rec: dict | None) -> list[str]:
    lines = ["# Table 3 — Regime selection / recommendation", ""]
    if not rec:
        lines.append("_No recommendation_eval.json provided._")
        lines.append("")
        return lines
    lines.extend(
        [
            f"| regime_match_rate | {_fmt4(rec.get('regime_selection_accuracy'))} |",
            f"| mean_regret_tasks_completed | {_fmt4(rec.get('mean_regret_tasks_completed'))} |",
            f"| regret_p95 | {_fmt4(rec.get('regret_p95'))} |",
            f"| Brier collapse (LOFO rows) | {_fmt4(rec.get('brier_collapse_on_test_rows'))} |",
            "",
        ],
    )
    return lines


def table4_family_agent(fam: dict | None, agent: dict | None) -> list[str]:
    lines = ["# Table 4 — Family- and agent-held-out generalization", ""]
    lines.append("| Protocol | regression_mae | trigger_met |")
    lines.append("|----------|----------------|-------------|")
    if fam:
        sc = fam.get("success_criteria_met") or {}
        lines.append(
            f"| Leave-one-family-out | {_fmt4(fam.get('overall_regression_mae'))} | "
            f"{sc.get('trigger_met')} |",
        )
    else:
        lines.append("| Leave-one-family-out | — | — |")
    if agent:
        sc = agent.get("success_criteria_met") or {}
        lines.append(
            f"| Leave-one-agent-count-out | {_fmt4(agent.get('overall_regression_mae'))} | "
            f"{sc.get('trigger_met')} |",
        )
    else:
        lines.append("| Leave-one-agent-count-out | — | — |")
    lines.append("")
    return lines


def table5_ablation(data: dict) -> list[str]:
    lines = ["# Table 5 — Feature ablation (mean MAE by feature set)", ""]
    lines.append("| Features | mean MAE |")
    lines.append("|----------|---------|")
    for a in data.get("feature_ablation") or []:
        lines.append(f"| {a.get('features')} | {_fmt(a.get('mae'))} |")
    lines.append("")
    return lines


def table6_calibration(data: dict) -> list[str]:
    lines = ["# Table 6 — Calibration / uncertainty", ""]
    lines.append(
        f"| mean_regression_pi_coverage_95 | {_fmt(data.get('mean_regression_pi_coverage_95'))} |",
    )
    em = data.get("excellence_metrics") or {}
    lines.append(
        f"| paired_t_p_value (global vs feat fold MAE) | "
        f"{_fmt4(em.get('paired_t_p_value'))} |",
    )
    lines.append("")
    return lines


def table7_sensitivity(sens: dict | None) -> list[str]:
    lines = ["# Table 7 — Sensitivity vs seed cap", ""]
    if not sens:
        lines.append("_No scaling_sensitivity.json provided._")
        lines.append("")
        return lines
    lines.append("| max_seed | regression_mae | trigger_met |")
    lines.append("|----------|----------------|-------------|")
    for cap, block in sorted(sens.get("by_max_seed", {}).items(), key=lambda kv: int(kv[0])):
        sc = block.get("success_criteria_met") or {}
        lines.append(
            f"| {cap} | {_fmt4(block.get('overall_regression_mae'))} | {sc.get('trigger_met')} |",
        )
    lines.append("")
    return lines


def table8_regime_agent_summary(summary: dict | None) -> list[str]:
    lines = ["# Table 8 — Regime x agent-count scaling summary (title grounding)", ""]
    if not summary:
        lines.append("_No regime_agent_summary.json provided._")
        lines.append("")
        return lines

    deltas = summary.get("high_vs_low_agent_count_deltas") or []
    lines.append("| family | regime | low->high agents | delta_tasks_completed_% | delta_coordination_tax_% | delta_p95_latency_% |")
    lines.append("|--------|--------|------------------|-------------------------|--------------------------|---------------------|")
    for d in deltas:
        lines.append(
            f"| {d.get('scenario_family')} | {d.get('coordination_regime')} | "
            f"{d.get('agent_count_low')}->{d.get('agent_count_high')} | "
            f"{_fmt(d.get('delta_tasks_completed_pct'))} | "
            f"{_fmt(d.get('delta_coordination_tax_proxy_pct'))} | "
            f"{_fmt(d.get('delta_task_latency_ms_p95_pct'))} |",
        )
    lines.append("")
    return lines


def main() -> int:
    ap = argparse.ArgumentParser(description="Export P5 Scaling tables for draft")
    ap.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    ap.add_argument("--family-results", type=Path, default=None)
    ap.add_argument("--agent-results", type=Path, default=None)
    ap.add_argument("--recommend-results", type=Path, default=None)
    ap.add_argument("--sensitivity-results", type=Path, default=None)
    ap.add_argument("--regime-agent-summary", type=Path, default=None)
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help="If set, write markdown tables to this path",
    )
    args = ap.parse_args()
    if not args.results.exists():
        print("Run scripts/scaling_heldout_eval.py then re-run this script.")
        return 1
    main_data = _load(args.results)
    assert main_data is not None
    fam_data = _load(args.family_results)
    agent_data = _load(args.agent_results)
    rec_data = _load(args.recommend_results)
    sens_data = _load(args.sensitivity_results)
    regime_agent_summary = _load(args.regime_agent_summary)

    chunks: list[str] = []
    rm = main_data.get("run_manifest") or {}
    commit = rm.get("commit") or ""
    total_rows = main_data.get("total_rows")
    chunks.append(
        "<!-- generated by export_scaling_tables.py; "
        f"holdout_mode={main_data.get('holdout_mode')}; "
        f"total_rows={total_rows}; "
        f"commit={commit} -->"
    )
    chunks.append("")
    chunks.extend(table1_main(main_data))
    chunks.extend(table2_baselines(main_data))
    chunks.extend(table3_recommend(rec_data))
    chunks.extend(table4_family_agent(fam_data, agent_data))
    chunks.extend(table5_ablation(main_data))
    chunks.extend(table6_calibration(main_data))
    chunks.extend(table7_sensitivity(sens_data))
    chunks.extend(table8_regime_agent_summary(regime_agent_summary))
    text = "\n".join(chunks)
    print(text)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
