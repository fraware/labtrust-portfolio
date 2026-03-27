#!/usr/bin/env python3
"""Bar chart: corpus trace counts per evidence lane (excludes thin_slice overhead row)."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_SUMMARY = REPO / "datasets" / "runs" / "replay_eval" / "summary.json"
DEFAULT_OUT = REPO / "papers" / "P3_Replay" / "figures" / "p3_corpus_lane_counts.png"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    if not args.summary.exists():
        raise SystemExit(f"Missing {args.summary}")
    data = json.loads(args.summary.read_text(encoding="utf-8"))
    counts: Counter[str] = Counter()
    for row in data.get("per_trace", []):
        if row.get("name") == "thin_slice":
            continue
        cat = row.get("corpus_category") or "unknown"
        counts[cat] += 1
    order = ["synthetic_pass", "field_proxy", "real_ingest", "synthetic_trap"]
    labels = [c.replace("_", " ") for c in order]
    values = [counts.get(c, 0) for c in order]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise SystemExit(f"matplotlib required: {exc}") from exc

    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    colors = ["#5dade2", "#58d68d", "#f5b041", "#e74c3c"]
    x = range(len(labels))
    ax.bar(x, values, color=colors, width=0.55, edgecolor="#333", linewidth=0.6)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=15, ha="right")
    ax.set_ylabel("Trace count")
    ax.set_title("Corpus traces per evidence lane (no thin-slice anchor)")
    for i, v in enumerate(values):
        ax.text(i, v + 0.08, str(int(v)), ha="center", fontsize=10, color="#222")
    ax.set_ylim(0, max(values, default=1) + 1)
    ax.grid(axis="y", linestyle=":", alpha=0.4)
    plt.tight_layout()
    plt.savefig(args.out, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
