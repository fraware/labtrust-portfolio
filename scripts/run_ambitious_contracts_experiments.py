#!/usr/bin/env python3
"""Orchestrate ambitious P1 evaluation: full parity, stress multi-seed, summary."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def main() -> int:
    out = REPO / "datasets" / "runs" / "contracts_ambitious"
    out.mkdir(parents=True, exist_ok=True)
    py = sys.executable

    # 1) Full-corpus transport parity (54 sequences)
    subprocess.run(
        [
            py,
            str(REPO / "scripts" / "contracts_transport_parity.py"),
            "--all-sequences",
            "--out",
            str(out),
        ],
        check=True,
        cwd=str(REPO),
    )

    # 2) Benchmark eval with throughput + scale in one eval.json (last wins for eval fields)
    subprocess.run(
        [
            py,
            str(REPO / "scripts" / "contracts_eval.py"),
            "--out",
            str(out),
            "--corpus",
            str(REPO / "bench" / "contracts" / "corpus"),
            "--throughput",
            "--scale",
            "50000",
            "--throughput-runs",
            "25",
        ],
        check=True,
        cwd=str(REPO),
    )

    # 3) Long synthetic scale (separate artifact; does not overwrite eval.json)
    subprocess.run(
        [
            py,
            str(REPO / "scripts" / "contracts_eval.py"),
            "--out",
            str(out),
            "--scale-test",
            "--scale-events",
            "5000000",
            "--scale-test-runs",
            "6",
        ],
        check=True,
        cwd=str(REPO),
    )

    # 3b) External / quasi-real corpus (recursive family subdirs)
    cr_out = out / "contracts_real_eval"
    cr_out.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            py,
            str(REPO / "scripts" / "contracts_eval.py"),
            "--out",
            str(cr_out),
            "--corpus",
            str(REPO / "datasets" / "contracts_real"),
            "--corpus-recursive",
        ],
        check=True,
        cwd=str(REPO),
    )

    # 4) Full-grid stress: multiple seeds (27 profiles x 54 seq = 1458 results per seed)
    stress_dir = out / "stress_full_grid"
    stress_dir.mkdir(parents=True, exist_ok=True)
    seeds = list(range(1, 11))
    summary = []
    for seed in seeds:
        subprocess.run(
            [
                py,
                str(REPO / "scripts" / "contracts_async_stress.py"),
                "--corpus-dir",
                str(REPO / "bench" / "contracts" / "corpus"),
                "--out",
                str(stress_dir),
                "--delay-sweep",
                "0,0.001,0.01",
                "--skew-sweep",
                "0,0.1,0.5",
                "--reorder-probs",
                "0,0.1,0.2",
                "--seed",
                str(seed),
            ],
            check=True,
            cwd=str(REPO),
        )
        data = json.loads((stress_dir / "stress_results.json").read_text(encoding="utf-8"))
        results = data.get("results", [])
        ok = sum(1 for r in results if r.get("detection_ok"))
        total = len(results)
        rate = ok / total if total else 0.0
        summary.append({"seed": seed, "detection_ok_rate": rate, "total_runs": total})
        (stress_dir / f"stress_results_seed_{seed}.json").write_text(
            json.dumps(data, indent=2) + "\n", encoding="utf-8"
        )

    (stress_dir / "multi_seed_summary.json").write_text(
        json.dumps({"stress_full_grid": True, "seeds": summary}, indent=2) + "\n",
        encoding="utf-8",
    )

    # 5) Aggregate summary for the run folder
    parity = json.loads((out / "transport_parity.json").read_text(encoding="utf-8"))
    eval_path = out / "eval.json"
    eval_data = json.loads(eval_path.read_text(encoding="utf-8")) if eval_path.exists() else {}
    scale_path = out / "scale_test.json"
    scale_data = json.loads(scale_path.read_text(encoding="utf-8")) if scale_path.exists() else {}
    cr_eval_path = out / "contracts_real_eval" / "eval.json"
    cr_eval = json.loads(cr_eval_path.read_text(encoding="utf-8")) if cr_eval_path.exists() else {}

    rates = [s["detection_ok_rate"] for s in summary]
    mean_r = sum(rates) / len(rates) if rates else 0.0
    var = sum((x - mean_r) ** 2 for x in rates) / len(rates) if rates else 0.0

    top = {
        "output_dir": str(out),
        "parity": {
            "parity_ok_all": parity.get("parity_ok_all"),
            "n_sequences": len(parity.get("per_sequence", [])),
            "total_events": parity.get("parity_confidence", {}).get("total_events_checked"),
            "parity_rate": parity.get("parity_confidence", {}).get("parity_rate"),
        },
        "benchmark": {
            "all_detection_ok": eval_data.get("success_criteria_met", {}).get("all_detection_ok"),
            "detection_metrics": eval_data.get("detection_metrics"),
            "throughput_events_per_sec_mean": eval_data.get("throughput_events_per_sec_mean"),
            "throughput_scale": eval_data.get("throughput_scale"),
            "throughput_runs": eval_data.get("throughput_runs"),
        },
        "scale_test": {
            "events_per_sec_mean": scale_data.get("events_per_sec_mean"),
            "scale_test_events": scale_data.get("run_manifest", {}).get("scale_test_events"),
            "scale_test_runs": scale_data.get("scale_test_runs"),
            "total_events_per_run": scale_data.get("total_events"),
        },
        "contracts_real_eval": {
            "corpus_sequence_count": cr_eval.get("run_manifest", {}).get("corpus_sequence_count"),
            "corpus_recursive": cr_eval.get("run_manifest", {}).get("corpus_recursive"),
            "all_detection_ok": cr_eval.get("success_criteria_met", {}).get("all_detection_ok"),
            "detection_metrics": cr_eval.get("detection_metrics"),
            "excellence_corpus_detection_rate_pct": cr_eval.get("excellence_metrics", {}).get(
                "corpus_detection_rate_pct"
            ),
            "eval_path": str(cr_eval_path) if cr_eval_path.exists() else None,
        },
        "stress_full_grid": {
            "n_seeds": len(summary),
            "mean_detection_ok_rate": round(mean_r, 6),
            "stdev_detection_ok_rate": round(var**0.5, 6),
            "min_rate": round(min(rates), 6) if rates else None,
            "max_rate": round(max(rates), 6) if rates else None,
        },
    }
    (out / "ambitious_experiment_summary.json").write_text(
        json.dumps(top, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(top, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
