#!/usr/bin/env python3
"""
Generate a P3 first-divergence localization timeline figure.

The figure shows committed vs replayed state-hash tracks, highlights the first
divergence, shades the witness slice, and de-emphasizes downstream events.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_SUMMARY = REPO / "datasets" / "runs" / "replay_eval" / "summary.json"
DEFAULT_OUT = (
    REPO / "papers" / "P3_Replay" / "figures" / "p3_first_divergence_timeline.png"
)
DEFAULT_TRACE_NAME = "mixed_failure_trap"


def _short_hash(value: str | None) -> str:
    if not value:
        return "n/a"
    return f"{value[:8]}...{value[-8:]}"


def _load_trace_row(summary: dict, trace_name: str) -> dict:
    for row in summary.get("per_trace", []):
        if row.get("name") == trace_name:
            return row
    raise SystemExit(f"Trace {trace_name!r} not found in summary")


def _load_trace_json(trace_name: str) -> dict:
    trace_path = REPO / "bench" / "replay" / "corpus" / f"{trace_name}_trace.json"
    if not trace_path.exists():
        raise SystemExit(f"Trace JSON not found: {trace_path}")
    return json.loads(trace_path.read_text(encoding="utf-8"))


def _recompute_hashes(trace: dict) -> list[str]:
    from labtrust_portfolio.replay import apply_event
    from labtrust_portfolio.trace import state_hash

    state: dict = {}
    replayed: list[str] = []
    for ev in trace.get("events", []):
        state = apply_event(state, ev)
        replayed.append(state_hash(state))
    return replayed


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Export P3 first-divergence localization timeline figure"
    )
    ap.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    ap.add_argument("--trace-name", default=DEFAULT_TRACE_NAME)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    if not args.summary.exists():
        raise SystemExit(f"Missing summary: {args.summary}")

    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    row = _load_trace_row(summary, args.trace_name)
    trace = _load_trace_json(args.trace_name)
    replayed_hashes = _recompute_hashes(trace)
    events = trace.get("events", [])
    if not events:
        raise SystemExit(f"Trace {args.trace_name!r} has no events")

    expected_hashes = [ev.get("state_hash_after", "") for ev in events]
    seqs = [int(ev["seq"]) for ev in events]
    divergence_seq = row.get("divergence_at_seq")
    if divergence_seq is None:
        raise SystemExit(
            f"Trace {args.trace_name!r} has no divergence_at_seq; choose a trap trace"
        )

    witness_slice = row.get("witness_slice", [])
    witness_seqs = [int(ev["seq"]) for ev in witness_slice] if witness_slice else [divergence_seq]
    witness_min = min(witness_seqs)
    witness_max = max(witness_seqs)
    div_idx = seqs.index(divergence_seq)
    expected_div = expected_hashes[div_idx]
    replayed_div = replayed_hashes[div_idx]

    sidecar = {
        "trace_name": args.trace_name,
        "divergence_seq": divergence_seq,
        "witness_seq_min": witness_min,
        "witness_seq_max": witness_max,
        "expected_hash": expected_div,
        "replayed_hash": replayed_div,
        "event_types": [ev.get("type", "") for ev in events],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.with_suffix(".json").write_text(
        json.dumps(sidecar, indent=2) + "\n",
        encoding="utf-8",
    )

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.lines import Line2D
    except ImportError as exc:
        raise SystemExit(
            f"matplotlib is required to generate the PNG asset: {exc}"
        )

    fig, ax = plt.subplots(figsize=(11, 4.8))

    y_expected = 1.0
    y_replayed = 0.0
    ax.axvspan(
        witness_min - 0.5,
        witness_max + 0.5,
        color="#e6f0ff",
        alpha=0.85,
        zorder=0,
    )

    for i, seq in enumerate(seqs):
        if seq < divergence_seq:
            color = "#2e8b57"
            alpha = 1.0
        elif seq == divergence_seq:
            color = "#c0392b"
            alpha = 1.0
        else:
            color = "#9aa0a6"
            alpha = 0.65

        ax.plot(
            [seq, seq],
            [y_replayed, y_expected],
            color=color,
            alpha=0.25,
            linewidth=1.0,
            zorder=1,
        )
        ax.scatter(seq, y_expected, color=color, s=90, marker="s", alpha=alpha, zorder=3)
        ax.scatter(seq, y_replayed, color=color, s=90, marker="o", alpha=alpha, zorder=3)

        event_label = events[i].get("type", "")
        short_event = (
            event_label.replace("coordination_message", "coord_msg")
            .replace("task_start", "start")
            .replace("task_end", "end")
        )
        ax.text(
            seq,
            -0.33,
            short_event,
            rotation=35,
            ha="right",
            va="top",
            fontsize=8,
            color="#444",
        )

    ax.annotate(
        f"first divergence\nseq={divergence_seq}",
        xy=(divergence_seq, y_expected),
        xytext=(divergence_seq + 0.55, 1.42),
        arrowprops={"arrowstyle": "->", "linewidth": 1.2, "color": "#c0392b"},
        fontsize=10,
        color="#8e2d21",
        ha="left",
    )

    ax.text(
        divergence_seq + 0.55,
        1.08,
        f"expected: {_short_hash(expected_div)}",
        fontsize=9,
        color="#8e2d21",
        ha="left",
    )
    ax.text(
        divergence_seq + 0.55,
        0.92,
        f"replayed: {_short_hash(replayed_div)}",
        fontsize=9,
        color="#8e2d21",
        ha="left",
    )
    ax.text(
        witness_min - 0.45,
        1.58,
        "witness slice",
        fontsize=9,
        color="#2c5aa0",
        ha="left",
        va="center",
    )
    ax.text(
        divergence_seq + 1.25,
        0.42,
        "downstream events are de-emphasized\nafter first contract violation",
        fontsize=9,
        color="#666",
        ha="left",
        va="center",
    )

    ax.set_title("P3 replay: first-divergence localization timeline", fontsize=13)
    ax.set_xlabel("Event sequence (seq)")
    ax.set_xlim(min(seqs) - 0.7, max(seqs) + 1.4)
    ax.set_ylim(-0.55, 1.75)
    ax.set_yticks([y_replayed, y_expected])
    ax.set_yticklabels(["replayed hash", "committed hash"])
    ax.grid(axis="x", linestyle=":", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    legend = [
        Line2D(
            [0],
            [0],
            marker="s",
            color="w",
            label="hash match",
            markerfacecolor="#2e8b57",
            markersize=9,
        ),
        Line2D(
            [0],
            [0],
            marker="s",
            color="w",
            label="first mismatch",
            markerfacecolor="#c0392b",
            markersize=9,
        ),
        Line2D(
            [0],
            [0],
            marker="s",
            color="w",
            label="downstream event",
            markerfacecolor="#9aa0a6",
            markersize=9,
        ),
    ]
    ax.legend(
        handles=legend,
        loc="lower left",
        frameon=False,
        ncol=3,
        bbox_to_anchor=(0.0, 1.02),
    )

    plt.tight_layout()
    plt.savefig(args.out, dpi=180, bbox_inches="tight")
    plt.close()
    print(f"Wrote {args.out}")
    print(f"Wrote {args.out.with_suffix('.json')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
