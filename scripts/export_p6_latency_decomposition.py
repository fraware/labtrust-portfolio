#!/usr/bin/env python3
"""
Export P6 latency decomposition table from adapter_latency.json (when --latency-decomposition was used).
Usage: python scripts/export_p6_latency_decomposition.py [--out-dir path] [--out file.md]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO / "datasets" / "runs" / "llm_eval"


def main() -> int:
    ap = argparse.ArgumentParser(description="Export P6 latency decomposition table")
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    path = args.out_dir / "adapter_latency.json"
    if not path.exists():
        print("Run llm_redteam_eval.py with --run-adapter --latency-decomposition first.", file=sys.stderr)
        return 1

    data = json.loads(path.read_text(encoding="utf-8"))
    decomp = data.get("latency_decomposition")
    if not decomp:
        print("No latency_decomposition in adapter_latency.json.", file=sys.stderr)
        return 0

    lines = [
        "# Latency decomposition",
        "",
        "Per-step validation and capture timings (ms). Run with --run-adapter --latency-decomposition.",
        "",
        "| Component | p50 | p95 | p99 | max | stdev | samples |",
        "|-----------|-----|-----|-----|-----|-------|--------|",
    ]
    for name, st in decomp.items():
        lines.append(
            f"| {name} | {st.get('p50', '-')} | {st.get('p95', '-')} | "
            f"{st.get('p99', '-')} | {st.get('max', '-')} | {st.get('stdev', '-')} | {st.get('samples', '-')} |"
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
