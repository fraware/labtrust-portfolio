from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .hashing import sha256_file, sha256_bytes


def _redact_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Replace payload with content-addressed ref (structure preserved)."""
    blob = json.dumps(
        payload, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    ref = sha256_bytes(blob)
    return {"_redacted_ref": ref}


def redact_trace_payloads(trace: Dict[str, Any]) -> Dict[str, Any]:
    """
    Copy of trace with event payloads replaced by content-addressed refs.
    Structure (event types, order, timestamps, state_hash_after) preserved.
    """
    out = dict(trace)
    out["events"] = []
    for ev in trace.get("events", []):
        e = dict(ev)
        if "payload" in e and e["payload"]:
            e["payload"] = _redact_payload(e["payload"])
        out["events"].append(e)
    return out


def build_evidence_bundle(
    run_id: str,
    kernel_version: str,
    artifacts: List[Path],
    schema_ids: List[str],
    schema_validation_ok: bool,
    replay_ok: bool,
    replay_diag: str,
    verification_mode: str = "evaluator",
    redaction_manifest: Dict[str, Any] | None = None,
    artifact_display_paths: List[str] | None = None,
) -> Dict[str, Any]:
    if len(artifacts) != len(schema_ids):
        raise ValueError("artifacts and schema_ids must have same length")
    if (
        artifact_display_paths is not None
        and len(artifact_display_paths) != len(artifacts)
    ):
        raise ValueError(
            "artifact_display_paths must have same length as artifacts"
        )

    items = []
    for i, (p, sid) in enumerate(zip(artifacts, schema_ids)):
        item_path = (
            artifact_display_paths[i]
            if artifact_display_paths is not None
            else str(p.as_posix())
        )
        items.append({
            "path": item_path,
            "sha256": sha256_file(p),
            "schema_id": sid,
        })

    bundle: Dict[str, Any] = {
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
    bundle["verification_mode"] = verification_mode or "evaluator"
    if redaction_manifest:
        bundle["redaction_manifest"] = redaction_manifest
    return bundle


def rewrite_evidence_bundle_artifact_paths(
    bundle_path: Path,
    artifact_display_paths: List[str],
) -> None:
    """Rewrite evidence bundle artifacts[].path values in-place."""
    data = json.loads(bundle_path.read_text(encoding="utf-8"))
    artifacts = data.get("artifacts", [])
    if len(artifacts) != len(artifact_display_paths):
        raise ValueError(
            "artifact_display_paths length must match "
            "evidence artifacts length"
        )
    for art, display in zip(artifacts, artifact_display_paths):
        art["path"] = display
    bundle_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
