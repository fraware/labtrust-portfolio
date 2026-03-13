#!/usr/bin/env python3
"""
Export P0 MADS-CPS assurance pipeline diagram (Figure 0).
Trace -> MAESTRO report -> Evidence bundle -> Conformance -> Release.
Output: docs/figures/p0_assurance_pipeline.mmd (Mermaid). Required for peer-review.
Usage: python scripts/export_p0_assurance_pipeline.py [--out path]
"""
from __future__ import annotations

import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO / "docs" / "figures" / "p0_assurance_pipeline.mmd"

MERMAID = """%% P0 MADS-CPS assurance pipeline (auto-generated)
%% Trace -> MAESTRO report -> Evidence bundle -> Conformance -> Release
flowchart LR
  subgraph capture[Capture]
    T[TRACE]
  end
  subgraph eval[Evaluation]
    M[MAESTRO_REPORT]
  end
  subgraph evidence[Evidence]
    E[Evidence bundle]
  end
  subgraph check[Conformance]
    C[Tier 1/2/3]
  end
  subgraph release[Release]
    R[Release manifest]
  end
  T --> M
  M --> E
  E --> C
  C -->|pass| R
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="Export P0 assurance pipeline diagram")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output .mmd path")
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(MERMAID.strip() + "\n", encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
