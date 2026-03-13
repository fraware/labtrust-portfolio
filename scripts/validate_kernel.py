#!/usr/bin/env python3
"""Validate all kernel JSON schemas and report kernel version."""
from __future__ import annotations

import json
import re
from pathlib import Path


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    kernel = repo / "kernel"
    if not kernel.exists():
        raise SystemExit("kernel/ not found")

    schema_files = sorted(kernel.rglob("*.schema.json"))
    if not schema_files:
        raise SystemExit("No schema files found under kernel/")

    # Expected $id pattern: .../kernel/<domain>/<NAME>.v<major>.<minor>
    id_pattern = re.compile(
        r"^https?://[^/]+/labtrust/kernel/[^/]+/[A-Z0-9_]+\.v\d+\.\d+$",
        re.IGNORECASE,
    )

    try:
        import jsonschema  # type: ignore
        from jsonschema.validators import validator_for  # type: ignore
        have_jsonschema = True
    except Exception:
        have_jsonschema = False

    for p in schema_files:
        obj = json.loads(p.read_text(encoding="utf-8"))
        if "$schema" not in obj or "$id" not in obj:
            raise SystemExit(f"Schema missing $schema or $id: {p}")
        schema_id = obj["$id"]
        if not id_pattern.match(schema_id):
            raise SystemExit(
                f"Schema $id does not match pattern .../kernel/<domain>/<NAME>.v<ver>: {p} ($id={schema_id!r})"
            )
        if have_jsonschema:
            V = validator_for(obj)
            V.check_schema(obj)

    version_file = kernel / "VERSION"
    kernel_version = version_file.read_text(encoding="utf-8").strip() if version_file.exists() else "unknown"
    print(f"OK: {len(schema_files)} schemas validated (jsonschema={'yes' if have_jsonschema else 'no'}), kernel VERSION={kernel_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
