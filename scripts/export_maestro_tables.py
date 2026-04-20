#!/usr/bin/env python3
"""
Export P4 MAESTRO markdown tables for the paper: fault sweep, baselines, coverage, anti-gaming.
Usage:
  python scripts/export_maestro_tables.py [--multi-sweep PATH] [--baseline PATH] [--out PATH]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_MULTI_SWEEP = REPO / "datasets" / "runs" / "maestro_fault_sweep" / "multi_sweep.json"
DEFAULT_BASELINE = REPO / "bench" / "maestro" / "baseline_summary.json"
DEFAULT_ANTIGAMING = REPO / "datasets" / "runs" / "maestro_antigaming" / "antigaming_results.json"
SCENARIOS_DIR = REPO / "bench" / "maestro" / "scenarios"


def _fmt(x: float | int | str | None) -> str:
    if x is None:
        return "n/a"
    if isinstance(x, float):
        return f"{x:.2f}"
    return str(x)


def table_fault_sweep(multi_sweep_path: Path) -> list[str]:
    if not multi_sweep_path.exists():
        return [
            "# Table A — Fault sweep",
            "",
            f"Missing `{multi_sweep_path}`. Run `scripts/maestro_fault_sweep.py`.",
            "",
        ]
    data = json.loads(multi_sweep_path.read_text(encoding="utf-8"))
    lines = [
        "# Table A - Fault sweep (MAESTRO_REPORT v0.2 aggregates)",
        "",
        "| Scenario | Setting | tasks_mean | tasks_stdev | p95_mean | p99_run | ttr_ms_mean | tts_ms_mean | "
        "recovery_rate_mean | safety_viol_mean | steps_after_fault_mean |",
        "|----------|---------|------------|-------------|----------|---------|-------------|-------------|----------------------|------------------|--------------------------|",
    ]
    for combined in data.get("per_scenario", []):
        scenario = combined.get("scenario", "")
        for summary in combined.get("sweep", []):
            setting = summary.get("setting", "")
            p99r = summary.get("p95_latency_ms_p99", "")
            lines.append(
                f"| {scenario} | {setting} | {_fmt(summary.get('tasks_completed_mean'))} | "
                f"{_fmt(summary.get('tasks_completed_stdev'))} | "
                f"{_fmt(summary.get('p95_latency_ms_mean'))} | {_fmt(p99r)} | "
                f"{_fmt(summary.get('time_to_recovery_ms_mean'))} | "
                f"{_fmt(summary.get('time_to_safe_state_ms_mean'))} | "
                f"{_fmt(summary.get('recovery_success_rate_mean'))} | "
                f"{_fmt(summary.get('safety_violation_count_mean'))} | "
                f"{_fmt(summary.get('steps_to_completion_after_first_fault_mean'))} |"
            )
    lines.append("")
    return lines


def table_baselines(baseline_path: Path) -> list[str]:
    if not baseline_path.exists():
        return [
            "# Table B — Baselines",
            "",
            f"Missing `{baseline_path}`. Run `scripts/maestro_baselines.py`.",
            "",
        ]
    data = json.loads(baseline_path.read_text(encoding="utf-8"))
    lines = [
        "# Table B - Baselines (per-seed + regimes)",
        "",
        "| Regime | Adapter | Seed | tasks | p95_ms | safety_viol | unsafe_succ | msgs/task | outcome |",
        "|--------|---------|------|-------|--------|-------------|-------------|-----------|---------|",
    ]
    for row in data.get("rows", []):
        lines.append(
            f"| {row.get('regime', '')} | {row.get('adapter', '')} | {row.get('seed', '')} | "
            f"{row.get('tasks_completed', '')} | {row.get('p95_latency_ms', '')} | "
            f"{row.get('safety_violation_count', '')} | {row.get('unsafe_success_count', '')} | "
            f"{_fmt(row.get('messages_per_completed_task'))} | {row.get('run_outcome', '')} |"
        )
    lines.append("")
    lines.append("## Baseline aggregates (by regime)")
    lines.append("")
    for regime, block in (data.get("aggregates") or {}).items():
        lines.append(f"### {regime}")
        lines.append("")
        lines.append(
            "| Adapter | tasks_mean | tasks_stdev | p95_mean | p99_mean | safety_mean | recovery_mean | ttr_mean | tts_mean | msgs/task_mean |"
        )
        lines.append("|---------|---------|---------|-------|-------|-----------|-----------|-------|-------|-------------|")
        for row in block.get("by_adapter", []):
            if not row:
                continue
            lines.append(
                f"| {row.get('adapter', '')} | {_fmt(row.get('tasks_completed_mean'))} | "
                f"{_fmt(row.get('tasks_completed_stdev'))} | {_fmt(row.get('p95_latency_ms_mean'))} | "
                f"{_fmt(row.get('p99_latency_ms_mean'))} | {_fmt(row.get('safety_violation_count_mean'))} | "
                f"{_fmt(row.get('recovery_success_rate_mean'))} | {_fmt(row.get('time_to_recovery_ms_mean'))} | "
                f"{_fmt(row.get('time_to_safe_state_ms_mean'))} | {_fmt(row.get('messages_per_completed_task_mean'))} |"
            )
        lines.append("")
    return lines


def table_scenario_coverage() -> list[str]:
    try:
        import yaml  # type: ignore
    except ImportError:
        return ["# Table C — Scenario coverage", "", "(PyYAML not installed)", ""]
    lines = [
        "# Table C - Scenario and fault coverage",
        "",
        "| scenario | family | tasks_n | resource_graph | fault_classes_in_spec | safe_state_semantics |",
        "|----------|--------|---------|----------------|------------------------|----------------------|",
    ]
    if not SCENARIOS_DIR.is_dir():
        return lines + ["(no scenarios dir)", ""]
    for path in sorted(SCENARIOS_DIR.glob("*.yaml")):
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        sid = doc.get("id", path.stem)
        fam = doc.get("family", "default")
        tasks_n = len(doc.get("tasks") or [])
        rg = "yes" if doc.get("resource_graph") else "no"
        fl = ", ".join(
            str((f or {}).get("name", "")) for f in (doc.get("faults") or []) if isinstance(f, dict)
        )
        safe_sem = "yes (trace safe_state_reached when all tasks complete cleanly)"
        lines.append(f"| {sid} | {fam} | {tasks_n} | {rg} | {fl} | {safe_sem} |")
    lines.append("")
    return lines


def table_antigaming(ant_path: Path) -> list[str]:
    if not ant_path.exists():
        return [
            "# Table D — Anti-gaming",
            "",
            f"Missing `{ant_path}`. Run `scripts/maestro_antigaming_eval.py`.",
            "",
        ]
    data = json.loads(ant_path.read_text(encoding="utf-8"))
    lines = [
        "# Table D - Anti-gaming / scoring robustness",
        "",
        "| strategy | tasks_completed | safety_violations | unsafe_success | composite_score | rank |",
        "|----------|-----------------|-------------------|----------------|-----------------|------|",
    ]
    for row in data.get("ranked", []):
        lines.append(
            f"| {row.get('strategy', '')} | {row.get('tasks_completed', '')} | "
            f"{row.get('safety_violation_count', '')} | {row.get('unsafe_success_count', '')} | "
            f"{_fmt(row.get('composite_score'))} | {row.get('rank', '')} |"
        )
    lines.append("")
    return lines


def main() -> int:
    ap = argparse.ArgumentParser(description="Export MAESTRO markdown tables for P4")
    ap.add_argument("--multi-sweep", type=Path, default=DEFAULT_MULTI_SWEEP)
    ap.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    ap.add_argument("--antigaming", type=Path, default=DEFAULT_ANTIGAMING)
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Write combined markdown here (default: stdout only)",
    )
    args = ap.parse_args()
    parts: list[str] = []
    parts.extend(table_fault_sweep(args.multi_sweep))
    parts.extend(table_baselines(args.baseline))
    parts.extend(table_scenario_coverage())
    parts.extend(table_antigaming(args.antigaming))
    text = "\n".join(parts) + "\n"
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
