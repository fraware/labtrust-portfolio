#!/usr/bin/env python3
"""
P7 robust assurance evaluation.

Runs a broad matrix across scenarios, seeds, and fault regimes, then aggregates
mechanical-check and review outcomes into a single robust_results.json suitable
for claim support in P7.

Usage:
  python scripts/run_assurance_robust_eval.py
  python scripts/run_assurance_robust_eval.py --seeds 1,2,3 \
      --out datasets/runs/assurance_eval
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "impl" / "src"))
if "LABTRUST_KERNEL_DIR" not in os.environ:
    os.environ["LABTRUST_KERNEL_DIR"] = str(REPO / "kernel")

DEFAULT_OUT = REPO / "datasets" / "runs" / "assurance_eval"
SCENARIOS = [
    "toy_lab_v0",
    "lab_profile_v0",
    "warehouse_v0",
    "traffic_v0",
]
PROFILE_PACKS = {
    "lab_v0.1": (
        REPO / "profiles" / "lab" / "v0.1" / "assurance_pack_instantiation.json"
    ),
    "warehouse_v0.1": (
        REPO
        / "profiles"
        / "warehouse"
        / "v0.1"
        / "assurance_pack_instantiation.json"
    ),
    "medical_v0.1": (
        REPO / "profiles" / "medical_v0.1" / "assurance_pack_instantiation.json"
    ),
}
# One pack per scenario for review; traffic_v0 uses medical_v0.1 as a minimal
# regulator-style template while stress-testing the same review pipeline (not a claim
# that traffic semantics match SaMD hazard text).
SCENARIO_PROFILE = {
    "toy_lab_v0": "lab_v0.1",
    "lab_profile_v0": "lab_v0.1",
    "warehouse_v0": "warehouse_v0.1",
    "traffic_v0": "medical_v0.1",
}
SCENARIO_PROFILE_NOTE = (
    "traffic_v0 is paired with medical_v0.1: a thin traffic scenario exercises trace/"
    "bundle/review mechanics with a minimal SaMD-style pack; it does not assert "
    "standards alignment between traffic control and medical device software content."
)
FAULT_REGIMES = [
    {
        "id": "nominal",
        "drop_completion_prob": 0.0,
        "delay_fault_prob": 0.0,
        "calibration_invalid_prob": 0.0,
        "max_retries_per_task": 0,
        "delay_p95_ms": 50.0,
    },
    {
        "id": "delay_spike",
        "drop_completion_prob": 0.0,
        "delay_fault_prob": 0.3,
        "calibration_invalid_prob": 0.0,
        "max_retries_per_task": 1,
        "delay_p95_ms": 120.0,
    },
    {
        "id": "drop_stress",
        "drop_completion_prob": 0.2,
        "delay_fault_prob": 0.0,
        "calibration_invalid_prob": 0.0,
        "max_retries_per_task": 2,
        "delay_p95_ms": 50.0,
    },
    {
        "id": "calibration_noise",
        "drop_completion_prob": 0.0,
        "delay_fault_prob": 0.0,
        "calibration_invalid_prob": 0.25,
        "max_retries_per_task": 1,
        "delay_p95_ms": 50.0,
    },
    {
        "id": "composite",
        "drop_completion_prob": 0.1,
        "delay_fault_prob": 0.15,
        "calibration_invalid_prob": 0.2,
        "max_retries_per_task": 2,
        "delay_p95_ms": 90.0,
    },
]


def _safe_mean(xs: list[float]) -> float | None:
    return round(sum(xs) / len(xs), 4) if xs else None


def _safe_median(xs: list[float]) -> float | None:
    return round(statistics.median(xs), 4) if xs else None


def _run_review(
    run_dir: Path,
    scenario_id: str,
    pack_path: Path,
    env: dict,
) -> dict:
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
        review_cmd,
        cwd=str(REPO),
        env=env,
        capture_output=True,
        text=True,
    )
    out: dict
    try:
        out = json.loads(r.stdout) if r.stdout else {}
    except json.JSONDecodeError:
        out = {"raw_stdout": r.stdout, "raw_stderr": r.stderr}
    out["exit_ok"] = r.returncode == 0
    return out


def _run_mapping_check(env: dict) -> dict:
    cmd = [
        sys.executable,
        str(REPO / "scripts" / "check_assurance_mapping.py"),
    ]
    r = subprocess.run(
        cmd,
        cwd=str(REPO),
        env=env,
        capture_output=True,
        text=True,
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
                    continue
    return {
        "ok": mapping_ok and (ponr_coverage_ok is not False),
        "ponr_coverage_ok": ponr_coverage_ok,
        "stdout": r.stdout.strip() if r.stdout else "",
        "stderr": r.stderr.strip() if r.stderr else "",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="P7 robust assurance evaluation")
    ap.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help="Output directory",
    )
    ap.add_argument(
        "--seeds",
        type=str,
        default=",".join(str(i) for i in range(1, 21)),
        help="Comma-separated seed list (default: 1..20 for publishable tables)",
    )
    args = ap.parse_args()

    out_dir = args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    seeds = [int(s.strip()) for s in args.seeds.split(",") if s.strip()]

    env = os.environ.copy()
    mapping_check = _run_mapping_check(env)
    rows: list[dict] = []

    from labtrust_portfolio.thinslice import run_thin_slice

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for scenario_id in SCENARIOS:
            profile_name = SCENARIO_PROFILE[scenario_id]
            pack_path = PROFILE_PACKS[profile_name]
            for regime in FAULT_REGIMES:
                for seed in seeds:
                    run_dir = root / f"run_{scenario_id}_{regime['id']}_{seed}"
                    run_dir.mkdir(parents=True, exist_ok=True)
                    run_thin_slice(
                        run_dir,
                        seed=seed,
                        scenario_id=scenario_id,
                        drop_completion_prob=float(regime["drop_completion_prob"]),
                        delay_fault_prob=float(regime["delay_fault_prob"]),
                        calibration_invalid_prob=float(
                            regime["calibration_invalid_prob"]
                        ),
                        max_retries_per_task=int(regime["max_retries_per_task"]),
                        delay_p95_ms=float(regime["delay_p95_ms"]),
                    )
                    review = _run_review(run_dir, scenario_id, pack_path, env)
                    maestro_path = run_dir / "maestro_report.json"
                    maestro = (
                        json.loads(maestro_path.read_text(encoding="utf-8"))
                        if maestro_path.exists()
                        else {}
                    )
                    latency_p95 = (
                        maestro.get("metrics", {}).get("task_latency_ms_p95")
                        if isinstance(maestro, dict)
                        else None
                    )
                    ponr_ratio = (review.get("ponr_coverage") or {}).get("ratio")
                    rows.append(
                        {
                            "scenario_id": scenario_id,
                            "profile": profile_name,
                            "fault_regime": regime["id"],
                            "seed": seed,
                            "review_exit_ok": bool(review.get("exit_ok")),
                            "evidence_bundle_ok": bool(
                                review.get("evidence_bundle_ok")
                            ),
                            "trace_ok": bool(review.get("trace_ok")),
                            "ponr_coverage_ratio": ponr_ratio,
                            "control_coverage_ratio": review.get(
                                "control_coverage_ratio"
                            ),
                            "task_latency_ms_p95": latency_p95,
                        }
                    )

    total = len(rows)
    review_passes = sum(1 for r in rows if r["review_exit_ok"])
    bundle_passes = sum(1 for r in rows if r["evidence_bundle_ok"])
    trace_passes = sum(1 for r in rows if r["trace_ok"])
    ponr_vals = [
        float(r["ponr_coverage_ratio"])
        for r in rows
        if isinstance(r.get("ponr_coverage_ratio"), (float, int))
    ]
    control_vals = [
        float(r["control_coverage_ratio"])
        for r in rows
        if isinstance(r.get("control_coverage_ratio"), (float, int))
    ]
    lat_vals = [
        float(r["task_latency_ms_p95"])
        for r in rows
        if isinstance(r.get("task_latency_ms_p95"), (float, int))
    ]
    real_world_proxy_rows = [
        r
        for r in rows
        if r["scenario_id"] in ("warehouse_v0", "traffic_v0")
    ]
    rw_total = len(real_world_proxy_rows)
    rw_pass = sum(1 for r in real_world_proxy_rows if r["review_exit_ok"])

    by_scenario: dict[str, dict] = {}
    for sid in SCENARIOS:
        subset = [r for r in rows if r["scenario_id"] == sid]
        s_total = len(subset)
        s_pass = sum(1 for r in subset if r["review_exit_ok"])
        s_ponr = [
            float(r["ponr_coverage_ratio"])
            for r in subset
            if isinstance(r.get("ponr_coverage_ratio"), (float, int))
        ]
        s_control = [
            float(r["control_coverage_ratio"])
            for r in subset
            if isinstance(r.get("control_coverage_ratio"), (float, int))
        ]
        by_scenario[sid] = {
            "n": s_total,
            "review_pass_rate": (
                round(s_pass / s_total, 4) if s_total else None
            ),
            "ponr_coverage_ratio_mean": _safe_mean(s_ponr),
            "control_coverage_ratio_mean": _safe_mean(s_control),
        }

    results = {
        "mapping_check": mapping_check,
        "run_manifest": {
            "script": "run_assurance_robust_eval.py",
            "scenarios": SCENARIOS,
            "profiles": sorted(PROFILE_PACKS.keys()),
            "scenario_profile_alignment": dict(SCENARIO_PROFILE),
            "scenario_profile_note": SCENARIO_PROFILE_NOTE,
            "fault_regimes": [r["id"] for r in FAULT_REGIMES],
            "seeds": seeds,
            "n_total_runs": total,
        },
        "aggregate": {
            "review_pass_rate": (
                round(review_passes / total, 4) if total else None
            ),
            "evidence_bundle_ok_rate": (
                round(bundle_passes / total, 4) if total else None
            ),
            "trace_ok_rate": round(trace_passes / total, 4) if total else None,
            "ponr_coverage_ratio_mean": _safe_mean(ponr_vals),
            "ponr_coverage_ratio_median": _safe_median(ponr_vals),
            "control_coverage_ratio_mean": _safe_mean(control_vals),
            "latency_p95_ms_median": _safe_median(lat_vals),
        },
        "real_world_proxy": {
            "scenarios": ["warehouse_v0", "traffic_v0"],
            "n_runs": rw_total,
            "review_pass_rate": (
                round(rw_pass / rw_total, 4) if rw_total else None
            ),
        },
        "by_scenario": by_scenario,
        "claim_support": {
            "C1": {
                "supported": bool(mapping_check.get("ok")),
                "evidence": "Schema + mapping completeness checker passes.",
            },
            "C2": {
                "supported": (
                    round(bundle_passes / total, 4) == 1.0 if total else False
                ),
                "evidence": (
                    "Mechanical checks and review scripts succeed "
                    "across robustness matrix."
                ),
            },
            "C3": {
                "supported": (
                    (round(rw_pass / rw_total, 4) if rw_total else 0.0) >= 0.95
                ),
                "evidence": (
                    "Worked examples extend to real-world proxy "
                    "scenarios (warehouse/traffic)."
                ),
            },
        },
        "rows": rows,
    }

    out_path = out_dir / "robust_results.json"
    out_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))

    ok = bool(mapping_check.get("ok")) and (review_passes == total)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
