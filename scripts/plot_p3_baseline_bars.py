#!/usr/bin/env python3
"""Bar chart: P3 baseline mean replay times (ms) from replay_eval summary.json."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_SUMMARY = REPO / "datasets" / "runs" / "replay_eval" / "summary.json"
DEFAULT_OUT = REPO / "papers" / "P3_Replay" / "figures" / "p3_baseline_mean_ms.png"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    if not args.summary.exists():
        raise SystemExit(f"Missing {args.summary}")
    data = json.loads(args.summary.read_text(encoding="utf-8"))
    bo = data.get("baseline_overhead", {})
    apply_m = bo.get("apply_only_no_hash", {}).get("mean_ms")
    final_m = bo.get("final_hash_only", {}).get("mean_ms")
    full_m = data.get("overhead_stats", {}).get("mean_ms")
    if apply_m is None or final_m is None or full_m is None:
        raise SystemExit("summary missing baseline_overhead / overhead_stats means")
    labels = ["apply-only", "final-hash-only", "full L0"]
    values = [float(apply_m), float(final_m), float(full_m)]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise SystemExit(f"matplotlib required: {exc}") from exc

    fig, ax = plt.subplots(figsize=(6.0, 3.8))
    colors = ["#7f8c8d", "#3498db", "#2e8b57"]
    x = range(len(labels))
    ax.bar(x, values, color=colors, width=0.55, edgecolor="#333", linewidth=0.6)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=12, ha="right")
    ax.set_ylabel("Mean time (ms)")
    ax.set_title("P3 baselines: mean replay time (primary thin-slice trace)")
    for i, v in enumerate(values):
        ax.text(i, v + 0.012, f"{v:.4f}", ha="center", fontsize=9, color="#222")
    ax.set_ylim(0, max(values) * 1.2)
    ax.grid(axis="y", linestyle=":", alpha=0.4)
    plt.tight_layout()
    plt.savefig(args.out, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
