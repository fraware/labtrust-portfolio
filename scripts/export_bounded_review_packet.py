#!/usr/bin/env python3
"""
Export a bounded-access review packet for the AIES 2026 assurance sprint.

Usage:
  PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel \
    python scripts/export_bounded_review_packet.py \
      --run-dir <run_dir> \
      --out datasets/runs/assurance_eval_aies/bounded_review_packet
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "impl" / "src"))
if "LABTRUST_KERNEL_DIR" not in os.environ:
    os.environ["LABTRUST_KERNEL_DIR"] = str(REPO / "kernel")

DEFAULT_PACK = REPO / "profiles" / "lab" / "v0.1" / "assurance_pack_instantiation.json"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _git_head() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=str(REPO),
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        return out or "unknown"
    except Exception:
        return "unknown"


def _copy_required(run_dir: Path, out_dir: Path, names: List[str]) -> Dict[str, str]:
    copied: Dict[str, str] = {}
    for name in names:
        src = run_dir / name
        if not src.exists():
            continue
        dst = out_dir / name
        shutil.copy2(src, dst)
        copied[name] = _sha256(dst)
    return copied


def main() -> int:
    ap = argparse.ArgumentParser(description="Export bounded review packet")
    ap.add_argument("--run-dir", type=Path, required=True, help="Source run directory")
    ap.add_argument("--out", type=Path, required=True, help="Packet output directory")
    ap.add_argument("--pack", type=Path, default=DEFAULT_PACK, help="Assurance pack JSON")
    ap.add_argument(
        "--scenario-id",
        type=str,
        default="lab_profile_v0",
        help="Scenario id under review",
    )
    ap.add_argument(
        "--review-mode",
        choices=["schema_only", "schema_plus_presence", "full_review"],
        default="full_review",
        help="Review mode for packet output",
    )
    ap.add_argument(
        "--claim-id",
        type=str,
        default="AIES-C1",
        help="Identifier for claim under review",
    )
    args = ap.parse_args()

    run_dir = args.run_dir.resolve()
    if not run_dir.is_dir():
        print(f"run-dir is not a directory: {run_dir}", file=sys.stderr)
        return 1
    if not args.pack.exists():
        print(f"pack not found: {args.pack}", file=sys.stderr)
        return 1

    out_dir = args.out.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    from labtrust_portfolio.assurance_review_pipeline import review_assurance_pipeline

    review_out = review_assurance_pipeline(
        run_dir,
        args.pack,
        args.scenario_id,
        args.review_mode,
        profile_dir=args.pack.parent,
        repo_root=REPO,
    )

    required = [
        "trace.json",
        "evidence_bundle.json",
        "release_manifest.json",
        "maestro_report.json",
    ]
    copied_hashes = _copy_required(run_dir, out_dir, required)

    pack_dst = out_dir / "assurance_pack.json"
    shutil.copy2(args.pack, pack_dst)
    copied_hashes["assurance_pack.json"] = _sha256(pack_dst)

    claim = {
        "claim_id": args.claim_id,
        "claim_text": (
            "The submitted run provides machine-checkable evidence that the "
            "declared assurance controls are structurally supported for the "
            "reviewed scenario."
        ),
        "scenario_id": args.scenario_id,
        "review_mode": args.review_mode,
        "run_dir_source": str(run_dir),
        "bounded_access_note": (
            "This packet is intended for external review with bounded artifact "
            "access and no privileged runtime internals."
        ),
    }
    (out_dir / "claim.json").write_text(json.dumps(claim, indent=2) + "\n", encoding="utf-8")
    copied_hashes["claim.json"] = _sha256(out_dir / "claim.json")

    (out_dir / "review_output.json").write_text(
        json.dumps(review_out, indent=2) + "\n",
        encoding="utf-8",
    )
    copied_hashes["review_output.json"] = _sha256(out_dir / "review_output.json")

    summary = {
        "claim_id": args.claim_id,
        "scenario_id": args.scenario_id,
        "review_mode": args.review_mode,
        "review_exit_ok": bool(review_out.get("exit_ok")),
        "failure_stage": review_out.get("failure_stage"),
        "failure_reason_codes": review_out.get("failure_reason_codes") or [],
        "validated_checks": [
            "pack_structure",
            "artifact_presence_schema",
            "scenario_alignment",
            "ponr_consistency",
            "control_coverage",
            "provenance_consistency",
        ],
        "out_of_scope": [
            "semantic domain sufficiency",
            "collusive full-chain forgery",
            "regulatory certification adequacy",
        ],
    }
    (out_dir / "review_packet_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    copied_hashes["review_packet_summary.json"] = _sha256(out_dir / "review_packet_summary.json")

    summary_csv = out_dir / "review_packet_summary.csv"
    summary_csv.write_text(
        "claim_id,scenario_id,review_mode,review_exit_ok,failure_stage,failure_reason_codes\n"
        f"{args.claim_id},{args.scenario_id},{args.review_mode},{int(bool(review_out.get('exit_ok')))},"
        f"{review_out.get('failure_stage') or ''},"
        f"\"{';'.join(review_out.get('failure_reason_codes') or [])}\"\n",
        encoding="utf-8",
    )
    copied_hashes["review_packet_summary.csv"] = _sha256(summary_csv)

    readme = out_dir / "README.md"
    readme.write_text(
        "\n".join(
            [
                "# Bounded Review Packet",
                "",
                "This folder is a bounded-access external reviewer packet.",
                "",
                "## Contents",
                "- `claim.json`: accountability claim under review",
                "- `assurance_pack.json`: machine-checkable assurance pack",
                "- `trace.json`: runtime trace artifact (if present in run dir)",
                "- `evidence_bundle.json`: evidence bundle artifact (if present)",
                "- `release_manifest.json`: release manifest (if present)",
                "- `review_output.json`: checker verdict and failure codes",
                "- `review_packet_summary.json`: compact reviewer-facing summary",
                "- `packet_manifest.json`: provenance and checksums",
                "",
                "## Reviewer intent",
                "A third-party reviewer can validate what was checked, what passed/failed, "
                "and what remains out of scope under bounded artifact access.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    copied_hashes["README.md"] = _sha256(readme)

    packet_manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit_sha": _git_head(),
        "script": "export_bounded_review_packet.py",
        "source_run_dir": str(run_dir),
        "scenario_id": args.scenario_id,
        "review_mode": args.review_mode,
        "files_sha256": copied_hashes,
    }
    (out_dir / "packet_manifest.json").write_text(
        json.dumps(packet_manifest, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote packet to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

