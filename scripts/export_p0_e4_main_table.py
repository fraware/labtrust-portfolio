#!/usr/bin/env python3
"""
Export main-paper-style table rows for P0 E4 (scenario × regime × controller).

Reads datasets/runs/p0_e4_raw_summary.json (or --in path to same shape / controller matrix bundle).
Usage: python scripts/export_p0_e4_main_table.py [--in FILE]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_IN = REPO / "datasets" / "runs" / "p0_e4_raw_summary.json"


def _load_rows(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if "raw_summary_rows" in data:
        return list(data["raw_summary_rows"])
    return list(data.get("rows", []))


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Export P0 E4 main table (Markdown)")
    ap.add_argument("--in", dest="in_path", type=Path, default=DEFAULT_IN, help="raw_summary.json or controller_matrix.json")
    args = ap.parse_args()
    if not args.in_path.exists():
        print(f"Input not found: {args.in_path}", file=sys.stderr)
        return 1
    rows = _load_rows(args.in_path)
    if not rows:
        print("No summary rows to export.", file=sys.stderr)
        return 1

    lines = [
        "## P0 E4 — Main table (raw conformance, normalized conformance, strong replay)",
        "",
        "Strong replay uses the full MAESTRO core slice plus PONR witness coverage when the scenario declares PONR tasks.",
        "",
        "| Scenario | Regime | Controller | Raw conf. rate | Norm. conf. rate | Strong replay | Weak replay | p95 mean (95% CI) ms |",
        "|----------|--------|------------|----------------|------------------|----------------|-------------|----------------------|",
    ]
    norm_path = args.in_path.parent / "p0_e4_normalized_summary.json"
    norm_by_key: dict[tuple[str, str, str], dict] = {}
    if norm_path.exists():
        nd = json.loads(norm_path.read_text(encoding="utf-8"))
        for nr in nd.get("rows", []):
            norm_by_key[(nr["regime"], nr["scenario"], nr["controller"])] = nr

    for r in sorted(rows, key=lambda x: (x["scenario"], x["regime"], x["controller"])):
        key = (r["regime"], r["scenario"], r["controller"])
        nr = norm_by_key.get(key, {})
        nrate_str = (
            f"{nr.get('normalized_conformance_rate', 0):.2f}"
            if key in norm_by_key
            else "—"
        )
        ci = r.get("p95_latency_ms_ci_95", [0, 0])
        ci_str = f"{r.get('p95_latency_ms_mean', 0):.2f} [{ci[0]:.2f}, {ci[1]:.2f}]" if len(ci) == 2 else "—"
        lines.append(
            f"| {r['scenario']} | {r['regime']} | {r['controller']} | "
            f"{r.get('raw_conformance_rate', 0):.2f} | {nrate_str} | "
            f"{r.get('strong_replay_match_rate', 0):.2f} | {r.get('weak_replay_match_rate', 0):.2f} | {ci_str} |"
        )
    lines.append("")
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
