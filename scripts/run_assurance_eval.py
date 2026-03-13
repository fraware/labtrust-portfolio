#!/usr/bin/env python3
"""
P7 Assurance eval: check_assurance_mapping + review_assurance_run on one or more
thin-slice runs; write results.json. With --out DIR writes there. Runs review for
toy_lab_v0 and lab_profile_v0 to exercise kernel PONR (lab has disposition_commit).
Usage: python run_assurance_eval.py [--out DIR]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "impl" / "src"))
if "LABTRUST_KERNEL_DIR" not in os.environ:
    os.environ["LABTRUST_KERNEL_DIR"] = str(REPO / "kernel")

DEFAULT_OUT = REPO / "datasets" / "runs" / "assurance_eval"
# (scenario_id, seed) for thin-slice runs; lab_profile_v0 exercises kernel PONR
REVIEW_SCENARIOS = [
    ("toy_lab_v0", 7),
    ("lab_profile_v0", 7),
]


def _run_review(run_dir: Path, scenario_id: str, env: dict) -> dict:
    review_cmd = [
        sys.executable,
        str(REPO / "scripts" / "review_assurance_run.py"),
        str(run_dir),
        "--scenario-id",
        scenario_id,
    ]
    r = subprocess.run(
        review_cmd, cwd=str(REPO), env=env, capture_output=True, text=True
    )
    try:
        out = json.loads(r.stdout) if r.stdout else {}
    except json.JSONDecodeError:
        out = {"raw_stdout": r.stdout, "raw_stderr": r.stderr}
    out["exit_ok"] = r.returncode == 0
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="P7: Assurance mapping + review eval")
    ap.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help="Output directory for results.json",
    )
    args = ap.parse_args()
    out_dir = args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    results = {"mapping_check": None, "reviews": {}}

    # 1) Run check_assurance_mapping (last line JSON: mapping_ok, ponr_coverage_ok)
    check_script = REPO / "scripts" / "check_assurance_mapping.py"
    cmd = [sys.executable, str(check_script)]
    env = os.environ.copy()
    r = subprocess.run(
        cmd, cwd=str(REPO), env=env, capture_output=True, text=True
    )
    mapping_ok = r.returncode == 0
    ponr_coverage_ok = None
    if r.stdout:
        for line in r.stdout.strip().splitlines():
            line = line.strip()
            if line.startswith("{"):
                try:
                    check_json = json.loads(line)
                    mapping_ok = check_json.get("mapping_ok", mapping_ok)
                    ponr_coverage_ok = check_json.get("ponr_coverage_ok")
                    break
                except json.JSONDecodeError:
                    pass
    results["mapping_check"] = {
        "ok": mapping_ok and (ponr_coverage_ok is not False),
        "ponr_coverage_ok": ponr_coverage_ok,
        "stdout": r.stdout.strip() if r.stdout else "",
        "stderr": r.stderr.strip() if r.stderr else "",
    }

    # 2) Produce runs and review per scenario
    with tempfile.TemporaryDirectory() as td:
        for scenario_id, seed in REVIEW_SCENARIOS:
            run_dir = Path(td) / f"run_{scenario_id}"
            run_dir.mkdir(parents=True)
            from labtrust_portfolio.thinslice import run_thin_slice
            run_thin_slice(
                run_dir,
                seed=seed,
                scenario_id=scenario_id,
                drop_completion_prob=0.0,
            )
            results["reviews"][scenario_id] = _run_review(
                run_dir, scenario_id, env
            )

    # Backward compatibility: primary review = toy_lab_v0
    results["review"] = results["reviews"].get("toy_lab_v0", {})

    results["run_manifest"] = {
        "scenarios": [s for s, _ in REVIEW_SCENARIOS],
        "profile_dir": str(REPO / "profiles" / "lab" / "v0.1"),
        "script": "run_assurance_eval.py",
    }
    results["success_criteria_met"] = {
        "mapping_ok": results["mapping_check"]["ok"],
        "ponr_coverage_ok": results["mapping_check"].get("ponr_coverage_ok", True),
    }
    # Excellence metrics (STANDARDS_OF_EXCELLENCE.md)
    review_exit_ok_all = all(
        r.get("exit_ok", False) for r in results["reviews"].values()
    )
    ponr_ratio = None
    for r in results["reviews"].values():
        if isinstance(r.get("ponr_coverage"), dict) and "ratio" in r["ponr_coverage"]:
            ponr_ratio = r["ponr_coverage"]["ratio"]
            break
    results["excellence_metrics"] = {
        "mapping_completeness_pct": 100.0 if results["mapping_check"]["ok"] else 0.0,
        "ponr_coverage_ratio": ponr_ratio,
        "review_pass_all_scenarios": review_exit_ok_all,
        "no_certification_claimed": True,
    }

    out_path = out_dir / "results.json"
    out_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))
    all_review_ok = all(
        r.get("exit_ok") for r in results["reviews"].values()
    )
    ok = results["mapping_check"]["ok"] and all_review_ok
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
