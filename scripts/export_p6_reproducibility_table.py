#!/usr/bin/env python3
"""
Export P6 appendix reproducibility table: one row per reported table with
model_id, timestamp, seed, prompt_template_hash, evaluator_version, policy_version, artifact_hash.
Reads from p6_artifact_hashes.json (run export_p6_artifact_hashes.py first) or builds from artifacts.
Usage: PYTHONPATH=impl/src python scripts/export_p6_reproducibility_table.py [--out-dir path] [--out file.md]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO / "datasets" / "runs" / "llm_eval"


def _fmt(v, max_len: int | None = None) -> str:
    if v is None:
        return "-"
    if isinstance(v, list):
        s = ",".join(str(x) for x in v[:5]) + ("..." if len(v) > 5 else "")
    else:
        s = str(v)
    if max_len and len(s) > max_len:
        return s[:max_len] + "..."
    return s or "-"


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Export P6 appendix reproducibility table"
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help="Directory containing p6_artifact_hashes.json and artifacts",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Write table to this file (default: stdout)",
    )
    args = ap.parse_args()

    hashes_path = args.out_dir / "p6_artifact_hashes.json"
    if not hashes_path.exists():
        print("Run export_p6_artifact_hashes.py first to create", hashes_path, file=sys.stderr)
        return 1

    data = json.loads(hashes_path.read_text(encoding="utf-8"))
    rows = data.get("reproducibility_table") or []
    if not rows:
        print("No reproducibility_table in p6_artifact_hashes.json", file=sys.stderr)
        return 1

    lines = [
        "## Reproducibility: result-to-artifact mapping",
        "",
        "Every result in the paper maps to one exact artifact. Table hash is SHA256 of the artifact file.",
        "",
        "| Table | Artifact | model_id | timestamp | seed | prompt_template_hash | evaluator_version | policy_version | artifact_hash |",
        "|-------|----------|----------|-----------|------|----------------------|-------------------|----------------|---------------|",
    ]
    for r in rows:
        lines.append(
            "| " + " | ".join([
                _fmt(r.get("table_id")),
                _fmt(r.get("artifact")),
                _fmt(r.get("model_id")),
                _fmt(r.get("timestamp_iso")),
                _fmt(r.get("seed")),
                _fmt(r.get("prompt_template_hash"), 16),
                _fmt(r.get("evaluator_version")),
                _fmt(r.get("policy_version")),
                _fmt(r.get("artifact_hash"), 16),
            ]) + " |"
        )
    lines.append("")
    text = "\n".join(lines)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
