#!/usr/bin/env python3
"""
Plot P2 REP-CPS: tasks_completed by policy from rep_cps_eval summary.json.
Outputs:
  - docs/figures/p2_rep_cps_tasks.png — global means with 95% CI for the mean (not stdev bars).
  - docs/figures/p2_rep_cps_tasks_per_scenario.png — faceted per-scenario bars (scheduling slice visible).
Usage: PYTHONPATH=impl/src python scripts/plot_rep_cps_summary.py [--summary path] [--out path]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_SUMMARY = REPO / "datasets" / "runs" / "rep_cps_eval" / "summary.json"
DEFAULT_OUT = REPO / "docs" / "figures" / "p2_rep_cps_tasks.png"
DEFAULT_PER_SCENARIO_OUT = REPO / "docs" / "figures" / "p2_rep_cps_tasks_per_scenario.png"


def _ci_yerr(mean: float, ci95: list[float] | None) -> tuple[float, float]:
    """Asymmetric error bar lengths for matplotlib bar(yerr=[[lows],[highs]])."""
    if not ci95 or len(ci95) != 2 or any(math.isnan(x) for x in ci95):
        return (0.0, 0.0)
    lo, hi = float(ci95[0]), float(ci95[1])
    return (max(0.0, mean - lo), max(0.0, hi - mean))


def _plot_global_tasks(data: dict, out: Path) -> bool:
    policies: list[str] = []
    means: list[float] = []
    err_lo: list[float] = []
    err_hi: list[float] = []
    spec = [
        ("rep_cps_tasks_completed_mean", "rep_cps_tasks_completed_ci95", "REP-CPS"),
        ("centralized_tasks_completed_mean", "centralized_tasks_completed_ci95", "Centralized"),
        ("rep_cps_naive_tasks_completed_mean", "rep_cps_naive_tasks_completed_ci95", "Naive-in-loop"),
        ("rep_cps_unsecured_tasks_completed_mean", "rep_cps_unsecured_tasks_completed_ci95", "Unsecured"),
    ]
    for mean_key, ci_key, label in spec:
        m = data.get(mean_key)
        if m is None:
            continue
        mean_f = float(m)
        policies.append(label)
        means.append(mean_f)
        el, eh = _ci_yerr(mean_f, data.get(ci_key))
        err_lo.append(el)
        err_hi.append(eh)

    if not policies:
        delay_sweep = data.get("delay_sweep", [])
        if delay_sweep:
            policies = [f"d={r.get('delay_fault_prob', '?')}" for r in delay_sweep]
            means = [
                float(r.get("rep_cps_tasks_mean", r.get("rep_cps_tasks_completed_mean", 0)))
                for r in delay_sweep
            ]
            err_lo = [0.0] * len(means)
            err_hi = [0.0] * len(means)
        else:
            return False

    out.parent.mkdir(parents=True, exist_ok=True)
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8.0, 4.5))
    x = range(len(policies))
    yerr = [err_lo, err_hi] if any(e > 0 for e in err_lo + err_hi) else None
    ax.bar(x, means, yerr=yerr, capsize=4, color=["#1f77b4", "#7f7f7f", "#ff7f0e", "#d62728"][: len(policies)])
    ax.set_xticks(list(x))
    ax.set_xticklabels(policies, rotation=15, ha="right")
    ax.set_ylabel("tasks_completed (mean)")
    ax.set_title("P2 REP-CPS: global tasks_completed by policy (95% CI for mean)")
    fig.text(
        0.5,
        0.02,
        "Error bars: 95% confidence interval for the mean (t-interval), not stdev.",
        ha="center",
        fontsize=8,
        style="italic",
    )
    plt.tight_layout(rect=(0, 0.06, 1, 1))
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"Wrote {out}")
    return True


def _plot_per_scenario(data: dict, out: Path) -> bool:
    per = data.get("per_scenario") or []
    if not per:
        return False
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    scenarios = [p.get("scenario_id", "?") for p in per]
    n = len(scenarios)
    policies_labels = ["REP-CPS", "Naive", "Unsecured", "Centralized"]
    colors = ["#1f77b4", "#ff7f0e", "#d62728", "#7f7f7f"]
    fig, axes = plt.subplots(1, n, figsize=(max(10, 3.2 * n), 4.2), squeeze=False)
    for i, ps in enumerate(per):
        ax = axes[0][i]
        sid = ps.get("scenario_id", "?")
        rows = [
            (
                ps.get("rep_cps_tasks_mean"),
                ps.get("rep_cps_tasks_ci95"),
                "REP-CPS",
            ),
            (
                ps.get("naive_in_loop_tasks_mean"),
                ps.get("naive_in_loop_tasks_ci95"),
                "Naive",
            ),
            (
                ps.get("unsecured_tasks_mean"),
                None,
                "Unsecured",
            ),
            (
                ps.get("centralized_tasks_mean"),
                None,
                "Centralized",
            ),
        ]
        means = []
        yerr = [[], []]
        labels = []
        color_by_label = dict(zip(policies_labels, colors))
        cols = []
        for mean_v, ci_k, lab in rows:
            if mean_v is None:
                continue
            m = float(mean_v)
            means.append(m)
            labels.append(lab)
            if isinstance(ci_k, (list, tuple)) and len(ci_k) == 2:
                el, eh = _ci_yerr(m, list(ci_k))
            else:
                stdev_k = {
                    "Naive": ps.get("naive_in_loop_tasks_stdev"),
                    "Unsecured": ps.get("unsecured_tasks_stdev"),
                    "Centralized": ps.get("centralized_tasks_stdev"),
                    "REP-CPS": ps.get("rep_cps_tasks_stdev"),
                }.get(lab)
                if stdev_k is not None and float(stdev_k) > 0:
                    el = eh = float(stdev_k)
                else:
                    el = eh = 0.0
            yerr[0].append(el)
            yerr[1].append(eh)
            cols.append(color_by_label.get(lab, "#1f77b4"))
        xb = range(len(means))
        ye = yerr if any(sum(yerr, [])) else None
        ax.bar(xb, means, yerr=ye, capsize=3, color=cols)
        ax.set_xticks(list(xb))
        ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=8)
        short = sid if len(sid) <= 28 else sid[:25] + "..."
        ax.set_title(short, fontsize=9)
        ax.set_ylabel("tasks (mean)" if i == 0 else "")
    fig.suptitle(
        "Per-scenario tasks_completed: parity vs scheduling-dependent divergence",
        fontsize=11,
    )
    fig.text(
        0.5,
        0.02,
        "REP-CPS vs naive vs unsecured vs centralized; CI where present in summary.",
        ha="center",
        fontsize=8,
        style="italic",
    )
    plt.tight_layout(rect=(0, 0.08, 1, 0.94))
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"Wrote {out}")
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description="Plot P2 REP-CPS tasks_completed by policy")
    ap.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY, help="summary.json path")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output PNG (global policy chart)")
    ap.add_argument(
        "--per-scenario-out",
        type=Path,
        default=DEFAULT_PER_SCENARIO_OUT,
        help="Output PNG (per-scenario faceted chart)",
    )
    ap.add_argument("--skip-per-scenario", action="store_true", help="Only emit global chart")
    args = ap.parse_args()

    if not args.summary.exists():
        print(f"Error: {args.summary} not found. Run scripts/rep_cps_eval.py first.")
        return 1

    data = json.loads(args.summary.read_text(encoding="utf-8"))
    try:
        if not _plot_global_tasks(data, args.out):
            print("Error: no adapter or delay_sweep data in summary.")
            return 1
        if not args.skip_per_scenario:
            _plot_per_scenario(data, args.per_scenario_out)
    except ImportError:
        print("matplotlib not installed.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
