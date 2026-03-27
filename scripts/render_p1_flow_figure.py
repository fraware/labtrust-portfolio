#!/usr/bin/env python3
"""Render P1 Figure 0 (coordination-admission flow) to PDF/PNG.

Writes:
  papers/P1_Contracts/figures/contracts_flow.pdf
  papers/P1_Contracts/figures/contracts_flow.png
  docs/figures/p1_contract_flow.png (mirror for docs)
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_PAPER_FIG = REPO / "papers" / "P1_Contracts" / "figures"
DEFAULT_DOCS_FIG = REPO / "docs" / "figures"


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Render P1 contract flow figure (PDF/PNG)"
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_PAPER_FIG,
        help="Directory for contracts_flow.pdf and .png",
    )
    ap.add_argument(
        "--docs-copy",
        type=Path,
        default=DEFAULT_DOCS_FIG / "p1_contract_flow.png",
        help="Optional second PNG copy for docs/figures",
    )
    args = ap.parse_args()

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import FancyBboxPatch
    except ImportError:
        print("matplotlib required: pip install matplotlib")
        return 1

    args.out_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10.2, 3.1))
    ax.set_xlim(0, 13.2)
    ax.set_ylim(0, 1)
    ax.axis("off")

    def add_box(
        x: float, y: float, w: float, h: float, text: str
    ) -> tuple[float, float, float, float]:
        p = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=0.06",
            linewidth=1.2,
            edgecolor="#1a1a1a",
            facecolor="#eef2f7",
        )
        ax.add_patch(p)
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=9)
        return (x, y, w, h)

    b_e = add_box(0.2, 0.36, 1.45, 0.36, "Trace event")
    b_s = add_box(1.95, 0.36, 1.75, 0.36, "Admitted-prefix state")
    b_v = add_box(4.0, 0.36, 2.0, 0.36, r"validate(state,event)")
    b_pred = add_box(
        6.3, 0.26, 2.1, 0.56, "Predicates:\nauthority\ntime\ntransition"
    )
    b_a = add_box(8.75, 0.60, 1.45, 0.26, "allow")
    b_d = add_box(8.75, 0.14, 1.45, 0.26, "deny + reason")
    b_apply = add_box(10.55, 0.60, 1.95, 0.26, "apply state")
    b_hold = add_box(10.55, 0.14, 1.95, 0.26, "state unchanged")

    def cx(b: tuple[float, float, float, float]) -> float:
        return b[0] + b[2] / 2

    def right(b: tuple[float, float, float, float]) -> float:
        return b[0] + b[2]

    def midy(b: tuple[float, float, float, float]) -> float:
        return b[1] + b[3] / 2

    # Arrows: event + state -> validator -> predicate stack -> allow/deny
    ax.annotate(
        "",
        xy=(b_s[0], midy(b_s)),
        xytext=(right(b_e), midy(b_e)),
        arrowprops=dict(arrowstyle="->", lw=1.2, color="#222"),
    )
    ax.annotate(
        "",
        xy=(b_v[0], midy(b_v) + 0.03),
        xytext=(right(b_s), midy(b_s)),
        arrowprops=dict(arrowstyle="->", lw=1.2, color="#222"),
    )
    ax.annotate(
        "",
        xy=(b_pred[0], midy(b_pred)),
        xytext=(right(b_v), midy(b_v)),
        arrowprops=dict(arrowstyle="->", lw=1.2, color="#222"),
    )
    # Predicate stack -> allow / deny
    vx = right(b_pred)
    ax.annotate(
        "",
        xy=(b_a[0], midy(b_a)),
        xytext=(vx, midy(b_pred) + 0.08),
        arrowprops=dict(
            arrowstyle="->", lw=1.0, color="#222", connectionstyle="arc3,rad=0"
        ),
    )
    ax.annotate(
        "",
        xy=(b_d[0], midy(b_d)),
        xytext=(vx, midy(b_pred) - 0.08),
        arrowprops=dict(
            arrowstyle="->", lw=1.0, color="#222", connectionstyle="arc3,rad=0"
        ),
    )
    ax.annotate(
        "",
        xy=(b_apply[0], midy(b_apply)),
        xytext=(right(b_a), midy(b_a)),
        arrowprops=dict(arrowstyle="->", lw=1.0, color="#222"),
    )
    ax.annotate(
        "",
        xy=(b_hold[0], midy(b_hold)),
        xytext=(right(b_d), midy(b_d)),
        arrowprops=dict(arrowstyle="->", lw=1.0, color="#222"),
    )
    ax.text(
        0.2,
        0.94,
        "Boundary semantics: identical event/state inputs imply "
        "identical verdict vectors.",
        fontsize=7,
        va="top",
        color="#444",
    )

    ax.set_title(
        "Coordination-admission flow (reference implementation)",
        fontsize=10,
        pad=10,
    )
    plt.tight_layout()

    pdf = args.out_dir / "contracts_flow.pdf"
    png = args.out_dir / "contracts_flow.png"
    plt.savefig(pdf, bbox_inches="tight", dpi=150)
    plt.savefig(png, bbox_inches="tight", dpi=150)
    plt.close()

    args.docs_copy.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(png, args.docs_copy)
    print(f"Wrote {pdf}")
    print(f"Wrote {png}")
    print(f"Wrote {args.docs_copy}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
