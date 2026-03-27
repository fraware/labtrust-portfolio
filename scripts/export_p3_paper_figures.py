#!/usr/bin/env python3
"""
Generate all camera-ready figures under papers/P3_Replay/figures/ for the P3 paper.
Also refreshes docs/figures/p3_replay_overhead.{png,json} for verify_p3_replay_summary.py.
Run from repo root with PYTHONPATH=impl/src.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PAPER_FIG = REPO / "papers" / "P3_Replay" / "figures"
DOCS_FIG = REPO / "docs" / "figures"
SCRIPTS = REPO / "scripts"


def run(py: str, extra: list[str] | None = None) -> None:
    cmd = [sys.executable, str(SCRIPTS / py)]
    if extra:
        cmd.extend(extra)
    r = subprocess.run(cmd, cwd=str(REPO), check=False)
    if r.returncode != 0:
        raise SystemExit(f"Failed: {' '.join(cmd)}")


def main() -> int:
    PAPER_FIG.mkdir(parents=True, exist_ok=True)
    run("export_p3_replay_levels_diagram.py")
    run("export_p3_replay_levels_figure.py")
    run("plot_replay_overhead.py", ["--out", str(DOCS_FIG / "p3_replay_overhead.png")])
    for name in ("p3_replay_overhead.png", "p3_replay_overhead.json"):
        src = DOCS_FIG / name
        dst = PAPER_FIG / name
        if src.exists():
            shutil.copy2(src, dst)
            print(f"Copied {src.name} -> {dst}")
    run("plot_p3_baseline_bars.py")
    run("plot_p3_corpus_lanes.py")
    run("export_p3_first_divergence_timeline.py", ["--out", str(PAPER_FIG / "p3_first_divergence_timeline.png")])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
