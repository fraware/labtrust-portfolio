#!/usr/bin/env python3
"""Cross-platform artifact hash manifest for P5 freeze (replaces find | sha256sum)."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description="Hash P5 canonical files under datasets/runs/")
    ap.add_argument(
        "--runs-root",
        type=Path,
        default=REPO / "datasets" / "runs",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=REPO / "papers" / "P5_ScalingLaws" / "p5_artifact_hashes.txt",
    )
    ap.add_argument("--max-depth", type=int, default=2)
    args = ap.parse_args()

    roots = args.runs_root
    files: list[Path] = []
    if roots.exists():
        files.extend(sorted(roots.rglob("*")))
    files = [p for p in files if p.is_file()]
    # Depth within runs_root
    filtered: list[Path] = []
    for p in files:
        rel = p.relative_to(roots)
        if len(rel.parts) <= args.max_depth:
            filtered.append(p)
    # Repo-relative paths so the manifest is identical on Linux CI and Windows.
    lines = [
        f"{_sha256_file(p)}  {p.resolve().relative_to(REPO.resolve()).as_posix()}"
        for p in sorted(filtered)
    ]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    print(f"Wrote {len(lines)} entries to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
