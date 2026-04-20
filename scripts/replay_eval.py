#!/usr/bin/env python3
"""
P3 Replay evaluation: run L0 replay on thin-slice and corpus trap traces;
report fidelity (pass/fail), divergence detection, optional baselines/ablations,
and overhead with reproducible percentiles and bootstrap CIs.
Output: JSON summary. Usage:
  PYTHONPATH=impl/src python scripts/replay_eval.py [--out FILE] [--corpus-dir DIR]
"""
from __future__ import annotations

import argparse
import json
import math
import os
import platform
import statistics
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "impl" / "src"))

if "LABTRUST_KERNEL_DIR" not in os.environ:
    os.environ["LABTRUST_KERNEL_DIR"] = str(REPO_ROOT / "kernel")


def _parse_seed_list(s: str) -> list[int]:
    out: list[int] = []
    for part in s.split(","):
        part = part.strip()
        if not part:
            continue
        out.append(int(part))
    return out if out else [42]


def _timing_stats(
    times_ms: list[float],
    bootstrap_reps: int,
    seed: int | None,
) -> dict:
    """Mean, stdev, empirical p95/p99 (linear percentile), bootstrap CIs, mean 95% CI."""
    from labtrust_portfolio.stats import (
        bootstrap_ci_stat,
        ci_width_95,
        percentile_linear,
    )

    n = len(times_ms)
    if n < 1:
        return {}
    mean_ms = statistics.mean(times_ms)
    stdev_ms = statistics.stdev(times_ms) if n > 1 else 0.0
    p95_ms = percentile_linear(times_ms, 0.95)
    p99_ms = percentile_linear(times_ms, 0.99)
    mean_ci95_lower = mean_ms - ci_width_95(times_ms) / 2.0
    mean_ci95_upper = mean_ms + ci_width_95(times_ms) / 2.0
    p95_ci95: tuple[float, float]
    p99_ci95: tuple[float, float]
    if n >= 2 and bootstrap_reps > 0:
        p95_ci95 = bootstrap_ci_stat(
            times_ms,
            lambda s: percentile_linear(s, 0.95),
            n_bootstrap=bootstrap_reps,
            seed=seed,
        )
        p99_ci95 = bootstrap_ci_stat(
            times_ms,
            lambda s: percentile_linear(s, 0.99),
            n_bootstrap=bootstrap_reps,
            seed=(seed + 1) if seed is not None else None,
        )
    else:
        p95_ci95 = (p95_ms, p95_ms)
        p99_ci95 = (p99_ms, p99_ms)
    return {
        "n_replays": n,
        "mean_ms": round(mean_ms, 4),
        "stdev_ms": round(stdev_ms, 4),
        "mean_ci95_lower_ms": round(mean_ci95_lower, 4),
        "mean_ci95_upper_ms": round(mean_ci95_upper, 4),
        "p95_ms": round(p95_ms, 4),
        "p99_ms": round(p99_ms, 4),
        "p95_ci95_lower_ms": round(p95_ci95[0], 4),
        "p95_ci95_upper_ms": round(p95_ci95[1], 4),
        "p99_ci95_lower_ms": round(p99_ci95[0], 4),
        "p99_ci95_upper_ms": round(p99_ci95[1], 4),
        "percentile_method": "linear_hf7",
    }


