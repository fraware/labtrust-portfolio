#!/usr/bin/env python3
"""
Export P7 assurance case graph skeleton (GSN-lite) from mapping YAML/JSON.
Reads assurance_pack_instantiation.json; outputs Mermaid diagram for draft.
Usage: python scripts/export_assurance_gsn.py [--inst path] [--out path]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_INST = REPO / "profiles" / "lab" / "v0.1" / "assurance_pack_instantiation.json"


def main() -> int:
    ap = argparse.ArgumentParser(description="Export P7 GSN-lite graph from assurance pack")
    ap.add_argument("--inst", type=Path, default=DEFAULT_INST, help="Assurance pack instantiation JSON")
    ap.add_argument("--out", type=Path, default=None, help="Output .md or .mmd path (default: stdout)")
    args = ap.parse_args()
    if not args.inst.exists():
        print(f"Error: {args.inst} not found.")
        return 1
    data = json.loads(args.inst.read_text(encoding="utf-8"))
    hazards = data.get("hazards", [])
    controls = data.get("controls", [])
    lines = ["%% GSN-lite: hazards -> controls -> evidence (auto-generated from assurance_pack_instantiation.json)", "graph LR", "  subgraph Hazards"]
    for h in hazards:
        hid = h.get("id", "").replace("-", "_")
        lines.append(f"    {hid}[{h.get('id', '')}]")
    lines.append("  end")
    lines.append("  subgraph Controls")
    for c in controls:
        cid = c.get("id", "").replace("-", "_")
        lines.append(f"    {cid}[{c.get('id', '')}]")
    lines.append("  end")
    lines.append("  subgraph Evidence")
    lines.append("    trace[trace]")
    lines.append("    bundle[evidence_bundle]")
    lines.append("  end")
    for h in hazards:
        hid = h.get("id", "").replace("-", "_")
        for cid in h.get("control_ids", []):
            cid_s = cid.replace("-", "_")
            lines.append(f"  {hid} --> {cid_s}")
    for c in controls:
        cid = c.get("id", "").replace("-", "_")
        for e in c.get("evidence_artifact_types", []):
            enode = e.replace("-", "_")
            if enode in ("trace", "evidence_bundle"):
                lines.append(f"  {cid} --> {enode}")
    out = "\n".join(lines)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(out + "\n", encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
