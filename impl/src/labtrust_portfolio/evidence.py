from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, List
from .hashing import sha256_file

def build_evidence_bundle(run_id: str, kernel_version: str, artifacts: List[Path], schema_ids: List[str], schema_validation_ok: bool, replay_ok: bool, replay_diag: str) -> Dict[str, Any]:
    if len(artifacts) != len(schema_ids):
        raise ValueError("artifacts and schema_ids must have same length")

    items = []
    for p, sid in zip(artifacts, schema_ids):
        items.append({
            "path": str(p.as_posix()),
            "sha256": sha256_file(p),
            "schema_id": sid,
        })

    return {
        "version": "0.1",
        "run_id": run_id,
        "kernel_version": kernel_version,
        "artifacts": items,
        "verification": {
            "schema_validation_ok": schema_validation_ok,
            "replay_ok": replay_ok,
            "replay_diagnostics": replay_diag,
        },
    }
