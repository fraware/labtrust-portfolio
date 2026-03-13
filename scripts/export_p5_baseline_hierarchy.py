#!/usr/bin/env python3
"""
Export P5 Scaling baseline hierarchy diagram (Figure 0).
Global mean -> per-scenario mean -> feature baseline -> regression.
Output: docs/figures/p5_baseline_hierarchy.mmd (Mermaid). Required for peer-review.
Usage: python scripts/export_p5_baseline_hierarchy.py [--out path]
"""
from __future__ import annotations

import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO / "docs" / "figures" / "p5_baseline_hierarchy.mmd"

MERMAID = """%% P5 Scaling baseline hierarchy (auto-generated)
%% Weak -> strong trivial baselines; model must beat these out-of-sample
flowchart LR
  B1[Global mean]
  B2[Per-scenario mean]
  B3[Feature baseline]
  B4[Regression]
  B1 --> B2
  B2 --> B3
  B3 --> B4
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="Export P5 baseline hierarchy diagram")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output .mmd path")
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(MERMAID.strip() + "\n", encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
