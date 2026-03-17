#!/usr/bin/env python3
"""
Export P6 LLM Planning decision-path figure: planner output -> typed step -> allow-list ->
safe_args -> capture -> allow/deny. Output: docs/figures/p6_firewall_flow.mmd (Mermaid).
Regenerate: python scripts/export_p6_firewall_flow.py [--out path]
"""
from __future__ import annotations

import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO / "docs" / "figures" / "p6_firewall_flow.mmd"

# Decision path: Planner output -> Typed step -> Allow-list -> (fail) Deny; (pass) -> Safe_args -> (fail) Deny; (pass) -> Capture -> Allow
MERMAID = """%% P6 Decision path (auto-generated): planner -> typed step -> allow-list -> safe_args -> capture -> allow/deny
flowchart LR
  subgraph in[Input]
    P[Planner output]
  end
  T[Typed step]
  AL[Allow-list]
  SA[Safe_args]
  Cap[Capture]
  Allow[Allow]
  Deny1[Deny]
  Deny2[Deny]
  P --> T
  T --> AL
  AL -->|pass| SA
  AL -->|fail| Deny1
  SA -->|pass| Cap
  SA -->|fail| Deny2
  Cap --> Allow
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
