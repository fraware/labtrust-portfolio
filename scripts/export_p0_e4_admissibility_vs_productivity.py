#!/usr/bin/env python3
"""
Export P0 E4 admissibility-vs-productivity summary from canonical E4 artifacts.

Outputs:
  - datasets/runs/p0_e4_admissibility_vs_productivity.json
  - datasets/runs/p0_e4_admissibility_vs_productivity.csv
  - datasets/runs/p0_e4_coordination_shock_focus.json
  - datasets/runs/p0_e4_coordination_shock_focus.csv
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, stdev
from typing import Any


REPO = Path(__file__).resolve().parents[1]
DEFAULT_RUNS = REPO / "datasets" / "runs"
FOCUS_SCENARIO = "rep_cps_scheduling_v0"
FOCUS_REGIME = "coordination_shock"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def _safe_mean(values: list[float]) -> float:
    return mean(values) if values else 0.0


def _safe_stdev(values: list[float]) -> float:
    return stdev(values) if len(values) > 1 else 0.0


def _top_label(counter: Counter[str], default: str = "none") -> str:
    if not counter:
        return default
    return counter.most_common(1)[0][0]


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(
        description="Export P0 E4 admissibility-vs-productivity summaries"
    )
    ap.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS)
    args = ap.parse_args()

    runs = args.runs_dir
    raw_summary = _load_json(runs / "p0_e4_raw_summary.json")
    per_seed = _load_jsonl(runs / "p0_e4_per_seed.jsonl")
    raw_fail = _load_json(runs / "p0_e4_raw_failure_reasons.json")

    fail_reason_by_key: dict[tuple[str, str, str], Counter[str]] = defaultdict(
        Counter
    )
    for rec in raw_fail.get("failures", []):
        key = (
            str(rec.get("regime")),
            str(rec.get("scenario")),
            str(rec.get("controller")),
        )
        reason = str(rec.get("schema_failure_reason") or "unknown")
        fail_reason_by_key[key][reason] += 1

    by_key_rows: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(
        list
    )
    for row in per_seed:
        key = (
            str(row.get("regime")),
            str(row.get("scenario")),
            str(row.get("controller")),
        )
        by_key_rows[key].append(row)

    out_rows: list[dict[str, Any]] = []
    for rs in raw_summary.get("rows", []):
        regime = str(rs.get("regime"))
        scenario = str(rs.get("scenario"))
        controller = str(rs.get("controller"))
        key = (regime, scenario, controller)
        seed_rows = by_key_rows.get(key, [])

        outcomes = Counter(
            str(r.get("run_outcome") or "unknown") for r in seed_rows
        )
        tasks = [float(r.get("tasks_completed") or 0.0) for r in seed_rows]
        p95 = [float(r.get("task_latency_ms_p95") or 0.0) for r in seed_rows]

        top_reason = _top_label(
            fail_reason_by_key.get(key, Counter()),
            default="none",
        )
        if top_reason == "none":
            # If no conformance failure dominates this row, surface dominant
            # safe-fail/outcome.
            top_reason = f"outcome:{_top_label(outcomes, default='unknown')}"

        out_rows.append(
            {
                "controller": controller,
                "scenario_id": scenario,
                "regime": regime,
                "raw_conformance_rate": float(
                    rs.get("raw_conformance_rate") or 0.0
                ),
                "strong_replay_rate": float(
                    rs.get("strong_replay_match_rate") or 0.0
                ),
                "productive_success_rate": float(
                    rs.get("productive_success_rate") or 0.0
                ),
                "safe_nonproductive_rate": float(
                    rs.get("safe_nonproductive_rate") or 0.0
                ),
                "tasks_completed_mean": _safe_mean(tasks),
                "tasks_completed_stdev": _safe_stdev(tasks),
                "task_latency_ms_p95_mean": _safe_mean(p95),
                "top_outcome_class": _top_label(outcomes, default="unknown"),
                "top_failure_or_safe_fail_reason": top_reason,
                "n_seeds": int(rs.get("n_seeds") or len(seed_rows)),
            }
        )

    out_rows.sort(
        key=lambda r: (r["scenario_id"], r["regime"], r["controller"])
    )
    focus_rows = [
        r
        for r in out_rows
        if r["scenario_id"] == FOCUS_SCENARIO and r["regime"] == FOCUS_REGIME
    ]

    json_out = runs / "p0_e4_admissibility_vs_productivity.json"
    csv_out = runs / "p0_e4_admissibility_vs_productivity.csv"
    focus_json_out = runs / "p0_e4_coordination_shock_focus.json"
    focus_csv_out = runs / "p0_e4_coordination_shock_focus.csv"

    payload = {
        "experiment": "P0_E4_admissibility_vs_productivity",
        "source_artifacts": {
            "raw_summary": "datasets/runs/p0_e4_raw_summary.json",
            "per_seed": "datasets/runs/p0_e4_per_seed.jsonl",
            "raw_failure_reasons": (
                "datasets/runs/p0_e4_raw_failure_reasons.json"
            ),
        },
        "rows": out_rows,
    }
    json_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    fields = [
        "controller",
        "scenario_id",
        "regime",
        "raw_conformance_rate",
        "strong_replay_rate",
        "productive_success_rate",
        "safe_nonproductive_rate",
        "tasks_completed_mean",
        "tasks_completed_stdev",
        "task_latency_ms_p95_mean",
        "top_outcome_class",
        "top_failure_or_safe_fail_reason",
        "n_seeds",
    ]
    with csv_out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out_rows)

    focus_payload = {
        "experiment": "P0_E4_coordination_shock_focus",
        "scenario_id": FOCUS_SCENARIO,
        "regime": FOCUS_REGIME,
        "rows": focus_rows,
    }
    focus_json_out.write_text(
        json.dumps(focus_payload, indent=2) + "\n",
        encoding="utf-8",
    )
    with focus_csv_out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(focus_rows)

    print(
        json.dumps(
            {
                "wrote": [
                    str(json_out),
                    str(csv_out),
                    str(focus_json_out),
                    str(focus_csv_out),
                ],
                "rows": len(out_rows),
                "focus_rows": len(focus_rows),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