def _diagnostic_payload_bytes_approx(diagnostics: list) -> int | None:
    """Approximate UTF-8 JSON size of the first diagnostic (for space accounting)."""
    if not diagnostics:
        return None
    d0 = diagnostics[0]
    diag_obj = {
        "seq": d0.seq,
        "expected_hash": d0.expected_hash,
        "got_hash": d0.got_hash,
        "event_type": d0.event_type,
        "root_cause_category": d0.root_cause_category,
        "witness_slice": d0.witness_slice,
    }
    blob = json.dumps(
        diag_obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return len(blob)


def _state_hash_after_count(trace: dict) -> int:
    return sum(1 for e in (trace.get("events") or []) if e.get("state_hash_after"))


def _overhead_curve_event_counts(n_events: int) -> list[int]:
    """
    Prefix sizes for overhead curve: scale with actual thin-slice length so the
    curve has multiple points (not a single-prefix pseudo-curve when n is small).
    """
    if n_events < 1:
        return []
    if n_events == 1:
        return [1]
    sizes: list[int] = []
    for frac in (0.2, 0.35, 0.5, 0.65, 0.8, 0.9, 1.0):
        sz = max(1, min(n_events, int(math.ceil(n_events * frac))))
        sizes.append(sz)
    out = sorted(set(sizes))
    if len(out) < 2:
        out = sorted({1, max(1, n_events // 2), n_events})
    return out


def _infer_corpus_category(trace_name: str, trace: dict) -> str:
    """
    Infer corpus category: synthetic_trap, field_proxy, real_ingest.
    Naming convention: real_bucket_* -> real_ingest; field_style_* -> field_proxy;
    *_trap -> synthetic_trap; else synthetic_pass.
    """
    if trace_name.startswith("real_bucket_"):
        return "real_ingest"
    if trace_name.startswith("field_style_"):
        return "field_proxy"
    if "_trap" in trace_name:
        return "synthetic_trap"
    if trace_name == "thin_slice":
        return "synthetic_pass"
    # Default for benign_perturbation_pass etc
    return "synthetic_pass"


def _corpus_space_summary(per_trace: list[dict]) -> dict:
    """Aggregate trace/diagnostic sizes for corpus rows (excludes thin_slice)."""
    corp = [r for r in per_trace if r.get("name") != "thin_slice"]
    if not corp:
        return {}
    sizes = [int(r.get("trace_json_bytes") or 0) for r in corp]
    hash_counts = [int(r.get("state_hash_after_count") or 0) for r in corp]
    diags = [
        int(r["diagnostic_payload_bytes_approx"])
        for r in corp
        if r.get("diagnostic_payload_bytes_approx") is not None
    ]
    out: dict = {
        "corpus_traces_n": len(corp),
        "trace_json_bytes_sum": int(sum(sizes)),
        "trace_json_bytes_mean": round(sum(sizes) / len(sizes), 4),
        "state_hash_after_count_sum": int(sum(hash_counts)),
        "state_hash_after_count_mean": round(
            sum(hash_counts) / len(hash_counts), 4
        ),
    }
    if diags:
        out["diagnostic_payload_bytes_approx_sum"] = int(sum(diags))
        out["diagnostic_payload_bytes_approx_mean"] = round(
            statistics.mean(diags), 4
        )
    return out


def _peak_rss_bytes() -> int | None:
    """Best-effort peak RSS for this process (platform-specific; None if unavailable)."""
    try:
        import resource

        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if sys.platform == "darwin":
            return int(rss)
        # Linux and most Unix: KiB
        return int(rss) * 1024
    except Exception:
        return None


def _paired_baseline_comparison(
    full_times: list[float],
    baseline_times: list[float],
    bootstrap_reps: int,
    seed: int | None,
) -> dict | None:
    from labtrust_portfolio.stats import bootstrap_ci_difference, effect_size_mean_diff

    if len(full_times) != len(baseline_times) or len(full_times) < 2:
        return None
    diff_mean, cohens_d = effect_size_mean_diff(full_times, baseline_times)
    lo, hi = bootstrap_ci_difference(
        full_times,
        baseline_times,
        n_bootstrap=bootstrap_reps,
        seed=seed,
    )
    return {
        "difference_mean_ms": round(diff_mean, 4),
        "difference_ci95_lower_ms": round(lo, 4),
        "difference_ci95_upper_ms": round(hi, 4),
        "cohens_d_paired": round(cohens_d, 4) if cohens_d == cohens_d else None,
        "interpretation": "positive means full L0 (per-event hash + localization) slower than baseline",
    }


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
        "--thin-slice-seeds",
        type=str,
        default="42",
        help="Comma-separated seeds for thin-slice generation (multi-seed family). "
        "First seed is primary unless --primary-seed is set.",
    )
    ap.add_argument(
        "--primary-seed",
        type=int,
        default=None,
        help="Seed for primary thin-slice (overhead, Table 2). Default: first in --thin-slice-seeds.",
    )
    ap.add_argument(
        "--overhead-runs",
        type=int,
        default=20,
        help="Number of replays for overhead stats (default 20)",
    )
    ap.add_argument(
        "--warmup",
        type=int,
        default=0,
        help="Discarded replay iterations before timing (default 0; use 1+ to stabilize microbench)",
    )
    ap.add_argument(
        "--overhead-curve",
        action="store_true",
        help="Record p95 replay time vs trace size (event count) for overhead curve",
    )
    ap.add_argument(
        "--l1-twin",
        action="store_true",
        help="Run full L1 twin (L0 + config + deterministic re-run); default is L1 stub only",
    )
    ap.add_argument(
        "--no-baselines",
        action="store_true",
        help="Skip apply-only and final-hash-only baseline timings",
    )
    ap.add_argument(
        "--bootstrap-reps",
        type=int,
        default=1000,
        help="Bootstrap resamples for percentile CIs (default 1000; 0 disables)",
    )
    args = ap.parse_args()

    from labtrust_portfolio.replay import (
        replay_trace_apply_only,
        replay_trace_final_hash_only,
        replay_trace_with_diagnostics,
        replay_l1_stub,
        replay_l1_twin,
    )
    from labtrust_portfolio.stats import percentile_linear, wilson_ci_binomial
    from labtrust_portfolio.thinslice import run_thin_slice

    seeds = _parse_seed_list(args.thin_slice_seeds)
    primary_seed = args.primary_seed if args.primary_seed is not None else seeds[0]
    if primary_seed not in seeds:
        seeds = [primary_seed] + [s for s in seeds if s != primary_seed]

    thin_traces: dict[int, dict] = {}
    for sd in seeds:
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td)
            run_thin_slice(run_dir, seed=sd, drop_completion_prob=0.0)
            trace_path = run_dir / "trace.json"
            thin_traces[sd] = json.loads(trace_path.read_text(encoding="utf-8"))

    thin_slice_trace = thin_traces[primary_seed]
    results: list[dict] = []

    # Thin-slice replay (primary)
    t0 = time.perf_counter()
    ok, diagnostics = replay_trace_with_diagnostics(thin_slice_trace)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    trace = thin_slice_trace
    thin_blob = json.dumps(
        thin_slice_trace, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    results.append(
        {
            "name": "thin_slice",
            "trace_file": "generated",
            "thin_slice_seed": primary_seed,
            "replay_ok": ok,
            "divergence_detected": not ok and len(diagnostics) > 0,
            "divergence_at_seq": diagnostics[0].seq if diagnostics else None,
            "root_cause_category": diagnostics[0].root_cause_category if diagnostics else None,
            "replay_time_ms": round(elapsed_ms, 2),
            "event_count": len(trace.get("events", [])),
            "trace_json_bytes": len(thin_blob),
            "state_hash_after_count": _state_hash_after_count(thin_slice_trace),
            "diagnostic_payload_bytes_approx": _diagnostic_payload_bytes_approx(
                diagnostics
            ),
            "localization_matches_expected": ok,
            "localization_ambiguous": len(diagnostics) > 1,
            "corpus_category": "synthetic_pass",
        }
    )

    # L1 stub / twin
    twin_config_path = args.corpus_dir / "twin_config.json"
    l1_stub_ok = False
    l1_stub_message = ""
    l1_twin_ok = False
    l1_twin_message = ""
    l1_twin_time_ms: float | None = None
    l1_twin_multi_seed: list[dict] = []
    l1_twin_real_ingest_rows: list[dict] = []
    if thin_slice_trace is not None:
        l1_stub_ok, l1_stub_message = replay_l1_stub(thin_slice_trace, twin_config_path)
        if args.l1_twin:
            # Primary seed L1 twin
            t_l1 = time.perf_counter()
            l1_twin_ok, l1_twin_message = replay_l1_twin(thin_slice_trace, twin_config_path)
            l1_twin_time_ms = round((time.perf_counter() - t_l1) * 1000, 4)
            # Multi-seed L1 twin (for aggregate reporting)
            for sd in seeds:
                tr = thin_traces[sd]
                t0 = time.perf_counter()
                ok_twin, msg_twin = replay_l1_twin(tr, twin_config_path)
                elapsed_twin = (time.perf_counter() - t0) * 1000
                l1_twin_multi_seed.append({
                    "seed": sd,
                    "l1_twin_ok": ok_twin,
                    "l1_twin_time_ms": round(elapsed_twin, 4),
                    "l1_twin_message": msg_twin,
                })

    bseed = None
    try:
        bseed = int(os.environ["LABTRUST_FIXED_SEED"])
    except (KeyError, ValueError):
        bseed = 42

    # Warmup + overhead: full L0
    overhead_times_ms: list[float] = []
    apply_times_ms: list[float] = []
    final_hash_times_ms: list[float] = []
    witness0_times_ms: list[float] = []

    if thin_slice_trace is not None and args.overhead_runs > 0:
        for _ in range(args.warmup):
            replay_trace_with_diagnostics(thin_slice_trace)
            if not args.no_baselines:
                replay_trace_apply_only(thin_slice_trace)
                replay_trace_final_hash_only(thin_slice_trace)
                replay_trace_with_diagnostics(thin_slice_trace, witness_window=0)

        for _ in range(args.overhead_runs):
            t0 = time.perf_counter()
            replay_trace_with_diagnostics(thin_slice_trace)
            overhead_times_ms.append((time.perf_counter() - t0) * 1000)
            if not args.no_baselines:
                t0 = time.perf_counter()
                replay_trace_apply_only(thin_slice_trace)
                apply_times_ms.append((time.perf_counter() - t0) * 1000)
                t0 = time.perf_counter()
                replay_trace_final_hash_only(thin_slice_trace)
                final_hash_times_ms.append((time.perf_counter() - t0) * 1000)
                t0 = time.perf_counter()
                replay_trace_with_diagnostics(thin_slice_trace, witness_window=0)
                witness0_times_ms.append((time.perf_counter() - t0) * 1000)

    overhead_stats: dict = {}
    if len(overhead_times_ms) >= 1:
        overhead_stats = _timing_stats(
            overhead_times_ms,
            max(0, args.bootstrap_reps),
            bseed,
        )

    baseline_overhead: dict = {}
    if not args.no_baselines and len(apply_times_ms) == len(overhead_times_ms):
        baseline_overhead["apply_only_no_hash"] = _timing_stats(
            apply_times_ms, max(0, args.bootstrap_reps), bseed + 2
        )
        baseline_overhead["final_hash_only"] = _timing_stats(
            final_hash_times_ms, max(0, args.bootstrap_reps), bseed + 3
        )
        baseline_overhead["full_l0_witness_window_0"] = _timing_stats(
            witness0_times_ms, max(0, args.bootstrap_reps), bseed + 4
        )
        bl = _paired_baseline_comparison(
            overhead_times_ms,
            apply_times_ms,
            max(100, args.bootstrap_reps),
            bseed + 10,
        )
        if bl:
            baseline_overhead["full_vs_apply_only"] = bl

    # Multi-seed overhead: one mean_ms per seed (reuse primary timing when same seed)
    multi_seed_overhead: list[dict] = []
    for sd in seeds:
        if sd == primary_seed and overhead_times_ms:
            st = _timing_stats(
                overhead_times_ms, max(0, args.bootstrap_reps), bseed
            )
            st["seed"] = sd
            multi_seed_overhead.append(st)
            continue
        tr = thin_traces[sd]
        times: list[float] = []
        for _ in range(max(0, args.warmup)):
            replay_trace_with_diagnostics(tr)
        for _ in range(args.overhead_runs):
            t0 = time.perf_counter()
            replay_trace_with_diagnostics(tr)
            times.append((time.perf_counter() - t0) * 1000)
        if times:
            st = _timing_stats(times, max(0, args.bootstrap_reps), bseed + sd)
            st["seed"] = sd
            multi_seed_overhead.append(st)

    across_means = [x["mean_ms"] for x in multi_seed_overhead if "mean_ms" in x]
    multi_seed_summary: dict | None = None
    if len(across_means) >= 1:
        multi_seed_summary = {
            "seeds": seeds,
            "n_seeds": len(seeds),
            "per_seed": multi_seed_overhead,
            "across_seeds_mean_of_means_ms": round(statistics.mean(across_means), 4),
            "across_seeds_stdev_of_means_ms": round(
                statistics.stdev(across_means) if len(across_means) > 1 else 0.0,
                4,
            ),
        }

    # Corpus trap traces
    trace_files = sorted(args.corpus_dir.glob("*_trace.json"))
    corpus_expected: list[tuple[str, int | None]] = []
    for trace_path in trace_files:
        trace_name = trace_path.stem.replace("_trace", "")
        expected_path = args.corpus_dir / f"{trace_name}_expected.json"
        if not trace_path.exists():
            continue
        trace_bytes_on_disk = trace_path.read_bytes()
        trace = json.loads(trace_bytes_on_disk.decode("utf-8"))
        expected: dict = {}
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
            "expected_divergence_at_seq": expected.get("expected_divergence_at_seq"),
            "replay_time_ms": round(elapsed_ms, 2),
            "event_count": len(trace.get("events", [])),
            "trace_json_bytes": len(trace_bytes_on_disk),
            "state_hash_after_count": _state_hash_after_count(trace),
            "diagnostic_payload_bytes_approx": _diagnostic_payload_bytes_approx(
                diagnostics
            ),
        }
        exp_seq = expected.get("expected_divergence_at_seq")
        if exp_seq is not None:
            loc_ok = (
                bool(diagnostics)
                and diagnostics[0].seq == exp_seq
            )
            entry["localization_matches_expected"] = loc_ok
            entry["localization_ambiguous"] = len(diagnostics) > 1
        elif expected.get("expected_replay_ok") is True:
            entry["localization_matches_expected"] = ok
            entry["localization_ambiguous"] = False
        else:
            entry["localization_matches_expected"] = None
            entry["localization_ambiguous"] = None
        if diagnostics:
            entry["witness_slice"] = getattr(
                diagnostics[0], "witness_slice", []
            )
        entry["corpus_category"] = _infer_corpus_category(trace_name, trace)
        results.append(entry)

    # L1 twin on real_ingest corpus rows (second evaluation family vs thin-slice seeds)
    if args.l1_twin and twin_config_path.exists():
        for r in results:
            if r["name"] == "thin_slice":
                continue
            if r.get("corpus_category") != "real_ingest":
                continue
            if not r.get("replay_ok"):
                continue
            tp = args.corpus_dir / f"{r['name']}_trace.json"
            if not tp.exists():
                continue
            tr_body = json.loads(tp.read_text(encoding="utf-8"))
            t0 = time.perf_counter()
            ok_tr, msg_tr = replay_l1_twin(tr_body, twin_config_path)
            elapsed_tr = (time.perf_counter() - t0) * 1000
            l1_twin_real_ingest_rows.append(
                {
                    "trace_name": r["name"],
                    "corpus_category": "real_ingest",
                    "l0_replay_ok": r.get("replay_ok"),
                    "l1_twin_ok": ok_tr,
                    "l1_twin_time_ms": round(elapsed_tr, 4),
                    "l1_twin_message": msg_tr,
                }
            )

    replay_level = "L0"
    if l1_stub_ok:
        replay_level = "L1"
    if args.l1_twin and l1_twin_ok:
        replay_level = "L1_twin"

    nondeterminism_budget = {
        "L0": "control-plane state must match exactly; one bit => non-replayable",
        "L1": "L0 plus twin config identity; distributional under twin fidelity",
        "L2": "aspirational; distributional, not bitwise",
    }

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

    loc_k = correct_localizations
    loc_n = total_corpus
    loc_wilson = wilson_ci_binomial(loc_k, loc_n) if loc_n > 0 else (float("nan"), float("nan"))

    fidelity_pass = all(
        r["replay_ok"] for r in results if r["name"] == "thin_slice"
    )

    overhead_curve: list[dict] = []
    if args.overhead_curve and thin_slice_trace is not None:
        events = thin_slice_trace.get("events", [])
        n_curve_runs = max(5, args.overhead_runs)
        for size in _overhead_curve_event_counts(len(events)):
            sub_trace = dict(thin_slice_trace)
            sub_trace["events"] = events[:size]
            times_ms = []
            for _ in range(n_curve_runs):
                t0 = time.perf_counter()
                replay_trace_with_diagnostics(sub_trace)
                times_ms.append((time.perf_counter() - t0) * 1000)
            p95 = percentile_linear(times_ms, 0.95)
            stdev_ms = statistics.stdev(times_ms) if len(times_ms) > 1 else 0.0
            p95_lo, p95_hi = (p95, p95)
            if len(times_ms) >= 2 and args.bootstrap_reps > 0:
                from labtrust_portfolio.stats import bootstrap_ci_stat

                p95_lo, p95_hi = bootstrap_ci_stat(
                    times_ms,
                    lambda s: percentile_linear(s, 0.95),
                    n_bootstrap=max(100, args.bootstrap_reps),
                    seed=bseed + size,
                )
            entry = {
                "event_count": size,
                "p95_replay_ms": round(p95, 4),
                "p95_replay_stdev_ms": round(stdev_ms, 4) if len(times_ms) > 1 else None,
                "p95_replay_ci95_lower_ms": round(p95_lo, 4),
                "p95_replay_ci95_upper_ms": round(p95_hi, 4),
            }
            overhead_curve.append(entry)

    overhead_curve_runs = max(5, args.overhead_runs) if args.overhead_curve else None
    witness_slices = [
        r.get("witness_slice", [])
        for r in results
        if r.get("divergence_detected") and r.get("witness_slice")
    ]

    corpus_traps_pre = [r for r in results if r["name"] != "thin_slice"]

    def _corpus_outcome_correct(r: dict) -> bool:
        exp_ok = r.get("expected_replay_ok")
        if exp_ok is True:
            return bool(r.get("replay_ok"))
        exp_seq = r.get("expected_divergence_at_seq")
        if exp_seq is not None:
            return bool(r.get("divergence_detected")) and r.get(
                "divergence_at_seq"
            ) == exp_seq
        return False

    n_corpus_correct = sum(
        1 for r in corpus_traps_pre if _corpus_outcome_correct(r)
    )
    div_accuracy_pre = (
        round(100.0 * n_corpus_correct / len(corpus_traps_pre), 1)
        if corpus_traps_pre
        else 100.0
    )
    corpus_outcome_wilson = (
        wilson_ci_binomial(n_corpus_correct, len(corpus_traps_pre))
        if corpus_traps_pre
        else (float("nan"), float("nan"))
    )

    # L1 twin aggregate summary (when multi-seed L1 twin was run)
    l1_twin_summary: dict | None = None
    if args.l1_twin and l1_twin_multi_seed:
        twin_oks = [x["l1_twin_ok"] for x in l1_twin_multi_seed]
        twin_times = [x["l1_twin_time_ms"] for x in l1_twin_multi_seed if x.get("l1_twin_time_ms") is not None]
        real_oks = [x["l1_twin_ok"] for x in l1_twin_real_ingest_rows]
        all_pass = all(twin_oks) and (all(real_oks) if real_oks else True)
        l1_twin_summary = {
            "n_seeds": len(l1_twin_multi_seed),
            "seeds": [x["seed"] for x in l1_twin_multi_seed],
            "all_pass": all_pass,
            "n_pass": sum(1 for ok in twin_oks if ok),
            "per_seed": l1_twin_multi_seed,
        }
        if l1_twin_real_ingest_rows:
            l1_twin_summary["real_ingest_traces"] = l1_twin_real_ingest_rows
            l1_twin_summary["real_ingest_all_pass"] = all(real_oks)
            l1_twin_summary["n_real_ingest_traces"] = len(l1_twin_real_ingest_rows)
        if twin_times:
            l1_twin_summary["mean_time_ms"] = round(statistics.mean(twin_times), 4)
            l1_twin_summary["stdev_time_ms"] = round(statistics.stdev(twin_times), 4) if len(twin_times) > 1 else 0.0
            if len(twin_times) >= 2:
                l1_twin_summary["min_time_ms"] = round(min(twin_times), 4)
                l1_twin_summary["max_time_ms"] = round(max(twin_times), 4)

    summary = {
        "replay_eval": True,
        "schema_version": "p3_replay_eval_v0.2",
        "replay_level": replay_level,
        "nondeterminism_budget": nondeterminism_budget,
        "divergence_localization_confidence": round(
            divergence_localization_confidence, 4
        ),
        "divergence_localization_wilson_ci95": [
            round(loc_wilson[0], 4),
            round(loc_wilson[1], 4),
        ]
        if loc_n > 0
        else None,
        "corpus_outcome_wilson_ci95": [
            round(corpus_outcome_wilson[0], 4),
            round(corpus_outcome_wilson[1], 4),
        ]
        if corpus_traps_pre
        else None,
        "fidelity_pass": fidelity_pass,
        "l1_stub_ok": l1_stub_ok,
        "l1_stub_message": l1_stub_message,
        "l1_twin_ok": l1_twin_ok if args.l1_twin else None,
        "l1_twin_message": l1_twin_message if args.l1_twin else None,
        "l1_twin_final_hash_match": l1_twin_ok if args.l1_twin else None,
        "l1_twin_replay_time_ms": l1_twin_time_ms,
        "l1_twin_multi_seed": l1_twin_multi_seed if args.l1_twin and l1_twin_multi_seed else None,
        "l1_twin_summary": l1_twin_summary,
        "overhead_stats": overhead_stats,
        "baseline_overhead": baseline_overhead if baseline_overhead else None,
        "multi_seed_overhead": multi_seed_summary,
        "thin_slice_seeds_used": seeds,
        "primary_thin_slice_seed": primary_seed,
        "overhead_curve": overhead_curve if overhead_curve else None,
        "witness_slices": witness_slices,
        "corpus_divergence_detected": [
            r for r in results if r["name"] != "thin_slice" and r["divergence_detected"]
        ],
        "per_trace": results,
        "corpus_space_summary": _corpus_space_summary(results),
        "process_peak_rss_bytes": _peak_rss_bytes(),
        "run_manifest": {
            "corpus_dir": str(args.corpus_dir),
            "replay_trap_count": len(corpus_expected),
            "overhead_runs": args.overhead_runs,
            "warmup_iterations": args.warmup,
            "overhead_curve_runs": overhead_curve_runs,
            "thin_slice_seeds": seeds,
            "primary_thin_slice_seed": primary_seed,
            "bootstrap_reps": args.bootstrap_reps,
            "baselines_enabled": not args.no_baselines,
            "percentile_method": "linear_hf7",
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
            "script": "replay_eval.py",
            "l1_twin_real_ingest_n": len(l1_twin_real_ingest_rows),
        },
        "success_criteria_met": {
            "fidelity_pass": fidelity_pass,
            "corpus_expected_outcomes_met": all(
                _corpus_outcome_correct(r) for r in corpus_traps_pre
            )
            if corpus_traps_pre
            else True,
            "corpus_divergences_detected": all(
                _corpus_outcome_correct(r) for r in corpus_traps_pre
            )
            if corpus_traps_pre
            else True,
        },
    }
    corpus_traps = corpus_traps_pre
    div_accuracy = div_accuracy_pre
    overhead_p99_ms = None
    if overhead_stats and overhead_stats.get("n_replays", 0) >= 1:
        overhead_p99_ms = overhead_stats.get("p99_ms")

    summary["excellence_metrics"] = {
        "divergence_localization_accuracy_pct": div_accuracy,
        "divergence_localization_n_traps": len(corpus_traps),
        "divergence_localization_n_correct": n_corpus_correct,
        "overhead_p99_ms": overhead_p99_ms,
        "overhead_p99_empirical": True,
        "l1_stub_ok": l1_stub_ok,
        "l1_twin_ok": l1_twin_ok if args.l1_twin else None,
        "witness_slices_present": len(witness_slices) > 0,
    }
    print(json.dumps(summary, indent=2))
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
