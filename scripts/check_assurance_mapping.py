#!/usr/bin/env python3
"""
Mapping completeness checker: every hazard has mapped controls and evidence.
Validates instantiation against ASSURANCE_PACK schema; checks mapping completeness.
Optional: PONR coverage (every profile PONR id in at least one hazard ponr_ids).
Outputs a final JSON line: {"mapping_ok": bool, "ponr_coverage_ok": bool}.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def load_profile_ponr_ids(profile_dir: Path) -> list[str]:
    """Load PONR ids from profiles/lab/.../ponrs.yaml."""
    ponrs_path = profile_dir / "ponrs.yaml"
    if not ponrs_path.exists():
        return []
    try:
        import yaml
        data = yaml.safe_load(ponrs_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    ponrs = data.get("ponrs") if isinstance(data, dict) else []
    if not isinstance(ponrs, list):
        return []
    ids = []
    for p in ponrs:
        if isinstance(p, dict) and "id" in p:
            ids.append(str(p["id"]))
    return ids


def main() -> int:
    ap = argparse.ArgumentParser(
        description="P7: Check assurance mapping completeness"
    )
    default_inst = REPO / "profiles" / "lab" / "v0.1"
    default_inst = default_inst / "assurance_pack_instantiation.json"
    ap.add_argument(
        "--inst",
        type=Path,
        default=default_inst,
        help="Assurance pack instantiation JSON",
    )
    ap.add_argument(
        "--profile-dir",
        type=Path,
        default=REPO / "profiles" / "lab" / "v0.1",
        help="Lab profile dir (for ponrs.yaml)",
    )
    args = ap.parse_args()
    inst_path = args.inst
    schema_path = REPO / "kernel" / "assurance_pack"
    schema_path = schema_path / "ASSURANCE_PACK.v0.1.schema.json"
    if not inst_path.exists():
        print(f"Missing: {inst_path}")
        print(json.dumps({"mapping_ok": False, "ponr_coverage_ok": False}))
        return 1
    if not schema_path.exists():
        print(f"Missing schema: {schema_path}")
        print(json.dumps({"mapping_ok": False, "ponr_coverage_ok": False}))
        return 1
    data = json.loads(inst_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    try:
        import jsonschema
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as e:
        print(f"Schema validation failed: {e}")
        print(json.dumps({"mapping_ok": False, "ponr_coverage_ok": False}))
        return 1
    except ImportError:
        pass
    hazards = {h["id"]: h for h in data.get("hazards", [])}
    controls = {c["id"]: c for c in data.get("controls", [])}
    failures = []
    for hid, h in hazards.items():
        control_ids = h.get("control_ids", [])
        if not control_ids:
            failures.append(f"Hazard {hid}: no control_ids")
        for cid in control_ids:
            if cid not in controls:
                failures.append(f"Hazard {hid}: control {cid} not in controls")
    for cid, c in controls.items():
        if not c.get("evidence_artifact_types"):
            failures.append(f"Control {cid}: no evidence_artifact_types")
    if failures:
        for f in failures:
            print(f)
        print(json.dumps({"mapping_ok": False, "ponr_coverage_ok": False}))
        return 1
    mapping_ok = True
    print(
        "OK: mapping complete (every hazard has controls, "
        "every control has evidence types)"
    )

    # PONR coverage: every profile PONR id in at least one hazard's ponr_ids
    profile_ponr_ids = load_profile_ponr_ids(args.profile_dir)
    hazard_ponr_ids = set()
    for h in data.get("hazards", []):
        for pid in h.get("ponr_ids") or []:
            hazard_ponr_ids.add(pid)
    ponr_coverage_ok = True
    if profile_ponr_ids:
        if not hazard_ponr_ids:
            print(
                "PONR coverage: no hazard has ponr_ids; "
                "cannot cover profile PONRs"
            )
            ponr_coverage_ok = False
        else:
            missing = [p for p in profile_ponr_ids if p not in hazard_ponr_ids]
            if missing:
                print(
                    "PONR coverage: profile PONRs not in any hazard "
                    f"ponr_ids: {missing}"
                )
                ponr_coverage_ok = False
            else:
                print(
                    "OK: PONR coverage (every profile PONR in at least "
                    "one hazard ponr_ids)"
                )
    out = {"mapping_ok": mapping_ok, "ponr_coverage_ok": ponr_coverage_ok}
    print(json.dumps(out))
    return 0 if (mapping_ok and ponr_coverage_ok) else 1


if __name__ == "__main__":
    raise SystemExit(main())
