#!/usr/bin/env python3
"""
P5: export direct regime x agent_count empirical summary for title grounding.
Writes JSON (+ optional markdown) from frozen multiscenario runs.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "impl" / "src"))


def _mean(xs: List[float]) -> float | None:
    return float(sum(xs) / len(xs)) if xs else None


def _stdev(xs: List[float]) -> float | None:
    if len(xs) < 2:
        return None
    return float(statistics.pstdev(xs))


def _ci95_half(xs: List[float]) -> float | None:
    if len(xs) < 2:
        return None
    sd = statistics.pstdev(xs)
    return float(1.96 * sd / math.sqrt(len(xs)))


def _pct(x: float | None, y: float | None) -> float | None:
    if x is None or y is None or abs(y) < 1e-12:
        return None
    return float(100.0 * (x - y) / y)


def _fmt4(x: float | None) -> str:
    if x is None:
        return "-"
    return f"{x:.4f}"


def main() -> int:
    ap = argparse.ArgumentParser(description="Export P5 regime x agent summary")
    ap.add_argument(
        "--runs-dir",
        type=Path,
        default=REPO / "datasets" / "runs" / "multiscenario_runs",
    )
    ap.add_argument(
        "--out-json",
        type=Path,
        default=REPO / "datasets" / "runs" / "scaling_summary" / "regime_agent_summary.json",
    )
    ap.add_argument(
        "--out-md",
        type=Path,
        default=REPO / "papers" / "P5_ScalingLaws" / "regime_agent_summary.md",
    )
    args = ap.parse_args()

    from labtrust_portfolio.scaling import build_dataset_from_runs

    if not args.runs_dir.exists():
        print(f"Runs dir not found: {args.runs_dir}")
        return 1

    rows = build_dataset_from_runs(args.runs_dir)
    if not rows:
        print("No rows in runs dir.")
        return 1

    grouped: Dict[Tuple[str, str, int], List[Dict[str, Any]]] = {}
    for r in rows:
        fam = str(r.get("scenario_family", "unknown"))
        reg = str(r.get("coordination_regime", "centralized"))
        ac = int(r.get("agent_count", 1) or 1)
        grouped.setdefault((fam, reg, ac), []).append(r)

    entries: List[Dict[str, Any]] = []
    for (fam, reg, ac), rs in sorted(grouped.items()):
        tc = [float(x.get("response", {}).get("tasks_completed", 0) or 0) for x in rs]
        cm = [float(x.get("response", {}).get("coordination_messages", 0) or 0) for x in rs]
        ct = [float(x.get("coordination_tax_proxy", 0) or 0) for x in rs]
        ea = [float(x.get("error_amplification_proxy", 0) or 0) for x in rs]
        p95 = [float(x.get("response", {}).get("task_latency_ms_p95", 0) or 0) for x in rs]
        collapse = [1.0 if x.get("collapse") else 0.0 for x in rs]
        entries.append(
            {
                "scenario_family": fam,
                "coordination_regime": reg,
                "agent_count": ac,
                "n_rows": len(rs),
                "mean_tasks_completed": _mean(tc),
                "stdev_tasks_completed": _stdev(tc),
                "ci95_half_tasks_completed": _ci95_half(tc),
                "mean_coordination_messages": _mean(cm),
                "mean_coordination_tax_proxy": _mean(ct),
                "mean_error_amplification_proxy": _mean(ea),
                "mean_task_latency_ms_p95": _mean(p95),
                "collapse_rate": _mean(collapse),
            },
        )

    # Direct title evidence: within each (family, regime), compare max agent_count to min.
    deltas: List[Dict[str, Any]] = []
    pair_groups: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
    for e in entries:
        pair_groups.setdefault((e["scenario_family"], e["coordination_regime"]), []).append(e)
    for (fam, reg), xs in sorted(pair_groups.items()):
        xs_sorted = sorted(xs, key=lambda z: int(z["agent_count"]))
        if len(xs_sorted) < 2:
            continue
        lo = xs_sorted[0]
        hi = xs_sorted[-1]
        deltas.append(
            {
                "scenario_family": fam,
                "coordination_regime": reg,
                "agent_count_low": lo["agent_count"],
                "agent_count_high": hi["agent_count"],
                "delta_tasks_completed_pct": _pct(
                    hi["mean_tasks_completed"], lo["mean_tasks_completed"],
                ),
                "delta_coordination_tax_proxy_pct": _pct(
                    hi["mean_coordination_tax_proxy"], lo["mean_coordination_tax_proxy"],
                ),
                "delta_task_latency_ms_p95_pct": _pct(
                    hi["mean_task_latency_ms_p95"], lo["mean_task_latency_ms_p95"],
                ),
                "delta_collapse_rate_pct_points": (
                    (hi["collapse_rate"] - lo["collapse_rate"]) * 100.0
                    if hi["collapse_rate"] is not None and lo["collapse_rate"] is not None
                    else None
                ),
            },
        )

    payload = {
        "run_manifest": {
            "script": "export_scaling_regime_agent_summary.py",
            "runs_dir": str(args.runs_dir),
            "n_rows_total": len(rows),
        },
        "group_summary": entries,
        "high_vs_low_agent_count_deltas": deltas,
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    md_lines = [
        "# Regime x Agent Summary",
        "",
        "| family | regime | agent_count | n | mean_tasks_completed | mean_coordination_messages | mean_coordination_tax_proxy | mean_error_amplification_proxy | mean_task_latency_ms_p95 | collapse_rate |",
        "|--------|--------|-------------|---|----------------------|----------------------------|-----------------------------|--------------------------------|-------------------------|---------------|",
    ]
    for e in entries:
        md_lines.append(
            f"| {e['scenario_family']} | {e['coordination_regime']} | {e['agent_count']} | {e['n_rows']} | "
            f"{e['mean_tasks_completed']:.4f} | {e['mean_coordination_messages']:.4f} | "
            f"{e['mean_coordination_tax_proxy']:.4f} | {e['mean_error_amplification_proxy']:.4f} | "
            f"{e['mean_task_latency_ms_p95']:.4f} | {e['collapse_rate']:.4f} |",
        )
    md_lines.extend(
        [
            "",
            "## High vs Low Agent Count Delta (within family x regime)",
            "",
            "| family | regime | low->high | delta_tasks_completed_% | delta_coordination_tax_% | delta_p95_latency_% | delta_collapse_rate_pp |",
            "|--------|--------|-----------|-------------------------|--------------------------|---------------------|------------------------|",
        ],
    )
    for d in deltas:
        md_lines.append(
            f"| {d['scenario_family']} | {d['coordination_regime']} | "
            f"{d['agent_count_low']}->{d['agent_count_high']} | "
            f"{_fmt4(d['delta_tasks_completed_pct'])} | "
            f"{_fmt4(d['delta_coordination_tax_proxy_pct'])} | "
            f"{_fmt4(d['delta_task_latency_ms_p95_pct'])} | "
            f"{_fmt4(d['delta_collapse_rate_pct_points'])} |",
        )
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
