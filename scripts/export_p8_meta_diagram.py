#!/usr/bin/env python3
"""
Export P8 Meta-controller state and switch criterion diagram (Figure 0).
Regimes (centralized / fallback) and switch on fault_count / latency_p95.
Output: docs/figures/p8_meta_diagram.mmd (Mermaid). Required for peer-review.
Usage: python scripts/export_p8_meta_diagram.py [--out path]
"""
from __future__ import annotations

import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO / "docs" / "figures" / "p8_meta_diagram.mmd"

MERMAID = """%% P8 Meta-controller state and switch (auto-generated)
%% Regimes and switch criterion: fault_count / latency_p95
flowchart LR
  subgraph regimes[Regimes]
    C[Centralized]
    F[Fallback]
  end
  subgraph criterion[Switch criterion]
    S[fault_count > thr OR latency_p95 > thr]
  end
  C -->|S| F
  F -->|below 0.5*thr| C
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="Export P8 meta-controller diagram")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output .mmd path")
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(MERMAID.strip() + "\n", encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
