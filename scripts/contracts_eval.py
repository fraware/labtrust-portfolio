#!/usr/bin/env python3
"""
P1 Contracts evaluation: run validator (and apply_event_to_state) on corpus
sequences; record detection/denial and overhead. Writes to
datasets/runs/contracts_eval/eval.json. Usage:
  PYTHONPATH=impl/src python scripts/contracts_eval.py [--out DIR]
  PYTHONPATH=impl/src python scripts/contracts_eval.py --throughput [--scale N]
  PYTHONPATH=impl/src python scripts/contracts_eval.py --scale-test [--scale-events 100000]
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import os
import random
import statistics
import sys
import time
from pathlib import Path

try:
    import resource
except ImportError:
    resource = None

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "impl" / "src"))

from labtrust_portfolio.contracts import validate, apply_event_to_state, ALLOW

SCRIPT_VERSION = "v0.3"


def _bootstrap_percentile_ci(
    samples: list[float],
    percentile: float,
    n_bootstrap: int = 1000,
    ci: float = 0.95,
    seed: int | None = None,
) -> tuple[float, float]:
    """Bootstrap CI for a percentile. percentile in [0,100]. Returns (lower, upper)."""
    if not samples:
        return (0.0, 0.0)
    if seed is None:
        seed = 42
    rng = random.Random(seed)
    n = len(samples)
    quantile = percentile / 100.0
    boot: list[float] = []
    for _ in range(n_bootstrap):
        resample = [samples[rng.randint(0, n - 1)] for _ in range(n)]
        resample.sort()
        idx = min(int(quantile * n), n - 1) if n else 0
        boot.append(resample[idx])
    boot.sort()
    alpha = 1 - ci
    lo_idx = int(alpha / 2 * n_bootstrap)
    hi_idx = min(int((1 - alpha / 2) * n_bootstrap), n_bootstrap - 1)
    return (boot[lo_idx], boot[hi_idx])


def _timestamp_only_allows(state: dict, event: dict) -> bool:
    """Baseline policy: allow iff event_ts > last_ts for key (no ownership check)."""
    last_ts = state.get("_last_ts", {})
    payload = event.get("payload", {})
    key = payload.get("task_id") or payload.get("key")
    if not key:
        return True
    event_ts = event.get("ts", 0.0)
    prev_ts = last_ts.get(key, -1.0)
    return event_ts > prev_ts


def _ownership_only_allows(state: dict, event: dict) -> bool:
    """Baseline policy: allow iff writer is owner or no owner (no temporal check)."""
    ownership = state.get("ownership", {})
    payload = event.get("payload", {})
    key = payload.get("task_id") or payload.get("key")
    if not key:
        return True
    writer = payload.get("writer") or event.get("actor", {}).get("id", "agent_1")
    owner = ownership.get(key)
    return owner is None or owner == writer


def _accept_all(_state: dict, _event: dict) -> bool:
    """Baseline policy: allow all writes."""
    return True


def _occ_only_allows(state: dict, event: dict) -> bool:
    """Baseline: OCC/version-style conflict check via per-key monotonic timestamps only (no ownership)."""
    return _timestamp_only_allows(state, event)


def _lease_only_allows(state: dict, event: dict) -> bool:
    """
    Baseline: lease admission proxy; reference corpus has no explicit lease fields, so temporal monotonicity only.
    In a full lease implementation, we would check lease validity windows and renewal semantics;
    here we approximate with temporal monotonicity as a proxy for lease-based temporal gating.
    """
    return _timestamp_only_allows(state, event)


def _lock_only_allows(state: dict, event: dict) -> bool:
    """
    Baseline: mutex/lock-style writer-key exclusivity (ownership) without temporal check.
    This approximates a distributed lock where only the lock holder may write;
    we use ownership as the lock state proxy. A full lock implementation would include
    lock acquisition/release semantics and timeout handling.
    """
    return _ownership_only_allows(state, event)


def _naive_lww_allows(_state: dict, _event: dict) -> bool:
    """
    Baseline: naive last-write-wins (accept all writes; no validity gate).
    This represents a system with no coordination checks beyond eventual consistency;
    all writes are accepted regardless of ownership, temporal ordering, or conflict semantics.
    """
    return True


def _infer_failure_class(sequence_name: str) -> str:
    """Infer failure class from sequence name for ablation breakdown."""
    s = sequence_name.lower()
    if "split_brain" in s or "multi_writer_contention" in s or "actor_payload" in s:
        return "split_brain"
    if "stale" in s:
        return "stale_write"
    if "reorder" in s or "unsafe_lww" in s:
        return "reorder"
    if "unknown_key" in s:
        return "unknown_key"
    return "control"


def _run_corpus_with_policy(corpus_files: list, policy: str) -> tuple[list[dict], int]:
    """Run corpus; policy in contract, timestamp_only, ownership_only, accept_all, occ_only,
    lease_only, lock_only, naive_lww. Returns (per_seq_results, total_denials)."""
    policy_fns = {
        "contract": lambda s, e: validate(s, e).verdict == ALLOW,
        "timestamp_only": _timestamp_only_allows,
        "ownership_only": _ownership_only_allows,
        "accept_all": _accept_all,
        "occ_only": _occ_only_allows,
        "lease_only": _lease_only_allows,
        "lock_only": _lock_only_allows,
        "naive_lww": _naive_lww_allows,
    }
    fn = policy_fns.get(policy)
    if not fn:
        return [], 0
    results = []
    total_denials = 0
    for path in corpus_files:
        data = json.loads(path.read_text(encoding="utf-8"))
        if "events" not in data or "expected_verdicts" not in data:
            continue
        state = dict(data["initial_state"])
        events = data["events"]
        expected = data["expected_verdicts"]
        allows = 0
        denials = 0
        for ev in events:
            ok = fn(state, ev)
            if ok:
                allows += 1
                state = apply_event_to_state(state, ev)
            else:
                denials += 1
        total_denials += denials
        results.append({"sequence": path.stem, "allows": allows, "denials": denials})
    return results, total_denials


def main() -> int:
    ap = argparse.ArgumentParser(description="P1: Contract corpus evaluation")
    ap.add_argument(
        "--out",
        type=Path,
        default=REPO / "datasets" / "runs" / "contracts_eval",
        help="Output directory for eval.json",
    )
    ap.add_argument(
        "--corpus",
        type=Path,
        default=REPO / "bench" / "contracts" / "corpus",
        help="Corpus directory",
    )
    ap.add_argument(
        "--throughput",
        action="store_true",
        help="Run corpus repeatedly and report events_per_sec",
    )
    ap.add_argument(
        "--scale",
        type=int,
        default=1000,
        help="When --throughput: number of corpus passes (default 1000)",
    )
    ap.add_argument(
        "--throughput-runs",
        type=int,
        default=5,
        help="When --throughput: number of runs for mean/stdev (default 5)",
    )
    ap.add_argument(
        "--baseline",
        action="store_true",
        help="Report violations that would be applied without validator (accept-all count)",
    )
    ap.add_argument(
        "--scale-test",
        action="store_true",
        help="Run validator on a long synthetic trace (multiple writers, reorder/delay); write scale_test.json",
    )
    ap.add_argument(
        "--scale-events",
        type=int,
        default=100_000,
        help="When --scale-test: number of events (default 100000)",
    )
    ap.add_argument(
        "--scale-test-runs",
        type=int,
        default=1,
        help="When --scale-test: number of runs for mean/stdev of throughput (default 1); use 5+ for variance",
    )
    ap.add_argument(
        "--scale-sweep",
        type=str,
        default="",
        help="Comma-separated scale sizes (e.g. 1000,10000,100000) for high-budget sweep; writes scale_sweep.json",
    )
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    if args.scale_sweep:
        sizes = [int(x.strip()) for x in args.scale_sweep.split(",") if x.strip()]
        runs_per_size = max(1, args.scale_test_runs)
        sweep_results = []
        for n_events in sizes:
            n = n_events
            total_events_per_run = n * 2
            runs_data = []
            for _ in range(runs_per_size):
                state = {"ownership": {}, "_last_ts": {}}
                t0 = time.perf_counter()
                denials = 0
                for i in range(n):
                    task_id = f"t{i % 1000}"
                    ts = 1.0 + i * 0.01
                    ev_start = {
                        "type": "task_start",
                        "ts": ts,
                        "actor": {"id": f"agent_{i % 3}"},
                        "payload": {"task_id": task_id, "name": "a", "writer": f"agent_{i % 3}"},
                    }
                    verdict = validate(state, ev_start)
                    if verdict.verdict == ALLOW:
                        state = apply_event_to_state(state, ev_start)
                    else:
                        denials += 1
                    ev_end = {
                        "type": "task_end",
                        "ts": ts + 0.005,
                        "actor": {"id": "agent_1"},
                        "payload": {"task_id": task_id, "name": "a", "writer": "agent_1"},
                    }
                    verdict = validate(state, ev_end)
                    if verdict.verdict == ALLOW:
                        state = apply_event_to_state(state, ev_end)
                    else:
                        denials += 1
                elapsed = time.perf_counter() - t0
                events_per_sec = total_events_per_run / elapsed if elapsed > 0 else 0
                time_per_write_us = elapsed * 1e6 / total_events_per_run if total_events_per_run else 0
                runs_data.append({
                    "total_time_sec": round(elapsed, 4),
                    "time_per_write_us": round(time_per_write_us, 4),
                    "events_per_sec": round(events_per_sec, 2),
                    "denials": denials,
                })
            eps_list = [r["events_per_sec"] for r in runs_data]
            tpu_list = [r["time_per_write_us"] for r in runs_data]
            sweep_results.append({
                "scale_events": n_events,
                "total_events_per_run": total_events_per_run,
                "runs": runs_per_size,
                "events_per_sec_mean": round(statistics.mean(eps_list), 2),
                "events_per_sec_stdev": round(statistics.stdev(eps_list), 2) if len(eps_list) > 1 else 0.0,
                "time_per_write_us_mean": round(statistics.mean(tpu_list), 4),
                "time_per_write_us_stdev": round(statistics.stdev(tpu_list), 4) if len(tpu_list) > 1 else 0.0,
            })
        sweep_out = {
            "scale_sweep": True,
            "sweep_results": sweep_results,
            "run_manifest": {
                "scale_sweep_sizes": sizes,
                "scale_test_runs_per_size": runs_per_size,
                "script": "contracts_eval.py",
                "script_version": SCRIPT_VERSION,
            },
        }
        (args.out / "scale_sweep.json").write_text(
            json.dumps(sweep_out, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps(sweep_out, indent=2))
        return 0

    if args.scale_test:
        n = args.scale_events
        total_events_per_run = n * 2
        runs_data = []
        for _ in range(args.scale_test_runs):
            state = {"ownership": {}, "_last_ts": {}}
            t0 = time.perf_counter()
            denials = 0
            for i in range(n):
                task_id = f"t{i % 1000}"
                ts = 1.0 + i * 0.01
                ev_start = {
                    "type": "task_start",
                    "ts": ts,
                    "actor": {"id": f"agent_{i % 3}"},
                    "payload": {"task_id": task_id, "name": "a", "writer": f"agent_{i % 3}"},
                }
                verdict = validate(state, ev_start)
                if verdict.verdict == ALLOW:
                    state = apply_event_to_state(state, ev_start)
                else:
                    denials += 1
                ev_end = {
                    "type": "task_end",
                    "ts": ts + 0.005,
                    "actor": {"id": "agent_1"},
                    "payload": {"task_id": task_id, "name": "a", "writer": "agent_1"},
                }
                verdict = validate(state, ev_end)
                if verdict.verdict == ALLOW:
                    state = apply_event_to_state(state, ev_end)
                else:
                    denials += 1
            elapsed = time.perf_counter() - t0
            events_per_sec = total_events_per_run / elapsed if elapsed > 0 else 0
            time_per_write_us = elapsed * 1e6 / total_events_per_run if total_events_per_run else 0
            runs_data.append({
                "total_time_sec": round(elapsed, 4),
                "time_per_write_us": round(time_per_write_us, 4),
                "events_per_sec": round(events_per_sec, 2),
                "denials": denials,
            })
        events_per_sec_list = [r["events_per_sec"] for r in runs_data]
        time_per_write_list = [r["time_per_write_us"] for r in runs_data]
        mean_eps = statistics.mean(events_per_sec_list)
        stdev_eps = statistics.stdev(events_per_sec_list) if len(events_per_sec_list) > 1 else 0.0
        mean_tpu = statistics.mean(time_per_write_list)
        stdev_tpu = statistics.stdev(time_per_write_list) if len(time_per_write_list) > 1 else 0.0
        rss_kb_st = None
        process_time_st = None
        if resource is not None:
            try:
                usage = resource.getrusage(resource.RUSAGE_SELF)
                process_time_st = usage.ru_utime + usage.ru_stime
                rss_kb_st = getattr(usage, "ru_maxrss", None)
            except Exception:
                pass
        cost_per_hour_st = None
        try:
            cost_per_hour_st = float(os.environ.get("LABTRUST_COST_PER_HOUR", "") or 0)
        except ValueError:
            pass
        events_per_dollar_st = (mean_eps * 3600 / cost_per_hour_st) if cost_per_hour_st and cost_per_hour_st > 0 else None
        scale_result = {
            "scale_test": True,
            "total_events": total_events_per_run,
            "denials": runs_data[0]["denials"] if runs_data else 0,
            "total_time_sec": round(runs_data[0]["total_time_sec"], 4) if runs_data else 0,
            "time_per_write_us": round(mean_tpu, 4),
            "events_per_sec": round(mean_eps, 2),
            "events_per_sec_mean": round(mean_eps, 2),
            "events_per_sec_stdev": round(stdev_eps, 2),
            "time_per_write_us_mean": round(mean_tpu, 4),
            "time_per_write_us_stdev": round(stdev_tpu, 4),
            "scale_test_runs": args.scale_test_runs,
            "run_manifest": {
                "scale_test_events": args.scale_events,
                "scale_test_runs": args.scale_test_runs,
                "script": "contracts_eval.py",
                "script_version": SCRIPT_VERSION,
            },
            "resource_and_cost": {
                "process_time_sec": round(process_time_st, 4) if process_time_st is not None else None,
                "rss_kb": rss_kb_st,
                "events_per_sec_per_core_assumption": "single-threaded (1 core)",
                "events_per_dollar": round(events_per_dollar_st, 2) if events_per_dollar_st is not None else None,
            },
        }
        (args.out / "scale_test.json").write_text(
            json.dumps(scale_result, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps(scale_result, indent=2))
        return 0

    corpus_files = sorted(args.corpus.glob("*.json"))
    results = []
    total_denials_with_validator = 0
    event_level_latencies_us: list[float] = []
    wall_clock_start = time.perf_counter()
    for path in corpus_files:
        data = json.loads(path.read_text(encoding="utf-8"))
        if "events" not in data or "expected_verdicts" not in data:
            continue
        state = dict(data["initial_state"])
        events = data["events"]
        expected = data["expected_verdicts"]
        allows = 0
        denials = 0
        actual_verdicts: list[str] = []
        seq_latencies_us: list[float] = []
        for i, ev in enumerate(events):
            t0 = time.perf_counter()
            verdict = validate(state, ev)
            elapsed_us = (time.perf_counter() - t0) * 1e6
            seq_latencies_us.append(elapsed_us)
            event_level_latencies_us.append(elapsed_us)
            actual = "allow" if verdict.verdict == ALLOW else "deny"
            actual_verdicts.append(actual)
            if verdict.verdict == ALLOW:
                allows += 1
                state = apply_event_to_state(state, ev)
            else:
                denials += 1
        n = len(events)
        total_denials_with_validator += denials
        detection_ok = actual_verdicts == expected
        total_time_us = sum(seq_latencies_us)
        results.append(
            {
                "sequence": path.stem,
                "events": n,
                "allows": allows,
                "denials": denials,
                "detection_ok": detection_ok,
                "actual_verdicts": actual_verdicts,
                "total_time_us": round(total_time_us, 2),
                "time_per_write_us": round(total_time_us / n, 2) if n else 0,
            }
        )

    corpus_sequences = [r["sequence"] for r in results]
    total_expected_denials = 0
    for path in corpus_files:
        data = json.loads(path.read_text(encoding="utf-8"))
        if "expected_verdicts" not in data:
            continue
        total_expected_denials += sum(1 for ex in data["expected_verdicts"] if ex == "deny")

    wall_clock_sec = time.perf_counter() - wall_clock_start
    total_events_eval = sum(r["events"] for r in results)
    rss_kb = None
    process_time_sec = None
    if resource is not None:
        try:
            usage = resource.getrusage(resource.RUSAGE_SELF)
            process_time_sec = usage.ru_utime + usage.ru_stime
            rss_kb = getattr(usage, "ru_maxrss", None)
            if rss_kb is not None and sys.platform != "win32":
                if sys.platform == "darwin":
                    rss_kb = rss_kb  # macOS reports bytes in some versions
                # Linux ru_maxrss is in KiB
        except Exception:
            pass
    cost_per_hour = None
    try:
        cost_per_hour = float(os.environ.get("LABTRUST_COST_PER_HOUR", "") or 0)
    except ValueError:
        pass
    events_per_sec_overall = total_events_eval / wall_clock_sec if wall_clock_sec > 0 else 0
    events_per_dollar = None
    if cost_per_hour and cost_per_hour > 0:
        events_per_dollar = (events_per_sec_overall * 3600) / cost_per_hour
    resource_and_cost = {
        "wall_clock_sec": round(wall_clock_sec, 4),
        "process_time_sec": round(process_time_sec, 4) if process_time_sec is not None else None,
        "rss_kb": rss_kb,
        "total_events_eval": total_events_eval,
        "events_per_sec_overall": round(events_per_sec_overall, 2),
        "events_per_sec_per_core_assumption": "single-threaded (1 core)",
        "cost_proxy": {
            "assumption": "LABTRUST_COST_PER_HOUR ($/hr) optional; not set" if not cost_per_hour else f"LABTRUST_COST_PER_HOUR={cost_per_hour} $/hr",
            "events_per_dollar": round(events_per_dollar, 2) if events_per_dollar is not None else None,
        },
    }

    corpus_fingerprint = hashlib.sha256(
        "".join(
            sorted(
                path.read_text(encoding="utf-8")
                for path in corpus_files
                if path.suffix == ".json"
            )
        ).encode("utf-8")
    ).hexdigest()[:16]

    out_data = {
        "corpus_eval": True,
        "sequences": results,
        "run_manifest": {
            "corpus_sequences": corpus_sequences,
            "corpus_sequence_count": len(corpus_sequences),
            "corpus_dir": str(args.corpus),
            "script": "contracts_eval.py",
            "script_version": SCRIPT_VERSION,
            "corpus_fingerprint": corpus_fingerprint,
        },
    }
    out_data["violations_denied_with_validator"] = total_denials_with_validator
    all_detection_ok = all(r.get("detection_ok", False) for r in results)
    out_data["success_criteria_met"] = {"all_detection_ok": all_detection_ok}
    if args.baseline:
        out_data["violations_would_apply_without_validator"] = total_denials_with_validator

    # Baselines and named comparators (keep per-seq results for ablation_by_class)
    ts_results, timestamp_only_denials = _run_corpus_with_policy(corpus_files, "timestamp_only")
    own_results, ownership_only_denials = _run_corpus_with_policy(corpus_files, "ownership_only")
    acc_results, accept_all_denials = _run_corpus_with_policy(corpus_files, "accept_all")
    occ_results, occ_only_denials = _run_corpus_with_policy(corpus_files, "occ_only")
    lease_results, lease_only_denials = _run_corpus_with_policy(corpus_files, "lease_only")
    lock_results, lock_only_denials = _run_corpus_with_policy(corpus_files, "lock_only")
    lww_results, naive_lww_denials = _run_corpus_with_policy(corpus_files, "naive_lww")
    out_data["baseline_timestamp_only_denials"] = timestamp_only_denials
    out_data["baseline_timestamp_only_missed"] = (
        total_denials_with_validator - timestamp_only_denials
    )
    out_data["baseline_ownership_only_denials"] = ownership_only_denials
    out_data["baseline_ownership_only_missed"] = (
        total_expected_denials - ownership_only_denials
    )
    out_data["baseline_accept_all_denials"] = accept_all_denials
    out_data["baseline_accept_all_missed"] = total_expected_denials
    out_data["baseline_occ_only_denials"] = occ_only_denials
    out_data["baseline_occ_only_missed"] = total_expected_denials - occ_only_denials
    out_data["baseline_lease_only_denials"] = lease_only_denials
    out_data["baseline_lease_only_missed"] = total_expected_denials - lease_only_denials
    out_data["baseline_lock_only_denials"] = lock_only_denials
    out_data["baseline_lock_only_missed"] = total_expected_denials - lock_only_denials
    out_data["baseline_naive_lww_denials"] = naive_lww_denials
    out_data["baseline_naive_lww_missed"] = total_expected_denials

    # Ablation: which failure classes slip through when disabling contract ingredients
    out_data["ablation"] = {
        "full_contract": {"violations_denied": total_denials_with_validator, "violations_missed": total_expected_denials - total_denials_with_validator},
        "timestamp_only": {"violations_denied": timestamp_only_denials, "violations_missed": total_expected_denials - timestamp_only_denials},
        "ownership_only": {"violations_denied": ownership_only_denials, "violations_missed": total_expected_denials - ownership_only_denials},
        "accept_all": {"violations_denied": accept_all_denials, "violations_missed": total_expected_denials},
        "occ_only": {"violations_denied": occ_only_denials, "violations_missed": total_expected_denials - occ_only_denials},
        "lease_only": {"violations_denied": lease_only_denials, "violations_missed": total_expected_denials - lease_only_denials},
        "lock_only": {"violations_denied": lock_only_denials, "violations_missed": total_expected_denials - lock_only_denials},
        "naive_lww": {"violations_denied": naive_lww_denials, "violations_missed": total_expected_denials},
    }

    # Class-level ablation: per failure class, which policy denies what
    seq_to_expected: dict[str, int] = {}
    for path in corpus_files:
        data = json.loads(path.read_text(encoding="utf-8"))
        if "expected_verdicts" not in data:
            continue
        seq_to_expected[path.stem] = sum(1 for e in data["expected_verdicts"] if e == "deny")
    seq_to_contract_denials = {r["sequence"]: r["denials"] for r in results}
    seq_to_ts_denials = {r["sequence"]: r["denials"] for r in ts_results}
    seq_to_own_denials = {r["sequence"]: r["denials"] for r in own_results}
    seq_to_acc_denials = {r["sequence"]: r["denials"] for r in acc_results}
    seq_to_occ_denials = {r["sequence"]: r["denials"] for r in occ_results}
    seq_to_lease_denials = {r["sequence"]: r["denials"] for r in lease_results}
    seq_to_lock_denials = {r["sequence"]: r["denials"] for r in lock_results}
    seq_to_lww_denials = {r["sequence"]: r["denials"] for r in lww_results}
    policy_keys = (
        "full_contract",
        "timestamp_only",
        "ownership_only",
        "accept_all",
        "occ_only",
        "lease_only",
        "lock_only",
        "naive_lww",
    )
    by_class: dict[str, dict[str, dict[str, int]]] = {}
    for seq_name, expected_den in seq_to_expected.items():
        fc = _infer_failure_class(seq_name)
        if fc not in by_class:
            by_class[fc] = {pk: {"violations_denied": 0, "violations_missed": 0} for pk in policy_keys}
        den_map = {
            "full_contract": seq_to_contract_denials.get(seq_name, 0),
            "timestamp_only": seq_to_ts_denials.get(seq_name, 0),
            "ownership_only": seq_to_own_denials.get(seq_name, 0),
            "accept_all": seq_to_acc_denials.get(seq_name, 0),
            "occ_only": seq_to_occ_denials.get(seq_name, 0),
            "lease_only": seq_to_lease_denials.get(seq_name, 0),
            "lock_only": seq_to_lock_denials.get(seq_name, 0),
            "naive_lww": seq_to_lww_denials.get(seq_name, 0),
        }
        for pk in policy_keys:
            d = den_map[pk]
            by_class[fc][pk]["violations_denied"] += d
            by_class[fc][pk]["violations_missed"] += expected_den - d
    out_data["ablation_by_class"] = by_class

    # TP/FP/FN and precision/recall (per-event; expected_verdicts = ground truth)
    tp = fp = fn = 0
    for path in corpus_files:
        data = json.loads(path.read_text(encoding="utf-8"))
        if "events" not in data or "expected_verdicts" not in data:
            continue
        state = dict(data["initial_state"])
        events = data["events"]
        expected = data["expected_verdicts"]
        for ev, exp in zip(events, expected):
            verdict = validate(state, ev)
            actual = "allow" if verdict.verdict == ALLOW else "deny"
            if exp == "deny" and actual == "deny":
                tp += 1
            elif exp == "allow" and actual == "deny":
                fp += 1
            elif exp == "deny" and actual == "allow":
                fn += 1
            if actual == "allow":
                state = apply_event_to_state(state, ev)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    out_data["detection_metrics"] = {
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }

    # Per inferred failure class (each event attributed to its sequence's class)
    all_inferred_classes: set[str] = set()
    for path in corpus_files:
        data = json.loads(path.read_text(encoding="utf-8"))
        if "events" not in data or "expected_verdicts" not in data:
            continue
        all_inferred_classes.add(_infer_failure_class(path.stem))
    class_tp: dict[str, int] = defaultdict(int)
    class_fp: dict[str, int] = defaultdict(int)
    class_fn: dict[str, int] = defaultdict(int)
    for path in corpus_files:
        data = json.loads(path.read_text(encoding="utf-8"))
        if "events" not in data or "expected_verdicts" not in data:
            continue
        fc = _infer_failure_class(path.stem)
        state = dict(data["initial_state"])
        events = data["events"]
        expected = data["expected_verdicts"]
        for ev, exp in zip(events, expected):
            verdict = validate(state, ev)
            actual = "allow" if verdict.verdict == ALLOW else "deny"
            if exp == "deny" and actual == "deny":
                class_tp[fc] += 1
            elif exp == "allow" and actual == "deny":
                class_fp[fc] += 1
            elif exp == "deny" and actual == "allow":
                class_fn[fc] += 1
            if actual == "allow":
                state = apply_event_to_state(state, ev)
    detection_by_class: dict[str, dict] = {}
    for fc in sorted(all_inferred_classes):
        ctp = class_tp[fc]
        cfp = class_fp[fc]
        cfn = class_fn[fc]
        # No expected denials in this class: recall/F1 for "detect deny" are undefined; FP still matters.
        if ctp == 0 and cfn == 0:
            prec = None if cfp == 0 else 0.0
            rec = None
            f1c = None
        else:
            prec = ctp / (ctp + cfp) if (ctp + cfp) > 0 else 0.0
            rec = ctp / (ctp + cfn) if (ctp + cfn) > 0 else 0.0
            f1c = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
        detection_by_class[fc] = {
            "true_positives": ctp,
            "false_positives": cfp,
            "false_negatives": cfn,
            "precision": None if prec is None else round(prec, 4),
            "recall": None if rec is None else round(rec, 4),
            "f1": None if f1c is None else round(f1c, 4),
        }
    out_data["detection_metrics_by_class"] = detection_by_class

    # Latency percentiles from event-level samples (not per-sequence averages)
    latency_median_us = latency_p95_us = latency_p99_us = None
    latency_median_ci95 = latency_p95_ci95 = latency_p99_ci95 = None
    if event_level_latencies_us:
        sorted_lat = sorted(event_level_latencies_us)
        n = len(sorted_lat)
        latency_median_us = round(sorted_lat[n // 2], 4)
        latency_p95_us = round(sorted_lat[min(int(0.95 * n), n - 1)], 4)
        latency_p99_us = round(sorted_lat[min(int(0.99 * n), n - 1)], 4)
        seed_bootstrap = 42
        latency_median_ci95 = [
            round(x, 4)
            for x in _bootstrap_percentile_ci(
                event_level_latencies_us, 50.0, n_bootstrap=1000, seed=seed_bootstrap
            )
        ]
        latency_p95_ci95 = [
            round(x, 4)
            for x in _bootstrap_percentile_ci(
                event_level_latencies_us, 95.0, n_bootstrap=1000, seed=seed_bootstrap
            )
        ]
        latency_p99_ci95 = [
            round(x, 4)
            for x in _bootstrap_percentile_ci(
                event_level_latencies_us, 99.0, n_bootstrap=1000, seed=seed_bootstrap
            )
        ]
    out_data["latency_percentiles_us"] = {
        "median": latency_median_us,
        "p95": latency_p95_us,
        "p99": latency_p99_us,
        "event_level_n": len(event_level_latencies_us) if event_level_latencies_us else 0,
        "median_ci95": latency_median_ci95,
        "p95_ci95": latency_p95_ci95,
        "p99_ci95": latency_p99_ci95,
    }

    # Excellence metrics (STANDARDS_OF_EXCELLENCE.md) with statistical comparisons
    n_ok = sum(1 for r in results if r.get("detection_ok", False))
    detection_rate_pct = round(100.0 * n_ok / len(results), 1) if results else 0.0
    overhead_p99_us = latency_p99_us
    
    # Statistical comparisons vs key baselines
    excellence_metrics = {
        "corpus_detection_rate_pct": detection_rate_pct,
        "overhead_p99_us": overhead_p99_us,
        "baseline_margin_denials": total_denials_with_validator - timestamp_only_denials,
    }
    
    # Add effect size and CI for key comparisons if we have per-class data
    if detection_by_class:
        # Compare full contract vs timestamp-only on split_brain (key differentiator)
        split_brain_contract = detection_by_class.get("split_brain", {})
        if split_brain_contract.get("true_positives", 0) > 0:
            excellence_metrics["split_brain_detection_advantage"] = {
                "contract_tp": split_brain_contract.get("true_positives"),
                "contract_fp": split_brain_contract.get("false_positives"),
                "contract_fn": split_brain_contract.get("false_negatives"),
            }
    
    # Add per-class uncertainty if we have multiple sequences per class
    if detection_by_class:
        for fc, metrics in detection_by_class.items():
            tp = metrics.get("true_positives", 0)
            fp = metrics.get("false_positives", 0)
            fn = metrics.get("false_negatives", 0)
            total = tp + fp + fn
            if total > 0:
                # Wilson CI for detection rate (TP / (TP + FN))
                tp_fn = tp + fn
                if tp_fn > 0:
                    detection_rate = tp / tp_fn
                    # Approximate Wilson CI (simplified)
                    z = 1.96  # 95% CI
                    n = tp_fn
                    p = detection_rate
                    denominator = 1 + (z**2 / n)
                    center = (p + (z**2 / (2 * n))) / denominator
                    margin = (z / denominator) * ((p * (1 - p) / n + z**2 / (4 * n**2)) ** 0.5)
                    excellence_metrics.setdefault("per_class_ci95", {})[fc] = {
                        "detection_rate": round(detection_rate, 4),
                        "ci95_lower": round(max(0.0, center - margin), 4),
                        "ci95_upper": round(min(1.0, center + margin), 4),
                    }
    
    out_data["excellence_metrics"] = excellence_metrics
    out_data["resource_and_cost"] = resource_and_cost

    if args.throughput:
        # Run full corpus --scale times, repeat --throughput-runs; report mean and stdev
        all_events = []
        for path in corpus_files:
            data = json.loads(path.read_text(encoding="utf-8"))
            if "events" not in data or "expected_verdicts" not in data:
                continue
            all_events.extend(data["events"])
        if not all_events:
            out_data["throughput_events_per_sec"] = 0
            out_data["throughput_events_per_sec_mean"] = 0
            out_data["throughput_events_per_sec_stdev"] = 0
            out_data["throughput_total_events"] = 0
        else:
            events_per_pass = len(all_events)
            total_events_per_run = events_per_pass * args.scale
            rates = []
            for _ in range(args.throughput_runs):
                state = {"ownership": {}, "_last_ts": {}}
                t0 = time.perf_counter()
                for _ in range(args.scale):
                    state = {"ownership": {}, "_last_ts": {}}
                    for ev in all_events:
                        verdict = validate(state, ev)
                        if verdict.verdict == ALLOW:
                            state = apply_event_to_state(state, ev)
                elapsed = time.perf_counter() - t0
                rate = total_events_per_run / elapsed if elapsed > 0 else 0
                rates.append(rate)
            mean_rate = statistics.mean(rates)
            stdev_rate = (
                statistics.stdev(rates)
                if len(rates) > 1
                else 0.0
            )
            out_data["throughput_total_events"] = total_events_per_run
            out_data["throughput_events_per_sec"] = round(mean_rate, 2)
            out_data["throughput_events_per_sec_mean"] = round(mean_rate, 2)
            out_data["throughput_events_per_sec_stdev"] = round(stdev_rate, 2)
            out_data["throughput_scale"] = args.scale
            out_data["throughput_runs"] = args.throughput_runs
    out_path = args.out / "eval.json"
    out_path.write_text(json.dumps(out_data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out_data, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
