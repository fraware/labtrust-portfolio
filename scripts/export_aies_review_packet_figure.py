#!/usr/bin/env python3
"""
Export a compact paper-facing figure source from bounded review packet metadata.

Usage:
  python scripts/export_aies_review_packet_figure.py \
    --in datasets/runs/assurance_eval_aies/bounded_review_packet \
    --out datasets/runs/assurance_eval_aies/figures
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _render_mermaid(mmd: Path, png: Path, pdf: Path) -> None:
    mmdc = shutil.which("mmdc")
    if mmdc:
        subprocess.run([mmdc, "-i", str(mmd), "-o", str(png)], check=False)
        subprocess.run([mmdc, "-i", str(mmd), "-o", str(pdf)], check=False)
        return
    npx = shutil.which("npx")
    if npx:
        subprocess.run(
            [npx, "-y", "-p", "@mermaid-js/mermaid-cli", "mmdc", "-i", str(mmd), "-o", str(png)],
            check=False,
        )
        subprocess.run(
            [npx, "-y", "-p", "@mermaid-js/mermaid-cli", "mmdc", "-i", str(mmd), "-o", str(pdf)],
            check=False,
        )


def main() -> int:
    ap = argparse.ArgumentParser(description="Export AIES bounded-review figure")
    ap.add_argument("--in", dest="in_dir", type=Path, required=True, help="bounded_review_packet dir")
    ap.add_argument("--out", dest="out_dir", type=Path, required=True, help="figures output dir")
    args = ap.parse_args()

    in_dir = args.in_dir.resolve()
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    summary_path = in_dir / "review_packet_summary.json"
    if not summary_path.exists():
        raise FileNotFoundError(f"Missing {summary_path}")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    verdict = "PASS" if summary.get("review_exit_ok") else "FAIL"
    failure_codes = "; ".join(summary.get("failure_reason_codes") or []) or "none"
    failure_stage = summary.get("failure_stage") or "none"

    mmd = out_dir / "review_packet_figure.mmd"
    mmd.write_text(
        "\n".join(
            [
                "flowchart TD",
                "  A[External Claim Under Review]",
                "  B[Bounded Artifact Packet]",
                "  C[Machine Review Layer]",
                f"  D[Verdict: {verdict}]",
                f"  E[Failure Stage: {failure_stage}]",
                f"  F[Failure Codes: {failure_codes}]",
                "  G[Out of Scope: Semantic Sufficiency, Full-chain Collusion]",
                "  A --> B --> C --> D",
                "  D --> E",
                "  D --> F",
                "  C -. limits .-> G",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    caption = out_dir / "review_packet_figure_caption.txt"
    caption.write_text(
        "Bounded external review flow: a claim is evaluated against a constrained "
        "artifact packet, producing a machine-checkable verdict with attributable "
        "failure stage/codes and explicit out-of-scope boundaries.\n",
        encoding="utf-8",
    )

    md = out_dir / "review_packet_figure.md"
    md.write_text(
        "\n".join(
            [
                "# Review Packet Figure Summary",
                "",
                f"- claim_id: `{summary.get('claim_id')}`",
                f"- scenario_id: `{summary.get('scenario_id')}`",
                f"- review_mode: `{summary.get('review_mode')}`",
                f"- review_exit_ok: `{summary.get('review_exit_ok')}`",
                f"- failure_stage: `{failure_stage}`",
                f"- failure_reason_codes: `{failure_codes}`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    png = out_dir / "review_packet_figure.png"
    pdf = out_dir / "review_packet_figure.pdf"
    _render_mermaid(mmd, png, pdf)

    print(f"Wrote {mmd}")
    print(f"Wrote {caption}")
    print(f"Wrote {md}")
    if png.exists():
        print(f"Wrote {png}")
    if pdf.exists():
        print(f"Wrote {pdf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

