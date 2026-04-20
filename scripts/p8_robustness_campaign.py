#!/usr/bin/env python3
"""
Run a state-of-the-art robustness campaign for P8 (Meta-Coordination).

This script orchestrates a matrix of P8 experiments designed to strengthen
evidence for claims C1-C3:
  - multi-scenario stress calibration (non-vacuous collapse settings),
  - multiple switch-signal stress channels (fault, latency, contention proxy),
  - hysteresis thrash-control ablations,
  - two-regime comparisons with retry_heavy fallback.

It writes:
  - campaign_summary.json (aggregated outcomes and claim coverage),
  - per-run comparison.json and collapse_sweep.json artifacts in subdirectories.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO / "datasets" / "runs" / "meta_eval" / "robustness_campaign"
SCENARIOS = ("regime_stress_v0", "regime_stress_v1")


def _env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("PYTHONPATH", str(REPO / "impl" / "src"))
    env.setdefault("LABTRUST_KERNEL_DIR", str(REPO / "kernel"))
    return env


def _run(cmd: list[str], label: str, timeout: int) -> None:
    print(f"\n--- {label} ---")
    print(" ".join(cmd))
    proc = subprocess.run(cmd, cwd=str(REPO), env=_env(), timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError(f"{label} failed (exit {proc.returncode})")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _collapse_sweep(
    out_dir: Path,
    scenario: str,
    seeds: str,
    drop_probs: str,
    collapse_threshold: int,
) -> Path:
    cmd = [
        sys.executable,
        str(REPO / "scripts" / "meta_collapse_sweep.py"),
        "--out",
        str(out_dir),
        "--scenario",
        scenario,
        "--seeds",
        seeds,
        "--drop-probs",
        drop_probs,
        "--collapse-threshold",
        str(collapse_threshold),
    ]
    _run(cmd, f"P8 collapse sweep ({scenario})", timeout=600)
    return out_dir / "collapse_sweep.json"


def _meta_eval(
    out_dir: Path,
    scenario: str,
    seeds: str,
    *,
    collapse_threshold: int,
    fault_threshold: int,
    hysteresis: int,
    latency_threshold_ms: float,
    contention_threshold: float,
    fallback_adapter: str = "",
    non_vacuous: bool = False,
    collapse_sweep_path: Path | None = None,
    drop_prob: float | None = None,
) -> Path:
    cmd = [
        sys.executable,
        str(REPO / "scripts" / "meta_eval.py"),
        "--out",
        str(out_dir),
        "--scenario",
        scenario,
        "--seeds",
        seeds,
        "--run-naive",
        "--fault-threshold",
        str(fault_threshold),
        "--collapse-threshold",
        str(collapse_threshold),
        "--hysteresis",
        str(hysteresis),
        "--latency-threshold-ms",
        str(latency_threshold_ms),
        "--contention-threshold",
        str(contention_threshold),
    ]
    if fallback_adapter:
        cmd.extend(["--fallback-adapter", fallback_adapter])
    if non_vacuous:
        cmd.append("--non-vacuous")
        cmd.extend(["--non-vacuous-select", "max_drop_any_collapse"])
    if collapse_sweep_path is not None:
        cmd.extend(["--collapse-sweep-path", str(collapse_sweep_path)])
    if drop_prob is not None:
        cmd.extend(["--drop-prob", str(drop_prob)])
    _run(
        cmd,
        (
            f"P8 meta_eval ({scenario}, H={hysteresis}, "
            f"lat={latency_threshold_ms}, cont={contention_threshold}, "
            f"fallback={fallback_adapter or 'none'}, non_vacuous={non_vacuous})"
        ),
        timeout=900,
    )
    return out_dir / "comparison.json"


def _verify(comparison_path: Path, sweep_path: Path, strict: bool) -> None:
    cmd = [
        sys.executable,
        str(REPO / "scripts" / "verify_p8_meta_artifacts.py"),
        "--comparison",
        str(comparison_path),
        "--sweep",
        str(sweep_path),
    ]
    if strict:
        cmd.append("--strict-publishable")
    _run(cmd, f"Verify artifacts ({comparison_path.parent.name})", timeout=90)


def _collect_switch_reasons(run_root: Path) -> dict[str, int]:
    """Count regime_switch reasons across meta trace artifacts under a run directory."""
    reason_counts: dict[str, int] = {}
    meta_root = run_root / "meta"
    if not meta_root.exists():
        return reason_counts
    for trace_path in sorted(meta_root.glob("seed_*/trace.json")):
        try:
            trace = _load_json(trace_path)
        except (json.JSONDecodeError, OSError):
            continue
        for event in trace.get("events", []):
            if event.get("type") != "regime_switch":
                continue
            payload = event.get("payload", {}) if isinstance(event.get("payload"), dict) else {}
            reason = str(payload.get("reason", "unknown"))
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
    return reason_counts


def _extract_run_row(
    run_id: str,
    scenario: str,
    profile: str,
    comparison: dict[str, Any],
    switch_reasons: dict[str, int] | None = None,
) -> dict[str, Any]:
    cpa = comparison.get("collapse_paired_analysis") or {}
    em = comparison.get("excellence_metrics") or {}
    sc = comparison.get("success_criteria_met") or {}
    meta = comparison.get("meta_controller") or {}
    fixed = comparison.get("fixed") or {}
    switch_total = sum(
        int(seed_row.get("regime_switch_count", 0))
        for seed_row in (meta.get("per_seed") or [])
    )
    reasons = switch_reasons or {}
    return {
        "run_id": run_id,
        "scenario_id": scenario,
        "profile": profile,
        "seed_count": (comparison.get("run_manifest") or {}).get("seed_count"),
        "drop_completion_prob": comparison.get("drop_completion_prob"),
        "fixed_collapse_count": fixed.get("collapse_count"),
        "meta_collapse_count": meta.get("collapse_count"),
        "meta_non_worse_collapse": comparison.get("meta_non_worse_collapse"),
        "meta_strictly_reduces_collapse": comparison.get("meta_strictly_reduces_collapse"),
        "no_safety_regression": comparison.get("no_safety_regression"),
        "trigger_met": sc.get("trigger_met"),
        "regime_switch_count_total": switch_total,
        "mcnemar_exact_p_value_two_sided": cpa.get("mcnemar_exact_p_value_two_sided"),
        "fixed_collapse_rate_wilson_ci95": cpa.get("fixed_collapse_rate_wilson_ci95"),
        "meta_collapse_rate_wilson_ci95": cpa.get("meta_collapse_rate_wilson_ci95"),
        "difference_ci95": em.get("difference_ci95"),
        "fallback_tasks_completed_mean": comparison.get("fallback_tasks_completed_mean"),
        "switch_reasons": reasons,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="P8 robustness campaign runner")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Campaign output directory")
    ap.add_argument(
        "--seeds",
        type=str,
        default="1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20",
        help="Seed list for publishable runs",
    )
    ap.add_argument(
        "--collapse-threshold",
        type=int,
        default=2,
        help="tasks_completed below this => collapse",
    )
    ap.add_argument(
        "--strict-publishable",
        action="store_true",
        help="Pass --strict-publishable to artifact verifier",
    )
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    runs: list[dict[str, Any]] = []
    scenario_drop_probs = {
        "regime_stress_v0": "0.15,0.2,0.25,0.3,0.35",
        "regime_stress_v1": "0.2,0.25,0.3,0.35,0.4",
    }

    for scenario in SCENARIOS:
        scen_dir = args.out / scenario
        sweep_dir = scen_dir / "sweep"
        base_dir = scen_dir / "baseline_non_vacuous"
        latency_dir = scen_dir / "latency_sensitive"
        contention_dir = scen_dir / "contention_sensitive"
        hysteresis_dir = scen_dir / "hysteresis_ablation"

        drop_probs = scenario_drop_probs[scenario]
        sweep_path = _collapse_sweep(
            sweep_dir,
            scenario,
            args.seeds,
            drop_probs,
            args.collapse_threshold,
        )

        # Baseline publishable run: non-vacuous + two real regimes.
        base_cmp = _meta_eval(
            base_dir,
            scenario,
            args.seeds,
            collapse_threshold=args.collapse_threshold,
            fault_threshold=1,
            hysteresis=1,
            latency_threshold_ms=200.0,
            contention_threshold=1.5,
            fallback_adapter="retry_heavy",
            non_vacuous=True,
            collapse_sweep_path=sweep_path,
        )
        _verify(base_cmp, sweep_path, strict=args.strict_publishable)
        base_data = _load_json(base_cmp)
        chosen_drop = float(base_data.get("drop_completion_prob", 0.15))
        base_reasons = _collect_switch_reasons(base_dir)
        runs.append(
            _extract_run_row(
                run_id=f"{scenario}/baseline_non_vacuous",
                scenario=scenario,
                profile="baseline_non_vacuous_retry_heavy",
                comparison=base_data,
                switch_reasons=base_reasons,
            )
        )

        # Latency-sensitive profile: force latency-trigger switches.
        lat_cmp = _meta_eval(
            latency_dir,
            scenario,
            args.seeds,
            collapse_threshold=args.collapse_threshold,
            fault_threshold=999,
            hysteresis=1,
            latency_threshold_ms=30.0,
            contention_threshold=999.0,
            fallback_adapter="retry_heavy",
            non_vacuous=False,
            drop_prob=chosen_drop,
        )
        _verify(lat_cmp, sweep_path, strict=False)
        lat_data = _load_json(lat_cmp)
        lat_reasons = _collect_switch_reasons(latency_dir)
        runs.append(
            _extract_run_row(
                run_id=f"{scenario}/latency_sensitive",
                scenario=scenario,
                profile="latency_trigger_profile",
                comparison=lat_data,
                switch_reasons=lat_reasons,
            )
        )

        # Contention-sensitive profile: force contention-trigger switches.
        cont_cmp = _meta_eval(
            contention_dir,
            scenario,
            args.seeds,
            collapse_threshold=args.collapse_threshold,
            fault_threshold=999,
            hysteresis=1,
            latency_threshold_ms=999.0,
            contention_threshold=0.5,
            fallback_adapter="retry_heavy",
            non_vacuous=False,
            drop_prob=chosen_drop,
        )
        _verify(cont_cmp, sweep_path, strict=False)
        cont_data = _load_json(cont_cmp)
        cont_reasons = _collect_switch_reasons(contention_dir)
        runs.append(
            _extract_run_row(
                run_id=f"{scenario}/contention_sensitive",
                scenario=scenario,
                profile="contention_trigger_profile",
                comparison=cont_data,
                switch_reasons=cont_reasons,
            )
        )

        # Hysteresis ablation: H=1 and H=3.
        for h in (1, 3):
            ab_dir = hysteresis_dir / f"h{h}"
            cmp_path = _meta_eval(
                ab_dir,
                scenario,
                args.seeds,
                collapse_threshold=args.collapse_threshold,
                fault_threshold=0,
                hysteresis=h,
                latency_threshold_ms=200.0,
                contention_threshold=1.5,
                fallback_adapter="retry_heavy",
                non_vacuous=False,
                drop_prob=chosen_drop,
            )
            _verify(cmp_path, sweep_path, strict=False)
            cmp_data = _load_json(cmp_path)
            h_reasons = _collect_switch_reasons(ab_dir)
            runs.append(
                _extract_run_row(
                    run_id=f"{scenario}/hysteresis_h{h}",
                    scenario=scenario,
                    profile=f"hysteresis_h{h}",
                    comparison=cmp_data,
                    switch_reasons=h_reasons,
                )
            )

    # Claim-coverage summary aligned with C1-C3.
    c1_switch_runs = [r for r in runs if r["regime_switch_count_total"] and r["regime_switch_count_total"] > 0]
    c1_ok = all(bool(r.get("no_safety_regression")) for r in c1_switch_runs) and len(c1_switch_runs) > 0
    c2_ok = len(c1_switch_runs) > 0  # trace-level audit replay is validated in integration + verifier.
    c3_rows = [r for r in runs if r["profile"] == "baseline_non_vacuous_retry_heavy"]
    c3_ok = all(bool(r.get("meta_non_worse_collapse")) for r in c3_rows) and len(c3_rows) > 0

    summary = {
        "schema_version": "p8_robustness_campaign_v0.1",
        "methodology_note": (
            "latency_trigger_profile and contention_trigger_profile set fault_threshold=999 "
            "to isolate latency vs contention channels; each profile reuses the baseline "
            "chosen_drop_completion_prob from baseline_non_vacuous_retry_heavy so stress "
            "severity matches the publishable non-vacuous row. Under latency-only isolation, "
            "meta_strictly_reduces_collapse may tie (non-inferiority still holds) while "
            "latency_threshold-driven switches remain observable. Primary evidence: "
            "baseline_non_vacuous_retry_heavy (meta fault_threshold=1; naive arm uses "
            "fault_threshold=0 inside meta_eval when --run-naive is set)."
        ),
        "run_manifest": {
            "script": "p8_robustness_campaign.py",
            "seeds": [int(x.strip()) for x in args.seeds.split(",") if x.strip()],
            "seed_count": len([x for x in args.seeds.split(",") if x.strip()]),
            "scenarios": list(SCENARIOS),
            "collapse_threshold": args.collapse_threshold,
        },
        "runs": runs,
        "claim_support": {
            "C1": {
                "switches_observed": len(c1_switch_runs),
                "no_safety_regression_all_switch_profiles": c1_ok,
            },
            "C2": {
                "audit_replay_artifacts_verified": c2_ok,
                "note": (
                    "Each run is validated with verify_p8_meta_artifacts.py; "
                    "trace-level regime_switch payloads are generated by MetaAdapter."
                ),
            },
            "C3": {
                "non_vacuous_baseline_runs": len(c3_rows),
                "meta_non_worse_collapse_all_non_vacuous": c3_ok,
                "strict_reduction_any": any(bool(r.get("meta_strictly_reduces_collapse")) for r in c3_rows),
            },
        },
        "success_criteria_met": {
            "campaign_completed": True,
            "c1_supported": c1_ok,
            "c2_supported": c2_ok,
            "c3_supported": c3_ok,
            "all_claims_supported": c1_ok and c2_ok and c3_ok,
        },
    }

    out_path = args.out / "campaign_summary.json"
    out_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"\nWrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
