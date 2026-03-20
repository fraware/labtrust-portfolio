#!/usr/bin/env python3
"""
Export P6 artifact SHA256 hashes and appendix markdown for reproduction.
Reads artifact files from the llm_eval run dir; outputs p6_artifact_hashes.json
and optional markdown for Appendix A.
Usage: PYTHONPATH=impl/src python scripts/export_p6_artifact_hashes.py [--out-dir path] [--repo-url URL] [--tag TAG] [--markdown]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO / "datasets" / "runs" / "llm_eval"

ARTIFACTS = [
    "red_team_results.json",
    "confusable_deputy_results.json",
    "adapter_latency.json",
    "e2e_denial_trace.json",
    "baseline_comparison.json",
    "baseline_comparison_args.json",
    "denial_trace_stats.json",
]

# Map artifact filename to paper table id for reproducibility table
ARTIFACT_TO_TABLE = {
    "red_team_results.json": "Table 1 / 1b",
    "confusable_deputy_results.json": "Table 1",
    "adapter_latency.json": "Table 2",
    "e2e_denial_trace.json": "Case study",
    "baseline_comparison.json": "Table (tool-level)",
    "baseline_comparison_args.json": "Table (argument-level)",
    "denial_trace_stats.json": "Table 2",
}


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Export P6 artifact hashes and appendix markdown"
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT,
        help="Directory containing P6 eval artifacts (llm_eval)",
    )
    ap.add_argument(
        "--repo-url",
        type=str,
        default="https://github.com/<org>/labtrust-portfolio",
        help="Repository URL for appendix",
    )
    ap.add_argument(
        "--tag",
        type=str,
        default="v0.1-p6-draft",
        help="Git tag for reproduction",
    )
    ap.add_argument(
        "--markdown",
        action="store_true",
        help="Print appendix markdown (commands + repo + hashes)",
    )
    args = ap.parse_args()

    sys.path.insert(0, str(REPO / "impl" / "src"))
    from labtrust_portfolio.hashing import sha256_file

    hashes = {}
    for name in ARTIFACTS:
        p = args.out_dir / name
        if p.exists():
            hashes[name] = sha256_file(p)

    # Per-table reproducibility rows: link each result to artifact hash and run_manifest
    reproducibility_table = []
    for name in ARTIFACTS:
        p = args.out_dir / name
        if not p.exists():
            continue
        artifact_hash = hashes.get(name, "")
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            reproducibility_table.append({
                "table_id": ARTIFACT_TO_TABLE.get(name, name),
                "artifact": name,
                "model_id": None,
                "timestamp_iso": None,
                "seed": None,
                "prompt_template_hash": None,
                "evaluator_version": None,
                "policy_version": None,
                "artifact_hash": artifact_hash,
            })
            continue
        rm = data.get("run_manifest") or {}
        if name == "red_team_results.json" and data.get("real_llm_models"):
            for m in data["real_llm_models"]:
                m_rm = m.get("run_manifest") or {}
                reproducibility_table.append({
                    "table_id": ARTIFACT_TO_TABLE.get(name, name),
                    "artifact": name,
                    "model_id": m_rm.get("model_id") or m.get("model_id"),
                    "timestamp_iso": m_rm.get("timestamp_iso") or rm.get("timestamp_iso"),
                    "seed": m_rm.get("n_runs_per_case"),
                    "prompt_template_hash": m_rm.get("prompt_template_hash"),
                    "evaluator_version": m_rm.get("evaluator_version") or rm.get("evaluator_version"),
                    "policy_version": m_rm.get("policy_version") or rm.get("policy_version"),
                    "artifact_hash": artifact_hash,
                })
        else:
            reproducibility_table.append({
                "table_id": ARTIFACT_TO_TABLE.get(name, name),
                "artifact": name,
                "model_id": rm.get("real_llm_model_id") or rm.get("model_id"),
                "timestamp_iso": rm.get("timestamp_iso"),
                "seed": rm.get("seeds") or rm.get("adapter_seeds"),
                "prompt_template_hash": rm.get("prompt_template_hash"),
                "evaluator_version": rm.get("evaluator_version"),
                "policy_version": rm.get("policy_version"),
                "artifact_hash": artifact_hash,
            })

    out_json = args.out_dir / "p6_artifact_hashes.json"
    out_data = {
        "artifacts": hashes,
        "reproducibility_table": reproducibility_table,
        "run_dir": str(args.out_dir),
        "repo_url": args.repo_url,
        "tag": args.tag,
    }
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(out_data, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out_json}")

    if args.markdown:
        lines = [
            "## Appendix A. Reproduction and artifact hashes",
            "",
            "**Environment.** Set `PYTHONPATH=impl/src` and `LABTRUST_KERNEL_DIR=kernel` (from repo root).",
            "",
            "**Commands (exact reproduction).**",
            "```",
            "python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval",
            "python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval --run-adapter --denial-stats",
            "python scripts/llm_redteam_eval.py --out datasets/runs/llm_eval --run-baseline",
            "python scripts/export_llm_redteam_table.py --out-dir datasets/runs/llm_eval",
            "python scripts/export_p6_baseline_table.py --out-dir datasets/runs/llm_eval",
            "python scripts/export_p6_firewall_flow.py",
            "python scripts/plot_llm_adapter_latency.py",
            "```",
            "",
            f"**Repository.** {args.repo_url}  Tag: `{args.tag}`",
            "",
            "**Artifact hashes (SHA256).**",
            "",
            "| Artifact | SHA256 |",
            "|----------|--------|",
        ]
        for name, h in sorted(hashes.items()):
            lines.append(f"| {name} | {h} |")
        lines.append("")
        print("\n".join(lines))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
