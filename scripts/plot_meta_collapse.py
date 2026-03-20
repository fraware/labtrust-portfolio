#!/usr/bin/env python3
"""
Plot P8 Meta: tasks_completed or collapse rate vs drop_prob from
collapse_sweep.json. Uncertainty: 95% t-interval for mean tasks_completed per
drop_prob; Wilson 95% for collapse rate. Output:
docs/figures/p8_meta_collapse.png.

Usage:
  PYTHONPATH=impl/src python scripts/plot_meta_collapse.py [--sweep path]
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_SWEEP = REPO / "datasets" / "runs" / "meta_eval" / "collapse_sweep.json"
DEFAULT_OUT = REPO / "docs" / "figures" / "p8_meta_collapse.png"


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Plot P8 collapse sweep: tasks_completed vs drop_prob",
    )
    ap.add_argument(
        "--sweep",
        type=Path,
        default=DEFAULT_SWEEP,
        help="collapse_sweep.json path",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help="Output PNG path",
    )
    args = ap.parse_args()

    if not args.sweep.exists():
        print(
            f"Error: {args.sweep} not found. "
            "Run scripts/meta_collapse_sweep.py first."
        )
        return 1

    sys.path.insert(0, str(REPO / "impl" / "src"))
    from labtrust_portfolio.stats import (
        mean_ci95_student_t,
        wilson_ci_binomial,
    )

    data = json.loads(args.sweep.read_text(encoding="utf-8"))
    per_run = data.get("per_run", [])
    if not per_run:
        print("Error: no per_run in collapse_sweep.json.")
        return 1

    by_drop: dict[float, list[int]] = {}
    for r in per_run:
        d = r.get("drop_prob")
        if d is not None:
            tc = int(r.get("tasks_completed", 0))
            by_drop.setdefault(float(d), []).append(tc)
    drop_probs = sorted(by_drop.keys())
    means = []
    mean_err_lo = []
    mean_err_hi = []
    for d in drop_probs:
        vals = by_drop[d]
        n = len(vals)
        m = sum(vals) / n
        sd = statistics.stdev(vals) if n > 1 else 0.0
        lo, hi = mean_ci95_student_t(m, sd, n)
        means.append(m)
        mean_err_lo.append(max(0.0, m - lo))
        mean_err_hi.append(max(0.0, hi - m))

    collapse_rates = []
    collapse_err_lo = []
    collapse_err_hi = []
    for d in drop_probs:
        runs_d = [
            r
            for r in per_run
            if r.get("drop_prob") is not None and float(r["drop_prob"]) == d
        ]
        n = len(runs_d)
        collapsed_n = sum(1 for r in runs_d if r.get("collapsed"))
        rate = collapsed_n / n if n else 0.0
        w_lo, w_hi = wilson_ci_binomial(collapsed_n, n)
        collapse_rates.append(rate)
        collapse_err_lo.append(max(0.0, rate - w_lo))
        collapse_err_hi.append(max(0.0, w_hi - rate))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax1 = plt.subplots()
        ax1.errorbar(
            drop_probs,
            means,
            yerr=[mean_err_lo, mean_err_hi],
            fmt="o-",
            color="C0",
            capsize=3,
            elinewidth=1,
        )
        ax1.set_xlabel("drop_completion_prob")
        ax1.set_ylabel("tasks_completed (mean, 95% t-CI)", color="C0")
        ax1.tick_params(axis="y", labelcolor="C0")
        ax2 = ax1.twinx()
        ax2.errorbar(
            drop_probs,
            collapse_rates,
            yerr=[collapse_err_lo, collapse_err_hi],
            fmt="s--",
            color="C1",
            capsize=3,
            elinewidth=1,
        )
        ax2.set_ylabel("collapse rate (Wilson 95% CI)", color="C1")
        ax2.tick_params(axis="y", labelcolor="C1")
        rm = data.get("run_manifest") or {}
        scen = data.get("scenario_id") or rm.get("scenario_id", "")
        title = "P8 Meta: tasks_completed and collapse rate vs drop_prob"
        if scen:
            title = f"{title} ({scen})"
        ax1.set_title(title)
        plt.tight_layout()
        plt.savefig(args.out, dpi=150)
        plt.close()
        print(f"Wrote {args.out}")
    except ImportError:
        out_data = {
            "drop_probs": drop_probs,
            "tasks_completed_mean": means,
            "tasks_completed_ci95_half_width_lower": mean_err_lo,
            "tasks_completed_ci95_half_width_upper": mean_err_hi,
            "collapse_rate": collapse_rates,
            "collapse_rate_wilson_half_width_lower": collapse_err_lo,
            "collapse_rate_wilson_half_width_upper": collapse_err_hi,
            "scenario_id": data.get("scenario_id"),
        }
        json_path = args.out.with_suffix(".json")
        text = json.dumps(out_data, indent=2) + "\n"
        json_path.write_text(text, encoding="utf-8")
        print(
            f"matplotlib not installed. Wrote {json_path} for external plotting."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
