#!/usr/bin/env python3
"""
Export a focused controller divergence table for:
  regime=coordination_shock, scenario=rep_cps_scheduling_v0

Usage:
  python scripts/export_p0_e4_controller_divergence_table.py
  python scripts/export_p0_e4_controller_divergence_table.py --format json
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_PER_SEED = REPO / "datasets" / "runs" / "p0_e4_per_seed.jsonl"
DEFAULT_RAW_SUMMARY = REPO / "datasets" / "runs" / "p0_e4_raw_summary.json"
TARGET_REGIME = "coordination_shock"
TARGET_SCENARIO = "rep_cps_scheduling_v0"


def _load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def _mean(vals: list[float]) -> float:
    return statistics.mean(vals) if vals else 0.0


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Export focused P0 E4 controller divergence table")
    ap.add_argument("--per-seed", type=Path, default=DEFAULT_PER_SEED)
    ap.add_argument("--raw-summary", type=Path, default=DEFAULT_RAW_SUMMARY)
    ap.add_argument("--regime", type=str, default=TARGET_REGIME)
    ap.add_argument("--scenario", type=str, default=TARGET_SCENARIO)
    ap.add_argument("--format", choices=("md", "json"), default="md")
    args = ap.parse_args()

    if not args.per_seed.exists() or not args.raw_summary.exists():
        print("Missing inputs: per-seed JSONL and/or raw summary JSON not found.", file=sys.stderr)
        return 1

    per_seed = [
        r
        for r in _load_jsonl(args.per_seed)
        if r.get("regime") == args.regime and r.get("scenario") == args.scenario
    ]
    raw_rows = json.loads(args.raw_summary.read_text(encoding="utf-8")).get("rows", [])
    raw_by_controller = {
        r.get("controller"): r
        for r in raw_rows
        if r.get("regime") == args.regime and r.get("scenario") == args.scenario
    }

    if not per_seed:
        print("No matching rows for selected regime/scenario.", file=sys.stderr)
        return 1

    controllers = sorted({str(r.get("controller")) for r in per_seed})
    table_rows: list[dict] = []
    for controller in controllers:
        rs = [r for r in per_seed if r.get("controller") == controller]
        summary_row = raw_by_controller.get(controller, {})
        n = len(rs)
        prod_rate = (
            float(summary_row["productive_success_rate"])
            if "productive_success_rate" in summary_row
            else (sum(1 for r in rs if bool(r.get("productive_success"))) / n if n else 0.0)
        )
        safe_nonprod_rate = (
            float(summary_row["safe_nonproductive_rate"])
            if "safe_nonproductive_rate" in summary_row
            else (sum(1 for r in rs if bool(r.get("safe_nonproductive"))) / n if n else 0.0)
        )
        table_rows.append(
            {
                "controller": controller,
                "raw_conformance_rate": float(summary_row.get("raw_conformance_rate", 0.0)),
                "strong_replay_rate": float(summary_row.get("strong_replay_match_rate", 0.0)),
                "productive_success_rate": prod_rate,
                "safe_nonproductive_rate": safe_nonprod_rate,
                "mean_tasks_completed": _mean([float(r.get("tasks_completed") or 0.0) for r in rs]),
                "mean_p95_latency_ms": _mean([float(r.get("task_latency_ms_p95") or 0.0) for r in rs]),
                "mean_coordination_messages": _mean(
                    [float(r.get("coordination_messages") or 0.0) for r in rs]
                ),
                "mean_event_count": _mean([float(r.get("trace_event_count") or 0.0) for r in rs]),
            }
        )

    if args.format == "json":
        out = {
            "scenario": args.scenario,
            "regime": args.regime,
            "rows": table_rows,
        }
        print(json.dumps(out, indent=2))
        return 0

    lines = [
        "## P0 E4 — Controller Divergence Focus Table",
        "",
        f"Scenario: `{args.scenario}`; Regime: `{args.regime}`",
        "",
        "| Controller | Raw conformance rate | Strong replay rate | Productive success rate | Safe nonproductive rate | Mean tasks completed | Mean p95 latency | Mean coordination messages | Mean event count |",
        "|------------|----------------------|--------------------|-------------------------|--------------------------|----------------------|------------------|----------------------------|------------------|",
    ]
    for r in table_rows:
        lines.append(
            f"| {r['controller']} | {r['raw_conformance_rate']:.2f} | {r['strong_replay_rate']:.2f} | "
            f"{r['productive_success_rate']:.2f} | {r['safe_nonproductive_rate']:.2f} | "
            f"{r['mean_tasks_completed']:.2f} | {r['mean_p95_latency_ms']:.2f} | "
            f"{r['mean_coordination_messages']:.2f} | {r['mean_event_count']:.2f} |"
        )
    lines.append("")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
