#!/usr/bin/env python3
"""
Plot P4 paper figures from multi_sweep.json (and optional baseline_summary.json):
 1) Mean time to recovery / safe state by setting (lab scenario slice or all).
 2) Safety violation rate by setting.
 3) Messages per completed task (mean) where present in per_run (optional).
Writes PNGs + JSON sidecars under docs/figures/.
Usage: python scripts/plot_maestro_recovery.py [--multi-sweep path] [--baseline path] [--out-dir path]
"""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_SWEEP = REPO / "datasets" / "runs" / "maestro_fault_sweep" / "multi_sweep.json"
DEFAULT_BASE = REPO / "bench" / "maestro" / "baseline_summary.json"
FIG_DIR = REPO / "docs" / "figures"


def _flatten_sweep(data: dict) -> list[dict]:
    rows = []
    for combined in data.get("per_scenario", []):
        scenario = combined.get("scenario", "")
        for s in combined.get("sweep", []):
            rows.append({"scenario": scenario, **s})
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description="Plot P4 MAESTRO figures from sweep JSON")
    ap.add_argument("--multi-sweep", type=Path, default=DEFAULT_SWEEP)
    ap.add_argument("--baseline", type=Path, default=DEFAULT_BASE)
    ap.add_argument("--out-dir", type=Path, default=FIG_DIR)
    args = ap.parse_args()
    if not args.multi_sweep.exists():
        print(f"Error: {args.multi_sweep} not found. Run maestro_fault_sweep.py first.")
        return 1
    data = json.loads(args.multi_sweep.read_text(encoding="utf-8"))
    rows = _flatten_sweep(data)
    if not rows:
        print("No sweep rows.")
        return 1

    args.out_dir.mkdir(parents=True, exist_ok=True)
    side_a = {
        "figure": "p4_recovery_times",
        "x": [r.get("setting", "") for r in rows],
        "time_to_recovery_ms_mean": [r.get("time_to_recovery_ms_mean") for r in rows],
        "time_to_safe_state_ms_mean": [r.get("time_to_safe_state_ms_mean") for r in rows],
        "scenario": [r.get("scenario", "") for r in rows],
    }
    (args.out_dir / "p4_recovery_times.json").write_text(json.dumps(side_a, indent=2) + "\n", encoding="utf-8")

    side_b = {
        "figure": "p4_safety_violations",
        "x": [r.get("setting", "") for r in rows],
        "safety_violation_count_mean": [r.get("safety_violation_count_mean") for r in rows],
        "scenario": [r.get("scenario", "") for r in rows],
    }
    (args.out_dir / "p4_safety_violations.json").write_text(json.dumps(side_b, indent=2) + "\n", encoding="utf-8")

    msgs_per_task = []
    for r in rows:
        pr = r.get("per_run") or []
        vals = []
        for x in pr:
            if x.get("coordination_messages") is not None and x.get("tasks_completed"):
                vals.append(float(x["coordination_messages"]) / max(1, int(x["tasks_completed"])))
        msgs_per_task.append(statistics.mean(vals) if vals else None)
    side_c = {
        "figure": "p4_efficiency_messages_per_task",
        "x": [r.get("setting", "") for r in rows],
        "messages_per_completed_task_mean": msgs_per_task,
        "scenario": [r.get("scenario", "") for r in rows],
    }
    (args.out_dir / "p4_efficiency_messages_per_task.json").write_text(
        json.dumps(side_c, indent=2) + "\n", encoding="utf-8"
    )

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        def _grouped_bar(path: Path, title: str, xs: list[str], series: list[tuple[str, list[float]]]) -> None:
            fig, ax = plt.subplots(figsize=(11, 4))
            n = len(xs)
            idx = list(range(n))
            width = 0.8 / max(1, len(series))
            for i, (label, ys) in enumerate(series):
                offset = (i - (len(series) - 1) / 2.0) * width
                ax.bar([j + offset for j in idx], ys, width, label=label)
            ax.set_xticks(idx)
            ax.set_xticklabels(xs, rotation=45, ha="right")
            ax.set_title(title)
            ax.legend()
            plt.tight_layout()
            plt.savefig(path, dpi=150)
            plt.close()

        ttr = [0.0 if v is None else float(v) for v in side_a["time_to_recovery_ms_mean"]]
        tts = [0.0 if v is None else float(v) for v in side_a["time_to_safe_state_ms_mean"]]
        _grouped_bar(
            args.out_dir / "p4_recovery_curve.png",
            "P4 Recovery: mean time to recovery vs safe state by sweep row (concatenated settings)",
            side_a["x"],
            [("ttr_ms_mean", ttr), ("tts_ms_mean", tts)],
        )
        sv = [0.0 if v is None else float(v) for v in side_b["safety_violation_count_mean"]]
        _grouped_bar(
            args.out_dir / "p4_safety_violations.png",
            "P4 Safety: mean safety violations by sweep row",
            side_b["x"],
            [("violations_mean", sv)],
        )
        mp = [0.0 if v is None else float(v) for v in side_c["messages_per_completed_task_mean"]]
        _grouped_bar(
            args.out_dir / "p4_efficiency_messages.png",
            "P4 Efficiency: messages per completed task (approx. from per_run)",
            side_c["x"],
            [("msgs_per_task", mp)],
        )
        print(f"Wrote figures under {args.out_dir}")
    except ImportError:
        print("matplotlib not installed; JSON sidecars only.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
