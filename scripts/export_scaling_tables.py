#!/usr/bin/env python3
"""
Export P5 Scaling tables from frozen JSON artifacts (NeurIPS-oriented layout).

Main Tables 1–4 match papers/P5_ScalingLaws/CLAIM_SOURCE_MAP.md; appendix retains
diagnostics (per-fold detail, oracle row, sensitivity, exploratory recommender).

Usage (from repo root):
  PYTHONPATH=impl/src python scripts/export_scaling_tables.py --out papers/P5_ScalingLaws/generated_tables.md
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS = REPO / "datasets" / "runs" / "scaling_eval" / "heldout_results.json"


def _fmt(x: float | int | str | None) -> str:
    if x is None:
        return "N/A"
    if isinstance(x, (int, float)):
        return f"{x:.4f}" if isinstance(x, float) else str(x)
    return str(x)


def _fmt2(x: float | int | str | None) -> str:
    if x is None:
        return "N/A"
    if isinstance(x, float):
        return f"{x:.2f}"
    return _fmt(x)


def _fmt4(x: float | int | str | None) -> str:
    if x is None:
        return "N/A"
    if isinstance(x, float):
        return f"{x:.4f}"
    return _fmt(x)


def _load(p: Path | None) -> dict | None:
    if p is None or not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def _latex_escape(s: str) -> str:
    return (
        s.replace("\\", "\\textbackslash{}")
        .replace("&", "\\&")
        .replace("%", "\\%")
        .replace("_", "\\_")
        .replace("#", "\\#")
    )


def _fold_beats_feat(r: dict[str, Any]) -> bool | None:
    reg = r.get("regression_mae")
    feat = r.get("feat_baseline_mae")
    if reg is None or feat is None:
        return None
    return bool(reg < feat - 1e-9)


def _main1_delta_rows(
    summary: dict | None,
) -> list[tuple[str, str, float | None, float | None, float | None]]:
    if not summary:
        return []
    by_pair: dict[tuple[str, str], dict[int, dict[str, Any]]] = {}
    for e in summary.get("group_summary") or []:
        fam = str(e.get("scenario_family", ""))
        reg = str(e.get("coordination_regime", ""))
        ac = int(e.get("agent_count", 0) or 0)
        by_pair.setdefault((fam, reg), {})[ac] = e
    out: list[tuple[str, str, float | None, float | None, float | None]] = []
    for (fam, reg) in sorted(by_pair.keys()):
        m = by_pair[(fam, reg)]
        lo = m.get(1)
        hi = m.get(8)
        if not lo or not hi:
            continue
        tc_lo = lo.get("mean_tasks_completed")
        tc_hi = hi.get("mean_tasks_completed")
        ct_lo = lo.get("mean_coordination_tax_proxy")
        ct_hi = hi.get("mean_coordination_tax_proxy")
        lat_lo = lo.get("mean_task_latency_ms_p95")
        lat_hi = hi.get("mean_task_latency_ms_p95")
        dt = (
            None
            if tc_lo is None or tc_hi is None
            else float(tc_hi) - float(tc_lo)
        )
        dct = (
            None
            if ct_lo is None or ct_hi is None
            else float(ct_hi) - float(ct_lo)
        )
        dlat = (
            None
            if lat_lo is None or lat_hi is None
            else float(lat_hi) - float(lat_lo)
        )
        out.append((fam, reg, dt, dct, dlat))
    return out


def table_main1_title_grounding(summary: dict | None) -> list[str]:
    lines = [
        "## Main Table 1 — Title grounding: regime × agent deltas (1→8)",
        "",
        "Absolute deltas (mean at agent count 8 minus mean at agent count 1) within each "
        "(family, regime); sourced from `group_summary` in "
        "`datasets/runs/scaling_summary/regime_agent_summary.json`. "
        "Percent versions appear in Appendix.",
        "",
        "| Family | Regime | Δ tasks 1→8 | Δ coordination tax 1→8 | Δ p95 latency (ms) 1→8 |",
        "|--------|--------|-------------|---------------------------|-------------------------|",
    ]
    rows = _main1_delta_rows(summary)
    if not rows:
        lines.append("| — | — | — | — | — |")
        lines.append("")
        return lines
    for fam, reg, dt, dct, dlat in rows:
        lines.append(
            f"| {fam} | {reg} | {_fmt4(dt)} | {_fmt4(dct)} | {_fmt4(dlat)} |",
        )
    lines.append("")
    return lines


def table_main2_scenario_heldout(data: dict) -> list[str]:
    lines = [
        "## Main Table 2 — Scenario-heldout main protocol (`tasks_completed`)",
        "",
        "Per-fold MAE on the held-out scenario. **Trigger** = per-fold **yes** iff regression "
        "beats the num-tasks bucket baseline on that fold (**no** / **N/A** otherwise). "
        "Protocol-level `trigger_met` uses aggregated admissible baselines "
        "(see JSON `success_criteria_met`).",
        "",
        "The main scenario-heldout protocol **does not trigger** because the strongest admissible "
        "**num-tasks bucket** baseline remains **harder to beat** than the global mean in aggregate "
        "(see also appendix baseline hierarchy).",
        "",
        "| Held-out scenario | Global mean MAE | Num-tasks bucket MAE | Regression MAE | Trigger |",
        "|-------------------|-----------------|----------------------|----------------|---------|",
    ]
    sc = data.get("success_criteria_met") or {}
    overall_trig = sc.get("trigger_met")
    for r in data.get("held_out_results") or []:
        beats = _fold_beats_feat(r)
        fold_cell = "yes" if beats is True else ("no" if beats is False else "N/A")
        lines.append(
            f"| {r.get('holdout_label', '')} | {_fmt2(r.get('baseline_mae'))} | "
            f"{_fmt2(r.get('feat_baseline_mae'))} | {_fmt2(r.get('regression_mae'))} | {fold_cell} |",
        )
    skip = data.get("regression_skipped_reason")
    lines.extend(
        [
            "",
            f"**Protocol-level trigger (`trigger_met`):** `{overall_trig}` "
            f"(regression overall MAE {_fmt2(data.get('overall_regression_mae'))} vs "
            f"num-tasks bucket {_fmt2(data.get('overall_feat_baseline_mae'))}).",
        ],
    )
    if skip:
        lines.extend(["", f"**Regression skip / strict nulling:** {skip}", ""])
    else:
        lines.append("")
    return lines


def table_main3_protocol_summary(paths: dict[str, Path | None]) -> list[str]:
    labels = [
        ("leave-one-scenario-out", "scenario", paths.get("scenario")),
        ("leave-one-family-out", "family", paths.get("family")),
        ("leave-one-regime-out", "regime", paths.get("regime")),
        ("leave-one-agent-count-out", "agent_count", paths.get("agent_count")),
        ("leave-one-fault-setting-out", "fault_setting", paths.get("fault")),
    ]
    lines = [
        "## Main Table 3 — Protocol summary (`tasks_completed`)",
        "",
        "**Best admissible baseline** = aggregate **num-tasks bucket** MAE (`overall_feat_baseline_mae`), "
        "the strongest baseline used in `trigger_met` semantics alongside global and regime train means.",
        "",
        "| Protocol | Regression MAE | Best admissible baseline MAE | Trigger |",
        "|----------|----------------|------------------------------|---------|",
    ]
    for pretty, _mode, p in labels:
        d = _load(p)
        if not d:
            lines.append(f"| {pretty} | — | — | — |")
            continue
        sc = d.get("success_criteria_met") or {}
        lines.append(
            f"| {pretty} | {_fmt4(d.get('overall_regression_mae'))} | "
            f"{_fmt4(d.get('overall_feat_baseline_mae'))} | {sc.get('trigger_met')} |",
        )
    lines.append("")
    return lines


def table_main4_secondary(data: dict) -> list[str]:
    lines = [
        "## Main Table 4 — Secondary targets (scenario-heldout bundle)",
        "",
        "Under scenario-heldout, **coordination tax is much more predictable than throughput "
        "(`tasks_completed`) or latency-derived error amplification** by admissible regression MAE "
        "and `trigger_met` (below); raw MAE scales differ across targets — interpret cautiously.",
        "",
        "Baseline MAE is the **global train-mean** baseline on each secondary target "
        "(same construction as primary `overall_baseline_mae` for that target).",
        "",
        "| Target | Regression MAE | Baseline MAE | Trigger | Interpretation |",
        "|--------|----------------|--------------|---------|----------------|",
    ]
    sec = data.get("secondary_targets") or {}
    inter = {
        "coordination_tax_proxy": (
            "Regression MAE much lower than error amplification; meets admissible trigger here "
            "while primary `tasks_completed` does not — interpret **per-target scale** vs throughput MAE; "
            "exploratory scaling_fit only."
        ),
        "error_amplification_proxy": (
            "Latency-derived proxy; higher regression MAE than coordination tax; exploratory."
        ),
    }
    for name in ("coordination_tax_proxy", "error_amplification_proxy"):
        block = sec.get(name) or {}
        sc = block.get("success_criteria_met") or {}
        lines.append(
            f"| `{name}` | {_fmt4(block.get('overall_regression_mae'))} | "
            f"{_fmt4(block.get('overall_baseline_mae'))} | "
            f"{sc.get('trigger_met')} | {inter.get(name, '')} |",
        )
    lines.append("")
    return lines


def appendix_collapse_prevalence(data: dict, rec: dict | None) -> list[str]:
    """Sparse-collapse disclosure; Brier scores are exploratory."""
    scen_prev = data.get("overall_collapse_rate")
    scen_brier = data.get("overall_collapse_brier_train_prevalence")
    rec_brier = rec.get("brier_collapse_on_test_rows") if rec else None
    lines = [
        "## Appendix — Collapse prevalence and Brier (exploratory)",
        "",
        "Train-prevalence Brier is macro-averaged across scenario-heldout folds "
        "(`overall_collapse_brier_train_prevalence` in `heldout_results.json`). "
        "Recommendation Brier is computed on LOFO recommender **test rows** — different protocol.",
        "",
        "| Protocol | Collapse prevalence | Brier score | Claim status |",
        "|----------|--------------------|-------------|--------------|",
        f"| scenario-heldout | {_fmt4(scen_prev)} | {_fmt4(scen_brier)} | exploratory |",
        f"| recommendation-LOFO (diagnostic) | N/A | {_fmt4(rec_brier)} | exploratory |",
        "",
    ]
    return lines


def appendix_per_fold_detail(data: dict) -> list[str]:
    h1 = (
        "| Held-out | train_n | test_n | global_mae | oracle_ps_mae | "
        "adm_train_ps_mae | regime_train_mae | feat_mae | reg_mae | mean_actual |"
    )
    h2 = (
        "|----------|--------|--------|------------|---------------|------------------|"
        "------------------|---------|---------|-------------|"
    )
    lines = ["## Appendix — Per-fold diagnostics (scenario-heldout)", "", h1, h2]
    for r in data.get("held_out_results") or []:
        lines.append(
            f"| {r.get('holdout_label', '')} | {r.get('train_n', '')} | "
            f"{r.get('test_n', '')} | {_fmt2(r.get('baseline_mae'))} | "
            f"{_fmt2(r.get('oracle_per_scenario_baseline_mae'))} | "
            f"{_fmt2(r.get('admissible_per_scenario_train_mae'))} | "
            f"{_fmt2(r.get('regime_train_mean_baseline_mae'))} | "
            f"{_fmt2(r.get('feat_baseline_mae'))} | "
            f"{_fmt2(r.get('regression_mae'))} | {_fmt2(r.get('actuals_mean'))} |",
        )
    lines.append("")
    return lines


def appendix_baseline_hierarchy(data: dict) -> list[str]:
    adm = data.get("admissible_baselines") or {}
    ora = data.get("oracle_baselines") or {}
    lines = [
        "## Appendix — Baseline hierarchy (admissible vs oracle)",
        "",
        "**Oracle row is diagnostic only** — not used for `trigger_met`.",
        "",
        "| Class | Baseline | MAE | CI95 lower | CI95 upper |",
        "|-------|----------|-----|------------|------------|",
    ]
    mae_b = data.get("overall_baseline_mae")
    lo_b = data.get("overall_baseline_mae_ci95_lower")
    hi_b = data.get("overall_baseline_mae_ci95_upper")
    lines.append(f"| Admissible | Global mean | {_fmt2(mae_b)} | {_fmt2(lo_b)} | {_fmt2(hi_b)} |")
    lines.append(
        f"| Admissible | Per-scenario train-only | {_fmt2(adm.get('per_scenario_train_only_mae'))} | — | — |",
    )
    lines.append(
        f"| Admissible | Regime train mean | {_fmt2(adm.get('regime_train_mean_mae'))} | — | — |",
    )
    lines.append(
        f"| Admissible | Agent-count train mean | {_fmt2(adm.get('agent_count_train_mean_mae'))} | — | — |",
    )
    mae_f = data.get("overall_feat_baseline_mae")
    lo_f = data.get("overall_feat_baseline_mae_ci95_lower")
    hi_f = data.get("overall_feat_baseline_mae_ci95_upper")
    lines.append(f"| Admissible | Num-tasks bucket | {_fmt2(mae_f)} | {_fmt2(lo_f)} | {_fmt2(hi_f)} |")
    mae_r = data.get("overall_regression_mae")
    lo_r = data.get("overall_regression_mae_ci95_lower")
    hi_r = data.get("overall_regression_mae_ci95_upper")
    lines.append(
        f"| Admissible | Regression (P5 features) | {_fmt2(mae_r)} | {_fmt2(lo_r)} | {_fmt2(hi_r)} |",
    )
    mae_o = ora.get("per_scenario_mean_including_test_mae")
    lines.append(f"| Oracle | Per-scenario (includes test) | {_fmt2(mae_o)} | — | — |")
    lines.append("")
    return lines


def appendix_recommend(rec: dict | None) -> list[str]:
    lines = ["## Appendix — Recommendation / regret (exploratory only)", ""]
    if not rec:
        lines.append("_No recommendation_eval.json provided._")
        lines.append("")
        return lines
    lines.extend(
        [
            f"`claim_status`: `{rec.get('claim_status', '?')}`; "
            f"`deployment_claim_allowed`: `{rec.get('deployment_claim_allowed', '?')}`",
            "",
            f"| regime_selection_accuracy | {_fmt4(rec.get('regime_selection_accuracy'))} |",
            f"| mean_regret_tasks_completed | {_fmt4(rec.get('mean_regret_tasks_completed'))} |",
            f"| regret_p95 | {_fmt4(rec.get('regret_p95'))} |",
            f"| Brier collapse (test rows) | {_fmt4(rec.get('brier_collapse_on_test_rows'))} |",
            "",
        ],
    )
    return lines


def appendix_sensitivity(sens: dict | None) -> list[str]:
    lines = ["## Appendix — Sensitivity vs seed cap", ""]
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


def appendix_regime_agent_pct(summary: dict | None) -> list[str]:
    lines = [
        "## Appendix — Regime x agent high-vs-low (percent deltas)",
        "",
        "| family | regime | low->high | d tasks % | d coord. tax % | d p95 latency % |",
        "|--------|--------|----------|-----------|------------------------|-----------------|",
    ]
    if not summary:
        lines.append("| — | — | — | — | — | — |")
        lines.append("")
        return lines
    for d in summary.get("high_vs_low_agent_count_deltas") or []:
        lines.append(
            f"| {d.get('scenario_family')} | {d.get('coordination_regime')} | "
            f"{d.get('agent_count_low')}->{d.get('agent_count_high')} | "
            f"{_fmt4(d.get('delta_tasks_completed_pct'))} | "
            f"{_fmt4(d.get('delta_coordination_tax_proxy_pct'))} | "
            f"{_fmt4(d.get('delta_task_latency_ms_p95_pct'))} |",
        )
    lines.append("")
    return lines


def appendix_exploratory_scaling_fit(data: dict) -> list[str]:
    sf = data.get("scaling_fit")
    lines = [
        "## Appendix — Exploratory log-log scaling fit (`scaling_fit`)",
        "",
        "**Exploratory only — not a universal scaling law.**",
        "",
    ]
    if isinstance(sf, dict) and sf:
        lines.append(
            f"| scaling_exponent | {_fmt4(sf.get('scaling_exponent'))} |",
        )
        lines.append(f"| scaling_r2 | {_fmt4(sf.get('scaling_r2'))} |")
        lines.append(f"| n_used | {sf.get('n_used', '')} |")
    else:
        lines.append("_No scaling_fit block._")
    lines.append("")
    return lines


def appendix_feature_ablation(data: dict) -> list[str]:
    lines = ["## Appendix — Feature ablation (mean MAE by feature set)", ""]
    lines.append("| Features | mean MAE |")
    lines.append("|----------|---------|")
    for a in data.get("feature_ablation") or []:
        lines.append(f"| `{a.get('features')}` | {_fmt(a.get('mae'))} |")
    lines.append("")
    return lines


def appendix_calibration(data: dict) -> list[str]:
    lines = ["## Appendix — Calibration / uncertainty", ""]
    lines.append(
        f"| mean_regression_pi_coverage_95 | {_fmt2(data.get('mean_regression_pi_coverage_95'))} |",
    )
    em = data.get("excellence_metrics") or {}
    lines.append(
        f"| paired_t_p_value (global vs feat fold MAE) | {_fmt4(em.get('paired_t_p_value'))} |",
    )
    lines.append("")
    return lines


def write_latex_booktabs_main_tables(
    out_dir: Path,
    main_data: dict[str, Any],
    regime_agent_summary: dict | None,
    proto_paths: dict[str, Path | None],
) -> None:
    """Camera-ready LaTeX for Main Tables 1–4 (requires \\usepackage{booktabs})."""
    out_dir.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "% Auto-generated by export_scaling_tables.py",
        "% \\usepackage{booktabs}",
        "",
    ]

    # Main Table 1
    lines.extend([
        "\\begin{table}[t]",
        "\\centering",
        "\\small",
        "\\caption{Main Table 1: regime $\\times$ agent deltas (mean at 8 agents minus mean at 1).}",
        "\\label{tab:p5_main1}",
        "\\begin{tabular}{@{}llrrr@{}}",
        "\\toprule",
        "Family & Regime & $\\Delta$tasks $1\\to 8$ & $\\Delta$coord.\\ tax & $\\Delta$p95 (ms) \\\\",
        "\\midrule",
    ])
    m1 = _main1_delta_rows(regime_agent_summary)
    if not m1:
        lines.append("\\multicolumn{5}{@{}l@{}}{--- (no summary JSON) ---} \\\\")
    for fam, reg, dt, dct, dlat in m1:
        lines.append(
            f"{_latex_escape(fam)} & {_latex_escape(reg)} & "
            f"{_fmt4(dt)} & {_fmt4(dct)} & {_fmt4(dlat)} \\\\",
        )
    lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}", ""])

    # Main Table 2
    lines.extend([
        "\\begin{table}[t]",
        "\\centering",
        "\\small",
        "\\caption{Main Table 2: scenario-heldout \\texttt{tasks_completed} (per-fold MAE).}",
        "\\label{tab:p5_main2}",
        "\\begin{tabular}{@{}lrrrl@{}}",
        "\\toprule",
        "Held-out & Global & Bucket & Regr. & Trigger \\\\",
        "\\midrule",
    ])
    for r in main_data.get("held_out_results") or []:
        beats = _fold_beats_feat(r)
        trig = "yes" if beats is True else ("no" if beats is False else "N/A")
        lines.append(
            f"{_latex_escape(str(r.get('holdout_label', '')))} & "
            f"{_fmt2(r.get('baseline_mae'))} & {_fmt2(r.get('feat_baseline_mae'))} & "
            f"{_fmt2(r.get('regression_mae'))} & {trig} \\\\",
        )
    lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}", ""])

    # Main Table 3
    proto_label_path = [
        ("leave-one-scenario-out", "scenario"),
        ("leave-one-family-out", "family"),
        ("leave-one-regime-out", "regime"),
        ("leave-one-agent-count-out", "agent_count"),
        ("leave-one-fault-setting-out", "fault"),
    ]
    lines.extend([
        "\\begin{table}[t]",
        "\\centering",
        "\\small",
        "\\caption{Main Table 3: protocol summary (\\texttt{tasks_completed}).}",
        "\\label{tab:p5_main3}",
        "\\begin{tabular}{@{}lrrl@{}}",
        "\\toprule",
        "Protocol & Regr.\\ MAE & Bucket MAE & Trigger \\\\",
        "\\midrule",
    ])
    for pretty, pk in proto_label_path:
        d = _load(proto_paths.get(pk))
        if not d:
            lines.append(
                f"\\multicolumn{{4}}{{@{{}}l@{{}}}}{{{_latex_escape(pretty)}: ---}} \\\\",
            )
            continue
        sc = d.get("success_criteria_met") or {}
        lines.append(
            f"{_latex_escape(pretty)} & {_fmt4(d.get('overall_regression_mae'))} & "
            f"{_fmt4(d.get('overall_feat_baseline_mae'))} & {sc.get('trigger_met')} \\\\",
        )
    lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}", ""])

    # Main Table 4
    sec = main_data.get("secondary_targets") or {}
    lines.extend([
        "\\begin{table}[t]",
        "\\centering",
        "\\small",
        "\\caption{Main Table 4: secondary targets (scenario-heldout bundle).}",
        "\\label{tab:p5_main4}",
        "\\begin{tabular}{@{}lrrl@{}}",
        "\\toprule",
        "Target & Regr.\\ MAE & Baseline MAE & Trigger \\\\",
        "\\midrule",
    ])
    for name in ("coordination_tax_proxy", "error_amplification_proxy"):
        block = sec.get(name) or {}
        sc = block.get("success_criteria_met") or {}
        tt = "\\texttt{" + name.replace("_", r"\_") + "}"
        lines.append(
            f"{tt} & {_fmt4(block.get('overall_regression_mae'))} & "
            f"{_fmt4(block.get('overall_baseline_mae'))} & {sc.get('trigger_met')} \\\\",
        )
    lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}", ""])

    (out_dir / "main_tables_booktabs.tex").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Export P5 Scaling tables for NeurIPS-oriented draft")
    ap.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    ap.add_argument("--family-results", type=Path, default=None)
    ap.add_argument("--regime-results", type=Path, default=None)
    ap.add_argument("--agent-results", type=Path, default=None)
    ap.add_argument("--fault-results", type=Path, default=None)
    ap.add_argument("--recommend-results", type=Path, default=None)
    ap.add_argument("--sensitivity-results", type=Path, default=None)
    ap.add_argument("--regime-agent-summary", type=Path, default=None)
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Write markdown tables to this path",
    )
    ap.add_argument(
        "--out-tex-dir",
        type=Path,
        default=None,
        help="Optional directory for verbatim .tex fragments",
    )
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    default_family = REPO / "datasets" / "runs" / "scaling_eval_family" / "heldout_results.json"
    default_regime = REPO / "datasets" / "runs" / "scaling_eval_regime" / "heldout_results.json"
    default_agent = REPO / "datasets" / "runs" / "scaling_eval_agent_count" / "heldout_results.json"
    default_fault = REPO / "datasets" / "runs" / "scaling_eval_fault" / "heldout_results.json"
    default_rec = REPO / "datasets" / "runs" / "scaling_recommend" / "recommendation_eval.json"
    default_sens = REPO / "datasets" / "runs" / "sensitivity_sweep" / "scaling_sensitivity.json"
    default_ra = REPO / "datasets" / "runs" / "scaling_summary" / "regime_agent_summary.json"

    family_p = args.family_results or default_family
    regime_p = args.regime_results or default_regime
    agent_p = args.agent_results or default_agent
    fault_p = args.fault_results or default_fault
    rec_p = args.recommend_results or default_rec
    sens_p = args.sensitivity_results or default_sens
    ra_p = args.regime_agent_summary or default_ra

    if not args.results.exists():
        print("Run scripts/scaling_heldout_eval.py then re-run this script.")
        return 1
    main_data = _load(args.results)
    assert main_data is not None
    fam_data = _load(family_p)
    regime_data = _load(regime_p)
    agent_data = _load(agent_p)
    fault_data = _load(fault_p)
    rec_data = _load(rec_p)
    sens_data = _load(sens_p)
    regime_agent_summary = _load(ra_p)

    rm = main_data.get("run_manifest") or {}
    commit = rm.get("commit") or ""
    total_rows = main_data.get("total_rows")
    chunks: list[str] = [
        "<!-- generated by export_scaling_tables.py; "
        f"holdout_mode={main_data.get('holdout_mode')}; "
        f"total_rows={total_rows}; "
        f"commit={commit}; "
        "scaling_fit=exploratory; recommendation=exploratory -->",
        "",
        "# P5 generated tables (NeurIPS Main 1–4 + appendix)",
        "",
        "**Interpretation guardrails:** scenario-heldout `trigger_met` is **protocol-specific**; "
        "`scaling_fit` and recommendation metrics are **exploratory** (see CLAIM_LOCK_NEURIPS2026.md).",
        "",
    ]
    chunks.extend(table_main1_title_grounding(regime_agent_summary))
    chunks.extend(table_main2_scenario_heldout(main_data))
    proto_paths = {
        "scenario": args.results,
        "family": family_p,
        "regime": regime_p,
        "agent_count": agent_p,
        "fault": fault_p,
    }
    chunks.extend(table_main3_protocol_summary(proto_paths))
    chunks.extend(table_main4_secondary(main_data))
    chunks.extend(appendix_collapse_prevalence(main_data, rec_data))
    chunks.extend(appendix_exploratory_scaling_fit(main_data))
    chunks.extend(appendix_baseline_hierarchy(main_data))
    chunks.extend(appendix_per_fold_detail(main_data))
    chunks.extend(appendix_regime_agent_pct(regime_agent_summary))
    chunks.extend(appendix_feature_ablation(main_data))
    chunks.extend(appendix_calibration(main_data))
    chunks.extend(appendix_sensitivity(sens_data))
    chunks.extend(appendix_recommend(rec_data))

    text = "\n".join(chunks)
    print(text)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")

    if args.out_tex_dir:
        write_latex_booktabs_main_tables(
            args.out_tex_dir,
            main_data,
            regime_agent_summary,
            proto_paths,
        )
        print(f"Wrote LaTeX booktabs bundle to {args.out_tex_dir / 'main_tables_booktabs.tex'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
