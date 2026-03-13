#!/usr/bin/env python3
"""
Export P1 Contracts validation flow diagram (Figure 0).
Event -> validate(state, event) -> allow | deny + reason_codes.
Output: docs/figures/p1_contract_flow.mmd (Mermaid). Required for peer-review.
Usage: python scripts/export_p1_contract_flow.py [--out path]
"""
from __future__ import annotations

import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO / "docs" / "figures" / "p1_contract_flow.mmd"

MERMAID = """%% P1 Contract validation flow (auto-generated)
%% event -> validate(state, event) -> allow | deny + reason_codes
flowchart LR
  subgraph input[Input]
    E[Trace event]
    S[State]
  end
  subgraph validator[Validator]
    V[validate(state, event)]
  end
  subgraph outcome[Outcome]
    A[allow]
    D[deny + reason_codes]
  end
  E --> V
  S --> V
  V --> A
  V --> D
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="Export P1 contract validation flow diagram")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output .mmd path")
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(MERMAID.strip() + "\n", encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
