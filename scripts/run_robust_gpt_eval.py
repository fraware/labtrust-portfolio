#!/usr/bin/env python3
"""
Entry point for the robust GPT real-LLM evaluation workflow.

Phase 1 (no API keys): materialize audit bundle from frozen canonical JSON:
  python scripts/run_robust_gpt_eval.py --materialize-only

Phase 2 (API): full reruns with transcripts and higher n (example; requires keys):
  PYTHONPATH=impl/src python scripts/llm_redteam_eval.py \\
    --out datasets/runs/llm_eval_robust_gpt_evalscratch \\
    --real-llm --real-llm-models gpt-5.4,gpt-5.4-pro \\
    --real-llm-runs 10 --real-llm-suite full --store-real-llm-transcripts

Prompt variants (strict_json, json_schema, …) are not yet wired as separate
CLI flags; extend ``_real_llm_prompt_for_case`` or add a variant registry before
expecting separate ``prompt_variant`` rows in JSONL.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser(description="Robust GPT eval orchestrator")
    ap.add_argument(
        "--materialize-only",
        action="store_true",
        help="Run scripts/p6_robust_gpt_materialize.py and exit",
    )
    args = ap.parse_args()
    if args.materialize_only:
        return subprocess.call(
            [sys.executable, str(REPO / "scripts" / "p6_robust_gpt_materialize.py")],
            cwd=str(REPO),
        )
    print(
        "Use --materialize-only for the committed audit bundle, or see docstring "
        "for llm_redteam_eval.py invocations.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
