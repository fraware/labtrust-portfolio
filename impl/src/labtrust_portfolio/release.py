from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .conformance import check_conformance
from .gatekeeper import allow_release
from .hashing import sha256_file
from .schema import validate

RELEASE_MANIFEST_SCHEMA = "policy/RELEASE_MANIFEST.v0.1.schema.json"
REQUIRED_ARTIFACTS = (
    "trace.json",
    "maestro_report.json",
    "evidence_bundle.json",
    "release_manifest.json",
)


def build_release_manifest(
    release_id: str,
    kernel_version: str,
    artifacts: List[Path],
) -> Dict[str, Any]:
    return {
        "version": "0.1",
        "release_id": release_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace(
            "+00:00", "Z"
        ),
        "kernel_version": kernel_version,
        "artifacts": [
            {"path": str(p.as_posix()), "sha256": sha256_file(p)}
            for p in artifacts
        ],
    }


def release_dataset(
    run_dir: Path,
    release_id: str,
    releases_root: Path,
    *,
    check_contracts: bool = False,
) -> Tuple[Path, Dict[str, Any]]:
    """
    Copy a run to datasets/releases/<release_id>/, validate artifacts, and
    write a new release manifest. Returns (release_dir, manifest_dict).
    Refuses release unless conformance is Tier 2 or higher (PONR gate).
    When check_contracts is True, also requires contract validator to allow
    all trace events (strict PONR gating).
    """
    run_dir = run_dir.resolve()
    releases_root = releases_root.resolve()
    if not allow_release(run_dir, check_contracts=check_contracts):
        result = check_conformance(run_dir)
        raise ValueError(f"Release denied: {result.message()}")
    for name in REQUIRED_ARTIFACTS:
        if not (run_dir / name).exists():
            raise FileNotFoundError(
                f"Run directory missing required artifact: {run_dir / name}"
            )
    existing_manifest_path = run_dir / "release_manifest.json"
    existing = json.loads(existing_manifest_path.read_text(encoding="utf-8"))
    validate(existing, RELEASE_MANIFEST_SCHEMA)
    release_dir = releases_root / release_id
    release_dir.mkdir(parents=True, exist_ok=True)
    new_artifacts: List[Path] = []
    for name in REQUIRED_ARTIFACTS:
        src = run_dir / name
        dst = release_dir / name
        shutil.copy2(src, dst)
        new_artifacts.append(dst)
    kernel_version = existing.get("kernel_version", "0.1")
    manifest = build_release_manifest(
        release_id, kernel_version, new_artifacts
    )
    manifest_path = release_dir / "release_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    validate(manifest, RELEASE_MANIFEST_SCHEMA)
    return release_dir, manifest
