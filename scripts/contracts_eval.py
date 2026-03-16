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
import json
import statistics
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "impl" / "src"))

from labtrust_portfolio.contracts import validate, apply_event_to_state, ALLOW


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


def _run_corpus_with_policy(corpus_files: list, policy: str) -> tuple[list[dict], int]:
    """Run corpus; policy in ('contract', 'timestamp_only'). Returns (per_seq_results, total_denials)."""
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
            if policy == "contract":
                verdict = validate(state, ev)
                ok = verdict.verdict == ALLOW
            else:
                ok = _timestamp_only_allows(state, ev)
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
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

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
    for path in corpus_files:
        data = json.loads(path.read_text(encoding="utf-8"))
        if "events" not in data or "expected_verdicts" not in data:
            continue
        state = dict(data["initial_state"])
        events = data["events"]
        expected = data["expected_verdicts"]
        allows = 0
        denials = 0
        t0 = time.perf_counter()
        for i, ev in enumerate(events):
            verdict = validate(state, ev)
            if verdict.verdict == ALLOW:
                allows += 1
                state = apply_event_to_state(state, ev)
            else:
                denials += 1
        elapsed = time.perf_counter() - t0
        n = len(events)
        total_denials_with_validator += denials
        results.append(
            {
                "sequence": path.stem,
                "events": n,
                "allows": allows,
                "denials": denials,
                "detection_ok": denials == sum(1 for e in expected if e == "deny"),
                "total_time_us": round(elapsed * 1e6, 2),
                "time_per_write_us": round(elapsed * 1e6 / n, 2) if n else 0,
            }
        )

    corpus_sequences = [r["sequence"] for r in results]
    out_data = {
        "corpus_eval": True,
        "sequences": results,
        "run_manifest": {
            "corpus_sequences": corpus_sequences,
            "corpus_sequence_count": len(corpus_sequences),
            "corpus_dir": str(args.corpus),
            "script": "contracts_eval.py",
        },
    }
    out_data["violations_denied_with_validator"] = total_denials_with_validator
    all_detection_ok = all(r.get("detection_ok", False) for r in results)
    out_data["success_criteria_met"] = {"all_detection_ok": all_detection_ok}
    if args.baseline:
        out_data["violations_would_apply_without_validator"] = total_denials_with_validator

    # Timestamp-only baseline (no ownership): comparison to another consistency approach
    _, timestamp_only_denials = _run_corpus_with_policy(corpus_files, "timestamp_only")
    out_data["baseline_timestamp_only_denials"] = timestamp_only_denials
    out_data["baseline_timestamp_only_missed"] = (
        total_denials_with_validator - timestamp_only_denials
    )

    # Excellence metrics (STANDARDS_OF_EXCELLENCE.md)
    n_ok = sum(1 for r in results if r.get("detection_ok", False))
    detection_rate_pct = round(100.0 * n_ok / len(results), 1) if results else 0.0
    times_us = [r.get("time_per_write_us", 0) for r in results if "time_per_write_us" in r]
    overhead_p99_us = None
    if times_us:
        sorted_times = sorted(times_us)
        p99_idx = min(int(0.99 * len(sorted_times)), len(sorted_times) - 1) if len(sorted_times) > 1 else 0
        overhead_p99_us = round(sorted_times[p99_idx], 2)
    out_data["excellence_metrics"] = {
        "corpus_detection_rate_pct": detection_rate_pct,
        "overhead_p99_us": overhead_p99_us,
        "baseline_margin_denials": total_denials_with_validator - timestamp_only_denials,
    }

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
