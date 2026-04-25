#!/usr/bin/env python3
"""
Entry point for the robust GPT real-LLM evaluation workflow.

Phase 1 (no API keys): materialize audit bundle from frozen canonical JSON:
  python scripts/run_robust_gpt_eval.py --materialize-only

Phase 1b (no API keys): validator-only audit of the stress corpus (no LLM):
  python scripts/run_robust_gpt_eval.py --synthetic-stress-audit PATH.json

Phase 2 (API): full reruns with transcripts, prompt variants, optional stress JSON:
  PYTHONPATH=impl/src python scripts/llm_redteam_eval.py \\
    --out datasets/runs/llm_eval_robust_gpt_evalscratch \\
    --real-llm --real-llm-models gpt-5.4,gpt-5.4-pro \\
    --real-llm-runs 10 --real-llm-suite full --store-real-llm-transcripts \\
    --real-llm-prompt-variants canonical,strict_json \\
    --real-llm-stress-json datasets/cases/p6_real_llm_stress_cases.json
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def write_synthetic_stress_audit(out_path: Path) -> dict:
    """Run validator on each stress case; no LLM calls."""
    sys.path.insert(0, str(REPO / "impl" / "src"))
    os.environ.setdefault("LABTRUST_KERNEL_DIR", str(REPO / "kernel"))
    from labtrust_portfolio.llm_planning import validate_plan_step

    stress_path = REPO / "datasets" / "cases" / "p6_real_llm_stress_cases.json"
    data = json.loads(stress_path.read_text(encoding="utf-8"))
    allowed = ["query_status", "submit_result"]
    rows: list[dict] = []
    for c in data.get("cases", []) or []:
        step = c["step"]
        ok, _ = validate_plan_step(step, allowed)
        blocked = not ok
        rows.append(
            {
                "id": c["id"],
                "expected_block": c["expected_block"],
                "validator_blocked": blocked,
                "label_matches_validator": blocked == c["expected_block"],
            }
        )
    out = {
        "audit": "synthetic_stress_validator_only",
        "stress_suite_path": str(stress_path.relative_to(REPO)).replace("\\", "/"),
        "n_cases": len(rows),
        "all_match": all(r["label_matches_validator"] for r in rows),
        "cases": rows,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Robust GPT eval orchestrator")
    ap.add_argument(
        "--materialize-only",
        action="store_true",
        help="Run scripts/p6_robust_gpt_materialize.py and exit",
    )
    ap.add_argument(
        "--synthetic-stress-audit",
        type=Path,
        metavar="OUT.json",
        default=None,
        help="Write validator-only audit of p6_real_llm_stress_cases.json to this path (no API keys).",
    )
    args = ap.parse_args()
    if args.materialize_only:
        return subprocess.call(
            [sys.executable, str(REPO / "scripts" / "p6_robust_gpt_materialize.py")],
            cwd=str(REPO),
        )
    if args.synthetic_stress_audit is not None:
        write_synthetic_stress_audit(args.synthetic_stress_audit.resolve())
        print("Wrote", args.synthetic_stress_audit.resolve())
        return 0
    print(
        "Use --materialize-only or --synthetic-stress-audit, or see docstring "
        "for llm_redteam_eval.py invocations.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
