#!/usr/bin/env python3
"""
Export P2 REP-CPS profile architecture diagram (Figure 0).
Agents -> aggregation -> safety gate -> actuation.
Output: docs/figures/p2_rep_profile_diagram.mmd (Mermaid). Required for peer-review.
Usage: python scripts/export_p2_rep_profile_diagram.py [--out path]
"""
from __future__ import annotations

import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO / "docs" / "figures" / "p2_rep_profile_diagram.mmd"

MERMAID = """%% P2 REP-CPS profile architecture (auto-generated)
%% Agents -> aggregation -> safety gate -> actuation
flowchart LR
  subgraph agents[Agents]
    A1[Agent 1]
    A2[Agent 2]
  end
  subgraph agg[Aggregation]
    R[Robust aggregate]
  end
  subgraph gate[Safety gate]
    G[MADS Tier / gate]
  end
  subgraph out[Output]
    O[Actuation]
  end
  A1 --> R
  A2 --> R
  R --> G
  G -->|pass| O
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="Export P2 REP-CPS profile diagram")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output .mmd path")
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(MERMAID.strip() + "\n", encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
