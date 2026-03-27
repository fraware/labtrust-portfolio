#!/usr/bin/env python3
"""
Plot P2 REP-CPS: wall time (latency) by policy from rep_cps_eval summary.json.
Bars show the mean; upper whiskers extend to p95 (one-sided tail), not symmetric uncertainty.
Output: docs/figures/p2_rep_cps_latency.png
Usage: PYTHONPATH=impl/src python scripts/plot_rep_cps_latency.py [--summary path] [--out path]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_SUMMARY = REPO / "datasets" / "runs" / "rep_cps_eval" / "summary.json"
DEFAULT_OUT = REPO / "docs" / "figures" / "p2_rep_cps_latency.png"


def main() -> int:
    ap = argparse.ArgumentParser(description="Plot P2 REP-CPS latency by policy")
    ap.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY, help="summary.json path")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output PNG path")
    args = ap.parse_args()

    if not args.summary.exists():
        print(f"Error: {args.summary} not found. Run scripts/rep_cps_eval.py first.")
        return 1

    data = json.loads(args.summary.read_text(encoding="utf-8"))
    lc = data.get("latency_cost", {})
    if not lc:
        print("Error: no latency_cost in summary. Re-run rep_cps_eval.py (with adapter runs).")
        return 1

    policies = ["REP-CPS", "Naive-in-loop", "Unsecured", "Centralized"]
    means = [
        lc.get("wall_sec_rep_cps_mean"),
        lc.get("wall_sec_naive_mean"),
        lc.get("wall_sec_unsecured_mean"),
        lc.get("wall_sec_centralized_mean"),
    ]
    p95s = [
        lc.get("wall_sec_rep_cps_p95"),
        lc.get("wall_sec_naive_p95"),
        lc.get("wall_sec_unsecured_p95"),
        lc.get("wall_sec_centralized_p95"),
    ]
    valid = [m is not None for m in means]
    if not any(valid):
        print("Error: no wall_sec_*_mean in latency_cost.")
        return 1
    means_f = [float(m) if m is not None else 0.0 for m in means]
    p95s_f = [float(p) if p is not None else 0.0 for p in p95s]
    # Asymmetric error: lower 0, upper (p95 - mean) — upper tail, not a CI.
    err_lo = [0.0] * 4
    err_hi = [max(0.0, p95s_f[i] - means_f[i]) for i in range(4)]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(8.0, 4.5))
        x = range(len(policies))
        yerr = [err_lo, err_hi] if any(e > 0 for e in err_hi) else None
        ax.bar(
            x,
            means_f,
            yerr=yerr,
            capsize=4,
            color=["#1f77b4", "#ff7f0e", "#d62728", "#7f7f7f"],
        )
        ax.set_xticks(list(x))
        ax.set_xticklabels(policies, rotation=15, ha="right")
        ax.set_ylabel("Wall time (s)")
        ax.set_title("P2 REP-CPS: run latency by policy (mean + upper tail to p95)")
        fig.text(
            0.5,
            0.02,
            "Whiskers: one-sided extent from mean to empirical p95 per policy (not a confidence interval).",
            ha="center",
            fontsize=8,
            style="italic",
        )
        plt.tight_layout(rect=(0, 0.08, 1, 1))
        plt.savefig(args.out, dpi=150)
        plt.close()
        print(f"Wrote {args.out}")
    except ImportError:
        out_data = {"policies": policies, "means": means_f, "p95s": p95s_f}
        json_path = args.out.with_suffix(".json")
        json_path.write_text(json.dumps(out_data, indent=2) + "\n", encoding="utf-8")
        print(f"matplotlib not installed. Wrote {json_path} for external plotting.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
