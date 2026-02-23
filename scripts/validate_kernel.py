#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    kernel = repo / "kernel"
    if not kernel.exists():
        raise SystemExit("kernel/ not found")

    schema_files = sorted(kernel.rglob("*.schema.json"))
    if not schema_files:
        raise SystemExit("No schema files found under kernel/")

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
        if have_jsonschema:
            V = validator_for(obj)
            V.check_schema(obj)

    print(f"OK: {len(schema_files)} schemas validated (jsonschema={'yes' if have_jsonschema else 'no'})")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
