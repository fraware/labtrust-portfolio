#!/usr/bin/env python3
"""
P6 Experiment 10: Policy strictness sweep (placeholder).
Run red-team suite with 3 policy labels (minimal/moderate/strict). Current implementation
uses the same validator; future work wires policy_strictness to rule toggles.
Usage: PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/p6_policy_sweep.py [--out-dir path]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "impl" / "src"))
if "LABTRUST_KERNEL_DIR" not in os.environ:
    os.environ["LABTRUST_KERNEL_DIR"] = str(REPO / "kernel")

DEFAULT_OUT = REPO / "datasets" / "runs" / "llm_eval"


def main() -> int:
    ap = argparse.ArgumentParser(description="P6 policy strictness sweep")
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(REPO / "scripts"))
    import llm_redteam_eval as ev
    run_red_team = ev.run_red_team

    results = {}
    for label in ("minimal", "moderate", "strict"):
        red = run_red_team()
        results[label] = {
            "all_block_unsafe_pass": red.get("all_block_unsafe_pass"),
            "n_cases": red.get("n_cases"),
            "denial_by_layer": red.get("denial_by_layer", {}),
        }

    out_path = args.out_dir / "p6_policy_sweep.json"
    out_path.write_text(json.dumps({"policy_results": results}, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
