#!/usr/bin/env python3
"""
Replay and verify denied typed-plan steps from P6 trace artifacts.

Requires `trace.json` files under the run directory (typically produced by a full
adapter/baseline sweep). The committed camera-ready bundle ships a frozen
`replay_denials.json` without committing every per-seed trace for size.

Usage:
  python scripts/replay_denials.py --run-dir datasets/runs/llm_eval
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "impl" / "src"))

from labtrust_portfolio.llm_planning import validate_plan_step  # noqa: E402

ALLOWED_TOOLS = ["query_status", "submit_result"]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _discover_trace_files(run_dir: Path) -> list[Path]:
    return sorted(run_dir.rglob("trace.json"))


def _manifest_versions(run_dir: Path) -> tuple[str | None, str | None]:
    red_team_path = run_dir / "red_team_results.json"
    if not red_team_path.exists():
        return (None, None)
    try:
        data = _load_json(red_team_path)
    except Exception:
        return (None, None)
    rm = data.get("run_manifest", {})
    return (rm.get("policy_version"), rm.get("evaluator_version"))


def replay_denials(run_dir: Path) -> dict:
    traces = _discover_trace_files(run_dir)
    denials_checked = 0
    replay_matches = 0
    mismatches: list[dict] = []

    for trace_path in traces:
        try:
            trace = _load_json(trace_path)
        except Exception as exc:
            mismatches.append(
                {"trace_path": str(trace_path), "error": f"invalid_json: {exc}"}
            )
            continue

        meta = trace.get("metadata", {})
        denied_steps = meta.get("denied_steps", [])
        run_id = trace.get("run_id")
        scenario_id = trace.get("scenario_id")
        seed = trace.get("seed")

        if not isinstance(denied_steps, list):
            mismatches.append(
                {
                    "trace_path": str(trace_path),
                    "run_id": run_id,
                    "scenario_id": scenario_id,
                    "seed": seed,
                    "error": "denied_steps_not_list",
                }
            )
            continue

        for idx, denied in enumerate(denied_steps):
            step = denied.get("step", {}) if isinstance(denied, dict) else {}
            recorded_reason = (
                denied.get("reason", []) if isinstance(denied, dict) else []
            )
            denials_checked += 1

            allowed, replay_reasons = validate_plan_step(step, ALLOWED_TOOLS)
            replay_denied = not allowed
            match = replay_denied
            if match:
                replay_matches += 1
            else:
                mismatches.append(
                    {
                        "trace_path": str(trace_path),
                        "run_id": run_id,
                        "scenario_id": scenario_id,
                        "seed": seed,
                        "denied_step_idx": idx,
                        "recorded_reason": recorded_reason,
                        "replay_reasons": replay_reasons,
                        "step": step,
                    }
                )

    policy_version, evaluator_version = _manifest_versions(run_dir)
    return {
        "run_id": run_dir.name,
        "policy_version": policy_version,
        "evaluator_version": evaluator_version,
        "denials_checked": denials_checked,
        "replay_matches": replay_matches,
        "mismatches": len(mismatches),
        "mismatch_details": mismatches,
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Replay denied typed-plan steps for P6."
    )
    ap.add_argument(
        "--run-dir",
        type=Path,
        default=REPO_ROOT / "datasets" / "runs" / "llm_eval",
        help=(
            "Directory containing trace artifacts "
            "(default: datasets/runs/llm_eval)."
        ),
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help=(
            "Optional output path for replay JSON "
            "(default: <run-dir>/replay_denials.json)."
        ),
    )
    args = ap.parse_args()

    result = replay_denials(args.run_dir)
    out_path = args.out or (args.run_dir / "replay_denials.json")
    out_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["mismatches"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
