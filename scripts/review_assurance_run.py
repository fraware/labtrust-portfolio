#!/usr/bin/env python3
"""
P7 Review script: run on a run directory to produce a review outcome (evidence
bundle validation, PONR event list, control coverage). When --scenario-id is
set, PONR events use kernel PONR task names from conformance. Usage:
  PYTHONPATH=impl/src python scripts/review_assurance_run.py <run_dir> [--pack path] [--scenario-id toy_lab_v0]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "impl" / "src"))
if "LABTRUST_KERNEL_DIR" not in os.environ:
    os.environ["LABTRUST_KERNEL_DIR"] = str(REPO / "kernel")


def main() -> int:
    ap = argparse.ArgumentParser(description="P7: Review run for assurance pack alignment")
    ap.add_argument("run_dir", type=Path, help="Run directory (trace.json, evidence_bundle.json)")
    ap.add_argument(
        "--pack",
        type=Path,
        default=REPO / "profiles" / "lab" / "v0.1" / "assurance_pack_instantiation.json",
        help="Assurance pack instantiation JSON",
    )
    ap.add_argument(
        "--scenario-id",
        type=str,
        default="toy_lab_v0",
        help="Scenario id for kernel PONR task names (from conformance)",
    )
    args = ap.parse_args()

    run_dir = args.run_dir
    if not run_dir.is_dir():
        print(f"Not a directory: {run_dir}")
        return 1

    outcome = {
        "run_dir": str(run_dir),
        "evidence_bundle_ok": False,
        "trace_ok": False,
        "ponr_events": [],
        "controls_covered": [],
        "ponr_coverage": None,
        "control_coverage_ratio": None,
    }

    # 1) Evidence bundle path + schema
    eb_path = run_dir / "evidence_bundle.json"
    if not eb_path.exists():
        print("FAIL: evidence_bundle.json missing")
        outcome["evidence_bundle_ok"] = False
    else:
        try:
            from labtrust_portfolio.schema import validate
            eb = json.loads(eb_path.read_text(encoding="utf-8"))
            validate(eb, "mads/EVIDENCE_BUNDLE.v0.1.schema.json")
            outcome["evidence_bundle_ok"] = True
        except Exception as e:
            print(f"FAIL: evidence bundle schema validation: {e}")
            outcome["evidence_bundle_error"] = str(e)

    # 2) Trace + PONR-relevant events (kernel or heuristic)
    trace_path = run_dir / "trace.json"
    if not trace_path.exists():
        print("FAIL: trace.json missing")
    else:
        try:
            from labtrust_portfolio.schema import validate
            trace = json.loads(trace_path.read_text(encoding="utf-8"))
            validate(trace, "trace/TRACE.v0.1.schema.json")
            outcome["trace_ok"] = True
            events = trace.get("events", [])
            from labtrust_portfolio.conformance import SCENARIO_PONR_TASK_NAMES
            # PONR coverage uses kernel task names only; no heuristic when scenario not in map
            required_ponr_tasks = set(
                SCENARIO_PONR_TASK_NAMES.get(args.scenario_id, [])
            )
            if not required_ponr_tasks and args.scenario_id not in SCENARIO_PONR_TASK_NAMES:
                outcome["ponr_coverage"] = {
                    "note": "PONR coverage requires --scenario-id; known: " + ",".join(sorted(SCENARIO_PONR_TASK_NAMES.keys())),
                    "required_task_names": [],
                    "found_in_trace": [],
                    "ratio": None,
                }
            else:
                found_ponr_tasks = set()
                for ev in events:
                    t = ev.get("type", "")
                    payload = ev.get("payload", {})
                    name = payload.get("name", "")
                    if t == "task_end" and name in required_ponr_tasks:
                        outcome["ponr_events"].append(
                            {"seq": ev.get("seq"), "type": t, "name": name}
                        )
                        found_ponr_tasks.add(name)
                req_list = sorted(required_ponr_tasks)
                found_list = sorted(found_ponr_tasks)
                ratio = len(found_list) / len(req_list) if req_list else 1.0
                outcome["ponr_coverage"] = {
                    "required_task_names": req_list,
                    "found_in_trace": found_list,
                    "ratio": round(ratio, 4),
                }
        except Exception as e:
            outcome["trace_error"] = str(e)

    # 3) Pack controls coverage + control_coverage_ratio
    evidence_present = set()
    if (run_dir / "trace.json").exists():
        evidence_present.add("trace")
    if (run_dir / "evidence_bundle.json").exists() and outcome.get("evidence_bundle_ok"):
        evidence_present.add("evidence_bundle")
    if args.pack.exists():
        pack = json.loads(args.pack.read_text(encoding="utf-8"))
        controls = pack.get("controls", [])
        covered = 0
        for c in controls:
            types = c.get("evidence_artifact_types", [])
            outcome["controls_covered"].append(
                {"id": c.get("id"), "evidence_types": types}
            )
            if any(et in evidence_present for et in types):
                covered += 1
        outcome["control_coverage_ratio"] = (
            round(covered / len(controls), 4) if controls else 1.0
        )

    print(json.dumps(outcome, indent=2))
    return 0 if outcome.get("evidence_bundle_ok") and outcome.get("trace_ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
