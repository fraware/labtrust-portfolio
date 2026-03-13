#!/usr/bin/env python3
"""
Export P4 MAESTRO scenario-adapter-report flow diagram (Figure 0).
Scenario -> Adapter -> Trace -> MAESTRO report.
Output: docs/figures/p4_maestro_flow.mmd (Mermaid). Required for peer-review.
Usage: python scripts/export_p4_maestro_flow.py [--out path]
"""
from __future__ import annotations

import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO / "docs" / "figures" / "p4_maestro_flow.mmd"

MERMAID = """%% P4 MAESTRO scenario-adapter-report flow (auto-generated)
%% Scenario -> Adapter -> Trace -> MAESTRO report
flowchart LR
  subgraph spec[Spec]
    SC[Scenario YAML]
  end
  subgraph run[Run]
    A[Adapter]
  end
  subgraph artifacts[Artifacts]
    T[TRACE]
    M[MAESTRO_REPORT]
  end
  SC --> A
  A --> T
  A --> M
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="Export P4 MAESTRO flow diagram")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output .mmd path")
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(MERMAID.strip() + "\n", encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
