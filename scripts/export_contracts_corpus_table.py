#!/usr/bin/env python3
"""
Export P1 corpus table: detection_ok + timestamp-only baseline misses.
Reads datasets/runs/contracts_eval/eval.json. Usage:
  python scripts/export_contracts_corpus_table.py [--eval path]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_EVAL = REPO / "datasets" / "runs" / "contracts_eval" / "eval.json"


def main() -> int:
    ap = argparse.ArgumentParser(description="Export P1 corpus table (detection_ok + baseline)")
    ap.add_argument("--eval", type=Path, default=DEFAULT_EVAL, help="Path to eval.json")
    args = ap.parse_args()
    if not args.eval.exists():
        print(f"Error: {args.eval} not found. Run contracts_eval.py first.")
        return 1
    data = json.loads(args.eval.read_text(encoding="utf-8"))
    sequences = data.get("sequences", [])
    ts_missed = data.get("baseline_timestamp_only_missed", 0)
    ts_denials = data.get("baseline_timestamp_only_denials", 0)
    lines = [
        "# Generated tables for P1 (P1_Contracts)",
        "",
        "## From export_contracts_corpus_table.py",
        "",
        "# Table 1 — Corpus evaluation. Per-sequence detection_ok and denials; run_manifest in eval.json.",
        "",
        "| Sequence | detection_ok | denials (contract) |",
        "|----------|---------------|-------------------|",
    ]
    for s in sequences:
        seq = s.get("sequence", "")
        ok = "yes" if s.get("detection_ok") else "no"
        denials = s.get("denials", 0)
        lines.append(f"| {seq} | {ok} | {denials} |")
    lines.append("")
    lines.append(
        f"**Timestamp-only baseline:** denials with timestamp-only policy: {ts_denials}. "
        f"Violations the contract catches but timestamp-only would allow (missed): {ts_missed}. "
        f"(Baselines and ablation are populated by every `contracts_eval.py` run; use `--baseline` only for the extra `violations_would_apply_without_validator` field.)"
    )
    ablation_by_class = data.get("ablation_by_class", {})
    policy_order = (
        "full_contract",
        "timestamp_only",
        "ownership_only",
        "occ_only",
        "lease_only",
        "lock_only",
        "accept_all",
        "naive_lww",
    )
    if ablation_by_class:
        lines.append("")
        lines.append("## Ablation by failure class")
        lines.append("")
        lines.append("| Class | Policy | Violations denied | Violations missed |")
        lines.append("|-------|--------|--------------------|--------------------|")
        for fc in sorted(ablation_by_class.keys()):
            for policy in policy_order:
                if policy not in ablation_by_class[fc]:
                    continue
                row = ablation_by_class[fc][policy]
                lines.append(
                    f"| {fc} | {policy} | {row['violations_denied']} | "
                    f"{row['violations_missed']} |"
                )
    dmbc = data.get("detection_metrics_by_class", {})
    if dmbc:
        lines.append("")
        lines.append("## Table 3 — Detection metrics by inferred failure class")
        lines.append("")
        lines.append("| Class | TP | FP | FN | Precision | Recall | F1 |")
        lines.append("|-------|----|----|----|-----------|--------|-----|")
        def _mval(x: object) -> str:
            return "n/a" if x is None else str(x)

        for fc in sorted(dmbc.keys()):
            m = dmbc[fc]
            lines.append(
                f"| {fc} | {m.get('true_positives')} | {m.get('false_positives')} | "
                f"{m.get('false_negatives')} | {_mval(m.get('precision'))} | {_mval(m.get('recall'))} | "
                f"{_mval(m.get('f1'))} |"
            )
    lines.append("")
    lines.append(
        "**Comparator notes:** `occ_only` and `lease_only` use temporal monotonicity only "
        "in the reference benchmark (OCC/version proxy; lease proxy without explicit lease "
        "fields). `lock_only` is ownership-only (mutex-style). `naive_lww` accepts all writes. "
        "These are reference proxies for conceptual comparison; full OCC/lease/lock implementations "
        "would include additional semantics (read sets, lease windows, lock acquisition) not captured "
        "in the corpus event model."
    )
    
    # Add stress robustness table if stress_results.json exists
    stress_path = args.eval.parent / "stress_results.json"
    if stress_path.exists():
        try:
            stress_data = json.loads(stress_path.read_text(encoding="utf-8"))
            if stress_data.get("stress_sweep"):
                lines.append("")
                lines.append("## Stress robustness (async delay/skew/reorder)")
                lines.append("")
                lines.append("| Stress profile | Sequences tested | Detection OK rate | Notes |")
                lines.append("|----------------|------------------|-------------------|-------|")
                # Aggregate by stress profile
                profile_stats: dict[str, dict] = {}
                for r in stress_data.get("results", []):
                    profile = r.get("stress_profile", {})
                    key = f"delay={profile.get('delay_mean', 0)}, skew={profile.get('clock_skew_max', 0)}, reorder={profile.get('reorder_prob', 0)}"
                    if key not in profile_stats:
                        profile_stats[key] = {"total": 0, "ok": 0}
                    profile_stats[key]["total"] += 1
                    if r.get("detection_ok"):
                        profile_stats[key]["ok"] += 1
                for key, stats in sorted(profile_stats.items()):
                    rate = round(100.0 * stats["ok"] / stats["total"], 1) if stats["total"] > 0 else 0.0
                    lines.append(f"| {key} | {stats['total']} | {rate}% | Async stress test |")
        except Exception:
            pass  # Skip if stress file is malformed
    
    # Add transport parity summary if available
    parity_path = args.eval.parent / "transport_parity.json"
    if parity_path.exists():
        try:
            parity_data = json.loads(parity_path.read_text(encoding="utf-8"))
            conf = parity_data.get("parity_confidence", {})
            if conf:
                lines.append("")
                lines.append("## Transport parity (boundary semantics)")
                lines.append("")
                lines.append(f"**Parity rate:** {conf.get('parity_rate', 0.0):.1%} ({conf.get('matching_events', 0)}/{conf.get('total_events_checked', 0)} events match between event-log and LADS-shaped paths).")
                lines.append(f"**All sequences parity:** {'OK' if parity_data.get('parity_ok_all') else 'FAIL'}.")
        except Exception:
            pass
    det = data.get("detection_metrics", {})
    if det:
        lines.append("")
        lines.append(f"**Detection metrics:** TP={det.get('true_positives')}, FP={det.get('false_positives')}, FN={det.get('false_negatives')}, precision={det.get('precision')}, recall={det.get('recall')}, F1={det.get('f1')}.")
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
