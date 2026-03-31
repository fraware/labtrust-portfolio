#!/usr/bin/env python3
"""
P1 Contracts async stress runner.

Interleaved event scheduling with delay/skew/reorder stressors to test
validator robustness under realistic concurrency patterns.
Writes to datasets/runs/contracts_eval/stress_results.json.
Usage:
  PYTHONPATH=impl/src python scripts/contracts_async_stress.py
    [--delay-sweep ...] [--skew-sweep ...] [--reorder-probs ...]
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import random
import statistics
import sys
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "impl" / "src"))

from labtrust_portfolio.contracts import (
    ALLOW,
    apply_event_to_state,
    validate,
    prepare_replay_state,
    finalize_event_observation,
)

SCRIPT_VERSION = "v0.1"


class AsyncEventScheduler:
    """Async scheduler with delay, skew, and reorder stressors."""

    def __init__(
        self,
        initial_state: dict,
        events: list[dict],
        delay_mean: float = 0.0,
        delay_stdev: float = 0.0,
        clock_skew: dict[str, float] | None = None,
        reorder_prob: float = 0.0,
        seed: int | None = None,
    ):
        self.state = prepare_replay_state(dict(initial_state))
        self.events = events
        self.delay_mean = delay_mean
        self.delay_stdev = delay_stdev
        self.clock_skew = clock_skew or {}
        self.reorder_prob = reorder_prob
        self.rng = random.Random(seed if seed is not None else 42)
        self.verdicts: list[dict[str, Any]] = []
        self.latencies_us: list[float] = []

    async def _apply_delay(self) -> float:
        """Apply random delay based on configured mean/stdev."""
        if self.delay_mean <= 0 and self.delay_stdev <= 0:
            return 0.0
        delay = max(0.0, self.rng.gauss(self.delay_mean, self.delay_stdev))
        await asyncio.sleep(delay)
        return delay

    def _apply_skew(self, event: dict, actor_id: str) -> dict:
        """Apply clock skew to event timestamp if configured."""
        if not self.clock_skew or actor_id not in self.clock_skew:
            return event
        skew = self.clock_skew[actor_id]
        ev_copy = dict(event)
        ev_copy["ts"] = event.get("ts", 0.0) + skew
        return ev_copy

    async def process_event(self, event: dict, index: int) -> dict:
        """Process a single event with async delay and skew."""
        actor_id = event.get("actor", {}).get("id", "agent_1")
        delay = await self._apply_delay()
        skewed_event = self._apply_skew(event, actor_id)

        t0 = time.perf_counter()
        verdict = validate(self.state, skewed_event, {})
        elapsed_us = (time.perf_counter() - t0) * 1e6
        self.latencies_us.append(elapsed_us)

        result = {
            "index": index,
            "event_type": skewed_event.get("type"),
            "verdict": verdict.verdict,
            "reason_codes": list(verdict.reason_codes),
            "latency_us": round(elapsed_us, 4),
            "delay_applied": round(delay, 6),
        }

        if verdict.verdict == ALLOW:
            self.state = apply_event_to_state(self.state, skewed_event)
        finalize_event_observation(self.state, skewed_event)

        return result

    async def run(self) -> dict:
        """Run all events with optional reordering."""
        event_indices = list(range(len(self.events)))
        if self.reorder_prob > 0 and len(self.events) > 1:
            for i in range(len(event_indices) - 1):
                if self.rng.random() < self.reorder_prob:
                    event_indices[i], event_indices[i + 1] = (
                        event_indices[i + 1],
                        event_indices[i],
                    )

        tasks = [self.process_event(self.events[idx], idx) for idx in event_indices]
        results = await asyncio.gather(*tasks)

        results.sort(key=lambda r: r["index"])
        self.verdicts = results
        return {"verdicts": results, "latencies_us": self.latencies_us, "final_state": self.state}


def _classify_profile_effect(delay: float, skew: float, reorder_prob: float) -> tuple[str, bool, str]:
    """Return (dominant_failure_class, semantically_expected, interpretation)."""
    if reorder_prob >= 0.2:
        return ("reorder_sensitive_invalidity", True, "High reorder perturbs temporal predicates; divergence is expected.")
    if skew >= 0.5:
        return ("stale_write", True, "Large clock skew perturbs timestamp admissibility; divergence is expected.")
    if delay > 0 and reorder_prob == 0 and skew == 0:
        return ("none", False, "Pure delay should preserve semantics under boundary replay.")
    return ("mixed", True, "Combined perturbations can alter replay-sensitive predicates.")


async def run_stress_sweep(
    corpus_files: list[Path],
    delay_sweep: list[float],
    skew_sweep: list[float],
    reorder_probs: list[float],
    seed: int | None = None,
) -> dict:
    """Run stress sweep across delay/skew/reorder parameters."""
    results = []
    rng = random.Random(seed if seed is not None else 42)

    for delay in delay_sweep:
        for skew in skew_sweep:
            for reorder_prob in reorder_probs:
                profile_hash = hashlib.sha256(
                    f"{delay}_{skew}_{reorder_prob}_{seed}".encode()
                ).hexdigest()[:8]

                for path in corpus_files:
                    data = json.loads(path.read_text(encoding="utf-8"))
                    if "events" not in data or "expected_verdicts" not in data:
                        continue

                    actors = set()
                    for ev in data["events"]:
                        actor_id = ev.get("actor", {}).get("id", "agent_1")
                        actors.add(actor_id)
                    clock_skew = (
                        {actor: rng.uniform(-skew, skew) for actor in actors}
                        if skew > 0
                        else {}
                    )

                    scheduler = AsyncEventScheduler(
                        initial_state=dict(data["initial_state"]),
                        events=data["events"],
                        delay_mean=delay,
                        delay_stdev=delay * 0.1 if delay > 0 else 0.0,
                        clock_skew=clock_skew,
                        reorder_prob=reorder_prob,
                        seed=rng.randint(1, 10000),
                    )

                    run_result = await scheduler.run()
                    expected = data["expected_verdicts"]
                    actual = [r["verdict"] for r in run_result["verdicts"]]
                    detection_ok = actual == expected

                    latencies = run_result["latencies_us"]
                    mean_us = round(statistics.mean(latencies), 4) if latencies else None
                    p95_us = (
                        round(sorted(latencies)[int(0.95 * len(latencies))], 4)
                        if latencies
                        else None
                    )
                    p99_us = (
                        round(sorted(latencies)[int(0.99 * len(latencies))], 4)
                        if latencies
                        else None
                    )
                    results.append(
                        {
                            "sequence": path.stem,
                            "stress_profile": {
                                "delay_mean": delay,
                                "clock_skew_max": skew,
                                "reorder_prob": reorder_prob,
                                "profile_hash": profile_hash,
                            },
                            "detection_ok": detection_ok,
                            "verdicts_match": detection_ok,
                            "latency_stats": {
                                "mean_us": mean_us,
                                "p95_us": p95_us,
                                "p99_us": p99_us,
                            },
                            "profile_semantics": {
                                "perturbed_dimensions": {
                                    "event_timestamps": skew > 0,
                                    "delivery_order": reorder_prob > 0,
                                    "processing_order": reorder_prob > 0,
                                    "replay_state_assumptions": False,
                                },
                                "dominant_failure_class": _classify_profile_effect(delay, skew, reorder_prob)[0],
                                "semantically_expected_divergence": _classify_profile_effect(delay, skew, reorder_prob)[1],
                                "interpretation": _classify_profile_effect(delay, skew, reorder_prob)[2],
                            },
                        }
                    )

    return {
        "stress_sweep": True,
        "results": results,
        "run_manifest": {
            "script": "contracts_async_stress.py",
            "script_version": SCRIPT_VERSION,
            "delay_sweep": delay_sweep,
            "skew_sweep": skew_sweep,
            "reorder_probs": reorder_probs,
            "seed": seed,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="P1: Async stress runner with delay/skew/reorder"
    )
    ap.add_argument(
        "--corpus-dir",
        type=Path,
        default=REPO / "bench" / "contracts" / "corpus",
        help="Corpus directory",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=REPO / "datasets" / "runs" / "contracts_eval",
        help="Output directory",
    )
    ap.add_argument(
        "--delay-sweep",
        type=str,
        default="0,0.001,0.01",
        help=(
            "Comma-separated delay means in seconds "
            "(default: 0,0.001,0.01)"
        ),
    )
    ap.add_argument(
        "--skew-sweep",
        type=str,
        default="0,0.1,0.5",
        help=(
            "Comma-separated max clock skew in seconds "
            "(default: 0,0.1,0.5)"
        ),
    )
    ap.add_argument(
        "--reorder-probs",
        type=str,
        default="0,0.1,0.2",
        help=(
            "Comma-separated reorder probabilities "
            "(default: 0,0.1,0.2)"
        ),
    )
    ap.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility",
    )
    args = ap.parse_args()
    
    delay_sweep = [float(x.strip()) for x in args.delay_sweep.split(",") if x.strip()]
    skew_sweep = [float(x.strip()) for x in args.skew_sweep.split(",") if x.strip()]
    reorder_probs = [float(x.strip()) for x in args.reorder_probs.split(",") if x.strip()]

    corpus_files = (
        sorted(args.corpus_dir.glob("*.json")) if args.corpus_dir.exists() else []
    )

    result = asyncio.run(
        run_stress_sweep(
            corpus_files,
            delay_sweep,
            skew_sweep,
            reorder_probs,
            args.seed,
        )
    )

    args.out.mkdir(parents=True, exist_ok=True)
    out_path = args.out / "stress_results.json"
    out_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
