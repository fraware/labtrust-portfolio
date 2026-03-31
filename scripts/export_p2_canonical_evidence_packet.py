#!/usr/bin/env python3
"""
Build papers/P2_REP-CPS/canonical_evidence_packet.json from
datasets/runs/rep_cps_eval/summary.json.
Re-run after rep_cps_eval to refresh the frozen packet and hashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


def mtime_iso(p: Path) -> str:
    return datetime.fromtimestamp(p.stat().st_mtime).isoformat()


def git_head() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, cwd=REPO
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return None


def scheduling_gate_counts(d: dict) -> dict | None:
    for s in d.get("per_scenario") or []:
        if s.get("scenario_id") != "rep_cps_scheduling_v0":
            continue
        rows = s.get("adapter_runs") or []
        rep_pass = sum(
            1 for r in rows if r.get("rep_cps_safety_gate_ok") is True
        )
        rep_den = sum(
            1 for r in rows if r.get("rep_cps_safety_gate_ok") is False
        )
        unsec_pass = sum(
            1 for r in rows if r.get("rep_cps_unsecured_safety_gate_ok") is True
        )
        unsec_den = sum(
            1 for r in rows if r.get("rep_cps_unsecured_safety_gate_ok") is False
        )
        gate_vals = sorted({r.get("safety_gate_max_load") for r in rows})
        return {
            "adapter_run_count": len(rows),
            "rep_cps_safety_gate_pass_count": rep_pass,
            "rep_cps_safety_gate_deny_count": rep_den,
            "unsecured_safety_gate_pass_count": unsec_pass,
            "unsecured_safety_gate_deny_count": unsec_den,
            "safety_gate_max_load_values_observed": gate_vals,
        }
    return None


def comparator_exact_recompute() -> dict:
    sys.path.insert(0, str(REPO / "impl" / "src"))
    from labtrust_portfolio.rep_cps import aggregate, compromised_updates

    honest = [
        {"variable": "load", "value": 0.3, "ts": 0.0, "agent_id": "a1"},
        {"variable": "load", "value": 0.35, "ts": 0.0, "agent_id": "a2"},
        {"variable": "load", "value": 0.32, "ts": 0.0, "agent_id": "a3"},
    ]
    comp = compromised_updates(
        "load", num_compromised=2, extreme_value=10.0, ts=0.0
    )
    comb = honest + comp
    agg_h = aggregate(
        "load", honest, method="trimmed_mean", trim_fraction=0.25
    )
    naive_agg = aggregate("load", comb, method="mean")
    out: dict = {
        "honest_trimmed_baseline": agg_h,
        "naive_mean_aggregate": naive_agg,
        "naive_mean_bias_vs_honest_trimmed": abs(naive_agg - agg_h),
    }
    for m in ("trimmed_mean", "median", "clipping", "median_of_means"):
        if m == "trimmed_mean":
            av = aggregate(
                "load", comb, method="trimmed_mean", trim_fraction=0.25
            )
        else:
            av = aggregate("load", comb, method=m)
        out[m] = {
            "aggregate": av,
            "bias_vs_honest_trimmed": abs(av - agg_h),
            "beats_naive_mean": abs(av - agg_h) < abs(naive_agg - agg_h),
        }
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Export P2 canonical evidence packet JSON"
    )
    ap.add_argument(
        "--summary",
        type=Path,
        default=REPO / "datasets" / "runs" / "rep_cps_eval" / "summary.json",
        help="Path to rep_cps_eval summary.json",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=(
            REPO / "papers" / "P2_REP-CPS" / "canonical_evidence_packet.json"
        ),
        help="Output JSON path",
    )
    args = ap.parse_args()

    if not args.summary.exists():
        print(f"Error: {args.summary} not found.", file=sys.stderr)
        return 1

    d = json.loads(args.summary.read_text(encoding="utf-8"))
    summary_path = args.summary.resolve()
    denial_path = (summary_path.parent / "safety_gate_denial.json").resolve()
    tables_path = (REPO / "papers" / "P2_REP-CPS" / "generated_tables.md").resolve()

    def file_meta(p: Path) -> dict:
        if not p.exists():
            return {"path": str(p.relative_to(REPO)).replace("\\", "/"), "sha256": None, "mtime_iso": None}
        return {
            "path": str(p.relative_to(REPO)).replace("\\", "/"),
            "sha256": sha256_file(p),
            "mtime_iso": mtime_iso(p),
        }

    packet = {
        "schema_version": "1.0",
        "paper_id": "P2_REP-CPS",
        "canonical_run": {
            "output_directory": "datasets/runs/rep_cps_eval",
            "run_id_field": None,
            "note": (
                "No explicit run_id in summary.json; directory path is canonical."
            ),
        },
        "provenance": {
            "git_commit_at_generation": git_head(),
            "summary_json": file_meta(summary_path),
            "safety_gate_denial_json": file_meta(denial_path),
            "generated_tables_md": file_meta(tables_path),
        },
        "reproducer_command": (
            "python scripts/rep_cps_eval.py "
            "--scenarios toy_lab_v0,lab_profile_v0,rep_cps_scheduling_v0 "
            "--delay-sweep 0,0.05,0.1,0.2 --drop-sweep 0.02 "
            "--gate-threshold-sweep 1.5,2.0,2.5"
        ),
        "environment": {
            "labtrust_kernel_dir": "kernel",
            "pythonpath_impl_src": "impl/src",
            "note": "Set LABTRUST_KERNEL_DIR and PYTHONPATH per DRAFT.md / docs/figures/README_P2_figures.md",
        },
        "run_manifest": d.get("run_manifest"),
        "top_level_sweep_keys": {
            "scenario_ids": d.get("scenario_ids"),
            "seeds": d.get("seeds"),
            "delay_fault_prob_sweep": d.get("delay_fault_prob_sweep"),
            "drop_completion_prob_sweep": d.get("drop_completion_prob_sweep"),
            "gate_threshold_sweep": d.get("gate_threshold_sweep"),
            "aggregation_steps": d.get("aggregation_steps"),
        },
        "latency_cost": d.get("latency_cost"),
        "per_scenario": [
            {
                "scenario_id": ps.get("scenario_id"),
                "rep_cps_tasks_mean": ps.get("rep_cps_tasks_mean"),
                "rep_cps_tasks_stdev": ps.get("rep_cps_tasks_stdev"),
                "naive_in_loop_tasks_mean": ps.get("naive_in_loop_tasks_mean"),
                "naive_in_loop_tasks_stdev": ps.get("naive_in_loop_tasks_stdev"),
                "unsecured_tasks_mean": ps.get("unsecured_tasks_mean"),
                "unsecured_tasks_stdev": ps.get("unsecured_tasks_stdev"),
                "centralized_tasks_mean": ps.get("centralized_tasks_mean"),
                "centralized_tasks_stdev": ps.get("centralized_tasks_stdev"),
            }
            for ps in d.get("per_scenario", [])
        ],
        "global_adapter_means": {
            "rep_cps_tasks_completed_mean": d.get(
                "rep_cps_tasks_completed_mean"
            ),
            "rep_cps_tasks_completed_stdev": d.get(
                "rep_cps_tasks_completed_stdev"
            ),
            "centralized_tasks_completed_mean": d.get(
                "centralized_tasks_completed_mean"
            ),
            "centralized_tasks_completed_stdev": d.get(
                "centralized_tasks_completed_stdev"
            ),
            "rep_cps_naive_tasks_completed_mean": d.get(
                "rep_cps_naive_tasks_completed_mean"
            ),
            "rep_cps_naive_tasks_completed_stdev": d.get(
                "rep_cps_naive_tasks_completed_stdev"
            ),
            "rep_cps_unsecured_tasks_completed_mean": d.get(
                "rep_cps_unsecured_tasks_completed_mean"
            ),
            "rep_cps_unsecured_tasks_completed_stdev": d.get(
                "rep_cps_unsecured_tasks_completed_stdev"
            ),
            "rep_cps_naive_aggregate_load_mean": d.get(
                "rep_cps_naive_aggregate_load_mean"
            ),
            "rep_cps_unsecured_aggregate_load_mean": d.get(
                "rep_cps_unsecured_aggregate_load_mean"
            ),
        },
        "scheduling_dependent_eval": d.get("scheduling_dependent_eval"),
        "scheduling_scenario_gate_counts": scheduling_gate_counts(d),
        "gate_threshold_sweep_results": d.get("gate_threshold_sweep_results"),
        "aggregation_under_compromise": d.get("aggregation_under_compromise"),
        "profile_ablation": d.get("profile_ablation"),
        "aggregation_variants": d.get("aggregation_variants"),
        "offline_comparator_baselines": d.get("offline_comparator_baselines"),
        "comparator_exact_recompute": comparator_exact_recompute(),
        "resilience_envelope": d.get("resilience_envelope"),
        "freshness_replay_evidence": d.get("freshness_replay_evidence"),
        "sybil_vs_spoofing_evidence": d.get("sybil_vs_spoofing_evidence"),
        "dynamic_aggregation_series": d.get("dynamic_aggregation_series"),
        "messaging_sim": d.get("messaging_sim"),
        "safety_gate_denial": d.get("safety_gate_denial"),
        "excellence_metrics": d.get("excellence_metrics"),
        "success_criteria_met": d.get("success_criteria_met"),
        "default_in_loop_aggregation": {
            "method": "trimmed_mean",
            "source": "REPCPSAdapter default aggregation_method",
        },
        "figure_pipeline": {
            "source_summary_default": (
                "datasets/runs/rep_cps_eval/summary.json"
            ),
            "scripts": {
                "figure_0_mermaid": "scripts/export_p2_rep_profile_diagram.py",
                "tasks_figures": "scripts/plot_rep_cps_summary.py",
                "gate_threshold_figure": "scripts/plot_rep_cps_gate_threshold.py",
                "dynamics_figure": "scripts/plot_rep_cps_dynamics.py",
                "latency_figure": "scripts/plot_rep_cps_latency.py",
                "tables": "scripts/export_rep_cps_tables.py",
            },
            "default_outputs": {
                "p2_rep_profile_diagram_mmd": (
                    "docs/figures/p2_rep_profile_diagram.mmd"
                ),
                "p2_rep_cps_tasks_png": "docs/figures/p2_rep_cps_tasks.png",
                "p2_rep_cps_tasks_per_scenario_png": (
                    "docs/figures/p2_rep_cps_tasks_per_scenario.png"
                ),
                "p2_rep_cps_gate_threshold_png": (
                    "docs/figures/p2_rep_cps_gate_threshold.png"
                ),
                "p2_rep_cps_dynamics_png": (
                    "docs/figures/p2_rep_cps_dynamics.png"
                ),
                "p2_rep_cps_latency_png": (
                    "docs/figures/p2_rep_cps_latency.png"
                ),
            },
        },
        "rounding_policy_recommended": {
            "tasks_means_stdev": "2 decimal places",
            "wall_time_seconds": "4 decimal places",
            "aggregation_compute_ms": "4 decimal places",
            "bias_and_aggregates": (
                "3 decimal places in main text; full precision in this packet"
            ),
            "deny_rates": "3 decimal places or exact 0/1 when binary",
        },
        "notes": {
            "bias_reduction_pct": (
                "excellence_metrics.bias_reduction_pct = "
                "round(100*(bias_naive-bias_robust)/bias_naive, 2) "
                "when bias_naive>0 (see scripts/rep_cps_eval.py)"
            ),
            "no_auth_vs_no_freshness_equality": (
                "Expected from harness construction; see run_profile_ablation "
                "in scripts/rep_cps_eval.py"
            ),
            "gate_threshold_sweep_naive_deny_rate": (
                "Not serialized in gate_threshold_sweep_results; derive from "
                "raw adapter runs if needed"
            ),
        },
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(packet, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
