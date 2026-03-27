#!/usr/bin/env python3
"""
Publication PNG for P3 Figure 0: replay levels and pipeline (matplotlib).
Mirrors docs/figures/p3_replay_levels_diagram.mmd without Mermaid CLI.
"""
from __future__ import annotations

import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO / "papers" / "P3_Replay" / "figures" / "p3_replay_levels_diagram.png"


def main() -> int:
    ap = argparse.ArgumentParser(description="Export P3 replay levels diagram PNG")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    except ImportError as exc:
        raise SystemExit(f"matplotlib required: {exc}") from exc

    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(9.5, 4.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")

    def box(x, y, w, h, text, fc="#e8f4fc", ec="#2c5aa0"):
        r = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            linewidth=1.2,
            edgecolor=ec,
            facecolor=fc,
        )
        ax.add_patch(r)
        ax.text(
            x + w / 2,
            y + h / 2,
            text,
            ha="center",
            va="center",
            fontsize=9,
            wrap=True,
        )

    def arrow(x1, y1, x2, y2):
        ax.add_patch(
            FancyArrowPatch(
                (x1, y1),
                (x2, y2),
                arrowstyle="-|>",
                mutation_scale=12,
                linewidth=1.0,
                color="#444",
            )
        )

    ax.text(
        1.0,
        4.55,
        "Replay levels",
        fontsize=10,
        fontweight="bold",
        color="#1a1a1a",
    )
    box(0.3, 3.15, 2.6, 0.95, "L0: control-plane\nreplay", "#e8f4fc")
    box(3.2, 3.15, 2.6, 0.95, "L1: + recorded\nobservations", "#eef8ee")
    box(
        6.1,
        3.15,
        2.6,
        0.95,
        "L2: hardware-assisted\n(aspirational)",
        "#f5f0f0",
    )

    ax.text(
        1.0,
        2.55,
        "Pipeline",
        fontsize=10,
        fontweight="bold",
        color="#1a1a1a",
    )
    box(0.3, 1.25, 1.7, 0.75, "Trace", "#fff8e6")
    box(2.4, 1.25, 1.9, 0.75, "Replay\nengine", "#fff8e6")
    box(4.8, 1.25, 1.9, 0.75, "state_hash\ncheck", "#fff8e6")
    box(7.2, 1.25, 1.7, 0.75, "Diagnostics", "#fff8e6")

    arrow(2.0, 1.625, 2.35, 1.625)
    arrow(4.3, 1.625, 4.75, 1.625)
    arrow(6.7, 1.625, 7.15, 1.625)

    ax.text(
        5.0,
        0.35,
        (
            "L0 is evaluated in this paper; L1 is partial; "
            "L2 is design-only."
        ),
        ha="center",
        fontsize=8.5,
        color="#555",
    )
    plt.tight_layout()
    plt.savefig(args.out, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
