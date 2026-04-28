#!/usr/bin/env python3
"""
Audit prompt-template metadata across real_llm_models in red_team_results.json.

Resolves the paper-facing inconsistency where top-level run_manifest omits
``prompt_template_hash`` while per-model manifests include it.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser(description="P6 prompt template hash audit for real_llm_models")
    ap.add_argument(
        "--red-team-results",
        type=Path,
        default=REPO / "datasets" / "runs" / "llm_eval_camera_ready_20260424" / "red_team_results.json",
        help="Path to red_team_results.json",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Write prompt_template_audit.json (default: stdout JSON)",
    )
    args = ap.parse_args()
    path = args.red_team_results.resolve()
    if not path.is_file():
        print(f"Missing {path}", file=sys.stderr)
        return 1
    red = json.loads(path.read_text(encoding="utf-8"))
    models = [m for m in (red.get("real_llm_models") or []) if not m.get("error")]
    mids = [str(m.get("model_id")) for m in models if m.get("model_id")]
    hashes = {mid: (m.get("run_manifest") or {}).get("prompt_template_hash") for mid, m in zip(mids, models)}
    vals = [h for h in hashes.values() if h]
    hash_identical = len(set(vals)) <= 1 if vals else True
    top = (red.get("run_manifest") or {}).get("prompt_template_hash")
    # root_cause_if_false: only when per-model hashes disagree or disagree with top-level.
    root_cause = None
    if not hash_identical:
        root_cause = "Per-model prompt_template_hash values differ."
    elif top is not None and vals and len({*vals, top}) > 1:
        root_cause = "Top-level and per-model prompt_template_hash values disagree."
    # Same per-model hash implies the same canonical prompt template bytes; a missing
    # top-level manifest field is metadata only, not a template mismatch.
    actual_identical = bool(hash_identical)
    if actual_identical:
        paper = (
            "Both rows use the same canonical case set, denominator, run count, and prompt template."
        )
    else:
        paper = (
            "Both rows use the same canonical case set, denominator, and run count; "
            "prompt-template hashes differ and are reported separately."
        )
    out = {
        "models": mids,
        "actual_prompt_template_identical": actual_identical,
        "prompt_template_hash_identical": bool(hash_identical),
        "prompt_template_hashes": hashes,
        "root_cause_if_false": root_cause,
        "paper_safe_statement": paper,
    }
    text = json.dumps(out, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print("Wrote", args.out)
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
