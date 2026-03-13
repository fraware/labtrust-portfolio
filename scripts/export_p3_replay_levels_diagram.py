#!/usr/bin/env python3
"""
Export P3 Replay levels and pipeline diagram (Figure 0).
L0 / L1 / L2 and replay pipeline: trace -> replay -> state_hash check -> diagnostics.
Output: docs/figures/p3_replay_levels_diagram.mmd (Mermaid). Required for peer-review.
Usage: python scripts/export_p3_replay_levels_diagram.py [--out path]
"""
from __future__ import annotations

import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO / "docs" / "figures" / "p3_replay_levels_diagram.mmd"

MERMAID = """%% P3 Replay levels and pipeline (auto-generated)
%% L0 control-plane; L1 with recorded observations; L2 aspirational
flowchart TB
  subgraph levels[Replay levels]
    L0[L0: Control-plane replay]
    L1[L1: + recorded observations]
    L2[L2: Hardware-assisted aspirational]
  end
  subgraph pipeline[Pipeline]
    T[Trace] --> R[Replay engine]
    R --> H[state_hash check]
    H --> D[Diagnostics]
  end
  L0 --> pipeline
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="Export P3 replay levels diagram")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output .mmd path")
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(MERMAID.strip() + "\n", encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
