#!/usr/bin/env python3
"""
Export a concise denial-trace case study from a P6 adapter trace (for the paper).
Reads one trace that has a denial; extracts metadata.denied_steps (or infers from
typed_plan + denials_count by re-running the validator); writes a short snippet.
Regenerate after running baseline: llm_redteam_eval.py --run-baseline ...
Usage: export_p6_denial_trace_case_study.py [--trace path] [--out path] [--format md|json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_LLM_EVAL = REPO / "datasets" / "runs" / "llm_eval"
DEFAULT_TRACE = DEFAULT_LLM_EVAL / "baseline_runs" / "gated" / "toy_lab_v0" / "seed_1" / "trace.json"


def _reasons_for_denied_step(step: dict) -> list[str]:
    """Re-run validator on step when denied_steps not in trace. Needs PYTHONPATH=impl/src."""
    try:
        from labtrust_portfolio.llm_planning import validate_plan_step

        ALLOWED_TOOLS = ["query_status", "submit_result"]
        allowed, reasons = validate_plan_step(step, ALLOWED_TOOLS)
        return reasons if not allowed else []
    except Exception:
        return ["re-run baseline with updated adapter for denied_steps"]


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Export P6 denial-trace case study snippet from a trace"
    )
    ap.add_argument(
        "--trace",
        type=Path,
        default=DEFAULT_TRACE,
        help="Path to trace.json with a denial (e.g. baseline_runs/gated/.../trace.json)",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Write snippet to this path (default: print to stdout)",
    )
    ap.add_argument(
        "--format",
        choices=("md", "json"),
        default="md",
        help="Output format: md (paper snippet) or json",
    )
    args = ap.parse_args()

    if not args.trace.exists():
        print(f"Trace not found: {args.trace}", file=sys.stderr)
        print(
            "Run: llm_redteam_eval.py --out datasets/runs/llm_eval --run-baseline "
            "--baseline-scenarios toy_lab_v0 --baseline-seeds 1",
            file=sys.stderr,
        )
        return 1

    trace = json.loads(args.trace.read_text(encoding="utf-8"))
    meta = trace.get("metadata") or {}
    denied_steps = meta.get("denied_steps")
    typed_plan = meta.get("typed_plan")
    denials_count = meta.get("denials_count", 0)

    if not denied_steps and denials_count > 0 and typed_plan:
        steps = typed_plan.get("steps") or []
        denied_steps = []
        for s in steps:
            reasons = _reasons_for_denied_step(s)
            if reasons:
                denied_steps.append({"step": s, "reason": reasons})

    if not denied_steps:
        print(
            "No denied steps; use a gated baseline trace with denial-injection plan.",
            file=sys.stderr,
        )
        return 1

    first = denied_steps[0]
    step = first.get("step", {})
    reasons = first.get("reason", [])
    tool = step.get("tool", "?")
    args_step = step.get("args", {})
    reason_txt = "; ".join(reasons) if reasons else "denied"

    if args.format == "json":
        out = {
            "step": {"tool": tool, "args": args_step},
            "outcome": "denied",
            "reason": reasons,
        }
        text = json.dumps(out, indent=2)
    else:
        step_json = json.dumps({"tool": tool, "args": args_step})
        text = (
            f"**Case study: denial trace.** Planner proposed step {step_json}. "
            f"Validator: {reason_txt} -> Deny. Step captured for audit; no execution."
        )

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
