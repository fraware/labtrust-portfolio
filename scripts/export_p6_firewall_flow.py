#!/usr/bin/env python3
"""
Export P6 LLM Planning typed-plan firewall flow diagram (Figure 0).
Plan -> validate_plan -> allow | deny (policy_check_step).
Output: docs/figures/p6_firewall_flow.mmd (Mermaid). Required for peer-review.
Usage: python scripts/export_p6_firewall_flow.py [--out path]
"""
from __future__ import annotations

import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO / "docs" / "figures" / "p6_firewall_flow.mmd"

MERMAID = """%% P6 Typed-plan firewall flow (auto-generated)
%% Plan -> validate_plan / policy_check_step -> allow | deny
flowchart LR
  subgraph input[Input]
    P[Typed plan]
  end
  subgraph firewall[Firewall]
    V[validate_plan]
    C[policy_check_step]
  end
  subgraph outcome[Outcome]
    A[allow]
    D[deny]
  end
  P --> V
  V --> C
  C --> A
  C --> D
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="Export P6 firewall flow diagram")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output .mmd path")
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(MERMAID.strip() + "\n", encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
