#!/usr/bin/env python3
"""
Check P6 narrative docs for freeze-critical consistency.

This guard is intentionally lightweight and deterministic:
- enforces canonical run-id wording in key docs
- enforces core headline numbers are present
- rejects known stale latency values in P6 docs
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
CANONICAL = "llm_eval_camera_ready_20260424"
REQUIRED_SNIPPETS: dict[str, list[str]] = {
    "papers/P6_LLMPlanning/DRAFT.md": [CANONICAL, "75/75", "95.1, 100.0", "36.70"],
    "papers/P6_LLMPlanning/P6_RESULTS_REPORT.md": [CANONICAL, "75 / 75", "36.70", "22.07", "[31.12, 42.29]"],
    "papers/P6_LLMPlanning/sat-cps2026/DRAFT_SaT-CPS.md": [CANONICAL, "75/75", "95.1, 100.0"],
    "papers/P6_LLMPlanning/sat-cps2026/main.tex": ["llm\\_eval\\_camera\\_ready\\_20260424", "75/75", "95.1, 100.0"],
    "docs/RESULTS_PER_PAPER.md": [CANONICAL, "36.70", "60/60/0"],
}
FORBIDDEN_SNIPPETS = ("32.07", "18.45", "27.41, 36.74")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def verify() -> tuple[list[dict[str, Any]], list[str]]:
    checks: list[dict[str, Any]] = []
    errors: list[str] = []
    for rel, required in REQUIRED_SNIPPETS.items():
        p = REPO / rel
        if not p.exists():
            errors.append(f"missing file: {rel}")
            checks.append({"path": rel, "exists": False, "missing_required": required, "forbidden_hits": []})
            continue
        text = _read(p)
        missing = [s for s in required if s not in text]
        forbidden_hits = [s for s in FORBIDDEN_SNIPPETS if s in text]
        checks.append(
            {
                "path": rel,
                "exists": True,
                "missing_required": missing,
                "forbidden_hits": forbidden_hits,
            }
        )
        if missing:
            errors.append(f"{rel}: missing required snippets: {missing}")
        if forbidden_hits:
            errors.append(f"{rel}: contains stale snippets: {forbidden_hits}")
    return checks, errors


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--write-report", type=Path, default=None)
    args = ap.parse_args()
    checks, errors = verify()
    report = {
        "status": "ok" if not errors else "failed",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "canonical_run_id": CANONICAL,
        "checks": checks,
        "errors": errors,
    }
    if args.write_report is not None:
        out = args.write_report.resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote narrative consistency report: {out.relative_to(REPO)}")
    if errors:
        print(f"P6 narrative consistency FAILED ({len(errors)} issue(s)):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("OK: P6 narrative docs are consistent with freeze metrics")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
