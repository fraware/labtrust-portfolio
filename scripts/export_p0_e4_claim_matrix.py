#!/usr/bin/env python3
"""
Export a compact claim-to-evidence matrix for P0 E4.

Usage:
  python scripts/export_p0_e4_claim_matrix.py
  python scripts/export_p0_e4_claim_matrix.py --format json
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Export P0 E4 claim matrix")
    ap.add_argument("--format", choices=("md", "json"), default="md")
    args = ap.parse_args()

    rows = [
        {
            "claim": "raw controller invariance in baseline",
            "artifact_path": "datasets/runs/p0_e4_raw_summary.json",
            "supporting_regimes_scenarios": (
                "baseline: toy_lab_v0, lab_profile_v0, rep_cps_scheduling_v0"
            ),
            "evidence_layer": "raw-only",
            "status": "supported",
        },
        {
            "claim": "normalized interface invariance in baseline and moderate",
            "artifact_path": "datasets/runs/p0_e4_normalized_summary.json",
            "supporting_regimes_scenarios": (
                "baseline+moderate: toy_lab_v0, lab_profile_v0, "
                "rep_cps_scheduling_v0"
            ),
            "evidence_layer": "normalized-only",
            "status": "supported",
        },
        {
            "claim": "controller divergence under harder coordination stress",
            "artifact_path": (
                "datasets/runs/p0_e4_diagnostics.json; "
                "datasets/runs/p0_e4_controller_pairs.jsonl"
            ),
            "supporting_regimes_scenarios": "coordination_shock: rep_cps_scheduling_v0",
            "evidence_layer": "both",
            "status": "supported",
        },
        {
            "claim": "raw universal invariance across all regimes",
            "artifact_path": (
                "datasets/runs/p0_e4_raw_summary.json; "
                "datasets/runs/p0_e4_raw_failure_reasons.json"
            ),
            "supporting_regimes_scenarios": "stress+coordination_shock rows",
            "evidence_layer": "raw-only",
            "status": "not supported",
        },
    ]

    if args.format == "json":
        print(json.dumps({"rows": rows}, indent=2))
        return 0

    lines = [
        "## P0 E4 Claim Matrix",
        "",
        "| Claim | Artifact path | Supporting regimes/scenarios | Layer | Status |",
        "|-------|---------------|------------------------------|-------|--------|",
    ]
    for r in rows:
        lines.append(
            f"| {r['claim']} | `{r['artifact_path']}` | {r['supporting_regimes_scenarios']} | "
            f"{r['evidence_layer']} | {r['status']} |"
        )
    lines.append("")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
