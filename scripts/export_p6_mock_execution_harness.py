#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "impl" / "src"))

from labtrust_portfolio.llm_planning import (  # noqa: E402
    MockToolExecutor,
    RED_TEAM_CASES,
    StepDecision,
    validate_plan_step_with_attribution,
)

ALLOWED_TOOLS = ["query_status", "submit_result"]


def main() -> int:
    ap = argparse.ArgumentParser(description="Export mock execution deny-vs-execute evidence for P6.")
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=REPO_ROOT / "datasets" / "runs" / "llm_eval_camera_ready_20260424",
    )
    args = ap.parse_args()

    gated = MockToolExecutor()
    for case in RED_TEAM_CASES:
        step = case["step"]
        allowed, reasons, _ = validate_plan_step_with_attribution(step, ALLOWED_TOOLS)
        gated.execute_if_allowed(step, StepDecision(allowed=allowed, reasons=reasons))

    ungated = MockToolExecutor()
    for case in RED_TEAM_CASES:
        step = case["step"]
        ungated.execute_if_allowed(step, StepDecision(allowed=True, reasons=["mock ungated mode"]))

    unsafe_proposed = sum(1 for case in RED_TEAM_CASES if case["expected_block"])
    artifact = {
        "mode": "gated",
        "unsafe_steps_proposed": unsafe_proposed,
        "unsafe_steps_executed": len(
            [s for s in gated.executed if s.get("tool") not in ALLOWED_TOOLS or "safe_args" in s.get("validators", [])]
        ),
        "safe_steps_executed": len(gated.executed),
        "unsafe_steps_denied": len(gated.denied),
        "ungated_reference": {
            "unsafe_steps_proposed": unsafe_proposed,
            "unsafe_steps_executed": unsafe_proposed,
            "safe_steps_executed": len(RED_TEAM_CASES) - unsafe_proposed,
        },
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    out_path = args.out_dir / "mock_execution_harness.json"
    out_path.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
