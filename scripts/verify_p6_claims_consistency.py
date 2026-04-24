#!/usr/bin/env python3
"""
Verify P6 claim YAML files are path-consistent for freeze.

Checks:
- Claim YAML files parse correctly
- Every artifact path exists
- For claims with release_id == canonical run id, datasets/runs paths point to
  that canonical run directory (except explicitly non-run artifacts)
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[1]
DEFAULT_CLAIMS = REPO / "papers" / "P6_LLMPlanning" / "claims.yaml"
DEFAULT_CLAIMS_SAT = (
    REPO / "papers" / "P6_LLMPlanning" / "sat-cps2026" / "claims_satcps.yaml"
)
DEFAULT_CANONICAL_RUN_ID = "llm_eval_camera_ready_20260424"


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _is_dataset_run_path(path: str) -> bool:
    return path.startswith("datasets/runs/")


def verify_file(
    path: Path, canonical_run_id: str
) -> tuple[list[dict[str, Any]], list[str]]:
    data = _load_yaml(path)
    checks: list[dict[str, Any]] = []
    errors: list[str] = []
    claims = data.get("claims") or []
    for claim in claims:
        claim_id = claim.get("id", "unknown")
        evidence = claim.get("evidence") or {}
        release_id = evidence.get("release_id")
        artifact_paths = evidence.get("artifact_paths") or []
        for rel in artifact_paths:
            p = REPO / rel
            exists = p.exists()
            checks.append(
                {
                    "claim_id": claim_id,
                    "release_id": release_id,
                    "artifact_path": rel,
                    "exists": exists,
                }
            )
            if not exists:
                errors.append(f"{path.name}:{claim_id} missing artifact: {rel}")
            if (
                release_id == canonical_run_id
                and _is_dataset_run_path(rel)
                and f"datasets/runs/{canonical_run_id}/" not in rel
            ):
                errors.append(
                    f"{path.name}:{claim_id} non-canonical run path "
                    f"for canonical release_id: {rel}"
                )
    return checks, errors


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--claims", type=Path, default=DEFAULT_CLAIMS)
    ap.add_argument("--claims-sat", type=Path, default=DEFAULT_CLAIMS_SAT)
    ap.add_argument(
        "--canonical-run-id",
        type=str,
        default=DEFAULT_CANONICAL_RUN_ID,
    )
    ap.add_argument("--write-report", type=Path, default=None)
    args = ap.parse_args()

    checks1, errors1 = verify_file(
        args.claims.resolve(), args.canonical_run_id
    )
    checks2, errors2 = verify_file(
        args.claims_sat.resolve(), args.canonical_run_id
    )
    checks = checks1 + checks2
    errors = errors1 + errors2
    report = {
        "status": "ok" if not errors else "failed",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        ),
        "canonical_run_id": args.canonical_run_id,
        "checks": checks,
        "errors": errors,
    }

    if args.write_report is not None:
        out = args.write_report.resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote claims consistency report: {out.relative_to(REPO)}")

    if errors:
        print(f"P6 claims consistency FAILED ({len(errors)} issue(s)):")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("OK: P6 claim YAML files are consistent with canonical run paths")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
