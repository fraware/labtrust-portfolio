#!/usr/bin/env python3
"""
P4 MAESTRO baselines: reference adapters on the same scenario and seed band.
Output: bench/maestro/baseline_results.md, baseline_summary.json (per-seed + aggregates).
Usage: PYTHONPATH=impl/src python scripts/maestro_baselines.py [--scenario ID] [--seeds N]
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "impl" / "src"))
if "LABTRUST_KERNEL_DIR" not in os.environ:
    os.environ["LABTRUST_KERNEL_DIR"] = str(REPO_ROOT / "kernel")


def _aggregate(rows: List[Dict[str, Any]], adapter: str) -> Dict[str, Any]:
    rsub = [r for r in rows if r.get("adapter") == adapter]
    if not rsub:
        return {}
    tc = [float(r["tasks_completed"]) for r in rsub]
    p95 = [float(r["p95_latency_ms"]) for r in rsub]
    p99 = [float(r.get("p99_latency_ms", r["p95_latency_ms"])) for r in rsub]
    sv = [int(r.get("safety_violation_count", 0)) for r in rsub]
    rs = [float(r.get("recovery_success_rate_seed", 0.0)) for r in rsub]
    ttr = [r.get("time_to_recovery_ms") for r in rsub if r.get("time_to_recovery_ms") is not None]
    tts = [r.get("time_to_safe_state_ms") for r in rsub if r.get("time_to_safe_state_ms") is not None]
    mpc = [float(r.get("messages_per_completed_task", 0.0)) for r in rsub]
    return {
        "adapter": adapter,
        "tasks_completed_mean": round(statistics.mean(tc), 4),
        "tasks_completed_stdev": round(statistics.stdev(tc), 4) if len(tc) > 1 else 0.0,
        "p95_latency_ms_mean": round(statistics.mean(p95), 4),
        "p95_latency_ms_stdev": round(statistics.stdev(p95), 4) if len(p95) > 1 else 0.0,
        "p99_latency_ms_mean": round(statistics.mean(p99), 4),
        "safety_violation_count_mean": round(statistics.mean(sv), 4),
        "recovery_success_rate_mean": round(statistics.mean(rs), 4),
        "time_to_recovery_ms_mean": round(statistics.mean(ttr), 4) if ttr else None,
        "time_to_safe_state_ms_mean": round(statistics.mean(tts), 4) if tts else None,
        "messages_per_completed_task_mean": round(statistics.mean(mpc), 4) if mpc else None,
    }


def _run_rows(
    adapters: List[Tuple[str, Any]],
    scenario: str,
    seeds: int,
    drop_completion_prob: float,
    delay_fault_prob: float,
    regime_label: str,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    from labtrust_portfolio.maestro import maestro_aggregate_recovery_success_rate

    rows: List[Dict[str, Any]] = []
    reports_by_adapter: Dict[str, List[Dict[str, Any]]] = {}
    for name, adapter in adapters:
        reports_by_adapter[name] = []
        for seed in range(1, seeds + 1):
            with tempfile.TemporaryDirectory() as td:
                out_dir = Path(td)
                res = adapter.run(
                    scenario,
                    out_dir,
                    seed=seed,
                    drop_completion_prob=drop_completion_prob,
                    delay_p95_ms=50.0,
                    delay_fault_prob=delay_fault_prob,
                )
                report = res.maestro_report
                m = report["metrics"]
                s = report.get("safety") or {}
                ce = report.get("coordination_efficiency") or {}
                fault_injected = bool((report.get("faults") or {}).get("fault_injected"))
                rec_ok = 1.0 if (m.get("fault_to_recovery_event_count") or 0) > 0 else (
                    1.0 if m.get("time_to_recovery_ms") is not None else (0.0 if fault_injected else 1.0)
                )
                rows.append(
                    {
                        "regime": regime_label,
                        "adapter": name,
                        "seed": seed,
                        "tasks_completed": m["tasks_completed"],
                        "coordination_messages": m["coordination_messages"],
                        "p95_latency_ms": round(m["task_latency_ms_p95"], 2),
                        "p99_latency_ms": round(m["task_latency_ms_p99"], 2),
                        "safety_violation_count": s.get("safety_violation_count", 0),
                        "unsafe_success_count": s.get("unsafe_success_count", 0),
                        "recovery_success_rate_seed": rec_ok,
                        "time_to_recovery_ms": m.get("time_to_recovery_ms"),
                        "time_to_safe_state_ms": m.get("time_to_safe_state_ms"),
                        "messages_per_completed_task": ce.get("messages_per_completed_task"),
                        "run_outcome": report.get("run_outcome"),
                    }
                )
                reports_by_adapter[name].append(report)
    agg_recovery = {
        name: maestro_aggregate_recovery_success_rate(reps)
        for name, reps in reports_by_adapter.items()
    }
    return rows, agg_recovery


def main() -> int:
    ap = argparse.ArgumentParser(description="P4: MAESTRO baseline adapters")
    ap.add_argument("--scenario", type=str, default="toy_lab_v0", help="Scenario id")
    ap.add_argument(
        "--seeds",
        type=int,
        default=20,
        help="Number of seeds (1..N); default 20 publishable",
    )
    ap.add_argument(
        "--faulted-drop-prob",
        type=float,
        default=0.2,
        help="Second regime: drop_completion_prob for faulted comparison (0 disables second regime)",
    )
    args = ap.parse_args()

    from labtrust_portfolio.adapters.centralized import CentralizedAdapter
    from labtrust_portfolio.adapters.blackboard import BlackboardAdapter
    from labtrust_portfolio.adapters.retry_heavy import RetryHeavyAdapter
    from labtrust_portfolio.adapters.no_recovery import NoRecoveryAdapter
    from labtrust_portfolio.adapters.conservative_safe_shutdown import (
        ConservativeSafeShutdownAdapter,
    )

    adapters: List[Tuple[str, Any]] = [
        ("Centralized", CentralizedAdapter()),
        ("Blackboard", BlackboardAdapter()),
        ("RetryHeavy", RetryHeavyAdapter()),
        ("NoRecovery", NoRecoveryAdapter()),
        ("ConservativeSafeShutdown", ConservativeSafeShutdownAdapter()),
    ]

    all_rows: List[Dict[str, Any]] = []
    recovery_by_regime: Dict[str, Dict[str, Any]] = {}

    rows_ff, rec_ff = _run_rows(
        adapters, args.scenario, args.seeds, 0.0, 0.0, "fault_free"
    )
    all_rows.extend(rows_ff)
    recovery_by_regime["fault_free"] = rec_ff

    fault_regime_label = ""
    if args.faulted_drop_prob and args.faulted_drop_prob > 0:
        fault_regime_label = f"drop_{str(args.faulted_drop_prob).replace('.', '_')}"
        rows_f, rec_f = _run_rows(
            adapters,
            args.scenario,
            args.seeds,
            args.faulted_drop_prob,
            0.0,
            fault_regime_label,
        )
        all_rows.extend(rows_f)
        recovery_by_regime[fault_regime_label] = rec_f

    aggregates: Dict[str, Any] = {}
    for regime in sorted(set(r["regime"] for r in all_rows)):
        sub = [r for r in all_rows if r["regime"] == regime]
        aggregates[regime] = {
            "by_adapter": [_aggregate(sub, a[0]) for a in adapters if _aggregate(sub, a[0])],
            "recovery_success_rate_by_adapter": recovery_by_regime.get(regime, {}),
        }

    out_dir = REPO_ROOT / "bench" / "maestro"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "baseline_results.md"
    summary_path = out_dir / "baseline_summary.json"
    summary_path.write_text(
        json.dumps(
            {
                "scenario": args.scenario,
                "seeds": args.seeds,
                "schema_version": "0.2",
                "rows": all_rows,
                "aggregates": aggregates,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    lines = [
        "# MAESTRO baseline comparison (P4)",
        "",
        f"Scenario: `{args.scenario}`. Seeds 1..{args.seeds}. MAESTRO_REPORT v0.2.",
        "",
        "## Per-seed rows",
        "",
        "| Regime | Adapter | Seed | tasks_completed | p95_latency_ms | safety_violations | "
        "recovery_ok_seed | msgs/task | run_outcome |",
        "|--------|---------|------|-----------------|----------------|-------------------|------------------|-----------|-------------|",
    ]
    for r in all_rows:
        rsr = r.get("recovery_success_rate_seed", "")
        lines.append(
            f"| {r.get('regime', '')} | {r['adapter']} | {r['seed']} | {r['tasks_completed']} | "
            f"{r['p95_latency_ms']} | {r.get('safety_violation_count', '')} | {rsr} | "
            f"{r.get('messages_per_completed_task', '')} | {r.get('run_outcome', '')} |"
        )
    lines.extend(["", "## Aggregate by adapter (mean / stdev)", ""])
    for regime, block in aggregates.items():
        lines.append(f"### {regime}")
        lines.append("")
        lines.append(
            "| Adapter | tasks_completed mean | tasks_completed stdev | p95_latency mean | "
            "p99_latency mean | safety_viol mean | recovery_rate mean | ttr_ms mean | tts_ms mean | msgs/task mean |"
        )
        lines.append("|---------|------------------|------------------|---------------|---------------|---------------|----------------|----------|----------|-------------|")
        for row in block.get("by_adapter", []):
            if not row:
                continue
            lines.append(
                f"| {row.get('adapter', '')} | {row.get('tasks_completed_mean', '')} | "
                f"{row.get('tasks_completed_stdev', '')} | {row.get('p95_latency_ms_mean', '')} | "
                f"{row.get('p99_latency_ms_mean', '')} | {row.get('safety_violation_count_mean', '')} | "
                f"{row.get('recovery_success_rate_mean', '')} | {row.get('time_to_recovery_ms_mean', '')} | "
                f"{row.get('time_to_safe_state_ms_mean', '')} | {row.get('messages_per_completed_task_mean', '')} |"
            )
        lines.append("")

    lines.extend(["", "Generated by `scripts/maestro_baselines.py`."])
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out_path.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
