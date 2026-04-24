#!/usr/bin/env python3
"""
Run all P6 freeze integrity gates and emit one consolidated report.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO = SCRIPT_DIR.parents[0]
sys.path.insert(0, str(SCRIPT_DIR))

from verify_p6_camera_ready_bundle import (  # noqa: E402
    DEFAULT_RUN_DIR,
    build_report as build_bundle_report,
    verify as verify_bundle,
)
from verify_p6_claims_consistency import (  # noqa: E402
    DEFAULT_CANONICAL_RUN_ID,
    DEFAULT_CLAIMS,
    DEFAULT_CLAIMS_SAT,
    verify_file,
)
from verify_p6_narrative_consistency import (  # noqa: E402
    verify as verify_narrative,
)


def run_claims() -> tuple[list[dict[str, Any]], list[str], str]:
    checks1, errors1 = verify_file(
        DEFAULT_CLAIMS.resolve(), DEFAULT_CANONICAL_RUN_ID
    )
    checks2, errors2 = verify_file(
        DEFAULT_CLAIMS_SAT.resolve(), DEFAULT_CANONICAL_RUN_ID
    )
    checks = checks1 + checks2
    errors = errors1 + errors2
    status = "ok" if not errors else "failed"
    return checks, errors, status


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    ap.add_argument(
        "--write-report",
        type=Path,
        default=REPO
        / "papers"
        / "P6_LLMPlanning"
        / "sat-cps2026"
        / "FREEZE_STACK_REPORT_2026-04-24.json",
    )
    args = ap.parse_args()

    run_dir = args.run_dir.resolve()
    bundle_errors = verify_bundle(run_dir)
    bundle_report = build_bundle_report(run_dir, bundle_errors)

    claim_checks, claim_errors, claim_status = run_claims()
    narrative_checks, narrative_errors = verify_narrative()
    narrative_status = "ok" if not narrative_errors else "failed"

    all_errors = bundle_errors + claim_errors + narrative_errors
    report = {
        "status": "ok" if not all_errors else "failed",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        ),
        "run_dir": str(run_dir.relative_to(REPO)),
        "gates": {
            "bundle": {
                "status": bundle_report.get("status"),
                "errors": bundle_errors,
            },
            "claims": {
                "status": claim_status,
                "checks": claim_checks,
                "errors": claim_errors,
            },
            "narrative": {
                "status": narrative_status,
                "checks": narrative_checks,
                "errors": narrative_errors,
            },
        },
        "errors": all_errors,
    }

    out = args.write_report.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote freeze stack report: {out.relative_to(REPO)}")

    if all_errors:
        print(f"P6 freeze stack FAILED ({len(all_errors)} issue(s)):")
        for err in all_errors:
            print(f"  - {err}")
        return 1

    print("OK: P6 freeze stack checks all passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
