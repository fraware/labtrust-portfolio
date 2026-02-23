from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

def find_repo_root(start: Path) -> Path:
    p = start.resolve()
    for _ in range(8):
        if (p / "kernel").exists():
            return p
        p = p.parent
    raise RuntimeError("Could not locate repo root containing kernel/")

def kernel_dir() -> Path:
    import os
    env = os.environ.get("LABTRUST_KERNEL_DIR")
    if env:
        return Path(env).resolve()
    repo = find_repo_root(Path(__file__).resolve())
    return repo / "kernel"

def load_schema(relpath: str) -> Dict[str, Any]:
    p = kernel_dir() / relpath
    return json.loads(p.read_text(encoding="utf-8"))

def validate(instance: Any, schema_relpath: str) -> None:
    schema = load_schema(schema_relpath)
    try:
        import jsonschema  # type: ignore
    except Exception as e:
        raise RuntimeError("jsonschema is required for validation (install jsonschema)") from e
    jsonschema.validate(instance=instance, schema=schema)
