#!/usr/bin/env python3
"""
Export P0 redaction preservation/loss diagram (Figure 3): what is preserved vs lost under redaction.
Output: docs/figures/p0_redaction_figure.mmd (Mermaid). Render to PNG for camera-ready.
Usage: python scripts/export_p0_redaction_figure.py [--out path]
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO / "docs" / "figures" / "p0_redaction_figure.mmd"

MERMAID = """%% P0 redaction preservation boundary (Figure 3)
%% Under structure-preserving redaction: schema and integrity preserved; replay lost
flowchart LR
  subgraph preserved [Preserved under redaction]
    S[schema_validation_ok]
    I[integrity_ok]
  end
  subgraph lost [Lost under redaction]
    R[replay_ok]
  end
  subgraph partial [Structure only]
    P[PONR coverage]
  end
"""


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Export P0 redaction figure (Figure 3)")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output .mmd path")
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(MERMAID.strip() + "\n", encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
