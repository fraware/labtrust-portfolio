#!/usr/bin/env python3
"""
P3 Replay evaluation: run L0 replay on thin-slice and corpus trap traces;
report fidelity (pass/fail), divergence detection, and optional overhead.
Output: JSON summary. Usage:
  PYTHONPATH=impl/src python scripts/replay_eval.py [--out FILE] [--corpus-dir DIR]
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "impl" / "src"))

if "LABTRUST_KERNEL_DIR" not in os.environ:
    os.environ["LABTRUST_KERNEL_DIR"] = str(REPO_ROOT / "kernel")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="P3: Replay eval on thin-slice and corpus traces"
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "datasets" / "runs" / "replay_eval" / "summary.json",
        help="Write summary JSON here",
    )
    ap.add_argument(
        "--corpus-dir",
        type=Path,
        default=REPO_ROOT / "bench" / "replay" / "corpus",
        help="Corpus directory with *_trace.json and *_expected.json",
    )
    ap.add_argument(
        "--overhead-runs",
        type=int,
        default=20,
        help="Number of replays for overhead stats (default 20)",
    )
    ap.add_argument(
        "--overhead-curve",
        action="store_true",
        help="Record p95 replay time vs trace size (event count) for overhead curve",
    )
    args = ap.parse_args()

    from labtrust_portfolio.replay import (
        replay_trace_with_diagnostics,
        replay_l1_stub,
    )
    from labtrust_portfolio.thinslice import run_thin_slice

    results = []
    thin_slice_trace = None

    # Thin-slice trace: generate one run, then replay
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        run_dir = Path(td)
        run_thin_slice(run_dir, seed=42, drop_completion_prob=0.0)
        trace_path = run_dir / "trace.json"
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        thin_slice_trace = trace
        t0 = time.perf_counter()
        ok, diagnostics = replay_trace_with_diagnostics(trace)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        results.append(
            {
                "name": "thin_slice",
                "trace_file": "generated",
                "replay_ok": ok,
                "divergence_detected": not ok and len(diagnostics) > 0,
                "divergence_at_seq": diagnostics[0].seq if diagnostics else None,
                "root_cause_category": diagnostics[0].root_cause_category if diagnostics else None,
                "replay_time_ms": round(elapsed_ms, 2),
                "event_count": len(trace.get("events", [])),
            }
        )

    # L1 stub: run on thin-slice trace with twin config
    twin_config_path = args.corpus_dir / "twin_config.json"
    l1_stub_ok = False
    l1_stub_message = ""
    if thin_slice_trace is not None:
        l1_stub_ok, l1_stub_message = replay_l1_stub(thin_slice_trace, twin_config_path)

    # Overhead stats: replay thin-slice trace N times
    overhead_times_ms: list[float] = []
    if thin_slice_trace is not None and args.overhead_runs > 0:
        for _ in range(args.overhead_runs):
            t0 = time.perf_counter()
            replay_trace_with_diagnostics(thin_slice_trace)
            overhead_times_ms.append((time.perf_counter() - t0) * 1000)
    overhead_stats = {}
    if len(overhead_times_ms) >= 1:
        overhead_stats = {
            "n_replays": len(overhead_times_ms),
            "mean_ms": round(statistics.mean(overhead_times_ms), 4),
            "stdev_ms": round(
                statistics.stdev(overhead_times_ms)
                if len(overhead_times_ms) > 1 else 0.0,
                4,
            ),
            "p95_ms": round(
                sorted(overhead_times_ms)[int(0.95 * len(overhead_times_ms))]
                if overhead_times_ms else 0.0,
                4,
            ),
        }

    # Corpus trap traces: discover all *_trace.json in corpus dir (nondeterminism_trap, reorder_trap, timestamp_reorder_trap, hash_mismatch_trap, etc.)
    trace_files = sorted(args.corpus_dir.glob("*_trace.json"))
    corpus_expected: list[tuple[str, int | None]] = []
    for trace_path in trace_files:
        trace_name = trace_path.stem.replace("_trace", "")
        expected_path = args.corpus_dir / f"{trace_name}_expected.json"
        if not trace_path.exists():
            continue
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        expected = {}
        if expected_path.exists():
            expected = json.loads(expected_path.read_text(encoding="utf-8"))
            exp_seq = expected.get("expected_divergence_at_seq")
            if exp_seq is not None:
                corpus_expected.append((trace_name, exp_seq))
        t0 = time.perf_counter()
        ok, diagnostics = replay_trace_with_diagnostics(trace)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        entry = {
            "name": trace_name,
            "trace_file": trace_path.name,
            "replay_ok": ok,
            "divergence_detected": not ok and len(diagnostics) > 0,
            "divergence_at_seq": diagnostics[0].seq if diagnostics else None,
            "root_cause_category": diagnostics[0].root_cause_category if diagnostics else None,
            "expected_replay_ok": expected.get("expected_replay_ok"),
            "expected_divergence_at_seq": expected.get(
                "expected_divergence_at_seq"
            ),
            "replay_time_ms": round(elapsed_ms, 2),
            "event_count": len(trace.get("events", [])),
        }
        if diagnostics:
            entry["witness_slice"] = getattr(
                diagnostics[0], "witness_slice", []
            )
        results.append(entry)

    # Replay levels: L0 (control-plane default), L1 (twin), L2 (hardware-assisted).
    # Guarantee is detection and localization of nondeterminism, not bit-identical hardware replay.
    replay_level = "L0"
    if l1_stub_ok:
        replay_level = "L1"  # L1 stub validated; full L1 twin replay not implemented

    # Nondeterminism budget (kernel/trace/REPLAY_LEVELS.v0.1.md).
    nondeterminism_budget = {
        "L0": "control-plane state must match exactly; one bit => non-replayable",
        "L1": "L0 plus twin config identity; distributional under twin fidelity",
        "L2": "aspirational; distributional, not bitwise",
    }

    # Divergence localization: fraction of corpus traps where divergence_at_seq matches expected.
    correct_localizations = sum(
        1
        for r in results
        for name, exp_seq in corpus_expected
        if r["name"] == name and r.get("divergence_at_seq") == exp_seq
    )
    total_corpus = len(corpus_expected)
    divergence_localization_confidence = (
        correct_localizations / total_corpus if total_corpus else 0.0
    )

    fidelity_pass = all(
        r["replay_ok"] for r in results if r["name"] == "thin_slice"
    )

    overhead_curve = []
    if args.overhead_curve and thin_slice_trace is not None:
        events = thin_slice_trace.get("events", [])
        n_curve_runs = max(5, args.overhead_runs)
        for size in [10, 25, 50, 100, 200, 500]:
            if size > len(events):
                break
            sub_trace = dict(thin_slice_trace)
            sub_trace["events"] = events[:size]
            times_ms = []
            for _ in range(n_curve_runs):
                t0 = time.perf_counter()
                replay_trace_with_diagnostics(sub_trace)
                times_ms.append((time.perf_counter() - t0) * 1000)
            p95 = sorted(times_ms)[int(0.95 * len(times_ms))] if times_ms else 0.0
            stdev_ms = statistics.stdev(times_ms) if len(times_ms) > 1 else 0.0
            entry = {"event_count": size, "p95_replay_ms": round(p95, 4)}
            if len(times_ms) > 1:
                entry["p95_replay_stdev_ms"] = round(stdev_ms, 4)
            overhead_curve.append(entry)

    overhead_curve_runs = max(5, args.overhead_runs) if args.overhead_curve else None
    witness_slices = [
        r.get("witness_slice", [])
        for r in results
        if r.get("divergence_detected") and r.get("witness_slice")
    ]
    summary = {
        "replay_eval": True,
        "replay_level": replay_level,
        "nondeterminism_budget": nondeterminism_budget,
        "divergence_localization_confidence": round(
            divergence_localization_confidence, 4
        ),
        "fidelity_pass": fidelity_pass,
        "l1_stub_ok": l1_stub_ok,
        "l1_stub_message": l1_stub_message,
        "overhead_stats": overhead_stats,
        "overhead_curve": overhead_curve if overhead_curve else None,
        "witness_slices": witness_slices,
        "corpus_divergence_detected": [
            r for r in results if r["name"] != "thin_slice" and r["divergence_detected"]
        ],
        "per_trace": results,
        "run_manifest": {
            "corpus_dir": str(args.corpus_dir),
            "replay_trap_count": len(corpus_expected),
            "overhead_runs": args.overhead_runs,
            "overhead_curve_runs": overhead_curve_runs,
            "script": "replay_eval.py",
        },
        "success_criteria_met": {
            "fidelity_pass": fidelity_pass,
            "corpus_divergences_detected": all(
                r["divergence_detected"] for r in results
                if r["name"] != "thin_slice"
            ) if any(r["name"] != "thin_slice" for r in results) else True,
        },
    }
    # Excellence metrics (STANDARDS_OF_EXCELLENCE.md)
    corpus_traps = [r for r in results if r["name"] != "thin_slice"]
    n_localized = sum(
        1 for r in corpus_traps
        if r.get("divergence_detected") and r.get("expected_divergence_at_seq") is not None
        and r.get("divergence_at_seq") == r.get("expected_divergence_at_seq")
    )
    div_accuracy = round(100.0 * n_localized / len(corpus_traps), 1) if corpus_traps else 100.0
    overhead_p99_ms = None
    if overhead_stats and overhead_stats.get("n_replays", 0) >= 2:
        # Approximate p99 from mean + 2.33*stdev for normal-ish distribution
        mean_ms = overhead_stats.get("mean_ms", 0) or 0
        stdev_ms = overhead_stats.get("stdev_ms", 0) or 0
        overhead_p99_ms = round(mean_ms + 2.33 * stdev_ms, 4)
    summary["excellence_metrics"] = {
        "divergence_localization_accuracy_pct": div_accuracy,
        "overhead_p99_ms": overhead_p99_ms,
        "l1_stub_ok": l1_stub_ok,
        "witness_slices_present": len(witness_slices) > 0,
    }
    print(json.dumps(summary, indent=2))
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
