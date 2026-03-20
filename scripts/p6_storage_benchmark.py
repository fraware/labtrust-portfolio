#!/usr/bin/env python3
"""
P6 Experiment 8: Storage and retention benchmark.
Measure mean trace size, denial-trace size, compression ratio, storage growth estimates.
Usage: python scripts/p6_storage_benchmark.py [--out-dir path]
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO / "datasets" / "runs" / "llm_eval"


def main() -> int:
    ap = argparse.ArgumentParser(description="P6 storage/retention benchmark")
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    sizes = []
    compressed_sizes = []
    denial_trace_sizes = []
    for base in [
        args.out_dir / "adapter_runs",
        args.out_dir / "baseline_runs",
    ]:
        if not base.exists():
            continue
        for trace_path in base.rglob("trace.json"):
            try:
                raw = trace_path.read_bytes()
                sizes.append(len(raw))
                compressed_sizes.append(len(gzip.compress(raw)))
                data = json.loads(trace_path.read_text(encoding="utf-8"))
                if data.get("metadata", {}).get("denials_count", 0) > 0:
                    denial_trace_sizes.append(len(raw))
            except Exception:
                pass

    n = len(sizes)
    if n == 0:
        print("No trace.json files found. Run adapter/baseline first.", file=sys.stderr)
        out = {"mean_trace_bytes": 0, "mean_compressed_bytes": 0, "compression_ratio": 0, "samples": 0}
    else:
        mean_trace = sum(sizes) / n
        mean_compressed = sum(compressed_sizes) / n
        ratio = mean_trace / mean_compressed if mean_compressed else 0
        mean_denial = sum(denial_trace_sizes) / len(denial_trace_sizes) if denial_trace_sizes else 0
        out = {
            "samples": n,
            "mean_trace_bytes": round(mean_trace, 2),
            "mean_compressed_bytes": round(mean_compressed, 2),
            "compression_ratio": round(ratio, 4),
            "mean_denial_trace_bytes": round(mean_denial, 2) if denial_trace_sizes else None,
            "denial_trace_samples": len(denial_trace_sizes),
            "storage_estimate_1k_plans_mb": round(mean_trace * 1000 / (1024 * 1024), 4),
            "storage_estimate_10k_plans_mb": round(mean_trace * 10000 / (1024 * 1024), 4),
            "storage_estimate_100k_plans_mb": round(mean_trace * 100000 / (1024 * 1024), 4),
        }

    out_path = args.out_dir / "p6_storage_benchmark.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
