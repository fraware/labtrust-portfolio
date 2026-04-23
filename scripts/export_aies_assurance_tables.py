#!/usr/bin/env python3
"""
AIES 2026 assurance-paper export packager.

Builds paper-facing tables and summaries from:
  - results.json (institutional positive path)
  - negative_results.json (negative controls / ablations)

Primary output root:
  datasets/runs/assurance_eval_aies/
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

REPO = Path(__file__).resolve().parents[1]


def _git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=str(REPO),
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _ensure(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _to_tex_table(headers: List[str], rows: List[List[Any]], label: str) -> str:
    cols = " | ".join(["l"] * len(headers))
    out = [
        "\\begin{table}[t]",
        "\\centering",
        f"\\begin{{tabular}}{{{cols}}}",
        "\\hline",
        " & ".join(headers) + " \\\\",
        "\\hline",
    ]
    for row in rows:
        out.append(" & ".join(str(x) for x in row) + " \\\\")
    out.extend(["\\hline", "\\end{tabular}", f"\\caption{{{label}}}", "\\end{table}", ""])
    return "\n".join(out)


def _write_csv(path: Path, headers: List[str], rows: List[List[Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(headers)
        for row in rows:
            w.writerow(row)


def main() -> int:
    ap = argparse.ArgumentParser(description="Export AIES assurance tables")
    ap.add_argument(
        "--in",
        dest="in_dir",
        type=Path,
        default=REPO / "datasets" / "runs" / "assurance_eval_aies",
        help="Input eval directory containing results.json and negative_results.json",
    )
    ap.add_argument(
        "--out",
        dest="out_dir",
        type=Path,
        default=None,
        help="Output tables dir (default: <in>/tables)",
    )
    args = ap.parse_args()

    in_dir = args.in_dir.resolve()
    out_tables = (args.out_dir.resolve() if args.out_dir else in_dir / "tables")
    _ensure(in_dir)
    _ensure(out_tables)
    _ensure(in_dir / "figures")
    _ensure(in_dir / "proxy_stress_only")

    results_path = in_dir / "results.json"
    neg_path = in_dir / "negative_results.json"
    if not results_path.exists():
        raise FileNotFoundError(f"Missing {results_path}")
    if not neg_path.exists():
        raise FileNotFoundError(f"Missing {neg_path}")

    results = json.loads(results_path.read_text(encoding="utf-8"))
    neg = json.loads(neg_path.read_text(encoding="utf-8"))

    reviews = results.get("reviews") or {}
    per_profile = results.get("per_profile") or {}
    lab = reviews.get("lab_profile_v0") or {}
    wh = per_profile.get("warehouse_v0.1") or {}
    traffic = per_profile.get("medical_v0.1") or {}

    baseline_summary = {
        "scenario_id": "lab_profile_v0",
        "mapping_check_ok": bool((results.get("mapping_check") or {}).get("ok")),
        "ponr_coverage_ok": (results.get("mapping_check") or {}).get("ponr_coverage_ok"),
        "review_exit_ok": lab.get("exit_ok"),
        "trace_ok": lab.get("trace_ok"),
        "evidence_bundle_ok": lab.get("evidence_bundle_ok"),
        "ponr_coverage_ratio": (lab.get("ponr_coverage") or {}).get("ratio"),
        "control_coverage_ratio": lab.get("control_coverage_ratio"),
        "review_latency_ms": lab.get("review_latency_ms"),
    }
    (in_dir / "baseline_summary.json").write_text(
        json.dumps(baseline_summary, indent=2) + "\n",
        encoding="utf-8",
    )

    institutional_positive_summary = {
        "primary_case": {"scenario_id": "lab_profile_v0", **baseline_summary},
        "portability_case": {
            "scenario_id": "warehouse_v0",
            "review_exit_ok": wh.get("exit_ok"),
            "trace_ok": wh.get("trace_ok"),
            "evidence_bundle_ok": wh.get("evidence_bundle_ok"),
            "ponr_coverage_ratio": (wh.get("ponr_coverage") or {}).get("ratio"),
            "control_coverage_ratio": wh.get("control_coverage_ratio"),
            "review_latency_ms": wh.get("review_latency_ms"),
        },
    }
    (in_dir / "institutional_positive_summary.json").write_text(
        json.dumps(institutional_positive_summary, indent=2) + "\n",
        encoding="utf-8",
    )

    proxy_summary = {
        "bucket": "proxy_stress_only",
        "scenario_id": "traffic_v0",
        "profile": "medical_v0.1",
        "review_exit_ok": traffic.get("exit_ok"),
        "trace_ok": traffic.get("trace_ok"),
        "evidence_bundle_ok": traffic.get("evidence_bundle_ok"),
        "ponr_coverage_ratio": (traffic.get("ponr_coverage") or {}).get("ratio"),
        "control_coverage_ratio": traffic.get("control_coverage_ratio"),
        "review_latency_ms": traffic.get("review_latency_ms"),
        "note": (
            "Proxy stress result retained for supplement only; excluded from "
            "main-text institutional baseline/portability tables."
        ),
    }
    (in_dir / "proxy_stress_only" / "traffic_medical_proxy_summary.json").write_text(
        json.dumps(proxy_summary, indent=2) + "\n",
        encoding="utf-8",
    )

    by_mode = neg.get("by_mode") or {}
    by_family = neg.get("by_family") or {}
    rows = neg.get("rows") or []
    failure_counts: Dict[str, int] = {}
    for row in rows:
        if row.get("review_mode") != "full_review" or row.get("review_exit_ok"):
            continue
        for code in row.get("failure_reason_codes") or []:
            failure_counts[code] = failure_counts.get(code, 0) + 1

    negative_summary = {
        "aggregate": neg.get("aggregate"),
        "by_mode": by_mode,
        "by_family": by_family,
        "top_failure_reasons": dict(
            sorted(failure_counts.items(), key=lambda kv: kv[1], reverse=True)[:10]
        ),
    }
    (in_dir / "negative_summary.json").write_text(
        json.dumps(negative_summary, indent=2) + "\n",
        encoding="utf-8",
    )

    baseline_headers = [
        "scenario_id",
        "mapping_check_ok",
        "ponr_coverage_ok",
        "review_exit_ok",
        "trace_ok",
        "evidence_bundle_ok",
        "ponr_coverage_ratio",
        "control_coverage_ratio",
    ]
    baseline_rows = [[
        "lab_profile_v0",
        baseline_summary["mapping_check_ok"],
        baseline_summary["ponr_coverage_ok"],
        baseline_summary["review_exit_ok"],
        baseline_summary["trace_ok"],
        baseline_summary["evidence_bundle_ok"],
        baseline_summary["ponr_coverage_ratio"],
        baseline_summary["control_coverage_ratio"],
    ]]
    _write_csv(out_tables / "baseline_table.csv", baseline_headers, baseline_rows)
    (out_tables / "baseline_table.tex").write_text(
        _to_tex_table(baseline_headers, baseline_rows, "AIES baseline (lab\\_profile\\_v0)")
        + "\n",
        encoding="utf-8",
    )

    portability_headers = [
        "scenario_id",
        "review_exit_ok",
        "trace_ok",
        "evidence_bundle_ok",
        "ponr_coverage_ratio",
        "control_coverage_ratio",
    ]
    portability_rows = [[
        "warehouse_v0",
        wh.get("exit_ok"),
        wh.get("trace_ok"),
        wh.get("evidence_bundle_ok"),
        (wh.get("ponr_coverage") or {}).get("ratio"),
        wh.get("control_coverage_ratio"),
    ]]
    _write_csv(out_tables / "portability_table.csv", portability_headers, portability_rows)
    (out_tables / "portability_table.tex").write_text(
        _to_tex_table(portability_headers, portability_rows, "AIES portability (warehouse\\_v0)")
        + "\n",
        encoding="utf-8",
    )

    mode_order = ["schema_only", "schema_plus_presence", "full_review"]
    ablation_headers = [
        "review_mode",
        "valid_accept_rate",
        "invalid_reject_rate",
        "false_accept_rate",
        "false_reject_rate",
        "localization_accuracy",
    ]
    ablation_rows = []
    for mode in mode_order:
        m = by_mode.get(mode) or {}
        ablation_rows.append([
            mode,
            m.get("valid_accept_rate"),
            m.get("invalid_reject_rate"),
            m.get("false_accept_rate"),
            m.get("false_reject_rate"),
            m.get("localization_accuracy"),
        ])
    _write_csv(out_tables / "negative_ablation_table.csv", ablation_headers, ablation_rows)
    (out_tables / "negative_ablation_table.tex").write_text(
        _to_tex_table(ablation_headers, ablation_rows, "Negative-control ablation")
        + "\n",
        encoding="utf-8",
    )

    family_headers = [
        "failure_family",
        "n_negative_cases",
        "reject_rate_on_negatives",
        "localization_accuracy",
    ]
    family_rows: List[List[Any]] = []
    for fam in sorted(k for k in by_family.keys() if k != "positive_control"):
        f = by_family[fam] or {}
        family_rows.append([
            fam,
            f.get("n"),
            f.get("reject_rate_on_negatives"),
            f.get("localization_accuracy"),
        ])
    _write_csv(out_tables / "failure_family_table.csv", family_headers, family_rows)
    (out_tables / "failure_family_table.tex").write_text(
        _to_tex_table(family_headers, family_rows, "Failure-family summary")
        + "\n",
        encoding="utf-8",
    )
    _write_csv(out_tables / "negative_failure_families.csv", family_headers, family_rows)

    reason_headers = ["failure_reason_code", "count_full_review_rejections"]
    reason_rows = [[k, v] for k, v in sorted(failure_counts.items(), key=lambda kv: kv[1], reverse=True)]
    _write_csv(out_tables / "negative_failure_reasons.csv", reason_headers, reason_rows)

    run_manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit_sha": _git_head(),
        "commands": [
            "python scripts/run_assurance_eval.py --out datasets/runs/assurance_eval_aies",
            "python scripts/run_assurance_negative_eval.py --out datasets/runs/assurance_eval_aies --submission-mode",
            "python -c \"from pathlib import Path; from labtrust_portfolio.thinslice import run_thin_slice; d=Path('datasets/runs/assurance_eval_aies/runs/lab_profile_v0_seed7'); d.mkdir(parents=True, exist_ok=True); run_thin_slice(d, seed=7, scenario_id='lab_profile_v0', drop_completion_prob=0.0)\"",
            "python scripts/export_bounded_review_packet.py --run-dir datasets/runs/assurance_eval_aies/runs/lab_profile_v0_seed7 --out datasets/runs/assurance_eval_aies/bounded_review_packet --scenario-id lab_profile_v0",
            "python scripts/export_aies_assurance_tables.py --in datasets/runs/assurance_eval_aies --out datasets/runs/assurance_eval_aies/tables",
            "python scripts/export_aies_review_packet_figure.py --in datasets/runs/assurance_eval_aies/bounded_review_packet --out datasets/runs/assurance_eval_aies/figures",
        ],
        "scenario_ids": ["lab_profile_v0", "warehouse_v0", "traffic_v0"],
        "primary_main_text_scenarios": ["lab_profile_v0", "warehouse_v0"],
        "proxy_bucket": "proxy_stress_only",
        "source_files": {
            "results_json": str(results_path),
            "negative_results_json": str(neg_path),
        },
        "output_checksums_sha256": {},
    }
    for p in sorted((in_dir).rglob("*")):
        if p.is_file() and p.name != "RUN_MANIFEST.json":
            run_manifest["output_checksums_sha256"][str(p.relative_to(in_dir))] = _sha256(p)
    (in_dir / "RUN_MANIFEST.json").write_text(
        json.dumps(run_manifest, indent=2) + "\n",
        encoding="utf-8",
    )

    readme = in_dir / "README.md"
    readme.write_text(
        "\n".join(
            [
                "# assurance_eval_aies",
                "",
                "AIES 2026 paper-facing assurance artifact bundle.",
                "",
                "## Main-text artifacts",
                "- `baseline_summary.json` (primary institutional baseline: lab_profile_v0)",
                "- `institutional_positive_summary.json` (lab + warehouse portability)",
                "- `negative_summary.json` (ablation/family/failure summaries)",
                "- `tables/baseline_table.tex`, `tables/portability_table.tex`",
                "- `tables/negative_ablation_table.tex`, `tables/failure_family_table.tex`",
                "",
                "## Supplement / proxy bucket",
                "- `proxy_stress_only/traffic_medical_proxy_summary.json`",
                "",
                "## Repro commands",
                "```bash",
                "export PYTHONPATH=impl/src",
                "export LABTRUST_KERNEL_DIR=kernel",
                "python scripts/run_assurance_eval.py --out datasets/runs/assurance_eval_aies",
                "python scripts/run_assurance_negative_eval.py --out datasets/runs/assurance_eval_aies --submission-mode",
                "python -c \"from pathlib import Path; from labtrust_portfolio.thinslice import run_thin_slice; d=Path('datasets/runs/assurance_eval_aies/runs/lab_profile_v0_seed7'); d.mkdir(parents=True, exist_ok=True); run_thin_slice(d, seed=7, scenario_id='lab_profile_v0', drop_completion_prob=0.0)\"",
                "python scripts/export_bounded_review_packet.py --run-dir datasets/runs/assurance_eval_aies/runs/lab_profile_v0_seed7 --out datasets/runs/assurance_eval_aies/bounded_review_packet --scenario-id lab_profile_v0",
                "python scripts/export_aies_assurance_tables.py --in datasets/runs/assurance_eval_aies --out datasets/runs/assurance_eval_aies/tables",
                "python scripts/export_aies_review_packet_figure.py --in datasets/runs/assurance_eval_aies/bounded_review_packet --out datasets/runs/assurance_eval_aies/figures",
                "```",
                "",
                "See `RUN_MANIFEST.json` for provenance and checksums.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Wrote AIES assurance bundle under {in_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

