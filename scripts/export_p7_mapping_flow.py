#!/usr/bin/env python3
"""
Export P7 Standards mapping flow diagram (Figure 0).
Hazards -> Controls -> Evidence artifacts -> Audit.
Output: docs/figures/p7_mapping_flow.mmd (Mermaid). Required for peer-review.
Usage: python scripts/export_p7_mapping_flow.py [--out path]
"""
from __future__ import annotations

import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO / "docs" / "figures" / "p7_mapping_flow.mmd"

MERMAID = """%% P7 Mapping flow (auto-generated)
%% Hazards -> Controls -> Evidence -> Audit
flowchart LR
  subgraph hazards[Hazards]
    H[Hazard log]
  end
  subgraph controls[Controls]
    C[Controls / invariants]
  end
  subgraph evidence[Evidence]
    E[Evidence artifacts]
  end
  subgraph audit[Audit]
    A[audit_bundle / review]
  end
  H --> C
  C --> E
  E --> A
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="Export P7 mapping flow diagram")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output .mmd path")
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(MERMAID.strip() + "\n", encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
