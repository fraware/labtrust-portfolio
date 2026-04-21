from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .conformance import check_conformance, write_conformance_artifact
from .evidence import rewrite_evidence_bundle_artifact_paths
from .gatekeeper import allow_release
from .hashing import sha256_file
from .schema import validate

RELEASE_MANIFEST_SCHEMA = "policy/RELEASE_MANIFEST.v0.1.schema.json"
REQUIRED_ARTIFACTS = (
    "trace.json",
    "maestro_report.json",
    "evidence_bundle.json",
)


def build_release_manifest(
    release_id: str,
    kernel_version: str,
    artifacts: List[Path],
    path_base: Path | None = None,
    artifact_hashes: Optional[List[str]] = None,
) -> Dict[str, Any]:
    if artifact_hashes is not None and len(artifact_hashes) != len(artifacts):
        raise ValueError("artifact_hashes must have same length as artifacts")

    def _path_for_manifest(p: Path) -> str:
        if path_base is None:
            return str(p.as_posix())
        try:
            return str(p.relative_to(path_base).as_posix())
        except ValueError:
            return str(p.as_posix())

    def _digest(i: int, p: Path) -> str:
        if artifact_hashes is not None:
            return artifact_hashes[i]
        return sha256_file(p)

    return {
        "version": "0.1",
        "release_id": release_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace(
            "+00:00", "Z"
        ),
        "kernel_version": kernel_version,
        "artifacts": [
            {"path": _path_for_manifest(p), "sha256": _digest(i, p)}
            for i, p in enumerate(artifacts)
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
    existing: Dict[str, Any] = {}
    existing_manifest_path = run_dir / "release_manifest.json"
    if existing_manifest_path.exists():
        existing_text = existing_manifest_path.read_text(encoding="utf-8")
        existing = json.loads(existing_text)
        validate(existing, RELEASE_MANIFEST_SCHEMA)
    release_dir = releases_root / release_id
    release_dir.mkdir(parents=True, exist_ok=True)
    release_artifacts: List[Path] = []
    for name in REQUIRED_ARTIFACTS:
        src = run_dir / name
        dst = release_dir / name
        shutil.copy2(src, dst)
        release_artifacts.append(dst)
    conformance_path = write_conformance_artifact(release_dir)
    release_artifacts.append(conformance_path)
    rewrite_evidence_bundle_artifact_paths(
        release_dir / "evidence_bundle.json",
        ["trace.json", "maestro_report.json"],
    )
    kernel_version = existing.get("kernel_version", "0.1")
    manifest = build_release_manifest(
        release_id,
        kernel_version,
        release_artifacts,
        path_base=release_dir,
    )
    manifest_path = release_dir / "release_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    validate(manifest, RELEASE_MANIFEST_SCHEMA)
    return release_dir, manifest
