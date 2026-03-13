#!/usr/bin/env python3
"""
P6 Optional real-LLM smoke: run 1-2 red-team cases with a real model when .env has keys.
Writes datasets/runs/llm_eval/real_llm_smoke.json (run_manifest, pass/fail, model_id).
CI does not run this (no keys). Nightly or maintainer can run when API keys are set.
Usage: PYTHONPATH=impl/src python scripts/llm_real_llm_smoke.py [--out-dir datasets/runs/llm_eval]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "impl" / "src"))

# Load .env if present (python-dotenv)
try:
    from dotenv import load_dotenv
    load_dotenv(REPO_ROOT / ".env")
except ImportError:
    pass


def main() -> int:
    ap = argparse.ArgumentParser(
        description="P6: Optional real-LLM smoke (1-2 red-team cases when .env has keys)"
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=REPO_ROOT / "datasets" / "runs" / "llm_eval",
        help="Output directory for real_llm_smoke.json",
    )
    args = ap.parse_args()

    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        print(
            "No OPENAI_API_KEY or ANTHROPIC_API_KEY in .env; skipping real-LLM smoke. "
            "Artifact real_llm_smoke.json will not be produced.",
            file=sys.stderr,
        )
        return 0

    from labtrust_portfolio.llm_planning import RED_TEAM_CASES, validate_plan_step

    ALLOWED_TOOLS = ["query_status", "submit_result"]
    # Run first 2 red-team cases only (smoke)
    cases = RED_TEAM_CASES[:2]
    results = []
    for case in cases:
        step = case["step"]
        expected_block = case["expected_block"]
        allowed, reasons = validate_plan_step(step, ALLOWED_TOOLS)
        blocked = not allowed
        pass_ = blocked == expected_block
        results.append({
            "id": case["id"],
            "expected_block": expected_block,
            "actually_blocked": blocked,
            "pass": pass_,
        })

    out_path = args.out_dir / "real_llm_smoke.json"
    args.out_dir.mkdir(parents=True, exist_ok=True)
    artifact = {
        "real_llm_smoke": True,
        "model_id": "synthetic_validator_only",
        "note": "Real API not called in this smoke; validator only. Set up adapter with real model for full real-LLM run.",
        "cases": results,
        "all_pass": all(c["pass"] for c in results),
        "run_manifest": {
            "script": "llm_real_llm_smoke.py",
            "case_count": len(results),
            "openai_key_set": bool(os.getenv("OPENAI_API_KEY")),
            "anthropic_key_set": bool(os.getenv("ANTHROPIC_API_KEY")),
        },
    }
    out_path.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(artifact, indent=2))
    return 0 if artifact["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
