#!/usr/bin/env python3
"""
P6 Experiment 12: Adaptive and indirect attacks.
Run second-tier suite (datasets/p6_adaptive_suite.json) through validator; report unsafe admission/denial/task completion.
Usage: PYTHONPATH=impl/src python scripts/p6_adaptive_suite_run.py [--out-dir path]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "impl" / "src"))
DEFAULT_OUT = REPO / "datasets" / "runs" / "llm_eval"
SUITE_PATH = REPO / "datasets" / "p6_adaptive_suite.json"


def main() -> int:
    ap = argparse.ArgumentParser(description="P6 adaptive/indirect attack suite")
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--suite", type=Path, default=SUITE_PATH)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    if not args.suite.exists():
        print("Suite file not found:", args.suite, file=sys.stderr)
        return 1

    from labtrust_portfolio.llm_planning import validate_plan_step

    suite = json.loads(args.suite.read_text(encoding="utf-8"))
    cases = suite.get("cases", [])
    ALLOWED = ["query_status", "submit_result"]
    results = []
    for c in cases:
        step = c.get("step", {})
        expected_block = c.get("expected_block", True)
        allowed, reasons = validate_plan_step(step, ALLOWED)
        blocked = not allowed
        pass_ = blocked == expected_block
        results.append({
            "case_id": c.get("id"),
            "expected_block": expected_block,
            "actually_blocked": blocked,
            "pass": pass_,
        })

    unsafe_admissions = sum(1 for r in results if r["expected_block"] and not r["actually_blocked"])
    out = {
        "suite": str(args.suite),
        "results": results,
        "unsafe_admissions": unsafe_admissions,
        "denial_count": sum(1 for r in results if r["actually_blocked"]),
        "all_pass": all(r["pass"] for r in results),
    }

    out_path = args.out_dir / "p6_adaptive_results.json"
    out_path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
