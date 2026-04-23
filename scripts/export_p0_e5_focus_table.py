#!/usr/bin/env python3
"""
Export focused E5 model-evolution tables from per-seed rows.

Outputs:
- by-cell table grouped by version/controller/scenario/regime
- focused slice including:
  - explicit rep_cps_scheduling_v0 baseline V0->V2 comparison
  - explicit rep_cps_scheduling_v0 coordination_shock V0->V2 comparison
  - max-delta cells across all controller/scenario/regime combinations
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


def _index_cells(
    cells: list[dict[str, Any]],
) -> dict[tuple[str, str, str, str], dict[str, Any]]:
    idx: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for row in cells:
        key = (
            str(row["version_label"]),
            str(row["controller"]),
            str(row["scenario_id"]),
            str(row["regime"]),
        )
        idx[key] = row
    return idx


def _build_focus_rows(
    by_cell: list[dict[str, Any]],
    *,
    v0_label: str = "V0_stable_baseline",
    v2_label: str = "V2_regressive_update",
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    idx = _index_cells(by_cell)
    focus_rows: list[dict[str, Any]] = []
    delta_rows: list[dict[str, Any]] = []

    explicit_targets = [
        ("rep_cps_scheduling_v0", "baseline"),
        ("rep_cps_scheduling_v0", "coordination_shock"),
    ]
    for scenario_id, regime in explicit_targets:
        for controller in ("centralized", "rep_cps"):
            for version_label in (v0_label, v2_label):
                row = idx.get((version_label, controller, scenario_id, regime))
                if row:
                    enriched = dict(row)
                    enriched["focus_type"] = "explicit_target"
                    focus_rows.append(enriched)
            v0 = idx.get((v0_label, controller, scenario_id, regime))
            v2 = idx.get((v2_label, controller, scenario_id, regime))
            if v0 and v2:
                delta_rows.append(
                    {
                        "focus_type": "explicit_target_delta",
                        "controller": controller,
                        "scenario_id": scenario_id,
                        "regime": regime,
                        "version_from": v0_label,
                        "version_to": v2_label,
                        "delta_raw_conformance_rate": float(v2["raw_conformance_rate"])
                        - float(v0["raw_conformance_rate"]),
                        "delta_strong_replay_rate": float(v2["strong_replay_rate"])
                        - float(v0["strong_replay_rate"]),
                        "delta_release_allow_rate": float(v2["release_allow_rate"])
                        - float(v0["release_allow_rate"]),
                        "delta_productive_success_rate": float(v2["productive_success_rate"])
                        - float(v0["productive_success_rate"]),
                        "delta_safe_nonproductive_rate": float(v2["safe_nonproductive_rate"])
                        - float(v0["safe_nonproductive_rate"]),
                        "delta_tasks_completed_mean": float(v2["tasks_completed_mean"])
                        - float(v0["tasks_completed_mean"]),
                    }
                )

    # Max-delta scan across all shared controller/scenario/regime cells.
    max_task_abs = -1.0
    max_task_delta_row: dict[str, Any] | None = None
    max_safe_nonprod = -1.0
    max_safe_nonprod_row: dict[str, Any] | None = None
    seen_triples: set[tuple[str, str, str]] = set()
    for row in by_cell:
        triple = (str(row["controller"]), str(row["scenario_id"]), str(row["regime"]))
        if triple in seen_triples:
            continue
        seen_triples.add(triple)
        v0 = idx.get((v0_label, triple[0], triple[1], triple[2]))
        v2 = idx.get((v2_label, triple[0], triple[1], triple[2]))
        if not v0 or not v2:
            continue
        delta_tasks = float(v2["tasks_completed_mean"]) - float(v0["tasks_completed_mean"])
        abs_delta_tasks = abs(delta_tasks)
        delta_safe = float(v2["safe_nonproductive_rate"]) - float(v0["safe_nonproductive_rate"])
        if abs_delta_tasks > max_task_abs:
            max_task_abs = abs_delta_tasks
            max_task_delta_row = {
                "focus_type": "max_abs_delta_tasks_completed_mean",
                "controller": triple[0],
                "scenario_id": triple[1],
                "regime": triple[2],
                "version_from": v0_label,
                "version_to": v2_label,
                "delta_tasks_completed_mean": delta_tasks,
                "delta_safe_nonproductive_rate": delta_safe,
                "delta_productive_success_rate": float(v2["productive_success_rate"])
                - float(v0["productive_success_rate"]),
                "delta_raw_conformance_rate": float(v2["raw_conformance_rate"])
                - float(v0["raw_conformance_rate"]),
                "delta_strong_replay_rate": float(v2["strong_replay_rate"])
                - float(v0["strong_replay_rate"]),
                "delta_release_allow_rate": float(v2["release_allow_rate"])
                - float(v0["release_allow_rate"]),
            }
        if delta_safe > max_safe_nonprod:
            max_safe_nonprod = delta_safe
            max_safe_nonprod_row = {
                "focus_type": "max_delta_safe_nonproductive_rate",
                "controller": triple[0],
                "scenario_id": triple[1],
                "regime": triple[2],
                "version_from": v0_label,
                "version_to": v2_label,
                "delta_tasks_completed_mean": delta_tasks,
                "delta_safe_nonproductive_rate": delta_safe,
                "delta_productive_success_rate": float(v2["productive_success_rate"])
                - float(v0["productive_success_rate"]),
                "delta_raw_conformance_rate": float(v2["raw_conformance_rate"])
                - float(v0["raw_conformance_rate"]),
                "delta_strong_replay_rate": float(v2["strong_replay_rate"])
                - float(v0["strong_replay_rate"]),
                "delta_release_allow_rate": float(v2["release_allow_rate"])
                - float(v0["release_allow_rate"]),
            }

    for row in (max_task_delta_row, max_safe_nonprod_row):
        if row:
            delta_rows.append(row)
            # Include corresponding V0/V2 value rows for direct reviewer readability.
            controller = str(row["controller"])
            scenario_id = str(row["scenario_id"])
            regime = str(row["regime"])
            for version_label in (v0_label, v2_label):
                value_row = idx.get((version_label, controller, scenario_id, regime))
                if value_row:
                    enriched = dict(value_row)
                    enriched["focus_type"] = str(row["focus_type"])
                    focus_rows.append(enriched)

    # De-duplicate value rows.
    dedup: dict[tuple[str, str, str, str, str], dict[str, Any]] = {}
    for row in focus_rows:
        k = (
            str(row["focus_type"]),
            str(row["version_label"]),
            str(row["controller"]),
            str(row["scenario_id"]),
            str(row["regime"]),
        )
        dedup[k] = row
    focus_rows = list(dedup.values())
    focus_rows.sort(
        key=lambda r: (
            str(r["focus_type"]),
            str(r["scenario_id"]),
            str(r["regime"]),
            str(r["controller"]),
            str(r["version_label"]),
        )
    )
    delta_rows.sort(
        key=lambda r: (str(r["focus_type"]), str(r["scenario_id"]), str(r["regime"]), str(r["controller"]))
    )
    return focus_rows, delta_rows


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

    focus, focus_deltas = _build_focus_rows(by_cell)

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
                "focus_policy": {
                    "explicit_targets": [
                        {"scenario_id": "rep_cps_scheduling_v0", "regime": "baseline"},
                        {"scenario_id": "rep_cps_scheduling_v0", "regime": "coordination_shock"},
                    ],
                    "max_delta_scan": "V0_stable_baseline->V2_regressive_update across all cells",
                },
                "value_rows": focus,
                "delta_rows": focus_deltas,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    fields = [
        "focus_type",
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
                "focus_delta_rows": len(focus_deltas),
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

