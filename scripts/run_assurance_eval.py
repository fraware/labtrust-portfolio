#!/usr/bin/env python3
"""
P7 Assurance eval: check_assurance_mapping + review_assurance_run on one or more
thin-slice runs; write results.json. With --out DIR writes there. Runs review for
toy_lab_v0 and lab_profile_v0 (Table 2); per-profile reviews use scenario-matched
runs (lab_profile_v0, warehouse_v0, traffic_v0 for medical proxy). Table 1 primary
review is lab_profile_v0 (kernel PONR disposition_commit).
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
DEFAULT_REVIEW_SEED = 7
# Pairwise scenario reviews for Table 2; lab_profile_v0 carries kernel PONR (disposition_commit).
REVIEW_SCENARIOS = [
    ("toy_lab_v0", DEFAULT_REVIEW_SEED),
    ("lab_profile_v0", DEFAULT_REVIEW_SEED),
]
# Materialize one run per scenario so per-profile review uses a scenario-matched trace.
SCENARIOS_MATERIALIZE = [
    "toy_lab_v0",
    "lab_profile_v0",
    "warehouse_v0",
    "traffic_v0",
]
# (profile_name, scenario_id): review each pack on a matching thin-slice run (not toy_lab only).
# medical_v0.1 uses traffic_v0 as a mechanical stress run; see run_manifest note (proxy, not SaMD semantics).
PROFILE_PACK_SCENARIOS = [
    ("lab_v0.1", "lab_profile_v0"),
    ("warehouse_v0.1", "warehouse_v0"),
    ("medical_v0.1", "traffic_v0"),
]
# Three assurance-pack instantiations (lab, warehouse, medical) for state-of-the-art
PROFILE_PACKS = [
    ("lab_v0.1", REPO / "profiles" / "lab" / "v0.1" / "assurance_pack_instantiation.json"),
    ("warehouse_v0.1", REPO / "profiles" / "warehouse" / "v0.1" / "assurance_pack_instantiation.json"),
    ("medical_v0.1", REPO / "profiles" / "medical_v0.1" / "assurance_pack_instantiation.json"),
]
PACK_BY_NAME = dict(PROFILE_PACKS)
# Table 1 flagship row: lab scenario with non-vacuous kernel PONR (disposition_commit).
PRIMARY_TABLE1_SCENARIO = "lab_profile_v0"


def _run_review(run_dir: Path, scenario_id: str, pack_path: Path, env: dict) -> dict:
    review_cmd = [
        sys.executable,
        str(REPO / "scripts" / "review_assurance_run.py"),
        str(run_dir),
        "--scenario-id",
        scenario_id,
        "--pack",
        str(pack_path),
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

    # 2) Materialize runs and review: scenario-matched traces for each profile pack
    from labtrust_portfolio.thinslice import run_thin_slice

    with tempfile.TemporaryDirectory() as td:
        run_dirs: dict[str, Path] = {}
        for scenario_id in SCENARIOS_MATERIALIZE:
            run_dir = Path(td) / f"run_{scenario_id}"
            run_dir.mkdir(parents=True)
            run_thin_slice(
                run_dir,
                seed=DEFAULT_REVIEW_SEED,
                scenario_id=scenario_id,
                drop_completion_prob=0.0,
            )
            run_dirs[scenario_id] = run_dir

        for scenario_id, _seed in REVIEW_SCENARIOS:
            results["reviews"][scenario_id] = _run_review(
                run_dirs[scenario_id],
                scenario_id,
                PROFILE_PACKS[0][1],
                env,
            )

        results["per_profile"] = {}
        for profile_name, scen in PROFILE_PACK_SCENARIOS:
            pack_path = PACK_BY_NAME.get(profile_name)
            if pack_path and pack_path.exists():
                results["per_profile"][profile_name] = _run_review(
                    run_dirs[scen], scen, pack_path, env
                )

    # Table 1 flagship summary: lab_profile_v0 (kernel PONR disposition_commit), not toy_lab_v0
    results["review"] = results["reviews"].get(PRIMARY_TABLE1_SCENARIO, {})

    results["run_manifest"] = {
        "scenarios": [s for s, _ in REVIEW_SCENARIOS],
        "scenarios_materialized": list(SCENARIOS_MATERIALIZE),
        "per_profile_scenario": {p: s for p, s in PROFILE_PACK_SCENARIOS},
        "table1_primary_scenario": PRIMARY_TABLE1_SCENARIO,
        "medical_pack_traffic_run_note": (
            "medical_v0.1 is reviewed on a traffic_v0 thin-slice run: the run stresses "
            "scheduler, trace, and review mechanics; the pack is a minimal regulator-style "
            "template. This pairing tests the review pipeline, not semantic alignment "
            "between traffic dynamics and SaMD content."
        ),
        "profile_dirs": [name for name, _ in PROFILE_PACKS],
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
    lab_rev = results["reviews"].get(PRIMARY_TABLE1_SCENARIO, {})
    if isinstance(lab_rev.get("ponr_coverage"), dict) and "ratio" in lab_rev["ponr_coverage"]:
        ponr_ratio = lab_rev["ponr_coverage"]["ratio"]
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
