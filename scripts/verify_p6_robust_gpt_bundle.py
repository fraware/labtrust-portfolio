#!/usr/bin/env python3
"""
Machine-check the committed P6 robust GPT audit package under datasets/runs/.

Verifies required materializer outputs exist, then runs
``audit_llm_results.py`` against the frozen camera-ready
``red_team_results.json`` for aggregate recomputation (unless
``--skip-audit``).

Usage (from repo root): ``python scripts/verify_p6_robust_gpt_bundle.py``
Or: ``python scripts/verify_p6_robust_gpt_bundle.py --run-dir …/other_bundle``
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_RUN_DIR = REPO / "datasets" / "runs" / "llm_eval_robust_gpt_20260424"
_DEFAULT_CAMERA_READY = REPO / "datasets" / "runs" / "llm_eval_camera_ready_20260424"
DEFAULT_RED_TEAM = _DEFAULT_CAMERA_READY / "red_team_results.json"

# Keep in sync with scripts/p6_robust_gpt_materialize.py outputs.
REQUIRED_FILES = (
    "README.md",
    "MANIFEST.json",
    "ROBUST_GPT_SUMMARY.json",
    "ROBUST_GPT_SUMMARY.md",
    "canonical_independence_audit.json",
    "negative_controls.json",
    "canonical_real_llm_results.json",
    "raw_outputs.jsonl",
    "parsed_outputs.jsonl",
    "per_case_results.csv",
    "per_case_results.json",
    "failure_audit.csv",
    "failure_audit.json",
    "prompt_variant_results.json",
    "parser_interface_results.json",
    "stress_results.json",
    "statistical_summary.json",
    "model_realization_layered_results.csv",
    "paper_table_recommended.csv",
    "paper_wording_recommended.md",
)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Verify robust GPT materialized bundle + scoring audit",
    )
    ap.add_argument(
        "--run-dir",
        type=Path,
        default=DEFAULT_RUN_DIR,
        help="Materialized bundle directory",
    )
    ap.add_argument(
        "--red-team-results",
        type=Path,
        default=DEFAULT_RED_TEAM,
        help="Source red_team_results.json for audit_llm_results.py recomputation",
    )
    ap.add_argument(
        "--skip-audit",
        action="store_true",
        help="Only check file presence (no audit_llm_results subprocess)",
    )
    args = ap.parse_args()
    run_dir = args.run_dir.resolve()
    if not run_dir.is_dir():
        print(f"run_dir is not a directory: {run_dir}", file=sys.stderr)
        return 1

    errors: list[str] = []
    for name in REQUIRED_FILES:
        p = run_dir / name
        if not p.is_file():
            errors.append(f"missing required file: {p.relative_to(REPO)}")

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1

    if args.skip_audit:
        print("verify_p6_robust_gpt_bundle: file checks OK (--skip-audit)")
        return 0

    red = args.red_team_results.resolve()
    if not red.is_file():
        print(f"--red-team-results not a file: {red}", file=sys.stderr)
        return 1

    r = subprocess.run(
        [
            sys.executable,
            str(REPO / "scripts" / "audit_llm_results.py"),
            "--run-dir",
            str(run_dir),
            "--red-team-results",
            str(red),
        ],
        cwd=str(REPO),
    )
    if r.returncode != 0:
        return r.returncode
    print("verify_p6_robust_gpt_bundle: OK", run_dir.relative_to(REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
