#!/usr/bin/env python3
"""
P7 Auditor walk-through: run mapping completeness + PONR coverage (+ optional
review on a run dir). Prints pass/fail with one-line reasons; outputs
machine-readable JSON. Usage:
  PYTHONPATH=impl/src python scripts/audit_bundle.py [--run-dir DIR] [--inst path] [--profile-dir path]
  PYTHONPATH=impl/src python scripts/audit_bundle.py --run-dir datasets/runs/e2_redaction_demo --scenario-id toy_lab_v0
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser(
        description="P7: Auditor walk-through — mapping completeness + PONR coverage + optional run review"
    )
    ap.add_argument(
        "--run-dir",
        type=Path,
        default=None,
        help="Run directory (trace.json, evidence_bundle.json); if set, also run review",
    )
    ap.add_argument(
        "--release",
        type=Path,
        default=None,
        help="Release directory (e.g. datasets/releases/portfolio_v0.1); runs mapping + PONR, then review if release dir contains evidence_bundle.json",
    )
    ap.add_argument(
        "--inst",
        type=Path,
        default=REPO / "profiles" / "lab" / "v0.1" / "assurance_pack_instantiation.json",
        help="Assurance pack instantiation JSON",
    )
    ap.add_argument(
        "--profile-dir",
        type=Path,
        default=REPO / "profiles" / "lab" / "v0.1",
        help="Lab profile dir (for ponrs.yaml)",
    )
    ap.add_argument(
        "--scenario-id",
        type=str,
        default="toy_lab_v0",
        help="Scenario id for review PONR task names",
    )
    ap.add_argument(
        "--json-only",
        action="store_true",
        help="Output only JSON (no human-readable lines)",
    )
    args = ap.parse_args()

    if args.release is not None:
        args.release = args.release.resolve()
        if args.run_dir is None and (args.release / "evidence_bundle.json").exists():
            args.run_dir = args.release

    result = {
        "mapping_completeness": "fail",
        "mapping_reason": "",
        "ponr_coverage": "fail",
        "ponr_reason": "",
        "review_exit_ok": None,
        "review_reason": "",
    }

    check_script = REPO / "scripts" / "check_assurance_mapping.py"
    if not check_script.exists():
        result["mapping_reason"] = "check_assurance_mapping.py not found"
        result["ponr_reason"] = "check_assurance_mapping.py not found"
        if not args.json_only:
            print("FAIL: mapping —", result["mapping_reason"])
            print("FAIL: PONR coverage —", result["ponr_reason"])
        print(json.dumps(result))
        return 1

    r = subprocess.run(
        [
            sys.executable,
            str(check_script),
            "--inst",
            str(args.inst),
            "--profile-dir",
            str(args.profile_dir),
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
    )
    last_line = r.stdout.strip().split("\n")[-1] if r.stdout else ""
    try:
        check_out = json.loads(last_line)
        mapping_ok = check_out.get("mapping_ok", False)
        ponr_ok = check_out.get("ponr_coverage_ok", False)
        result["mapping_completeness"] = "pass" if mapping_ok else "fail"
        result["mapping_reason"] = "mapping complete" if mapping_ok else "mapping incomplete or schema invalid"
        result["ponr_coverage"] = "pass" if ponr_ok else "fail"
        result["ponr_reason"] = "every profile PONR in at least one hazard" if ponr_ok else "PONR coverage missing or profile PONRs not covered"
    except json.JSONDecodeError:
        result["mapping_reason"] = "check script did not output valid JSON"
        result["ponr_reason"] = result["mapping_reason"]

    if not args.json_only:
        print("Mapping completeness:", result["mapping_completeness"], "—", result["mapping_reason"])
        print("PONR coverage:", result["ponr_coverage"], "—", result["ponr_reason"])

    if args.run_dir is not None:
        run_dir = args.run_dir.resolve()
        if not run_dir.is_dir():
            result["review_exit_ok"] = False
            result["review_reason"] = f"not a directory: {run_dir}"
            if not args.json_only:
                print("Review: FAIL —", result["review_reason"])
        else:
            review_script = REPO / "scripts" / "review_assurance_run.py"
            if not review_script.exists():
                result["review_exit_ok"] = False
                result["review_reason"] = "review_assurance_run.py not found"
                if not args.json_only:
                    print("Review: FAIL —", result["review_reason"])
            else:
                env = os.environ.copy()
                env["PYTHONPATH"] = str(REPO / "impl" / "src")
                env.setdefault("LABTRUST_KERNEL_DIR", str(REPO / "kernel"))
                r2 = subprocess.run(
                    [
                        sys.executable,
                        str(review_script),
                        str(run_dir),
                        "--scenario-id",
                        args.scenario_id,
                    ],
                    cwd=str(REPO),
                    env=env,
                    capture_output=True,
                    text=True,
                )
                result["review_exit_ok"] = r2.returncode == 0
                result["review_reason"] = "review passed" if r2.returncode == 0 else "review failed (see stderr)"
                if not args.json_only:
                    print("Review:", "pass" if result["review_exit_ok"] else "fail", "—", result["review_reason"])

    print(json.dumps(result))
    if result["mapping_completeness"] != "pass" or result["ponr_coverage"] != "pass":
        return 1
    if result["review_exit_ok"] is False:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
