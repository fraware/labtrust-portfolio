#!/usr/bin/env python3
"""
Render P7 Mermaid figure sources to PNG and PDF under docs/figures/ (camera-ready).
Requires `mmdc` on PATH (npm i -g @mermaid-js/mermaid-cli) or Node for npx.

Usage (repo root): python scripts/render_p7_mermaid_figures.py
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FIG = REPO / "docs" / "figures"
FILES = (
    "p7_mapping_flow.mmd",
    "p7_gsn.mmd",
    "p7_review_stages.mmd",
)


def _mmdc_prefix() -> list[str] | None:
    m = shutil.which("mmdc")
    if m:
        return [m]
    if shutil.which("npx"):
        return ["npx", "-y", "-p", "@mermaid-js/mermaid-cli", "mmdc"]
    return None


def main() -> int:
    prefix = _mmdc_prefix()
    if not prefix:
        print("Neither mmdc nor npx on PATH; skip Mermaid render.", file=sys.stderr)
        return 1
    failed = False
    for name in FILES:
        src = FIG / name
        if not src.exists():
            print(f"Missing {src}", file=sys.stderr)
            failed = True
            continue
        for ext in ("png", "pdf"):
            out = src.with_suffix(f".{ext}")
            cmd = [*prefix, "-i", str(src), "-o", str(out)]
            r = subprocess.run(
                cmd,
                cwd=str(REPO),
                capture_output=True,
                text=True,
                timeout=180,
                encoding="utf-8",
                errors="replace",
            )
            if r.returncode != 0:
                print(
                    f"Render failed ({name} -> {ext}): {r.stderr or r.stdout}",
                    file=sys.stderr,
                )
                failed = True
            else:
                print(f"Wrote {out.relative_to(REPO)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
