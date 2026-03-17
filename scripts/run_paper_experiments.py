#!/usr/bin/env python3
"""
Launch paper-tailored experiments (P0–P8). Each paper gets a focused set of runs
with parameters chosen for that paper's claims. Outputs go to datasets/runs/<paper>/.
Usage (from repo root):
  PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/run_paper_experiments.py [--paper P0|P1|...|P8|all] [--quick]
  --paper: run only that paper (default: all).
  --quick: use fewer seeds/runs for faster smoke (e.g. 3 seeds instead of 5–10).
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUNS = REPO / "datasets" / "runs"


def env() -> dict:
    e = os.environ.copy()
    e.setdefault("LABTRUST_KERNEL_DIR", str(REPO / "kernel"))
    e.setdefault("PYTHONPATH", str(REPO / "impl" / "src"))
    return e


def run(cmd: list[str], label: str, timeout: int | None = 600) -> bool:
    print(f"\n--- {label} ---")
    print(" ".join(cmd))
    r = subprocess.run(
        cmd,
        cwd=str(REPO),
        env=env(),
        timeout=timeout,
    )
    ok = r.returncode == 0
    if not ok:
        print(f"FAILED exit {r.returncode}: {label}")
    return ok


def p0(quick: bool) -> bool:
    runs = 5 if quick else 10
    # E3 multi-scenario variance
    ok = run(
        [
            sys.executable,
            str(REPO / "scripts" / "produce_p0_e3_release.py"),
            "--runs", str(runs),
            "--scenarios", "toy_lab_v0,lab_profile_v0",
            "--no-release",
        ],
        "P0 E3 multi-scenario variance",
        timeout=300,
    )
    if not ok:
        return False
    # E2 redaction demo
    ok = run(
        [
            sys.executable,
            str(REPO / "scripts" / "e2_redaction_demo.py"),
            "--out", str(RUNS / "e2_redaction_demo"),
        ],
        "P0 E2 redaction demo",
        timeout=60,
    )
    if not ok:
        return False
    run(
        [sys.executable, str(REPO / "scripts" / "export_e3_table.py")],
        "P0 export E3 table",
        timeout=15,
    )
    return True


def p1(quick: bool) -> bool:
    out = RUNS / "contracts_eval"
    ok = run(
        [
            sys.executable,
            str(REPO / "scripts" / "contracts_eval.py"),
            "--out", str(out),
        ],
        "P1 Contracts corpus eval",
        timeout=60,
    )
    if not ok:
        return False
    # Scale test (surgical: 10k events if quick, else 100k); multiple runs for variance when publishable
    n = 10_000 if quick else 100_000
    scale_test_runs = 1 if quick else 5
    ok = run(
        [
            sys.executable,
            str(REPO / "scripts" / "contracts_eval.py"),
            "--out", str(out),
            "--scale-test",
            "--scale-events", str(n),
            "--scale-test-runs", str(scale_test_runs),
        ],
        "P1 Contracts scale test",
        timeout=180 if scale_test_runs > 1 else 120,
    )
    return ok


def p2(quick: bool) -> bool:
    seeds = "1,2,3" if quick else "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20"
    scenarios = "toy_lab_v0" if quick else "toy_lab_v0,lab_profile_v0"
    return run(
        [
            sys.executable,
            str(REPO / "scripts" / "rep_cps_eval.py"),
            "--out", str(RUNS / "rep_cps_eval"),
            "--scenarios", scenarios,
            "--seeds", seeds,
            "--delay-sweep", "0,0.05,0.1" if quick else "0,0.05,0.1,0.2",
        ],
        "P2 REP-CPS delay sweep (toy_lab_v0)",
        timeout=300,
    )


def p3(quick: bool) -> bool:
    out = RUNS / "replay_eval" / "summary.json"
    overhead_runs = 5 if quick else 20
    return run(
        [
            sys.executable,
            str(REPO / "scripts" / "replay_eval.py"),
            "--out", str(out),
            "--overhead-curve",
            "--overhead-runs", str(overhead_runs),
        ],
        "P3 Replay eval + overhead curve",
        timeout=120,
    )


def p4(quick: bool) -> bool:
    seeds = 3 if quick else 20
    ok = run(
        [
            sys.executable,
            str(REPO / "scripts" / "maestro_fault_sweep.py"),
            "--out", str(RUNS / "maestro_fault_sweep"),
            "--scenarios", "toy_lab_v0,lab_profile_v0",
            "--seeds", str(seeds),
        ],
        "P4 MAESTRO fault sweep (two scenarios)",
        timeout=600 if seeds > 5 else 400,
    )
    if not ok:
        return False
    ok = run(
        [
            sys.executable,
            str(REPO / "scripts" / "maestro_antigaming_eval.py"),
            "--out", str(RUNS / "maestro_antigaming"),
        ],
        "P4 MAESTRO anti-gaming",
        timeout=30,
    )
    if not ok:
        return False
    run(
        [
            sys.executable,
            str(REPO / "scripts" / "maestro_baselines.py"),
            "--scenario", "toy_lab_v0",
            "--seeds", str(seeds),
        ],
        "P4 MAESTRO baselines (toy_lab_v0)",
        timeout=180 if seeds > 5 else 120,
    )
    return True


def p5(quick: bool) -> bool:
    seeds = 3 if quick else 20
    multiscenario = RUNS / "multiscenario_runs"
    cmd = [
        sys.executable,
        str(REPO / "scripts" / "generate_multiscenario_runs.py"),
        "--out", str(multiscenario),
        "--seeds", str(seeds),
    ]
    if not quick:
        cmd.append("--fault-mix")
    ok = run(
        cmd,
        "P5 Generate multi-scenario runs",
        timeout=900 if seeds >= 20 else 600,
    )
    if not ok:
        return False
    ok = run(
        [
            sys.executable,
            str(REPO / "scripts" / "scaling_heldout_eval.py"),
            "--runs-dir", str(multiscenario),
            "--out", str(RUNS / "scaling_eval"),
        ],
        "P5 Scaling held-out eval",
        timeout=60,
    )
    if not ok:
        return False
    run(
        [
            sys.executable,
            str(REPO / "scripts" / "export_scaling_tables.py"),
            "--results", str(RUNS / "scaling_eval" / "heldout_results.json"),
        ],
        "P5 Export scaling tables",
        timeout=15,
    )
    return True


def p6(quick: bool) -> bool:
    # Red-team + confusable + adapter latency + denial-stats + baseline (tool-level and args-unsafe)
    # Publishable: 3 scenarios, 20 seeds. Real-LLM (Table 1b): run manually with --real-llm (requires .env API keys)
    scenarios = "toy_lab_v0" if quick else "toy_lab_v0,lab_profile_v0,warehouse_v0"
    adapter_seeds = "7" if quick else "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20"
    cmd = [
        sys.executable,
        str(REPO / "scripts" / "llm_redteam_eval.py"),
        "--out", str(RUNS / "llm_eval"),
        "--run-adapter",
        "--denial-stats",
        "--run-baseline",
        "--adapter-scenarios", scenarios,
        "--adapter-seeds", adapter_seeds,
    ]
    if not run(
        cmd,
        "P6 LLM red-team + adapter + denial-stats + baseline (tool-level)",
        timeout=300 if not quick else 180,
    ):
        return False
    if not quick:
        cmd_args = [
            sys.executable,
            str(REPO / "scripts" / "llm_redteam_eval.py"),
            "--out", str(RUNS / "llm_eval"),
            "--run-baseline",
            "--baseline-plan", "args_unsafe",
            "--baseline-scenarios", scenarios,
            "--baseline-seeds", adapter_seeds,
        ]
        if not run(
            cmd_args,
            "P6 baseline (args-unsafe, safe_args ablation)",
            timeout=120,
        ):
            return False
    return True


def p7(quick: bool) -> bool:
    ok = run(
        [
            sys.executable,
            str(REPO / "scripts" / "run_assurance_eval.py"),
            "--out", str(RUNS / "assurance_eval"),
        ],
        "P7 Assurance mapping + review",
        timeout=180,
    )
    if not ok:
        return False
    run(
        [
            sys.executable,
            str(REPO / "scripts" / "audit_bundle.py"),
        ],
        "P7 Audit bundle (mapping + PONR)",
        timeout=30,
    )
    run(
        [
            sys.executable,
            str(REPO / "scripts" / "export_assurance_tables.py"),
            "--results", str(RUNS / "assurance_eval" / "results.json"),
        ],
        "P7 Export assurance tables",
        timeout=15,
    )
    return True


def p8(quick: bool) -> bool:
    seeds = "1,2,3" if quick else "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20"
    meta_out = str(RUNS / "meta_eval")
    # Publishable (not quick): run collapse sweep first, then meta_eval --non-vacuous so Table 1 uses drop_prob where collapse occurs
    if not quick:
        ok = run(
            [
                sys.executable,
                str(REPO / "scripts" / "meta_collapse_sweep.py"),
                "--out", meta_out,
                "--drop-probs", "0.15,0.2,0.25,0.3",
                "--seeds", seeds,
            ],
            "P8 Meta collapse sweep (for non-vacuous drop_prob)",
            timeout=400,
        )
        if not ok:
            return False
        ok = run(
            [
                sys.executable,
                str(REPO / "scripts" / "meta_eval.py"),
                "--out", meta_out,
                "--seeds", seeds,
                "--run-naive",
                "--fault-threshold", "0",
                "--non-vacuous",
                "--fallback-adapter", "retry_heavy",
            ],
            "P8 Meta-coordination (non-vacuous: fixed vs meta vs naive, two regimes)",
            timeout=500,
        )
    else:
        ok = run(
            [
                sys.executable,
                str(REPO / "scripts" / "meta_eval.py"),
                "--out", meta_out,
                "--seeds", seeds,
                "--run-naive",
                "--fault-threshold", "0",
            ],
            "P8 Meta-coordination (fixed vs meta vs naive)",
            timeout=300,
        )
    if not ok:
        return False
    run(
        [
            sys.executable,
            str(REPO / "scripts" / "export_meta_tables.py"),
            "--comparison", str(RUNS / "meta_eval" / "comparison.json"),
        ],
        "P8 Export meta tables",
        timeout=15,
    )
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description="Run paper-tailored experiments")
    ap.add_argument(
        "--paper",
        choices=["P0", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "all"],
        default="all",
        help="Paper to run (default: all)",
    )
    ap.add_argument(
        "--quick",
        action="store_true",
        help="Use fewer seeds/runs for faster smoke",
    )
    args = ap.parse_args()

    RUNS.mkdir(parents=True, exist_ok=True)

    runners = {
        "P0": p0,
        "P1": p1,
        "P2": p2,
        "P3": p3,
        "P4": p4,
        "P5": p5,
        "P6": p6,
        "P7": p7,
        "P8": p8,
    }

    if args.paper == "all":
        papers = list(runners.keys())
    else:
        papers = [args.paper]

    failed = []
    for paper in papers:
        if not runners[paper](args.quick):
            failed.append(paper)

    if failed:
        print(f"\nFailed: {', '.join(failed)}")
        return 1
    print("\nAll paper experiments completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
