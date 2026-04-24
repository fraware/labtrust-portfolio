#!/usr/bin/env python3
"""
Audit helpers for real-LLM run directories (independence slice, scoring checks).

Example:
  python scripts/audit_llm_results.py --run-dir datasets/runs/llm_eval_robust_gpt_20260424
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser(description="Audit LLM eval run directory.")
    ap.add_argument(
        "--run-dir",
        type=Path,
        default=REPO / "datasets" / "runs" / "llm_eval_robust_gpt_20260424",
        help="Run directory containing canonical_independence_audit.json",
    )
    ap.add_argument(
        "--rematerialize",
        action="store_true",
        help="Re-run p6_robust_gpt_materialize before reading outputs",
    )
    args = ap.parse_args()
    if args.rematerialize:
        import subprocess

        r = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "p6_robust_gpt_materialize.py")],
            cwd=str(REPO),
        )
        if r.returncode != 0:
            return r.returncode
    ind = args.run_dir / "canonical_independence_audit.json"
    if not ind.exists():
        print("Missing", ind, "; run: python scripts/p6_robust_gpt_materialize.py", file=sys.stderr)
        return 1
    data = json.loads(ind.read_text(encoding="utf-8"))
    print("verdict:", data.get("verdict"))
    print("models:", data.get("models"))
    print("distinct_model_ids:", data.get("distinct_model_ids"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
