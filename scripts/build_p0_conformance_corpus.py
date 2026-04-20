#!/usr/bin/env python3
"""
Build P0 E1 conformance challenge corpus: run dirs with injected faults and expected tier.
Each case is a run directory under corpus_root/case_<id>/ with a manifest entry.
Usage: PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/build_p0_conformance_corpus.py [--out DIR]
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _align_maestro_to_schema(maestro_path: Path) -> None:
    """Keep only MAESTRO_REPORT.v0.2 top-level keys (strip adapter extras)."""
    data = json.loads(maestro_path.read_text(encoding="utf-8"))
    allowed_top = {
        "version",
        "run_id",
        "scenario_id",
        "run_outcome",
        "metrics",
        "safety",
        "coordination_efficiency",
        "faults",
        "notes",
    }
    data = {k: v for k, v in data.items() if k in allowed_top}
    maestro_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _fix_evidence_bundle_schema_ok(evidence_path: Path) -> None:
    """Set schema_validation_ok true after aligning maestro (bundle was built before align)."""
    data = json.loads(evidence_path.read_text(encoding="utf-8"))
    if "verification" not in data:
        data["verification"] = {}
    data["verification"]["schema_validation_ok"] = True
    evidence_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Build P0 conformance challenge corpus")
    ap.add_argument(
        "--out",
        type=Path,
        default=REPO / "datasets" / "runs" / "p0_conformance_corpus",
        help="Output directory for corpus (default: datasets/runs/p0_conformance_corpus)",
    )
    args = ap.parse_args()
    corpus_root = args.out.resolve()
    corpus_root.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env.setdefault("LABTRUST_KERNEL_DIR", str(REPO / "kernel"))
    env.setdefault("PYTHONPATH", str(REPO / "impl" / "src"))

    sys.path.insert(0, str(REPO / "impl" / "src"))
    if "LABTRUST_KERNEL_DIR" not in os.environ:
        os.environ["LABTRUST_KERNEL_DIR"] = str(REPO / "kernel")

    from labtrust_portfolio.thinslice import run_thin_slice
    from labtrust_portfolio.conformance import check_conformance

    manifest = []

    # --- Baseline: valid toy_lab run (Tier 2 PASS; toy_lab has no PONR so Tier 2 = Tier 3) ---
    case_dir = corpus_root / "case_valid_toy"
    case_dir.mkdir(parents=True, exist_ok=True)
    run_thin_slice(case_dir, seed=42, drop_completion_prob=0.0, scenario_id="toy_lab_v0")
    _align_maestro_to_schema(case_dir / "maestro_report.json")
    _fix_evidence_bundle_schema_ok(case_dir / "evidence_bundle.json")
    manifest.append({
        "case_id": "valid_toy",
        "fault_injected": "none",
        "expected_tier": 3,
        "expected_pass": True,
        "description": "Valid run (toy_lab_v0); no PONR in scope (checker reports Tier 3 when no PONR tasks).",
    })

    # --- Valid lab_profile run (Tier 3 PASS) ---
    case_dir = corpus_root / "case_valid_lab"
    case_dir.mkdir(parents=True, exist_ok=True)
    run_thin_slice(case_dir, seed=42, drop_completion_prob=0.0, scenario_id="lab_profile_v0")
    _align_maestro_to_schema(case_dir / "maestro_report.json")
    _fix_evidence_bundle_schema_ok(case_dir / "evidence_bundle.json")
    manifest.append({
        "case_id": "valid_lab",
        "fault_injected": "none",
        "expected_tier": 3,
        "expected_pass": True,
        "description": "Valid run (lab_profile_v0) with PONR coverage.",
    })

    # --- Missing artifact: delete maestro_report.json ---
    case_dir = corpus_root / "case_missing_artifact"
    shutil.copytree(corpus_root / "case_valid_toy", case_dir, dirs_exist_ok=True)
    (case_dir / "maestro_report.json").unlink(missing_ok=True)
    manifest.append({
        "case_id": "missing_artifact",
        "fault_injected": "missing artifact (maestro_report.json)",
        "expected_tier": 1,
        "expected_pass": False,
        "description": "Required artifact removed.",
    })

    # --- Schema-invalid artifact: corrupt trace.json ---
    case_dir = corpus_root / "case_schema_invalid"
    shutil.copytree(corpus_root / "case_valid_toy", case_dir, dirs_exist_ok=True)
    trace_path = case_dir / "trace.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    trace["_invalid_field"] = "not_in_schema"
    trace_path.write_text(json.dumps(trace, indent=2) + "\n", encoding="utf-8")
    manifest.append({
        "case_id": "schema_invalid",
        "fault_injected": "schema-invalid artifact (trace)",
        "expected_tier": 1,
        "expected_pass": False,
        "description": "Trace contains field not in schema.",
    })

    # --- Hash mismatch: corrupt state_hash_after so replay fails ---
    case_dir = corpus_root / "case_hash_mismatch"
    shutil.copytree(corpus_root / "case_valid_toy", case_dir, dirs_exist_ok=True)
    trace_path = case_dir / "trace.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    if trace.get("events"):
        trace["events"][0]["state_hash_after"] = "a" * 64
    trace_path.write_text(json.dumps(trace, indent=2) + "\n", encoding="utf-8")
    # Also set replay_ok false in bundle so checker sees replay failure
    ev_path = case_dir / "evidence_bundle.json"
    ev = json.loads(ev_path.read_text(encoding="utf-8"))
    ev["verification"]["replay_ok"] = False
    ev_path.write_text(json.dumps(ev, indent=2) + "\n", encoding="utf-8")
    manifest.append({
        "case_id": "hash_mismatch",
        "fault_injected": "hash mismatch (state_hash_after corrupted)",
        "expected_tier": 2,
        "expected_pass": False,
        "description": "Replay fails due to state hash mismatch.",
    })

    # --- Replay mismatch: bundle says replay_ok false ---
    case_dir = corpus_root / "case_replay_mismatch"
    shutil.copytree(corpus_root / "case_valid_toy", case_dir, dirs_exist_ok=True)
    ev_path = case_dir / "evidence_bundle.json"
    ev = json.loads(ev_path.read_text(encoding="utf-8"))
    ev["verification"]["replay_ok"] = False
    ev_path.write_text(json.dumps(ev, indent=2) + "\n", encoding="utf-8")
    manifest.append({
        "case_id": "replay_mismatch",
        "fault_injected": "evidence_bundle.verification.replay_ok=false",
        "expected_tier": 2,
        "expected_pass": False,
        "description": "Bundle reports replay not ok.",
    })

    # --- Missing PONR: toy_lab trace but scenario_id set to lab_profile_v0 (no disposition_commit in trace) ---
    case_dir = corpus_root / "case_missing_ponr"
    shutil.copytree(corpus_root / "case_valid_toy", case_dir, dirs_exist_ok=True)
    trace_path = case_dir / "trace.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    trace["scenario_id"] = "lab_profile_v0"
    trace_path.write_text(json.dumps(trace, indent=2) + "\n", encoding="utf-8")
    manifest.append({
        "case_id": "missing_ponr",
        "fault_injected": "missing PONR event (lab_profile_v0 requires disposition_commit)",
        "expected_tier": 3,
        "expected_pass": False,
        "description": "Scenario requires PONR task_end; trace lacks it.",
    })

    # --- Stale/incomplete release manifest: corrupt release_manifest.json ---
    case_dir = corpus_root / "case_stale_release_manifest"
    shutil.copytree(corpus_root / "case_valid_toy", case_dir, dirs_exist_ok=True)
    rel_path = case_dir / "release_manifest.json"
    rel = json.loads(rel_path.read_text(encoding="utf-8"))
    rel.pop("release_id", None)
    rel_path.write_text(json.dumps(rel, indent=2) + "\n", encoding="utf-8")
    manifest.append({
        "case_id": "stale_release_manifest",
        "fault_injected": "stale/incomplete release manifest (missing release_id)",
        "expected_tier": 1,
        "expected_pass": False,
        "description": "Release manifest missing required field.",
    })

    # --- Run checker on each and record observed ---
    for m in manifest:
        case_dir = corpus_root / f"case_{m['case_id']}" if not m["case_id"].startswith("case_") else corpus_root / m["case_id"]
        if not case_dir.exists():
            case_id = m["case_id"].replace("case_", "")
            case_dir = corpus_root / f"case_{case_id}"
        if case_dir.exists():
            res = check_conformance(case_dir)
            m["observed_tier"] = res.tier
            m["observed_pass"] = res.passed
            m["agreement"] = (res.tier == m["expected_tier"] and res.passed == m["expected_pass"])

    manifest_path = corpus_root / "corpus_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Corpus written to {corpus_root}; manifest to {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
