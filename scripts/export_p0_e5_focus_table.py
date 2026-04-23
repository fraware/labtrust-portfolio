#!/usr/bin/env python3
"""
Export focused E5 model-evolution tables from per-seed rows.

Outputs:
- by-cell table grouped by version/controller/scenario/regime
- coordination_shock focused slice for manuscript-facing comparison
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from statistics import mean, stdev
from typing import Any

REPO = Path(__file__).resolve().parents[1]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def _mean(values: list[float]) -> float:
    return mean(values) if values else 0.0


def _stdev(values: list[float]) -> float:
    return stdev(values) if len(values) > 1 else 0.0


def _rate(flags: list[bool]) -> float:
    return (sum(1 for x in flags if x) / len(flags)) if flags else 0.0


def _aggregate_cell(rows: list[dict[str, Any]]) -> dict[str, Any]:
    raw_ok = [bool((r.get("raw_conformance") or {}).get("pass")) for r in rows]
    strong_ok = [bool(r.get("strong_replay_match")) for r in rows]
    release_ok = raw_ok  # consistent with E5 summary derivation
    productive_ok = [bool(r.get("productive_success")) for r in rows]
    safe_nonprod_ok = [bool(r.get("safe_nonproductive")) for r in rows]
    tasks = [float(r.get("tasks_completed") or 0.0) for r in rows]
    p95 = [float(r.get("task_latency_ms_p95") or 0.0) for r in rows]
    sample = rows[0] if rows else {}
    return {
        "version_label": sample.get("version_label"),
        "version_type": sample.get("version_type"),
        "controller": sample.get("controller"),
        "scenario_id": sample.get("scenario"),
        "regime": sample.get("regime"),
        "raw_conformance_rate": _rate(raw_ok),
        "strong_replay_rate": _rate(strong_ok),
        "release_allow_rate": _rate(release_ok),
        "productive_success_rate": _rate(productive_ok),
        "safe_nonproductive_rate": _rate(safe_nonprod_ok),
        "tasks_completed_mean": _mean(tasks),
        "tasks_completed_stdev": _stdev(tasks),
        "task_latency_ms_p95_mean": _mean(p95),
        "n_runs": len(rows),
    }


def _version_rollup_from_cells(cells: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    rollup: dict[str, dict[str, float]] = {}
    by_version: dict[str, list[dict[str, Any]]] = {}
    for row in cells:
        label = str(row["version_label"])
        by_version.setdefault(label, []).append(row)
    for label, rows in by_version.items():
        total = sum(int(r["n_runs"]) for r in rows)
        if total <= 0:
            continue
        metrics = [
            "raw_conformance_rate",
            "strong_replay_rate",
            "release_allow_rate",
            "productive_success_rate",
            "safe_nonproductive_rate",
            "tasks_completed_mean",
        ]
        agg: dict[str, float] = {}
        for metric in metrics:
            agg[metric] = sum(float(r[metric]) * int(r["n_runs"]) for r in rows) / total
        agg["n_runs"] = float(total)
        rollup[label] = agg
    return rollup


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k) for k in fields})


def _repo_rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO.resolve())).replace("\\", "/")
    except ValueError:
        return str(path.resolve()).replace("\\", "/")


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Export focused E5 by-cell tables")
    ap.add_argument(
        "--per-seed",
        type=Path,
        default=REPO
        / "papers"
        / "P0_MADS_CPS"
        / "kdd_workshop"
        / "artifacts"
        / "p0_e5_model_evolution_per_seed.jsonl",
    )
    ap.add_argument(
        "--summary-json",
        type=Path,
        default=REPO
        / "papers"
        / "P0_MADS_CPS"
        / "kdd_workshop"
        / "artifacts"
        / "p0_e5_model_evolution.json",
    )
    ap.add_argument(
        "--out-json",
        type=Path,
        default=REPO
        / "papers"
        / "P0_MADS_CPS"
        / "kdd_workshop"
        / "artifacts"
        / "p0_e5_model_evolution_by_cell.json",
    )
    ap.add_argument(
        "--out-csv",
        type=Path,
        default=REPO
        / "papers"
        / "P0_MADS_CPS"
        / "kdd_workshop"
        / "artifacts"
        / "p0_e5_model_evolution_by_cell.csv",
    )
    ap.add_argument(
        "--focus-json",
        type=Path,
        default=REPO
        / "papers"
        / "P0_MADS_CPS"
        / "kdd_workshop"
        / "artifacts"
        / "p0_e5_coordination_shock_focus.json",
    )
    ap.add_argument(
        "--focus-csv",
        type=Path,
        default=REPO
        / "papers"
        / "P0_MADS_CPS"
        / "kdd_workshop"
        / "artifacts"
        / "p0_e5_coordination_shock_focus.csv",
    )
    args = ap.parse_args()

    rows = _read_jsonl(args.per_seed)
    grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = {}
    for row in rows:
        key = (
            str(row.get("version_label")),
            str(row.get("controller")),
            str(row.get("scenario")),
            str(row.get("regime")),
        )
        grouped.setdefault(key, []).append(row)

    by_cell = [_aggregate_cell(v) for _, v in sorted(grouped.items())]
    by_cell.sort(
        key=lambda r: (
            str(r["version_label"]),
            str(r["controller"]),
            str(r["scenario_id"]),
            str(r["regime"]),
        )
    )

    focus = [
        r
        for r in by_cell
        if str(r["scenario_id"]) == "rep_cps_scheduling_v0"
        and str(r["regime"]) == "coordination_shock"
        and str(r["version_label"]) in {"V0_stable_baseline", "V2_regressive_update"}
    ]
    focus.sort(key=lambda r: (str(r["version_label"]), str(r["controller"])))

    summary = _read_json(args.summary_json)
    version_summary = {
        str(row["version_label"]): row for row in (summary.get("per_version_summary") or [])
    }
    rollup = _version_rollup_from_cells(by_cell)
    reconciliation: list[dict[str, Any]] = []
    for version_label, rolled in sorted(rollup.items()):
        ref = version_summary.get(version_label) or {}
        reconciliation.append(
            {
                "version_label": version_label,
                "rolled_n_runs": int(rolled["n_runs"]),
                "summary_n_runs": int(ref.get("n_runs") or 0),
                "delta_raw_conformance_rate": float(rolled["raw_conformance_rate"])
                - float(ref.get("raw_conformance_rate") or 0.0),
                "delta_strong_replay_rate": float(rolled["strong_replay_rate"])
                - float(ref.get("strong_replay_rate") or 0.0),
                "delta_release_allow_rate": float(rolled["release_allow_rate"])
                - float(ref.get("release_allow_rate") or 0.0),
                "delta_productive_success_rate": float(rolled["productive_success_rate"])
                - float(ref.get("productive_success_rate") or 0.0),
                "delta_safe_nonproductive_rate": float(rolled["safe_nonproductive_rate"])
                - float(ref.get("safe_nonproductive_rate") or 0.0),
                "delta_tasks_completed_mean": float(rolled["tasks_completed_mean"])
                - float(ref.get("tasks_completed_mean") or 0.0),
            }
        )

    payload = {
        "experiment": "P0_E5_model_evolution_by_cell",
        "source_artifact": _repo_rel(args.per_seed),
        "source_summary": _repo_rel(args.summary_json),
        "row_definition": "aggregated by version_label, controller, scenario_id, regime",
        "reconciliation_vs_per_version_summary": reconciliation,
        "rows": by_cell,
    }
    args.out_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    args.focus_json.write_text(
        json.dumps(
            {
                "experiment": "P0_E5_model_evolution_coordination_shock_focus",
                "source_by_cell": _repo_rel(args.out_json),
                "filter": {
                    "scenario_id": "rep_cps_scheduling_v0",
                    "regime": "coordination_shock",
                    "version_label": ["V0_stable_baseline", "V2_regressive_update"],
                },
                "rows": focus,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    fields = [
        "version_label",
        "version_type",
        "controller",
        "scenario_id",
        "regime",
        "raw_conformance_rate",
        "strong_replay_rate",
        "release_allow_rate",
        "productive_success_rate",
        "safe_nonproductive_rate",
        "tasks_completed_mean",
        "tasks_completed_stdev",
        "task_latency_ms_p95_mean",
        "n_runs",
    ]
    _write_csv(args.out_csv, by_cell, fields)
    _write_csv(args.focus_csv, focus, fields)

    print(
        json.dumps(
            {
                "by_cell_rows": len(by_cell),
                "focus_rows": len(focus),
                "out_json": str(args.out_json),
                "out_csv": str(args.out_csv),
                "focus_json": str(args.focus_json),
                "focus_csv": str(args.focus_csv),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

