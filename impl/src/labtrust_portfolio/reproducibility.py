"""
P6 reproducibility: prompt template hash, evaluator version, policy version.
Used by llm_redteam_eval and export scripts for run-manifest audit and appendix table.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any


EVALUATOR_VERSION = "llm_redteam_eval.v1"


def sha256_utf8(s: str) -> str:
    """SHA256 hex digest of UTF-8 encoded string."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def get_real_llm_variant_fingerprint(prompt_variants: list[str]) -> str:
    """Hash of active real-LLM prompt variants (sorted for stability)."""
    norm = sorted(set(prompt_variants))
    return sha256_utf8("p6_prompt_variants:" + json.dumps(norm))


def get_prompt_template_hash(cases: list[dict[str, Any]]) -> str:
    """
    Canonical hash of the prompt template context: sorted case ids and step shapes.
    Same cases in same order => same hash. Used for real-LLM run reproducibility.
    """
    canonical = []
    for c in sorted(cases, key=lambda x: x.get("id", "")):
        step = c.get("step") or {}
        canonical.append({
            "id": c.get("id"),
            "tool": step.get("tool"),
            "args": step.get("args"),
        })
    return sha256_utf8(json.dumps(canonical, sort_keys=True))


def get_evaluator_version() -> str:
    """Script/evaluator version stamp for run manifests."""
    return EVALUATOR_VERSION


def get_policy_version() -> str:
    """
    Policy/schema version from kernel. Reads TYPED_PLAN schema version if available;
    otherwise returns a default.
    """
    kernel_dir = os.environ.get("LABTRUST_KERNEL_DIR")
    if kernel_dir:
        schema_path = Path(kernel_dir) / "llm_runtime" / "TYPED_PLAN.v0.1.schema.json"
        if schema_path.exists():
            try:
                data = json.loads(schema_path.read_text(encoding="utf-8"))
                ver = data.get("properties", {}).get("version", {}).get("const")
                if ver:
                    return f"typed_plan.{ver}"
            except Exception:
                pass
    return "typed_plan.0.1"


def get_timestamp_iso() -> str:
    """Current UTC timestamp in ISO format for run manifests."""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
