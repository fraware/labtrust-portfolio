#!/usr/bin/env python3
"""Generate P1 figures from eval artifacts.

Outputs:
  - docs/figures/p1_latency_percentiles.png (+ .json sidecar)
  - docs/figures/p1_comparator_heatmap.png (+ .json sidecar)
  - docs/figures/p1_corpus_coverage.png (+ .json sidecar)
  - docs/figures/p1_stress_summary.png (+ .json sidecar, if stress exists)
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
DEFAULT_EVAL = REPO / "datasets" / "runs" / "contracts_eval" / "eval.json"
DEFAULT_OUT = REPO / "docs" / "figures"

POLICY_ORDER = (
    "full_contract",
    "timestamp_only",
    "ownership_only",
    "occ_only",
    "lease_only",
    "lock_only",
    "naive_lww",
    "accept_all",
)


def _classify_sequence(name: str) -> str:
    if name in {
        "actor_payload_writer_mismatch",
        "cross_key_interleaved_race",
        "delayed_release_reassignment",
        "concurrent_controller_race",
    }:
        return "adversarial"
    if name.startswith("good_"):
        return "control"
    if "split_brain" in name:
        return "split_brain"
    if "stale" in name:
        return "stale_write"
    if "reorder" in name:
        return "reorder"
    if "unknown" in name:
        return "unknown_key"
    return "other"


def plot_latency(eval_path: Path, out_dir: Path) -> dict[str, Any] | None:
    data = json.loads(eval_path.read_text(encoding="utf-8"))
    lat = data.get("latency_percentiles_us")
    if not lat:
        return None
    out_png = out_dir / "p1_latency_percentiles.png"
    meta = {
        "source": str(eval_path),
        "latency_percentiles_us": lat,
    }
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        (out_dir / "p1_latency_percentiles.json").write_text(
            json.dumps(meta, indent=2), encoding="utf-8"
        )
        print("matplotlib missing; wrote JSON only for latency.")
        return meta

    labels = ["median", "p95", "p99"]
    vals = [lat["median"], lat["p95"], lat["p99"]]
    yerr_low = [vals[i] - lat[f"{labels[i]}_ci95"][0] for i in range(3)]
    yerr_high = [lat[f"{labels[i]}_ci95"][1] - vals[i] for i in range(3)]
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(5.0, 3.2))
    ax.bar(
        x,
        vals,
        width=0.55,
        color="#2c5282",
        edgecolor="#1a365d",
        yerr=[yerr_low, yerr_high],
        capsize=4,
    )
    for i, v in enumerate(vals):
        ax.text(i, v + max(yerr_high) * 0.08, f"{v:.1f}", ha="center", va="bottom", fontsize=8)
    ax.set_xticks(x)
    tick_labels = [
        (
            f"{lb}\n"
            f"({lat[lb + '_ci95'][0]:.1f}--"
            f"{lat[lb + '_ci95'][1]:.1f})"
        )
        for lb in labels
    ]
    ax.set_xticklabels(tick_labels, fontsize=8)
    ax.set_ylabel("Latency (microseconds)")
    n_ev = lat.get("event_level_n", "?")
    ax.set_title(
        f"Event-level latency (bootstrap 95% CI)\nSingle-process trace replay; n={n_ev} events"
    )
    plt.tight_layout()
    plt.savefig(out_png, dpi=150)
    plt.close()
    (out_dir / "p1_latency_percentiles.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8"
    )
    print(f"Wrote {out_png}")
    return meta


def plot_heatmap(eval_path: Path, out_dir: Path) -> dict[str, Any] | None:
    data = json.loads(eval_path.read_text(encoding="utf-8"))
    abc = data.get("ablation_by_class")
    if not abc:
        return None
    # Rows: failure classes (exclude control where baseline accounting can produce negative misses via over-rejection)
    classes = []
    for fc in sorted(abc.keys()):
        if fc == "control":
            continue
        classes.append(fc)
    policies = [p for p in POLICY_ORDER if any(p in abc[c] for c in classes)]
    mat = []
    for fc in classes:
        row = []
        for pol in policies:
            cell = abc[fc].get(pol, {})
            missed = cell.get("violations_missed", 0)
            if missed < 0:
                missed = 0.0
            row.append(float(missed))
        mat.append(row)
    meta = {
        "source": str(eval_path),
        "classes": classes,
        "policies": policies,
        "missed_matrix": mat,
    }
    out_png = out_dir / "p1_comparator_heatmap.png"
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        (out_dir / "p1_comparator_heatmap.json").write_text(
            json.dumps(meta, indent=2), encoding="utf-8"
        )
        print("matplotlib missing; wrote JSON only for heatmap.")
        return meta

    arr = np.array(mat)
    fig, ax = plt.subplots(
        figsize=(max(9.0, len(policies) * 0.9), max(3.5, len(classes) * 0.55))
    )
    vmax = max(arr.max(), 1.0)
    im = ax.imshow(arr, aspect="auto", cmap="YlOrRd", vmin=0, vmax=vmax)
    ax.set_xticks(range(len(policies)))
    ax.set_xticklabels(policies, rotation=35, ha="right", fontsize=8)
    ax.set_yticks(range(len(classes)))
    ax.set_yticklabels(classes, fontsize=9)
    ax.set_title(
        "Violations missed by policy and failure class (lower is better)\n"
        "Control class handled separately due to over-rejection accounting"
    )
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            val = int(arr[i, j]) if float(arr[i, j]).is_integer() else arr[i, j]
            ax.text(j, i, f"{val}", ha="center", va="center", fontsize=7, color="#111")
    fig.colorbar(im, ax=ax, label="Missed violations")
    plt.tight_layout()
    plt.savefig(out_png, dpi=150)
    plt.close()
    (out_dir / "p1_comparator_heatmap.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8"
    )
    print(f"Wrote {out_png}")
    return meta


def plot_corpus_coverage(eval_path: Path, out_dir: Path) -> dict[str, Any] | None:
    data = json.loads(eval_path.read_text(encoding="utf-8"))
    sequences = data.get("sequences", [])
    if not sequences:
        return None
    buckets: dict[str, int] = {}
    for s in sequences:
        name = s.get("sequence", "")
        cat = _classify_sequence(name)
        buckets[cat] = buckets.get(cat, 0) + 1
    order = ["control", "split_brain", "stale_write", "reorder", "unknown_key", "adversarial", "other"]
    cats = [c for c in order if c in buckets]
    if not cats:
        cats = sorted(buckets.keys())
    counts = [buckets[c] for c in cats]
    meta = {
        "source": str(eval_path),
        "buckets": buckets,
        "total_sequences": len(sequences),
    }
    out_png = out_dir / "p1_corpus_coverage.png"
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        (out_dir / "p1_corpus_coverage.json").write_text(
            json.dumps(meta, indent=2), encoding="utf-8"
        )
        print("matplotlib missing; wrote JSON only for corpus coverage.")
        return meta

    fig, ax = plt.subplots(figsize=(6.0, 3.5))
    ax.bar(cats, counts, color="#4a5568", edgecolor="#2d3748")
    ax.set_ylabel("Sequence count")
    ax.set_title(
        "Benchmark corpus coverage by coarse family "
        "(sequence-name/metadata heuristic)"
    )
    fig.autofmt_xdate()
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(out_png, dpi=150)
    plt.close()
    (out_dir / "p1_corpus_coverage.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8"
    )
    print(f"Wrote {out_png}")
    return meta


def plot_stress(stress_path: Path, out_dir: Path) -> dict[str, Any] | None:
    if not stress_path.exists():
        return None
    stress_data = json.loads(stress_path.read_text(encoding="utf-8"))
    results = stress_data.get("results", [])
    if not results:
        return None
    profile_stats: dict[str, dict[str, int]] = {}
    for r in results:
        profile = r.get("stress_profile", {})
        key = (
            f"d={profile.get('delay_mean', 0):.2g},"
            f"sk={profile.get('clock_skew_max', 0):.2g},"
            f"ro={profile.get('reorder_prob', 0):.2g}"
        )
        if key not in profile_stats:
            profile_stats[key] = {"total": 0, "ok": 0}
        profile_stats[key]["total"] += 1
        if r.get("detection_ok"):
            profile_stats[key]["ok"] += 1
    labels = list(sorted(profile_stats.keys()))
    rates = [
        100.0 * profile_stats[k]["ok"] / profile_stats[k]["total"]
        if profile_stats[k]["total"]
        else 0.0
        for k in labels
    ]
    totals = sum(v["total"] for v in profile_stats.values())
    meta = {
        "source": str(stress_path),
        "profiles": profile_stats,
        "total_profiled_runs": totals,
    }
    out_png = out_dir / "p1_stress_summary.png"
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        (out_dir / "p1_stress_summary.json").write_text(
            json.dumps(meta, indent=2), encoding="utf-8"
        )
        return meta

    fig, ax = plt.subplots(
        figsize=(7.0, max(3.0, len(labels) * 0.35))
    )
    y = range(len(labels))
    ax.barh(list(y), rates, color="#744210", edgecolor="#4a3728")
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=7)
    ax.set_xlabel("Detection OK rate (%)")
    ax.set_title(
        "Async stress: detection_ok rate by stress profile\n"
        "Profiles encode delay (d), skew (sk), reorder probability (ro)"
    )
    plt.tight_layout()
    plt.savefig(out_png, dpi=150)
    plt.close()
    (out_dir / "p1_stress_summary.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8"
    )
    print(f"Wrote {out_png}")
    return meta


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Plot P1 paper figures from eval.json"
    )
    ap.add_argument("--eval", type=Path, default=DEFAULT_EVAL, help="Path to eval.json")
    ap.add_argument(
        "--stress",
        type=Path,
        default=None,
        help=(
            "Path to stress_results.json "
            "(default: eval parent / stress_results.json)"
        ),
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help="Output directory for PNG/JSON",
    )
    args = ap.parse_args()
    if not args.eval.exists():
        print(f"Missing {args.eval}; run contracts_eval.py first.")
        return 1
    args.out.mkdir(parents=True, exist_ok=True)
    stress_path = (
        args.stress
        if args.stress is not None
        else args.eval.parent / "stress_results.json"
    )
    plot_latency(args.eval, args.out)
    plot_heatmap(args.eval, args.out)
    plot_corpus_coverage(args.eval, args.out)
    plot_stress(stress_path, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
