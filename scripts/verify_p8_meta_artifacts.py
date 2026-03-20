#!/usr/bin/env python3
"""
Verify P8 meta_eval comparison.json (and optional collapse_sweep.json) schema
and camera-ready fields. Exit 0 if checks pass.

Usage (from repo root):
  PYTHONPATH=impl/src python scripts/verify_p8_meta_artifacts.py \\
    --comparison datasets/runs/meta_eval/comparison.json
  PYTHONPATH=impl/src python scripts/verify_p8_meta_artifacts.py \\
    --comparison path/to/comparison.json \\
    --sweep path/to/collapse_sweep.json \\
    --strict-publishable
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED_COMPARISON_KEYS = (
    "schema_version",
    "scenario_id",
    "run_manifest",
    "fixed",
    "meta_controller",
    "collapse_paired_analysis",
    "meta_non_worse_collapse",
    "meta_strictly_reduces_collapse",
    "meta_reduces_collapse",
    "excellence_metrics",
    "success_criteria_met",
)

REQUIRED_MANIFEST_KEYS = (
    "seeds",
    "seed_count",
    "scenario_id",
    "script",
    "schema_version",
)

REQUIRED_COLLAPSE_PAIRED_KEYS = (
    "mcnemar_exact_p_value_two_sided",
    "fixed_collapse_rate_wilson_ci95",
    "meta_collapse_rate_wilson_ci95",
    "discordant_fixed_collapsed_meta_ok",
    "discordant_fixed_ok_meta_collapsed",
)


def _fail(msg: str) -> int:
    print(f"verify_p8_meta_artifacts: FAIL: {msg}", file=sys.stderr)
    return 1


def verify_comparison(path: Path, strict_publishable: bool) -> int:
    if not path.is_file():
        return _fail(f"missing comparison file: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    for k in REQUIRED_COMPARISON_KEYS:
        if k not in data:
            return _fail(f"comparison.json missing key {k!r}")
    rm = data["run_manifest"]
    if not isinstance(rm, dict):
        return _fail("run_manifest must be an object")
    for k in REQUIRED_MANIFEST_KEYS:
        if k not in rm:
            return _fail(f"run_manifest missing key {k!r}")
    cpa = data["collapse_paired_analysis"]
    if not isinstance(cpa, dict):
        return _fail("collapse_paired_analysis must be an object")
    for k in REQUIRED_COLLAPSE_PAIRED_KEYS:
        if k not in cpa:
            return _fail(f"collapse_paired_analysis missing key {k!r}")
    em = data["excellence_metrics"]
    if not isinstance(em, dict):
        return _fail("excellence_metrics must be an object")
    for k in (
        "difference_ci95_method",
        "mcnemar_exact_p_value_two_sided",
        "collapse_outcome_non_worse",
        "collapse_outcome_strict_improvement",
    ):
        if k not in em:
            return _fail(f"excellence_metrics missing key {k!r}")
    fix = data["fixed"]
    meta = data["meta_controller"]
    for arm, label in ((fix, "fixed"), (meta, "meta_controller")):
        if not isinstance(arm, dict):
            return _fail(f"{label} must be an object")
        if "tasks_completed_ci95_method" not in arm:
            return _fail(f"{label} missing tasks_completed_ci95_method")
        tc = arm.get("tasks_completed_ci95")
        if not isinstance(tc, list) or len(tc) != 2:
            return _fail(
                f"{label}.tasks_completed_ci95 must be a length-2 list"
            )
        m = arm.get("tasks_completed_mean")
        lo, hi = tc[0], tc[1]
        nums_ok = isinstance(m, (int, float)) and isinstance(lo, (int, float))
        nums_ok = nums_ok and isinstance(hi, (int, float))
        if nums_ok and not (lo <= m <= hi):
            return _fail(
                f"{label}: mean not inside tasks_completed_ci95 interval"
            )
    nw = bool(data.get("meta_non_worse_collapse"))
    mr = bool(data.get("meta_reduces_collapse"))
    if nw != mr:
        return _fail(
            "meta_non_worse_collapse must equal meta_reduces_collapse (alias)"
        )
    if strict_publishable:
        n = int(rm.get("seed_count", 0))
        if n < 20:
            return _fail(
                f"--strict-publishable requires seed_count >= 20, got {n}"
            )
        if rm.get("non_vacuous") and not rm.get("stress_selection_policy"):
            return _fail(
                "strict-publishable: non_vacuous runs must record "
                "stress_selection_policy"
            )
    return 0


def verify_sweep(path: Path) -> int:
    if not path.is_file():
        return _fail(f"missing sweep file: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if "schema_version" not in data:
        return _fail("collapse_sweep.json missing schema_version")
    rm = data.get("run_manifest")
    if not isinstance(rm, dict) or "scenario_id" not in rm:
        return _fail(
            "collapse_sweep.json run_manifest.scenario_id required"
        )
    top_sid = data.get("scenario_id")
    rm_sid = rm.get("scenario_id")
    if top_sid and top_sid != rm_sid:
        return _fail(
            "collapse_sweep top-level scenario_id must match "
            "run_manifest.scenario_id"
        )
    if "per_run" not in data or not data["per_run"]:
        return _fail("collapse_sweep.json must have non-empty per_run")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Verify P8 comparison.json / collapse_sweep.json schema",
    )
    ap.add_argument(
        "--comparison",
        type=Path,
        required=True,
        help="Path to comparison.json",
    )
    ap.add_argument(
        "--sweep",
        type=Path,
        default=None,
        help="Optional collapse_sweep.json to verify",
    )
    ap.add_argument(
        "--strict-publishable",
        action="store_true",
        help="Require 20+ seeds and stress_selection_policy when non_vacuous",
    )
    args = ap.parse_args()
    rc = verify_comparison(args.comparison, args.strict_publishable)
    if rc != 0:
        return rc
    if args.sweep is not None:
        rc = verify_sweep(args.sweep)
        if rc != 0:
            return rc
    print("verify_p8_meta_artifacts: OK", args.comparison)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
