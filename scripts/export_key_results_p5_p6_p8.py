#!/usr/bin/env python3
"""
Export key results (P5, P6, P8) as markdown for camera-ready drafts.
Reads heldout_results.json, comparison.json, red_team_results.json
(and optionally adapter_latency.json, confusable_deputy_results.json).
Run after the publishable pipeline to paste into a doc or verify numbers.
Usage (from repo root):
  python scripts/export_key_results_p5_p6_p8.py
  python scripts/export_key_results_p5_p6_p8.py --runs-dir path/to/datasets/runs
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_RUNS = REPO / "datasets" / "runs"


def _load(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def p5_block(runs: Path) -> list[str]:
    p = runs / "scaling_eval" / "heldout_results.json"
    data = _load(p)
    if not data:
        return ["## P5 — Key results", "", "*No heldout_results.json found.*", ""]
    lines = ["## P5 — Key results", ""]
    b_mae = data.get("overall_baseline_mae")
    ps_mae = data.get("overall_per_scenario_baseline_mae")
    r_mae = data.get("overall_regression_mae")
    reason = data.get("regression_skipped_reason")
    scm = data.get("success_criteria_met") or {}
    fit = data.get("scaling_fit") or {}
    if ps_mae is not None:
        lines.append(f"- Per-scenario baseline MAE: {ps_mae:.3f}")
    else:
        lines.append("- Per-scenario baseline MAE: —")
    if b_mae is not None:
        lines.append(f"- Global mean MAE: {b_mae:.3f}")
    else:
        lines.append("- Global mean MAE: —")
    if r_mae is not None:
        lines.append(f"- Regression MAE: {r_mae:.3f}")
    else:
        reason_txt = reason or "insufficient train rows"
        lines.append(f"- Regression: N/A ({reason_txt})")
    lines.append(f"- beat_baseline_out_of_sample: {scm.get('beat_baseline_out_of_sample', '—')}")
    lines.append(f"- trigger_met: {scm.get('trigger_met', '—')}")
    if fit:
        exp, r2 = fit.get("scaling_exponent", "—"), fit.get("scaling_r2", "—")
        lines.append(f"- Scaling fit: exponent {exp}, R² {r2}")
    lines.append("")
    return lines


def p6_block(runs: Path) -> list[str]:
    p = runs / "llm_eval" / "red_team_results.json"
    data = _load(p)
    lines = ["## P6 — Key results", ""]
    if not data:
        lines.append("*No red_team_results.json found.*")
        lines.append("")
        return lines
    scm = data.get("success_criteria_met") or {}
    n_pass = sum(1 for c in data.get("cases", []) if c.get("pass"))
    n_cases = len(data.get("cases", []))
    rt_pass = scm.get("red_team_all_pass", "—")
    lines.append(f"- Red-team: {n_pass}/{n_cases} pass, all_block_unsafe_pass: {rt_pass}")
    jb = data.get("jailbreak_style") or {}
    if jb:
        jb_pass = jb.get("all_pass", "—")
        lines.append(f"- Jailbreak-style: all_pass {jb_pass}")
    conf = _load(runs / "llm_eval" / "confusable_deputy_results.json")
    if conf:
        cd_pass = conf.get("all_pass", "—")
        n_cd = len(conf.get("confusable_deputy_cases", []))
        lines.append(f"- Confusable deputy: {n_cd} cases, all_pass {cd_pass}")
    adapter = _load(runs / "llm_eval" / "adapter_latency.json")
    if adapter:
        lat = adapter.get("tail_latency_p95_mean_ms")
        if lat is not None:
            lines.append(f"- Adapter latency (p95 mean ms): {lat}")
        else:
            lines.append("- Adapter latency: (run with --run-adapter)")
    if data.get("real_llm"):
        lines.append("- Table 1b (real-LLM): present; model_id in run_manifest.")
    lines.append("")
    return lines


def p8_block(runs: Path) -> list[str]:
    p = runs / "meta_eval" / "comparison.json"
    data = _load(p)
    lines = ["## P8 — Key results", ""]
    if not data:
        lines.append("*No comparison.json found.*")
        lines.append("")
        return lines
    lines.append(f"- no_safety_regression: {data.get('no_safety_regression', '—')}")
    lines.append(f"- meta_reduces_collapse: {data.get('meta_reduces_collapse', '—')}")
    meta = data.get("meta_controller") or {}
    fixed = data.get("fixed") or {}
    rsc = meta.get("regime_switch_count_total", "—")
    lines.append(f"- regime_switch_count_total: {rsc}")
    lines.append(f"- fixed collapse_count: {fixed.get('collapse_count', '—')}")
    if data.get("fallback_tasks_completed_mean") is not None:
        fb = data.get("fallback_tasks_completed_mean")
        lines.append(f"- fallback_tasks_completed_mean (two regimes): {fb}")
    lines.append(
        "- When collapse_count = 0: methodology and auditability only; "
        "use --non-vacuous for collapse comparison."
    )
    lines.append("")
    return lines


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Export key results P5, P6, P8 as markdown."
    )
    ap.add_argument(
        "--runs-dir", type=Path, default=DEFAULT_RUNS, help="Path to datasets/runs"
    )
    args = ap.parse_args()
    out = ["# Key results (P5, P6, P8)", ""]
    out.extend(p5_block(args.runs_dir))
    out.extend(p6_block(args.runs_dir))
    out.extend(p8_block(args.runs_dir))
    print("\n".join(out))


if __name__ == "__main__":
    main()
