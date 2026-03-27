#!/usr/bin/env python3
"""
Export P2 REP-CPS profile architecture diagram (Figure 0).
Agents -> aggregation -> safety gate -> actuation.
Outputs:
  - docs/figures/p2_rep_profile_diagram.mmd (Mermaid source; always written)
  - docs/figures/p2_rep_profile_diagram.png (optional; requires Mermaid CLI)
  - docs/figures/p2_rep_profile_diagram.svg (optional; vector)
  - docs/figures/p2_rep_profile_diagram.pdf (optional; vector/rasterized by renderer)

Camera-ready PNG: install `@mermaid-js/mermaid-cli` globally (`npm i -g @mermaid-js/mermaid-cli`)
so `mmdc` is on PATH, then run with `--render-png`. Alternatively use the Mermaid Live Editor
or `npx @mermaid-js/mermaid-cli -i ... -o ...` from the repo root.

Usage:
  python scripts/export_p2_rep_profile_diagram.py [--out path]
  python scripts/export_p2_rep_profile_diagram.py --render-png [--png-out path]
  python scripts/export_p2_rep_profile_diagram.py --render-svg [--svg-out path]
  python scripts/export_p2_rep_profile_diagram.py --render-pdf [--pdf-out path]
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO / "docs" / "figures" / "p2_rep_profile_diagram.mmd"
DEFAULT_PNG = REPO / "docs" / "figures" / "p2_rep_profile_diagram.png"
DEFAULT_SVG = REPO / "docs" / "figures" / "p2_rep_profile_diagram.svg"
DEFAULT_PDF = REPO / "docs" / "figures" / "p2_rep_profile_diagram.pdf"

MERMAID = """%% P2 REP-CPS profile architecture (auto-generated)
%% Decision-relevant informational state with explicit gate mediation.
flowchart LR
  subgraph agents [AgentSignals]
    a1[Local state and telemetry]
    a2["Sensitivity update x,v,a,t,n,pi"]
  end
  subgraph profile [REP_CPS_Profile]
    p1[Type checks]
    p2[Auth and provenance hook]
    p3[Freshness window and replay filter]
    p4[Per sender rate limit]
  end
  subgraph aggregate [AggregationFamily]
    ag1[Trimmed mean or permitted variant]
    ag2[Informational state s_hat]
  end
  subgraph safety [SafetyGate]
    g1["Policy gate G d,s_hat,z"]
    g2[pass]
    g3[deny with trace]
  end
  subgraph downstream [OperationalPath]
    d1[Scheduler or admission logic]
    d2[Actuation]
  end

  a1 --> a2
  a2 --> p1
  p1 --> p2
  p2 --> p3
  p3 --> p4
  p4 --> ag1
  ag1 --> ag2
  ag2 --> g1
  g1 --> g2
  g1 --> g3
  g2 --> d1
  d1 --> d2

  spoof[Attack: duplicate sender spoof] --> p2
  stale[Attack: stale or replay burst] --> p3
  burst[Attack: burst influence] --> p4
  byz[Attack: compromised extreme values] --> ag1
"""


def _find_mmdc() -> str | None:
    return shutil.which("mmdc")


def _render_with_mmdc(mmdc: str, src: Path, out: Path, ext: str) -> int:
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [mmdc, "-i", str(src), "-o", str(out), "-e", ext]
    if ext == "png":
        cmd.extend(["-w", "2048", "-H", "1200"])
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print(proc.stderr or proc.stdout, file=sys.stderr)
        return proc.returncode
    print(f"Wrote {out}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Export P2 REP-CPS profile diagram")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output .mmd path")
    ap.add_argument(
        "--render-png",
        action="store_true",
        help="Run mmdc to produce PNG next to the .mmd (requires @mermaid-js/mermaid-cli)",
    )
    ap.add_argument(
        "--png-out",
        type=Path,
        default=DEFAULT_PNG,
        help="Output PNG path when --render-png is set",
    )
    ap.add_argument(
        "--render-svg",
        action="store_true",
        help="Run mmdc to produce SVG vector output",
    )
    ap.add_argument(
        "--svg-out",
        type=Path,
        default=DEFAULT_SVG,
        help="Output SVG path when --render-svg is set",
    )
    ap.add_argument(
        "--render-pdf",
        action="store_true",
        help="Run mmdc to produce PDF output",
    )
    ap.add_argument(
        "--pdf-out",
        type=Path,
        default=DEFAULT_PDF,
        help="Output PDF path when --render-pdf is set",
    )
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(MERMAID.strip() + "\n", encoding="utf-8")
    print(f"Wrote {args.out}")

    if args.render_png or args.render_svg or args.render_pdf:
        mmdc = _find_mmdc()
        if not mmdc:
            print(
                "Warning: mmdc not found on PATH. Install: npm i -g @mermaid-js/mermaid-cli\n"
                "Or run: npx -y @mermaid-js/mermaid-cli -i ... -o ...",
                file=sys.stderr,
            )
            return 1
        if args.render_png:
            rc = _render_with_mmdc(mmdc, args.out, args.png_out, "png")
            if rc != 0:
                return rc
        if args.render_svg:
            rc = _render_with_mmdc(mmdc, args.out, args.svg_out, "svg")
            if rc != 0:
                return rc
        if args.render_pdf:
            rc = _render_with_mmdc(mmdc, args.out, args.pdf_out, "pdf")
            if rc != 0:
                return rc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
