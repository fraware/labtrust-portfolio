"""
Multi-mode assurance review for P7: schema-only, schema+presence, full governance review.

Used by review_assurance_run.py and run_assurance_negative_eval.py.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from . import assurance_failure_codes as FC
from .conformance import SCENARIO_PONR_TASK_NAMES

REVIEW_MODES = ("schema_only", "schema_plus_presence", "full_review")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def validate_pack_structure(
    pack_path: Path,
    schema_path: Path,
    profile_dir: Optional[Path],
) -> Tuple[bool, List[str], str]:
    """
    Return (ok, failure_codes, stage) where stage is 'pack' on failure.
    """
    codes: List[str] = []
    if not pack_path.exists():
        return False, [FC.PACK_SCHEMA_INVALID], "pack"
    try:
        data = _load_json(pack_path)
    except json.JSONDecodeError:
        return False, [FC.PACK_SCHEMA_INVALID], "pack"
    if not schema_path.exists():
        return False, [FC.PACK_SCHEMA_INVALID], "pack"
    schema = _load_json(schema_path)
    try:
        import jsonschema

        jsonschema.validate(instance=data, schema=schema)
    except Exception:
        codes.append(FC.PACK_SCHEMA_INVALID)
        return False, codes, "pack"
    hazards = {h["id"]: h for h in data.get("hazards", [])}
    controls = {c["id"]: c for c in data.get("controls", [])}
    evidence_map = data.get("evidence_map") or {}
    for hid, h in hazards.items():
        cids = h.get("control_ids") or []
        if not cids:
            codes.append(FC.CONTROL_REFERENCE_MISSING)
        for cid in cids:
            if cid not in controls:
                codes.append(FC.CONTROL_REFERENCE_MISSING)
    for cid, c in controls.items():
        types = c.get("evidence_artifact_types") or []
        if not types:
            codes.append(FC.CONTROL_EVIDENCE_TYPES_MISSING)
    for hid, h in hazards.items():
        em = evidence_map.get(hid)
        if isinstance(em, list):
            for cid in h.get("control_ids") or []:
                if cid not in em:
                    codes.append(FC.EVIDENCE_MAP_INCONSISTENT)
    if codes:
        return False, list(dict.fromkeys(codes)), "pack"
    # Profile PONR ids must appear in hazard ponr_ids when profile has ponrs.yaml
    if profile_dir:
        ponrs_path = profile_dir / "ponrs.yaml"
        if ponrs_path.exists():
            try:
                import yaml

                raw = yaml.safe_load(ponrs_path.read_text(encoding="utf-8"))
                ponrs = raw.get("ponrs") if isinstance(raw, dict) else []
                profile_ponr_ids: List[str] = []
                if isinstance(ponrs, list):
                    for p in ponrs:
                        if isinstance(p, dict) and p.get("id"):
                            profile_ponr_ids.append(str(p["id"]))
                hazard_ponr: Set[str] = set()
                for h in data.get("hazards", []):
                    for pid in h.get("ponr_ids") or []:
                        hazard_ponr.add(pid)
                if profile_ponr_ids:
                    missing = [p for p in profile_ponr_ids if p not in hazard_ponr]
                    if missing:
                        return False, [FC.PROFILE_PONR_UNCOVERED], "pack"
            except Exception:
                pass
    return True, [], "pack"


def _validate_trace_schema(run_dir: Path) -> Tuple[bool, List[str]]:
    trace_path = run_dir / "trace.json"
    if not trace_path.exists():
        return False, [FC.TRACE_MISSING]
    try:
        from .schema import validate

        trace = _load_json(trace_path)
        validate(trace, "trace/TRACE.v0.1.schema.json")
    except Exception:
        return False, [FC.TRACE_SCHEMA_INVALID]
    return True, []


def _validate_bundle_schema(run_dir: Path) -> Tuple[bool, List[str]]:
    eb_path = run_dir / "evidence_bundle.json"
    if not eb_path.exists():
        return False, [FC.BUNDLE_MISSING]
    try:
        from .schema import validate

        eb = _load_json(eb_path)
        validate(eb, "mads/EVIDENCE_BUNDLE.v0.1.schema.json")
    except Exception:
        return False, [FC.BUNDLE_SCHEMA_INVALID]
    return True, []


def _validate_maestro_schema(run_dir: Path) -> Tuple[bool, List[str]]:
    p = run_dir / "maestro_report.json"
    if not p.exists():
        return False, [FC.MAESTRO_MISSING]
    try:
        from .schema import validate

        validate(_load_json(p), "eval/MAESTRO_REPORT.v0.2.schema.json")
    except Exception:
        return False, [FC.UNKNOWN_REVIEW_FAILURE]
    return True, []


def _validate_release_schema(run_dir: Path) -> Tuple[bool, List[str]]:
    p = run_dir / "release_manifest.json"
    if not p.exists():
        return False, [FC.RELEASE_MANIFEST_MISSING]
    try:
        from .schema import validate

        validate(_load_json(p), "policy/RELEASE_MANIFEST.v0.1.schema.json")
    except Exception:
        return False, [FC.UNKNOWN_REVIEW_FAILURE]
    return True, []


def _check_release_manifest_provenance(run_dir: Path) -> Tuple[bool, List[str]]:
    """Release manifest artifact SHA256 entries must match files in run_dir."""
    p = run_dir / "release_manifest.json"
    if not p.exists():
        return False, [FC.RELEASE_MANIFEST_MISSING]
    try:
        rm = _load_json(p)
    except json.JSONDecodeError:
        return False, [FC.UNKNOWN_REVIEW_FAILURE]
    for art in rm.get("artifacts") or []:
        if not isinstance(art, dict):
            continue
        ap = str(art.get("path", ""))
        name = Path(ap).name
        target = run_dir / name
        if not target.exists():
            return False, [FC.PROVENANCE_MISMATCH]
        exp = art.get("sha256", "")
        if exp and exp != _sha256_file(target):
            return False, [FC.PROVENANCE_MISMATCH]
    return True, []


def _check_bundle_trace_provenance(run_dir: Path) -> Tuple[bool, List[str]]:
    """Artifact SHA256 entries for trace.json must match file on disk."""
    eb_path = run_dir / "evidence_bundle.json"
    if not eb_path.exists():
        return False, [FC.BUNDLE_MISSING]
    try:
        bundle = _load_json(eb_path)
    except json.JSONDecodeError:
        return False, [FC.BUNDLE_SCHEMA_INVALID]
    trace_path = run_dir / "trace.json"
    if not trace_path.exists():
        return False, [FC.TRACE_MISSING]
    for art in bundle.get("artifacts") or []:
        if not isinstance(art, dict):
            continue
        rel = art.get("path", "")
        expected = art.get("sha256", "")
        if rel.endswith("trace.json") or rel == "trace.json":
            actual = _sha256_file(trace_path)
            if expected and expected != actual:
                return False, [FC.PROVENANCE_MISMATCH]
    return True, []


def review_assurance_pipeline(
    run_dir: Path,
    pack_path: Path,
    scenario_id: str,
    mode: str,
    *,
    profile_dir: Optional[Path] = None,
    repo_root: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Run assurance review in one of REVIEW_MODES.

    Returns outcome dict including exit_ok, failure_stage, failure_reason_codes,
    evidence_bundle_ok, trace_ok, ponr_coverage, control_coverage_ratio, review_mode.
    """
    if mode not in REVIEW_MODES:
        raise ValueError(f"mode must be one of {REVIEW_MODES}")
    rr = repo_root or pack_path.resolve().parents[3]
    if not (rr / "kernel").exists():
        rr = pack_path.resolve().parents[2]
    schema_pack = rr / "kernel" / "assurance_pack" / "ASSURANCE_PACK.v0.1.schema.json"
    prof = profile_dir or (rr / "profiles" / "lab" / "v0.1")

    outcome: Dict[str, Any] = {
        "run_dir": str(run_dir),
        "review_mode": mode,
        "scenario_id": scenario_id,
        "evidence_bundle_ok": False,
        "trace_ok": False,
        "ponr_events": [],
        "controls_covered": [],
        "ponr_coverage": None,
        "control_coverage_ratio": None,
        "failure_stage": None,
        "failure_reason_codes": [],
        "exit_ok": False,
    }

    all_codes: List[str] = []
    fail_stage: Optional[str] = None

    def fail(stage: str, codes: List[str]) -> None:
        nonlocal fail_stage, all_codes
        if fail_stage is None:
            fail_stage = stage
        all_codes.extend(c for c in codes if c not in all_codes)

    # --- Pack (all modes) ---
    ok_pack, pack_codes, _ = validate_pack_structure(pack_path, schema_pack, prof)
    if not ok_pack:
        fail("pack", pack_codes)
        outcome["failure_reason_codes"] = all_codes
        outcome["failure_stage"] = fail_stage
        outcome["exit_ok"] = False
        return outcome

    pack = _load_json(pack_path)
    system = pack.get("system") if isinstance(pack, dict) else {}
    compatible = system.get("compatible_scenarios") if isinstance(system, dict) else None

    trace_exists = (run_dir / "trace.json").exists()
    bundle_exists = (run_dir / "evidence_bundle.json").exists()

    # --- Schema-only: optional trace/bundle schema if files exist ---
    if mode == "schema_only":
        if trace_exists:
            ok_t, c_t = _validate_trace_schema(run_dir)
            if not ok_t:
                fail("artifact_schema", c_t)
        if bundle_exists:
            ok_b, c_b = _validate_bundle_schema(run_dir)
            if not ok_b:
                fail("artifact_schema", c_b)
        outcome["failure_reason_codes"] = all_codes
        outcome["failure_stage"] = fail_stage
        outcome["trace_ok"] = trace_exists and not any(
            x in all_codes for x in (FC.TRACE_SCHEMA_INVALID, FC.TRACE_MISSING)
        )
        outcome["evidence_bundle_ok"] = bundle_exists and FC.BUNDLE_SCHEMA_INVALID not in all_codes
        outcome["exit_ok"] = fail_stage is None
        return outcome

    # --- Presence + schema (schema_plus_presence and full) ---
    if not trace_exists:
        fail("artifact_presence", [FC.TRACE_MISSING])
    else:
        ok_t, c_t = _validate_trace_schema(run_dir)
        if not ok_t:
            fail("artifact_schema", c_t)
        else:
            outcome["trace_ok"] = True
    if not bundle_exists:
        fail("artifact_presence", [FC.BUNDLE_MISSING])
    else:
        ok_b, c_b = _validate_bundle_schema(run_dir)
        if not ok_b:
            fail("artifact_schema", c_b)
        else:
            outcome["evidence_bundle_ok"] = True
    ok_m, c_m = _validate_maestro_schema(run_dir)
    if not ok_m:
        fail("artifact_presence", c_m)
    ok_r, c_r = _validate_release_schema(run_dir)
    if not ok_r:
        fail("artifact_presence", c_r)

    if mode == "schema_plus_presence":
        outcome["failure_reason_codes"] = all_codes
        outcome["failure_stage"] = fail_stage
        outcome["exit_ok"] = fail_stage is None
        return outcome

    # --- full_review: scenario alignment, PONR, control coverage, provenance ---
    assert mode == "full_review"
    if fail_stage is not None:
        outcome["failure_reason_codes"] = all_codes
        outcome["failure_stage"] = fail_stage
        outcome["exit_ok"] = False
        return outcome

    # Explicit pack scope check: reviewed scenario must be declared compatible.
    if not isinstance(compatible, list) or scenario_id not in {str(x) for x in compatible}:
        fail("scenario_alignment", [FC.SCENARIO_PACK_MISMATCH])

    try:
        trace = _load_json(run_dir / "trace.json")
    except Exception:
        fail("artifact_schema", [FC.TRACE_SCHEMA_INVALID])
        outcome["failure_reason_codes"] = all_codes
        outcome["failure_stage"] = fail_stage
        outcome["exit_ok"] = False
        return outcome

    tid = trace.get("scenario_id") or "toy_lab_v0"
    if tid != scenario_id:
        fail("scenario_alignment", [FC.SCENARIO_PACK_MISMATCH])

    events = trace.get("events", [])
    required = set(SCENARIO_PONR_TASK_NAMES.get(scenario_id, []))
    if scenario_id in SCENARIO_PONR_TASK_NAMES and not required:
        ponr_cov = {
            "required_task_names": [],
            "found_in_trace": [],
            "ratio": 1.0,
        }
    elif required:
        found: Set[str] = set()
        ponr_events: List[Dict[str, Any]] = []
        for ev in events:
            if ev.get("type") == "task_end":
                name = (ev.get("payload") or {}).get("name", "")
                if name in required:
                    found.add(name)
                    ponr_events.append(
                        {"seq": ev.get("seq"), "type": "task_end", "name": name}
                    )
        ratio = len(found) / len(required) if required else 1.0
        ponr_cov = {
            "required_task_names": sorted(required),
            "found_in_trace": sorted(found),
            "ratio": round(ratio, 4),
        }
        outcome["ponr_events"] = ponr_events
        if ratio < 1.0:
            fail("ponr", [FC.PONR_MISSING])
    else:
        ponr_cov = {
            "note": "scenario_id not in SCENARIO_PONR_TASK_NAMES map",
            "required_task_names": [],
            "found_in_trace": [],
            "ratio": None,
        }
    outcome["ponr_coverage"] = ponr_cov

    evidence_present: Set[str] = set()
    if trace_exists:
        evidence_present.add("trace")
    if outcome.get("evidence_bundle_ok"):
        evidence_present.add("evidence_bundle")
    controls = pack.get("controls", [])
    covered = 0
    controls_covered: List[Dict[str, Any]] = []
    for c in controls:
        types = c.get("evidence_artifact_types") or []
        controls_covered.append({"id": c.get("id"), "evidence_types": types})
        if types and all(et in evidence_present for et in types):
            covered += 1
    ratio_ctrl = round(covered / len(controls), 4) if controls else 1.0
    outcome["controls_covered"] = controls_covered
    outcome["control_coverage_ratio"] = ratio_ctrl
    if ratio_ctrl < 1.0:
        fail("control_coverage", [FC.INCOMPLETE_EVIDENCE])

    ok_prov, c_prov = _check_bundle_trace_provenance(run_dir)
    if not ok_prov:
        fail("provenance", c_prov)

    ok_rel, c_rel = _check_release_manifest_provenance(run_dir)
    if not ok_rel:
        fail("provenance", c_rel)

    outcome["failure_reason_codes"] = all_codes
    outcome["failure_stage"] = fail_stage
    outcome["exit_ok"] = fail_stage is None
    return outcome
