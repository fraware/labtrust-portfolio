#!/usr/bin/env python3
"""
Export appendix-style controller-pair diagnostics for P0 E4.

Reads datasets/runs/p0_e4_diagnostics.json (or --in).
Usage: python scripts/export_p0_e4_diagnostics_table.py [--in FILE]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_IN = REPO / "datasets" / "runs" / "p0_e4_diagnostics.json"


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Export P0 E4 diagnostics table (Markdown)")
    ap.add_argument("--in", dest="in_path", type=Path, default=DEFAULT_IN)
    args = ap.parse_args()
    if not args.in_path.exists():
        print(f"Input not found: {args.in_path}", file=sys.stderr)
        return 1
    data = json.loads(args.in_path.read_text(encoding="utf-8"))
    pairs = data.get("pairs", [])
    if not pairs:
        print("No pairwise diagnostics.", file=sys.stderr)
        return 1
    a = data.get("controller_a", "A")
    b = data.get("controller_b", "B")
    lines = [
        f"## P0 E4 — Diagnostics ({a} vs {b})",
        "",
        "| Regime | Scenario | Paired seeds | Trace hash = | MAESTRO hash = | Evidence hash = | Final state = | Mean |Δp95| ms | Seeds divergent (trace/maestro) |",
        "|--------|----------|--------------|--------------|----------------|-----------------|---------------|----------------|----------------------------------|",
    ]
    for p in pairs:
        lines.append(
            f"| {p['regime']} | {p['scenario']} | {p['n_paired_seeds']} | "
            f"{p['trace_hash_equality_rate']:.2f} | {p['maestro_hash_equality_rate']:.2f} | "
            f"{p['evidence_hash_equality_rate']:.2f} | {p['final_state_hash_equality_rate']:.2f} | "
            f"{p['mean_abs_p95_latency_diff_ms']:.4f} | {p['n_seeds_with_divergence']} |"
        )
    lines.append("")
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
