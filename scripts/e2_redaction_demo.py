#!/usr/bin/env python3
"""
E2 (Restricted auditability): Run thin-slice once, redact trace payloads,
write redacted trace to datasets/runs/e2_redaction_demo for CI and local use.
Usage:
  PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/e2_redaction_demo.py
  [--out DIR]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "impl" / "src"))
if "LABTRUST_KERNEL_DIR" not in os.environ:
    os.environ["LABTRUST_KERNEL_DIR"] = str(REPO_ROOT / "kernel")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="E2: Produce one redacted trace under datasets/runs"
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "datasets" / "runs" / "e2_redaction_demo",
        help="Output directory (trace.json + trace_redacted.json)",
    )
    args = ap.parse_args()

    from labtrust_portfolio.thinslice import run_thin_slice
    from labtrust_portfolio.evidence import redact_trace_payloads, build_evidence_bundle
    from labtrust_portfolio.replay import replay_trace
    from labtrust_portfolio.schema import validate

    args.out.mkdir(parents=True, exist_ok=True)
    run_thin_slice(args.out, seed=1, drop_completion_prob=0.0)
    trace_path = args.out / "trace.json"
    if not trace_path.exists():
        print("trace.json not produced", file=sys.stderr)
        return 1
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    redacted = redact_trace_payloads(trace)
    redacted_path = args.out / "trace_redacted.json"
    redacted_path.write_text(
        json.dumps(redacted, indent=2) + "\n", encoding="utf-8"
    )
    # Redacted payloads are content-addressed refs; replay expects full payloads (e.g. task_id).
    # E2 redacted trace is for audit only; do not run L0 replay on it.
    replay_ok = False
    replay_diag = "redacted trace not replayed (payloads replaced by refs; structure preserved for audit)"
    schema_ok = True
    try:
        validate(redacted, "trace/TRACE.v0.1.schema.json")
    except Exception:
        schema_ok = False
    run_id = trace.get("run_id", "run_e2_redacted")
    kernel_version = "0.1"
    schema_trace_id = "https://example.org/labtrust/kernel/trace/TRACE.v0.1"
    schema_maestro_id = "https://example.org/labtrust/kernel/eval/MAESTRO_REPORT.v0.2"
    maestro_path = args.out / "maestro_report.json"
    redaction_manifest = {
        "policy_ref": "e2_redaction_v0.1",
        "redacted_artifacts": ["trace.json"],
        "reason": "payloads replaced by content-addressed refs; structure preserved",
    }
    bundle_redacted = build_evidence_bundle(
        run_id=run_id,
        kernel_version=kernel_version,
        artifacts=[redacted_path, maestro_path],
        schema_ids=[schema_trace_id, schema_maestro_id],
        schema_validation_ok=schema_ok,
        replay_ok=replay_ok,
        replay_diag=replay_diag,
        verification_mode="evaluator",
        redaction_manifest=redaction_manifest,
    )
    bundle_path = args.out / "evidence_bundle_redacted.json"
    bundle_path.write_text(json.dumps(bundle_redacted, indent=2) + "\n", encoding="utf-8")
    print(f"E2 redaction: {redacted_path}; bundle: {bundle_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
