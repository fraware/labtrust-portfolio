#!/usr/bin/env python3
"""
Export Table 3 for P0: Replay-link and conformance across controllers/scenarios (E3 + E4).
Reads p0_e4_summary.json (from run_p0_e4_multi_adapter.py) and optionally e3_summary.json.
Usage: python scripts/export_p0_table3.py [--e4 FILE] [--e3 FILE]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_E4 = REPO / "datasets" / "runs" / "p0_e4_summary.json"
DEFAULT_E3 = REPO / "datasets" / "runs" / "e3_summary.json"


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Export P0 Table 3 (replay-link and conformance by scenario/controller)")
    ap.add_argument("--e4", type=Path, default=DEFAULT_E4, help="E4 summary JSON")
    ap.add_argument("--e3", type=Path, default=DEFAULT_E3, help="E3 summary JSON to merge (default datasets/runs/e3_summary.json)")
    args = ap.parse_args()

    e3_rows: list[dict] = []
    e4_rows: list[dict] = []
    if args.e3.exists():
        e3 = json.loads(args.e3.read_text(encoding="utf-8"))
        per = e3.get("per_scenario", [e3])
        for p in per if isinstance(per, list) else [per]:
            scenario = p.get("scenario_id", e3.get("scenarios", ["—"])[0] if isinstance(e3.get("scenarios"), list) else "—")
            ci = p.get("p95_latency_ms_ci_95", [0, 0])
            ci_str = f"{p.get('p95_latency_ms_mean', 0):.2f} [{ci[0]:.2f}, {ci[1]:.2f}]" if len(ci) == 2 else "—"
            e3_rows.append({
                "scenario": scenario,
                "controller": "thinslice",
                "seeds": e3.get("runs", 0),
                "replay_match_rate": 1.0 if p.get("all_match") else 0.0,
                "latency_mean_ci": ci_str,
                "conformance_rate": 1.0 if p.get("all_match") else 0.0,
            })
    if args.e4.exists():
        e4 = json.loads(args.e4.read_text(encoding="utf-8"))
        for r in e4.get("per_adapter", []):
            ci = r.get("p95_latency_ms_ci_95", [0, 0])
            ci_str = f"{r.get('p95_latency_ms_mean', 0):.2f} [{ci[0]:.2f}, {ci[1]:.2f}]" if len(ci) == 2 else "—"
            e4_rows.append({
                "scenario": r.get("scenario", "—"),
                "controller": r.get("controller", "—"),
                "seeds": len(r.get("seeds", [])),
                "replay_match_rate": r.get("replay_match_rate", 0),
                "latency_mean_ci": ci_str,
                "conformance_rate": r.get("conformance_rate", 0),
            })

    rows = e3_rows + e4_rows
    if not rows:
        print("No E4 or E3 data found. Run run_p0_e4_multi_adapter.py and/or produce_p0_e3_release.py first.", file=sys.stderr)
        return 1

    lines = [
        "## Table 3 — E3 + E4 summary (replay-link and controller-independence)",
        "",
        "Latency column: mean of per-seed **task_latency_ms_p95** with 95% CI (t-interval on seed-level samples).",
        "",
        "| Scenario | Controller | Seeds | Replay match rate | p95 latency mean (95% CI) ms | Conformance rate |",
        "|----------|-------------|-------|-------------------|------------------------------|------------------|",
    ]
    for r in rows:
        lines.append(
            f"| {r['scenario']} | {r['controller']} | {r['seeds']} | "
            f"{r['replay_match_rate']:.2f} | {r['latency_mean_ci']} | {r['conformance_rate']:.2f} |"
        )
    lines.append("")
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
