#!/usr/bin/env python3
"""
Export P3 Replay corpus tables from replay_eval summary.json.

- Table 1: trace name, expected/observed replay_ok and divergence seq.
- Table 1b: localization visibility (detected, match, ambiguous, category, space).

Regenerate after replay_eval. Usage:
  python scripts/export_replay_corpus_table.py [--summary path] [--out-md path]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_SUMMARY = REPO / "datasets" / "runs" / "replay_eval" / "summary.json"

HDR1 = (
    "| Trace | expected_replay_ok | expected_divergence_at_seq | "
    "observed_replay_ok | observed_divergence_at_seq |"
)
SEP1 = (
    "|-------|--------------------|----------------------------|"
    "---------------------|----------------------------|"
)
HDR1B = (
    "| Trace | corpus_category | divergence_detected | "
    "localization_matches_expected | localization_ambiguous | "
    "root_cause_category | trace_json_bytes | state_hash_after_count | "
    "diagnostic_payload_bytes_approx |"
)
SEP1B = (
    "|-------|-----------------|---------------------|"
    "-------------------------------|-------------------------|"
    "----------------------|------------------|-------------------------|"
    "--------------------------------|"
)


def _fmt(x) -> str:
    if x is None:
        return "—"
    if isinstance(x, bool):
        return "true" if x else "false"
    return str(x)


def _loc_match_cell(r: dict) -> str:
    v = r.get("localization_matches_expected")
    if v is None:
        return "—"
    return "true" if v else "false"


def _ambig_cell(r: dict) -> str:
    v = r.get("localization_ambiguous")
    if v is None:
        return "—"
    return "true" if v else "false"


def build_markdown(
    data: dict,
    *,
    include_thin_slice: bool,
) -> str:
    per_trace = data.get("per_trace", [])
    rows = [
        r
        for r in per_trace
        if include_thin_slice or r.get("name") != "thin_slice"
    ]
    n = len(rows)
    lines = [
        "# Table 1 — Corpus and fidelity",
        "",
        "All corpus traces (from summary.json); "
        f"N = {n}. Regenerate with export_replay_corpus_table.py.",
        "",
        HDR1,
        SEP1,
    ]
    for r in rows:
        lines.append(
            f"| {r.get('name', '')} | {_fmt(r.get('expected_replay_ok'))} | "
            f"{_fmt(r.get('expected_divergence_at_seq'))} | "
            f"{_fmt(r.get('replay_ok'))} | {_fmt(r.get('divergence_at_seq'))} |"
        )
    desc_1b = (
        "Per-trace divergence detection, localization vs expected "
        "(when declared), ambiguous multi-diagnostic flag (reserved), "
        "root-cause category, and on-disk trace size / hash-field count / "
        "approximate diagnostic JSON size."
    )
    lines.extend(
        [
            "",
            "# Table 1b — Localization and corpus space (per trace)",
            "",
            desc_1b,
            "",
            HDR1B,
            SEP1B,
        ]
    )
    for r in rows:
        lines.append(
            f"| {r.get('name', '')} | {_fmt(r.get('corpus_category', '—'))} | "
            f"{_fmt(r.get('divergence_detected'))} | "
            f"{_loc_match_cell(r)} | {_ambig_cell(r)} | "
            f"{_fmt(r.get('root_cause_category'))} | "
            f"{_fmt(r.get('trace_json_bytes'))} | "
            f"{_fmt(r.get('state_hash_after_count'))} | "
            f"{_fmt(r.get('diagnostic_payload_bytes_approx'))} |"
        )
    css = data.get("corpus_space_summary") or {}
    if css:
        lines.extend(
            [
                "",
                "## Corpus space summary (aggregate, corpus rows only)",
                "",
                f"- corpus_traces_n: {css.get('corpus_traces_n', '—')}",
                f"- trace_json_bytes_sum: {css.get('trace_json_bytes_sum', '—')}",
                f"- trace_json_bytes_mean: {css.get('trace_json_bytes_mean', '—')}",
                f"- state_hash_after_count_sum: "
                f"{css.get('state_hash_after_count_sum', '—')}",
                f"- state_hash_after_count_mean: "
                f"{css.get('state_hash_after_count_mean', '—')}",
            ]
        )
        if "diagnostic_payload_bytes_approx_sum" in css:
            dsum = css.get("diagnostic_payload_bytes_approx_sum")
            dmean = css.get("diagnostic_payload_bytes_approx_mean")
            lines.append(f"- diagnostic_payload_bytes_approx_sum: {dsum}")
            lines.append(f"- diagnostic_payload_bytes_approx_mean: {dmean}")
    rss = data.get("process_peak_rss_bytes")
    if rss is not None:
        lines.extend(
            [
                "",
                "process_peak_rss_bytes (best-effort, end of eval process): "
                f"{rss}",
            ]
        )
    l1_twin_summary = data.get("l1_twin_summary")
    if l1_twin_summary:
        lines.extend(
            [
                "",
                "## L1 twin summary (multi-seed aggregate)",
                "",
                f"- n_seeds: {l1_twin_summary.get('n_seeds', '—')}",
                f"- all_pass: {_fmt(l1_twin_summary.get('all_pass'))}",
                f"- n_pass: {l1_twin_summary.get('n_pass', '—')}",
            ]
        )
        if "mean_time_ms" in l1_twin_summary:
            lines.append(f"- mean_time_ms: {l1_twin_summary.get('mean_time_ms')}")
            lines.append(f"- stdev_time_ms: {l1_twin_summary.get('stdev_time_ms')}")
            if "min_time_ms" in l1_twin_summary:
                lines.append(f"- min_time_ms: {l1_twin_summary.get('min_time_ms')}")
                lines.append(f"- max_time_ms: {l1_twin_summary.get('max_time_ms')}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Export P3 Replay corpus tables from summary.json"
    )
    ap.add_argument(
        "--summary",
        type=Path,
        default=DEFAULT_SUMMARY,
        help="Path to replay_eval summary.json",
    )
    ap.add_argument(
        "--include-thin-slice",
        action="store_true",
        default=True,
        help="Include thin_slice row (default True)",
    )
    ap.add_argument(
        "--no-include-thin-slice",
        action="store_false",
        dest="include_thin_slice",
        help="Exclude thin_slice from tables",
    )
    ap.add_argument(
        "--out-md",
        type=Path,
        default=None,
        help="Write markdown to this path (default: print to stdout only)",
    )
    args = ap.parse_args()
    if not args.summary.exists():
        print("Run scripts/replay_eval.py first to produce summary.json.")
        return 1
    data = json.loads(args.summary.read_text(encoding="utf-8"))
    if not data.get("per_trace"):
        print("No per_trace in summary.")
        return 1
    md = build_markdown(data, include_thin_slice=args.include_thin_slice)
    if args.out_md is not None:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(md, encoding="utf-8")
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
