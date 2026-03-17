#!/usr/bin/env python3
"""
Export E1 conformance challenge set as Table 1 (Markdown) for the draft.
Reads corpus_manifest.json from the corpus dir (default datasets/runs/p0_conformance_corpus).
If manifest has observed_tier/observed_pass/agreement, uses them; else runs checker.
Usage: python scripts/export_e1_corpus_table.py [--corpus DIR]
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Export E1 conformance corpus table")
    ap.add_argument(
        "--corpus",
        type=Path,
        default=REPO / "datasets" / "runs" / "p0_conformance_corpus",
        help="Corpus root (contains corpus_manifest.json)",
    )
    args = ap.parse_args()
    corpus_root = args.corpus.resolve()
    manifest_path = corpus_root / "corpus_manifest.json"
    if not manifest_path.exists():
        print("Run build_p0_conformance_corpus.py first to create the corpus.", file=sys.stderr)
        return 1

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    # Ensure observed fields: run checker if missing
    sys.path.insert(0, str(REPO / "impl" / "src"))
    if "LABTRUST_KERNEL_DIR" not in os.environ:
        os.environ["LABTRUST_KERNEL_DIR"] = str(REPO / "kernel")

    from labtrust_portfolio.conformance import check_conformance

    for m in manifest:
        if "observed_tier" in m and "agreement" in m:
            continue
        case_dir = corpus_root / f"case_{m['case_id']}"
        if not case_dir.exists():
            continue
        res = check_conformance(case_dir)
        m["observed_tier"] = res.tier
        m["observed_pass"] = res.passed
        m["agreement"] = (
            res.tier == m["expected_tier"] and res.passed == m["expected_pass"]
        )

    # Print Table 1 (Markdown)
    lines = [
        "## Table 1 — Conformance challenge set (E1)",
        "",
        "| Case ID | Fault injected | Expected outcome | Observed outcome | Agreement |",
        "|---------|-----------------|------------------|------------------|-----------|",
    ]
    for m in manifest:
        exp = f"Tier {m['expected_tier']} {'PASS' if m['expected_pass'] else 'FAIL'}"
        obs = f"Tier {m.get('observed_tier', '—')} {'PASS' if m.get('observed_pass') else 'FAIL'}"
        agree = "yes" if m.get("agreement", False) else "no"
        fault = m.get("fault_injected") or m.get("description") or ""
        if len(fault) > 48:
            fault = fault[:45] + "..."
        lines.append(f"| {m['case_id']} | {fault} | {exp} | {obs} | {agree} |")
    lines.append("")
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
