#!/usr/bin/env python3
"""
Export P0 tier lattice (Figure 2): what each tier adds.
Output: docs/figures/p0_tier_lattice.mmd (Mermaid). Render to PNG for camera-ready.
Usage: python scripts/export_p0_tier_lattice.py [--out path]
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO / "docs" / "figures" / "p0_tier_lattice.mmd"

MERMAID = """%% P0 MADS-CPS tier lattice (Figure 2)
%% Tier 1 = artifacts + schema; Tier 2 = + replay; Tier 3 = + PONR coverage
flowchart TB
  T1[Tier 1: Artifacts present and schema-valid]
  T2[Tier 2: Tier 1 + replay_ok and schema_validation_ok]
  T3[Tier 3: Tier 2 + PONR coverage]
  T1 --> T2
  T2 --> T3
"""


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Export P0 tier lattice (Figure 2)")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output .mmd path")
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(MERMAID.strip() + "\n", encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
