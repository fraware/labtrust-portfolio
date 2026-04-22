#!/usr/bin/env python3
"""
P7 Review script: run on a run directory to produce a review outcome (evidence
bundle validation, PONR event list, control coverage, provenance checks).

Modes (ablation baselines):
  schema_only — pack structure + optional trace/bundle schema if files exist
  schema_plus_presence — pack + required artifacts present and schema-valid
  full_review — governance review: scenario alignment, PONR, control coverage,
                bundle/release SHA consistency vs files on disk

Usage:
  PYTHONPATH=impl/src python scripts/review_assurance_run.py <run_dir> [--pack path] \\
      [--scenario-id lab_profile_v0] [--review-mode full_review]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "impl" / "src"))
if "LABTRUST_KERNEL_DIR" not in os.environ:
    os.environ["LABTRUST_KERNEL_DIR"] = str(REPO / "kernel")


def main() -> int:
    ap = argparse.ArgumentParser(description="P7: Review run for assurance pack alignment")
    ap.add_argument("run_dir", type=Path, help="Run directory (trace.json, evidence_bundle.json)")
    ap.add_argument(
        "--pack",
        type=Path,
        default=REPO / "profiles" / "lab" / "v0.1" / "assurance_pack_instantiation.json",
        help="Assurance pack instantiation JSON",
    )
    ap.add_argument(
        "--scenario-id",
        type=str,
        default="toy_lab_v0",
        help="Scenario id for kernel PONR task names (from conformance)",
    )
    ap.add_argument(
        "--review-mode",
        type=str,
        default="full_review",
        choices=["schema_only", "schema_plus_presence", "full_review"],
        help="Reviewer ablation mode (default full_review)",
    )
    ap.add_argument(
        "--profile-dir",
        type=Path,
        default=REPO / "profiles" / "lab" / "v0.1",
        help="Profile directory for pack PONR coverage checks",
    )
    args = ap.parse_args()

    run_dir = args.run_dir
    if not run_dir.is_dir():
        print(f"Not a directory: {run_dir}")
        return 1

    from labtrust_portfolio.assurance_review_pipeline import review_assurance_pipeline

    outcome = review_assurance_pipeline(
        run_dir,
        args.pack,
        args.scenario_id,
        args.review_mode,
        profile_dir=args.profile_dir,
        repo_root=REPO,
    )
    print(json.dumps(outcome, indent=2))
    return 0 if outcome.get("exit_ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
