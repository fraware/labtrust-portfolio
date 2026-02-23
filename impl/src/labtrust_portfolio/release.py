from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
from .hashing import sha256_file
from datetime import datetime, timezone

def build_release_manifest(release_id: str, kernel_version: str, artifacts: List[Path]) -> Dict[str, Any]:
    return {
        "version": "0.1",
        "release_id": release_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
        "kernel_version": kernel_version,
        "artifacts": [{"path": str(p.as_posix()), "sha256": sha256_file(p)} for p in artifacts],
    }
