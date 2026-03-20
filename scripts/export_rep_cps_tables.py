#!/usr/bin/env python3
"""
Export P2 REP-CPS generated tables from summary.json.
Writes papers/P2_REP-CPS/generated_tables.md with Table 1-7 from the artifact.
Usage: python scripts/export_rep_cps_tables.py [--summary path] [--out path]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_SUMMARY = REPO / "datasets" / "runs" / "rep_cps_eval" / "summary.json"
DEFAULT_OUT = REPO / "papers" / "P2_REP-CPS" / "generated_tables.md"


def _round(v, ndigits=2):
    if v is None:
        return "—"
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return round(float(v), ndigits) if ndigits is not None else v
    return v


def main() -> int:
    ap = argparse.ArgumentParser(description="Export P2 tables from summary.json")
    ap.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY, help="summary.json path")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output markdown path (default: papers/P2_REP-CPS/generated_tables.md)")
    args = ap.parse_args()

    if not args.summary.exists():
        print(f"Error: {args.summary} not found. Run scripts/rep_cps_eval.py first.")
        return 1

    data = json.loads(args.summary.read_text(encoding="utf-8"))
    rm = data.get("run_manifest", {})
    seed_count = rm.get("seed_count", 0)
    scenario_ids = rm.get("scenario_ids", [])

    agg = data.get("aggregation_under_compromise", {})
    tc_mean = data.get("rep_cps_tasks_completed_mean")
    tc_stdev = data.get("rep_cps_tasks_completed_stdev")
    agg_load_rep = data.get("rep_cps_naive_aggregate_load_mean")  # same as rep for auth
    agg_load_unsec = data.get("rep_cps_unsecured_aggregate_load_mean")

    lines = [
        "# Generated tables for P2 (P2_REP-CPS)",
        "",
        "**How to read:** Table 1 compares adapter policies; Table 2 aggregation under compromise; Table 3 baselines; Table 4 convergence (optional); Table 5 latency/cost; Table 6 profile ablation; Table 7 resilience envelope. Source: `datasets/runs/rep_cps_eval/summary.json`. Run manifest (seeds, scenario_ids, delay_fault_prob_sweep, script) in that file. Publishable default: 20 seeds.",
        "",
        "## From rep_cps_eval.py and summary.json",
        "",
        f"**Table 1 — Adapter comparison (source: summary.json).** REP-CPS vs Centralized vs naive-in-loop vs unsecured; {seed_count} seeds (publishable default), scenarios {', '.join(scenario_ids)}.",
        "",
        "| Policy | tasks_completed_mean | tasks_stdev | aggregate_load (in-loop) |",
        "|--------|----------------------|-------------|---------------------------|",
    ]
    tc_s = _round(tc_stdev, 2)
    lines.append(f"| REP-CPS (trimmed, auth) | {_round(tc_mean, 2)} | {tc_s} | {_round(agg_load_rep, 2)} |")
    lines.append(f"| Naive-in-loop (mean, auth) | {_round(data.get('rep_cps_naive_tasks_completed_mean'), 2)} | {_round(data.get('rep_cps_naive_tasks_completed_stdev'), 2)} | {_round(agg_load_rep, 2)} |")
    lines.append(f"| Unsecured (mean, no auth, compromised) | {_round(data.get('rep_cps_unsecured_tasks_completed_mean'), 2)} | {_round(data.get('rep_cps_unsecured_tasks_completed_stdev'), 2)} | {_round(agg_load_unsec, 2)} |")
    lines.append(f"| Centralized | {_round(data.get('centralized_tasks_completed_mean'), 2)} | {_round(data.get('centralized_tasks_completed_stdev'), 2)} | — |")
    lines.extend(["", ""])

    lines.extend([
        "**Table 2 — Aggregation under compromise (offline; source: summary.json aggregation_under_compromise).** Robust aggregation reduces observed compromise-induced bias relative to naive averaging.",
        "",
        "| Metric | Value |",
        "|--------|--------|",
        f"| honest_only_aggregate | {_round(agg.get('honest_only_aggregate'), 2)} |",
        f"| with_compromise_robust_aggregate | {_round(agg.get('with_compromise_robust_aggregate'), 2)} (trimmed mean) |",
        f"| with_compromise_naive_aggregate | {_round(agg.get('with_compromise_naive_aggregate'), 2)} (plain mean) |",
        "| unsecured_aggregate | same as naive (all updates) |",
        f"| bias_robust | {_round(agg.get('bias_robust'), 2)} |",
        f"| bias_naive | {_round(agg.get('bias_naive'), 2)} |",
        "", "",
    ])

    lines.extend([
        "**Table 3 — Baselines.**",
        "",
        "| Policy | Auth | Aggregation | Aggregate bias (under compromise) |",
        "|--------|------|-------------|------------------------------------|",
        f"| REP-CPS (robust) | yes | trimmed_mean | bias_robust ({_round(agg.get('bias_robust'), 2)}) |",
        f"| Naive-in-loop | yes | mean | bias_naive ({_round(agg.get('bias_naive'), 2)}) |",
        "| Unsecured | no (all agents) | mean | same as naive |",
        "", "",
    ])

    steps = data.get("aggregation_steps", 1)
    if steps > 1:
        lines.extend([
            "**Table 4 — Convergence under multi-step aggregation.**",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| aggregation_steps | {steps} |",
            f"| convergence_achieved_rate | {data.get('convergence_achieved_rate', '—')} |",
            f"| steps_to_convergence_mean | {data.get('convergence_steps_to_convergence_mean', '—')} |",
            f"| steps_to_convergence_stdev | {data.get('convergence_steps_to_convergence_stdev', '—')} |",
            "", "",
        ])
    else:
        lines.extend([
            "**Table 4 — Convergence under multi-step aggregation (when aggregation_steps > 1).** Source: summary.json after `rep_cps_eval.py --aggregation-steps 5`. Export: `python scripts/export_rep_cps_convergence_table.py`.",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            "| aggregation_steps | 1 (default); use --aggregation-steps 5 for convergence table |",
            "| convergence_achieved_rate | from summary.json |",
            "| steps_to_convergence_mean | from summary.json |",
            "| steps_to_convergence_stdev | from summary.json |",
            "", "",
        ])

    lc = data.get("latency_cost", {})
    if lc:
        lines.extend([
            "**Table 5 — Latency and cost (source: summary.json latency_cost).** Wall time per run (sec) and aggregation compute time (ms); overhead vs centralized baseline.",
            "",
            "| Policy / metric | Mean (s) | p95 (s) | Overhead vs centralized (ms) |",
            "|------------------|----------|---------|-------------------------------|",
            f"| REP-CPS | {lc.get('wall_sec_rep_cps_mean', '—')} | {lc.get('wall_sec_rep_cps_p95', '—')} | {lc.get('policy_overhead_vs_centralized_ms_rep_cps', '—')} |",
            f"| Naive-in-loop | {lc.get('wall_sec_naive_mean', '—')} | {lc.get('wall_sec_naive_p95', '—')} | {lc.get('policy_overhead_vs_centralized_ms_naive', '—')} |",
            f"| Unsecured | {lc.get('wall_sec_unsecured_mean', '—')} | {lc.get('wall_sec_unsecured_p95', '—')} | {lc.get('policy_overhead_vs_centralized_ms_unsecured', '—')} |",
            f"| Centralized | {lc.get('wall_sec_centralized_mean', '—')} | {lc.get('wall_sec_centralized_p95', '—')} | 0 |",
            "",
            "| Aggregation compute | Mean (ms) | p95 (ms) | p99 (ms) |",
            "|----------------------|-----------+----------|----------|",
            f"| aggregate() (trimmed_mean) | {lc.get('aggregation_compute_ms_mean', '—')} | {lc.get('aggregation_compute_ms_p95', '—')} | {lc.get('aggregation_compute_ms_p99', '—')} |",
            "", "",
        ])

    ablation = data.get("profile_ablation", [])
    lines.extend([
        "**Table 6 — Profile ablation (source: summary.json profile_ablation).** Each row disables one profile component; bias and aggregate vs honest-only.",
        "",
        "| Variant | Description | Bias | Aggregate | Failure |",
        "|---------|-------------|------|-----------+---------|",
    ])
    for row in ablation:
        v = row.get("variant", "")
        desc = (row.get("description") or "")[:45]
        b = _round(row.get("bias"), 4)
        a = _round(row.get("aggregate"), 4)
        f = row.get("failure")
        f_str = "yes" if f is True else ("no" if f is False else "—")
        lines.append(f"| {v} | {desc} | {b} | {a} | {f_str} |")
    lines.extend(["", ""])

    sg = data.get("safety_gate_denial", {})
    campaign = sg.get("safety_gate_campaign", {})
    if campaign:
        lines.extend([
            "**Safety-gate campaign (source: summary.json safety_gate_denial).** Pass/deny counts from adapter runs; denial when aggregate exceeds threshold.",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| denial_trace_recorded | {sg.get('denial_trace_recorded', '—')} |",
            f"| pass_count_rep_cps | {campaign.get('pass_count_rep_cps', '—')} |",
            f"| deny_count_rep_cps | {campaign.get('deny_count_rep_cps', '—')} |",
            f"| deny_count_unsecured | {campaign.get('deny_count_unsecured', '—')} |",
            f"| total_runs | {campaign.get('total_runs', '—')} |",
            "", "",
        ])

    env_res = data.get("resilience_envelope", {})
    if env_res:
        lines.extend([
            "**Table 7 — Resilience envelope (source: summary.json resilience_envelope).** Safe operating region and failure boundary from compromise/magnitude/trim sweeps.",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| bias_threshold | {env_res.get('bias_threshold', '—')} |",
            f"| safe_operating_region_n_compromised_max | {env_res.get('safe_operating_region_n_compromised_max', '—')} |",
            f"| failure_boundary_n_compromised | {env_res.get('failure_boundary_n_compromised', '—')} |",
            f"| magnitude_sweep robust beats naive | {env_res.get('magnitude_sweep_robust_beats_naive', '—')} |",
            f"| trim_sweep robust beats naive | {env_res.get('trim_sweep_robust_beats_naive', '—')} |",
            "", "",
        ])

    lines.extend([
        "Regenerate: `python scripts/rep_cps_eval.py --scenarios lab_profile_v0` (writes summary.json). Tables: `python scripts/export_rep_cps_tables.py`. Latency/cost: in summary.json latency_cost; Table 5. Resilience: summary.json resilience_envelope, magnitude_sweep, trim_fraction_sweep. For convergence: `python scripts/rep_cps_eval.py --aggregation-steps 5` then `python scripts/export_rep_cps_convergence_table.py`. See DRAFT.md repro block and RESULTS_PER_PAPER.md.",
        "",
    ])

    out_text = "\n".join(lines)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(out_text, encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
