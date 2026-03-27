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
        "**How to read:** Table 1 compares adapter policies; Table 2 aggregation under compromise; Table 3 baselines; Table 4 convergence (optional); Table 5 latency/cost; Table 6 profile ablation; Table 7 resilience envelope; scheduling-dependent eval and threat-evidence blocks (when present) summarize `rep_cps_scheduling_v0` and micro-harness rows from summary.json. Source: `datasets/runs/rep_cps_eval/summary.json`. Run manifest (seeds, scenario_ids, delay_fault_prob_sweep, script) in that file. Publishable default: 20 seeds; scenarios include `rep_cps_scheduling_v0`.",
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
            "|----------------------|-----------|----------|----------|",
            f"| aggregate() (trimmed_mean) | {lc.get('aggregation_compute_ms_mean', '—')} | {lc.get('aggregation_compute_ms_p95', '—')} | {lc.get('aggregation_compute_ms_p99', '—')} |",
            "", "",
        ])

    ablation = data.get("profile_ablation", [])
    lines.extend([
        "**Table 6 — Profile ablation (source: summary.json profile_ablation).** Each row disables one profile component; bias and aggregate vs honest-only.",
        "",
        "| Variant | Description | Bias | Aggregate | Failure |",
        "|---------|-------------|------|-----------|---------|",
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
    sched = data.get("scheduling_dependent_eval")
    if sched:
        lines.extend([
            "**Scheduling-dependent scenario (source: summary.json scheduling_dependent_eval).** Task-level outcome when the safety gate blocks scheduling under duplicate-sender spoof stress (`rep_cps_scheduling_v0`).",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| scenario_id | {sched.get('scenario_id', '—')} |",
            f"| rep_cps_tasks_mean | {_round(sched.get('rep_cps_tasks_mean'), 2)} |",
            f"| naive_in_loop_tasks_mean | {_round(sched.get('naive_in_loop_tasks_mean'), 2)} |",
            f"| centralized_tasks_mean | {_round(sched.get('centralized_tasks_mean'), 2)} |",
            f"| rep_beats_naive_tasks | {sched.get('rep_beats_naive_tasks', '—')} |",
            "", "",
        ])

    fr = data.get("freshness_replay_evidence", {})
    if fr:
        lines.extend([
            "**Threat evidence — freshness and replay burst (summary.json freshness_replay_evidence).** Micro-harness for max_age_sec and rate_limit (not a live replay engine).",
            "",
            "| Check | Value |",
            "|-------|-------|",
            f"| stale_value_dropped_by_max_age | {fr.get('stale_value_dropped_by_max_age', '—')} |",
            f"| mean_with_freshness_window | {fr.get('mean_with_freshness_window', '—')} |",
            f"| rate_limit_reduces_replay_influence | {fr.get('rate_limit_reduces_replay_influence', '—')} |",
            "", "",
        ])

    sv = data.get("sybil_vs_spoofing_evidence", {})
    if sv:
        lines.extend([
            "**Threat evidence — sybil vs spoofing (summary.json sybil_vs_spoofing_evidence).** Sybil: many distinct fake agent ids; spoofing: duplicate sender id with poison value.",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| sybil_robust_beats_naive | {sv.get('sybil_robust_beats_naive', '—')} |",
            f"| spoof_robust_beats_naive | {sv.get('spoof_robust_beats_naive', '—')} |",
            f"| spoof_naive_aggregate_exceeds_gate_2 | {sv.get('spoof_naive_aggregate_exceeds_gate_2', '—')} |",
            "", "",
        ])

    msg_sim = data.get("messaging_sim", {})
    if msg_sim:
        lines.extend([
            "**Threat evidence — messaging simulation (summary.json messaging_sim).** Ordered delivery simulation: duplicate and reorder handling (synthetic message ordering only; not a deployed bus or ROS/OPC UA path).",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| duplicate_delivery_mean | {_round(msg_sim.get('duplicate_delivery_mean'), 4)} |",
            f"| duplicate_delivery_trimmed_mean | {_round(msg_sim.get('duplicate_delivery_trimmed_mean'), 4)} |",
            f"| reordered_same_multiset_mean | {_round(msg_sim.get('reordered_same_multiset_mean'), 4)} |",
            "", "",
        ])

    dyn_series = data.get("dynamic_aggregation_series", {})
    if dyn_series:
        lines.extend([
            "**Threat evidence — dynamic aggregation series (summary.json dynamic_aggregation_series).** Multi-tick synthetic series: growing sybil count per tick (offline).",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| honest_only_trimmed_baseline | {_round(dyn_series.get('honest_only_trimmed_baseline'), 4)} |",
            f"| max_trim_bias_drift_across_ticks | {_round(dyn_series.get('max_trim_bias_drift_across_ticks'), 4)} |",
            f"| trim_bias_drift_area | {_round(dyn_series.get('trim_bias_drift_area'), 4)} |",
            f"| trim_bias_persistence_ticks_gt_1 | {_round(dyn_series.get('trim_bias_persistence_ticks_gt_1'), 4)} |",
            f"| temporal_series_kind | {dyn_series.get('temporal_series_kind', '—')} |",
            "", "",
        ])
        steps = dyn_series.get("steps", [])
        if steps:
            lines.extend([
                "| Tick | n_compromised | trimmed_mean | naive_mean | bias_trim_vs_honest_only |",
                "|------|---------------|--------------|------------|--------------------------|",
            ])
            for step in steps[:10]:  # Limit to first 10 for readability
                lines.append(
                    f"| {step.get('tick', '—')} | {step.get('n_compromised', '—')} | "
                    f"{_round(step.get('trimmed_mean'), 4)} | {_round(step.get('naive_mean'), 4)} | "
                    f"{_round(step.get('bias_trim_vs_honest_only'), 4)} |"
                )
            if len(steps) > 10:
                lines.append(f"| ... | ({len(steps) - 10} more rows) | | | |")
            lines.extend(["", ""])

    per_scenario = data.get("per_scenario", [])
    if per_scenario:
        lines.extend([
            "**Per-scenario summary (source: summary.json per_scenario).** Aggregated metrics per scenario across all delay/drop combinations.",
            "",
            "| Scenario | REP-CPS mean | REP stdev | Naive mean | Naive stdev | Unsecured mean | Centralized mean |",
            "|----------|-------------|-----------|------------|-------------|----------------|------------------|",
        ])
        for ps in per_scenario:
            sid = ps.get("scenario_id", "—")
            rep_mean = _round(ps.get("rep_cps_tasks_mean"), 2)
            rep_stdev = _round(ps.get("rep_cps_tasks_stdev"), 2)
            naive_m = _round(ps.get("naive_in_loop_tasks_mean"), 2)
            naive_s = _round(ps.get("naive_in_loop_tasks_stdev"), 2)
            unsec_m = _round(ps.get("unsecured_tasks_mean"), 2)
            cen_mean = _round(ps.get("centralized_tasks_mean"), 2)
            lines.append(
                f"| {sid} | {rep_mean} | {rep_stdev} | {naive_m} | {naive_s} | {unsec_m} | {cen_mean} |"
            )
        lines.extend(["", ""])

    variants = data.get("aggregation_variants", [])
    if variants:
        lines.extend([
            "**Offline aggregation comparators (source: summary.json aggregation_variants).** Same honest+compromised multiset as Table 2; robust operators vs plain mean.",
            "",
            "| method | bias vs honest trimmed | beats_naive_mean |",
            "|--------|-------------------------|------------------|",
        ])
        for v in variants:
            lines.append(
                f"| {v.get('method', '—')} | {_round(v.get('bias'), 4)} | {v.get('beats_naive_mean', '—')} |"
            )
        lines.extend(["", ""])

    ocb = data.get("offline_comparator_baselines", {})
    if ocb:
        classes = ocb.get("comparator_classes", {})
        robust_cls = ", ".join(classes.get("robust_statistical", [])) if isinstance(classes, dict) else "—"
        heuristic_cls = ", ".join(classes.get("practical_heuristic", [])) if isinstance(classes, dict) else "—"
        lines.extend([
            "**Offline comparator baselines (source: summary.json offline_comparator_baselines).** Includes honest-range clamp heuristic (oracle bounds strawman).",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| bias_naive_mean | {_round(ocb.get('bias_naive_mean'), 4)} |",
            f"| honest_range_clamped_bias_vs_honest_trimmed | {_round(ocb.get('honest_range_clamped_bias_vs_honest_trimmed'), 4)} |",
            f"| honest_range_clamped_beats_naive_mean | {ocb.get('honest_range_clamped_beats_naive_mean', '—')} |",
            f"| robust_statistical_comparators | {robust_cls or '—'} |",
            f"| practical_heuristic_comparators | {heuristic_cls or '—'} |",
            f"| selection_rationale | {ocb.get('selection_rationale', '—')} |",
            "", "",
        ])

    excellence = data.get("excellence_metrics", {})
    if excellence and any(k in excellence for k in ["difference_mean", "difference_ci95", "paired_t_p_value"]):
        lines.extend([
            "**Comparison statistics (source: summary.json excellence_metrics).** Paired comparison metrics for REP-CPS vs Centralized (non-scheduling scenarios only).",
            "",
            "| Metric | Value |",
            "|--------|-------|",
        ])
        if "difference_mean" in excellence:
            lines.append(f"| difference_mean (REP-CPS - Centralized) | {_round(excellence.get('difference_mean'), 4)} |")
        if "difference_ci95" in excellence:
            ci = excellence.get("difference_ci95", [])
            if isinstance(ci, list) and len(ci) == 2:
                lines.append(f"| difference_ci95_lower | {_round(ci[0], 4)} |")
                lines.append(f"| difference_ci95_upper | {_round(ci[1], 4)} |")
        if "difference_ci_width" in excellence:
            lines.append(f"| difference_ci_width | {_round(excellence.get('difference_ci_width'), 4)} |")
        if "paired_t_p_value" in excellence:
            p_val = excellence.get("paired_t_p_value")
            lines.append(f"| paired_t_p_value | {_round(p_val, 4) if p_val is not None else '—'} |")
        if "power_post_hoc" in excellence:
            lines.append(f"| power_post_hoc | {_round(excellence.get('power_post_hoc'), 4) if excellence.get('power_post_hoc') is not None else '—'} |")
        if "alpha" in excellence:
            lines.append(f"| alpha | {excellence.get('alpha', '—')} |")
        lines.extend(["", ""])

    gate_sweep = data.get("gate_threshold_sweep_results", [])
    if gate_sweep:
        lines.extend([
            "**Gate-threshold sensitivity (source: summary.json gate_threshold_sweep_results).** Scheduling scenario sweep of `safety_gate_max_load`; shows where naive trips gate while REP-CPS remains admissible.",
            "",
            "| safety_gate_max_load | REP-CPS tasks_mean | naive_in_loop tasks_mean | unsecured tasks_mean | REP-CPS gate_deny_rate | unsecured gate_deny_rate | rep_beats_naive_tasks |",
            "|----------------------|--------------------|--------------------------|---------------------|------------------------|--------------------------|-----------------------|",
        ])
        for row in gate_sweep:
            lines.append(
                f"| {_round(row.get('safety_gate_max_load'), 3)} | "
                f"{_round(row.get('rep_cps_tasks_mean'), 2)} | "
                f"{_round(row.get('naive_in_loop_tasks_mean'), 2)} | "
                f"{_round(row.get('unsecured_tasks_mean'), 2)} | "
                f"{_round(row.get('rep_cps_gate_deny_rate'), 4)} | "
                f"{_round(row.get('unsecured_gate_deny_rate'), 4)} | "
                f"{row.get('rep_beats_naive_tasks', '—')} |"
            )
        lines.extend(["", ""])

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
        "Regenerate: `python scripts/rep_cps_eval.py` (default scenarios: toy_lab_v0, lab_profile_v0, rep_cps_scheduling_v0). Tables: `python scripts/export_rep_cps_tables.py`. Latency/cost: summary.json latency_cost; Table 5. Resilience: resilience_envelope, magnitude_sweep, trim_fraction_sweep. Threat micro-evidence: freshness_replay_evidence, sybil_vs_spoofing_evidence, messaging_sim, dynamic_aggregation_series. Convergence: `python scripts/rep_cps_eval.py --aggregation-steps 5` then `python scripts/export_rep_cps_convergence_table.py`. See DRAFT.md repro block and RESULTS_PER_PAPER.md.",
        "",
    ])

    out_text = "\n".join(lines)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(out_text, encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
