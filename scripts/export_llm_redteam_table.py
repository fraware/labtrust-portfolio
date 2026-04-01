#!/usr/bin/env python3
"""
Export P6 LLM red-team and confusable deputy results as markdown tables.
Reads red_team_results.json and confusable_deputy_results.json; outputs
Table 1 (red-team, row count from run) and Table 2 (confusable deputy).
Usage: python scripts/export_llm_redteam_table.py [--out-dir datasets/runs/llm_eval]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO / "datasets" / "runs" / "llm_eval"


def _fmt(x) -> str:
    if x is None:
        return "—"
    if isinstance(x, bool):
        return "yes" if x else "no"
    return str(x)


def _append_real_llm_table(
    lines: list,
    real_llm: dict,
    run_manifest: dict,
    section_label: str | None = None,
) -> None:
    """Append Table 1b content for one real_llm result. section_label used for multi-model subsection header."""
    model_id = run_manifest.get("real_llm_model_id") or real_llm.get("model_id", "—")
    if section_label is not None:
        model_id = section_label
    n_runs = real_llm.get("n_runs_per_case", 1)
    if real_llm.get("cases"):
        if n_runs > 1:
            title = "# Table 1b — Real-LLM (red-team + confusable-deputy; N runs per case, pass_rate and latency with 95% CI)"
            if section_label is not None:
                title = f"# Table 1b — Real-LLM: {section_label}"
            lines.extend([
                title,
                "",
                "| Case ID | expected_block | pass_rate_pct | pass_rate_ci95 | latency_mean_ms | latency_stdev_ms |",
                "|---------|----------------|---------------|----------------|-----------------|------------------|",
            ])
            for c in real_llm["cases"]:
                ci = f"[{c.get('pass_rate_ci95_lower', '—')}, {c.get('pass_rate_ci95_upper', '—')}]"
                lines.append(
                    f"| {c.get('case_id', '')} | {_fmt(c.get('expected_block'))} | "
                    f"{c.get('pass_rate_pct', '—')} | {ci} | "
                    f"{c.get('latency_mean_ms', '—')} | {c.get('latency_stdev_ms', '—')} |"
                )
            lines.extend([
                "",
                "Summary (same suites as Table 1):",
                "| Model | n_runs_per_case | pass_rate_pct | pass_rate_ci95 | all_block_unsafe_pass | total_latency_ms |",
                "|-------|-----------------|--------------|----------------|------------------------|------------------|",
                f"| {model_id} | {n_runs} | {real_llm.get('pass_rate_pct', '—')} | "
                f"[{real_llm.get('pass_rate_ci95_lower', '—')}, {real_llm.get('pass_rate_ci95_upper', '—')}] | "
                f"{_fmt(real_llm.get('all_block_unsafe_pass'))} | {_fmt(real_llm.get('total_latency_ms'))} |",
                "",
            ])
        else:
            title = "# Table 1b — Real-LLM (red-team + confusable-deputy suites; run with --real-llm and .env keys)"
            if section_label is not None:
                title = f"# Table 1b — Real-LLM: {section_label}"
            lines.extend([
                title,
                "",
                "| Case ID | expected_block | actually_blocked | pass | latency_ms |",
                "|---------|----------------|------------------|------|------------|",
            ])
            for c in real_llm["cases"]:
                lines.append(
                    f"| {c.get('case_id', '')} | {_fmt(c.get('expected_block'))} | "
                    f"{_fmt(c.get('actually_blocked'))} | {_fmt(c.get('pass'))} | {_fmt(c.get('latency_ms'))} |"
                )
            lines.extend([
                "",
                "Summary (same suites as Table 1):",
                "| Model | all_block_unsafe_pass | total_latency_ms |",
                "|-------|------------------------|------------------|",
                f"| {model_id} | {_fmt(real_llm.get('all_block_unsafe_pass'))} | {_fmt(real_llm.get('total_latency_ms'))} |",
                "",
            ])
    else:
        title = "# Table 1b — Real-LLM (run with --real-llm and .env keys)"
        if section_label is not None:
            title = f"# Table 1b — Real-LLM: {section_label}"
        lines.extend([
            title,
            "",
            "| Model | all_block_unsafe_pass | latency_ms |",
            "|-------|------------------------|------------|",
            f"| {model_id} | {_fmt(real_llm.get('all_block_unsafe_pass'))} | {_fmt(real_llm.get('latency_sec'))} |",
            "",
        ])


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Export P6 red-team and confusable deputy tables"
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT,
        help="Directory containing red_team_results.json and confusable_deputy_results.json",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Optional file path to write table markdown (also prints to stdout)",
    )
    args = ap.parse_args()
    red_path = args.out_dir / "red_team_results.json"
    conf_path = args.out_dir / "confusable_deputy_results.json"
    if not red_path.exists():
        print("Run scripts/llm_redteam_eval.py first to produce red_team_results.json.")
        return 1
    red = json.loads(red_path.read_text(encoding="utf-8"))
    cases = red.get("cases", [])
    n_red = len(cases)
    lines = [
        f"# Table 1 — Red-team ({n_red} cases)",
        "",
        "Validator: allow_list + safe_args + ponr_gate (PONR / gate-bypass proposals) + privilege heuristic. Regenerate with export_llm_redteam_table.py.",
        "",
        "| Case ID | expected_block | actually_blocked | pass |",
        "|---------|----------------|------------------|------|",
    ]
    for c in cases:
        lines.append(
            f"| {c.get('id', '')} | {_fmt(c.get('expected_block'))} | "
            f"{_fmt(c.get('actually_blocked'))} | {_fmt(c.get('pass'))} |"
        )
    lines.append("")
    # Table 1b — Real-LLM (when run with --real-llm); multi-model when real_llm_models present
    real_llm_models = red.get("real_llm_models", [])
    real_llm = red.get("real_llm", {})
    if real_llm_models:
        # Multi-model: one subsection per model, then combined summary table
        for real_llm in real_llm_models:
            if real_llm.get("error"):
                lines.extend([
                    "# Table 1b — Real-LLM: " + real_llm.get("model_id", "?"),
                    "",
                    "Error: " + str(real_llm.get("error", "")),
                    "",
                ])
                continue
            _append_real_llm_table(lines, real_llm, red.get("run_manifest", {}), section_label=real_llm.get("model_id", "?"))
        # Combined summary across models
        lines.extend([
            "# Table 1b — Real-LLM summary (all models)",
            "",
            "| Model | provider | n_runs_per_case | pass_rate_pct | pass_rate_ci95 | all_block_unsafe_pass | total_latency_ms |",
            "|-------|----------|-----------------|--------------|----------------|------------------------|------------------|",
        ])
        for m in real_llm_models:
            if m.get("error"):
                lines.append(f"| {m.get('model_id', '?')} | — | — | — | — | failed | — |")
            else:
                ci = f"[{m.get('pass_rate_ci95_lower', '—')}, {m.get('pass_rate_ci95_upper', '—')}]"
                lines.append(
                    f"| {m.get('model_id', '—')} | {m.get('provider', '—')} | {m.get('n_runs_per_case', '—')} | "
                    f"{m.get('pass_rate_pct', '—')} | {ci} | {_fmt(m.get('all_block_unsafe_pass'))} | {_fmt(m.get('total_latency_ms'))} |"
                )
        lines.append("")
    elif real_llm and real_llm.get("real_llm_used"):
        _append_real_llm_table(lines, real_llm, red.get("run_manifest", {}))
    elif real_llm and real_llm.get("error"):
        lines.extend([
            "# Table 1b — Real-LLM",
            "",
            "Error (e.g. missing .env keys): " + str(real_llm.get("error", "")),
            "",
        ])
    # Jailbreak-style cases (when present)
    jb = red.get("jailbreak_style", {})
    if jb and jb.get("cases"):
        lines.extend([
            "# Table — Jailbreak-style cases",
            "",
            "Containment, not elimination. Validator blocks steps whose args contain jailbreak-style phrases (ignore previous instructions, disregard instruction).",
            "",
            "| Case ID | expected_block | actually_blocked | pass |",
            "|---------|----------------|------------------|------|",
        ])
        for c in jb["cases"]:
            lines.append(
                f"| {c.get('id', '')} | {_fmt(c.get('expected_block'))} | "
                f"{_fmt(c.get('actually_blocked'))} | {_fmt(c.get('pass'))} |"
            )
        lines.append("")
    if conf_path.exists():
        conf = json.loads(conf_path.read_text(encoding="utf-8"))
        cd_cases = conf.get("confusable_deputy_cases", [])
        n_cd = len(cd_cases)
        lines.extend([
            f"# Table 2 — Confusable deputy ({n_cd} cases)",
            "",
            "| Case ID | expected_block | actually_blocked | pass |",
            "|---------|----------------|------------------|------|",
        ])
        for c in cd_cases:
            lines.append(
                f"| {c.get('id', '')} | {_fmt(c.get('expected_block'))} | "
                f"{_fmt(c.get('actually_blocked'))} | {_fmt(c.get('pass'))} |"
            )
        lines.append("")
    text = "\n".join(lines)
    print(text)
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
        print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
