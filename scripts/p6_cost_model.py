#!/usr/bin/env python3
"""
P6 Experiment 9: Cost model (engineering estimate).
Estimate validator compute overhead per 1k plans, trace storage cost, incremental gated-over-weak,
amortized cost per denied step. Present as operator-facing table; not definitive billing.
Usage: python scripts/p6_cost_model.py [--out-dir path]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO / "datasets" / "runs" / "llm_eval"


def main() -> int:
    ap = argparse.ArgumentParser(description="P6 cost model (engineering estimate)")
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--storage-cost-per-gb-year", type=float, default=0.023, help="Example: AWS S3 standard")
    args = ap.parse_args()

    # Read adapter_latency and baseline artifacts if present
    mean_latency_ms = 0.0
    lat_path = args.out_dir / "adapter_latency.json"
    if lat_path.exists():
        lat = json.loads(lat_path.read_text(encoding="utf-8"))
        mean_latency_ms = lat.get("tail_latency_p95_mean_ms", 0) or 0

    storage_path = args.out_dir / "p6_storage_benchmark.json"
    mean_trace_bytes = 0.0
    if storage_path.exists():
        st = json.loads(storage_path.read_text(encoding="utf-8"))
        mean_trace_bytes = st.get("mean_trace_bytes", 0) or 0

    baseline_path = args.out_dir / "baseline_comparison.json"
    denial_count_gated = 0
    if baseline_path.exists():
        bl = json.loads(baseline_path.read_text(encoding="utf-8"))
        denial_count_gated = bl.get("excellence_metrics", {}).get("denial_count_gated", 0) or 0

    plans_1k = 1000
    storage_1k_mb = (mean_trace_bytes * plans_1k) / (1024 * 1024) if mean_trace_bytes else 0
    storage_cost_1k_year = (storage_1k_mb / 1024) * args.storage_cost_per_gb_year if storage_1k_mb else 0
    # Compute: assume validator overhead is proportional to mean latency (simplified)
    validator_compute_1k_plans_sec = (mean_latency_ms / 1000.0) * plans_1k if mean_latency_ms else 0
    # Amortized cost per denied step: no dollar cost modeled, just "relative compute" and "audit size"
    table = {
        "note": "Engineering estimate only; not definitive cloud billing.",
        "mode": "gated",
        "mean_latency_ms": round(mean_latency_ms, 2),
        "relative_compute_1k_plans_sec": round(validator_compute_1k_plans_sec, 2),
        "audit_size_bytes_per_plan": round(mean_trace_bytes, 2),
        "storage_1k_plans_mb": round(storage_1k_mb, 4),
        "storage_cost_1k_plans_year_usd": round(storage_cost_1k_year, 6),
        "unsafe_denials_60_runs": denial_count_gated,
        "amortized_denials_per_run": round(denial_count_gated / 60, 2) if denial_count_gated else 0,
    }

    out_path = args.out_dir / "p6_cost_model.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(table, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
