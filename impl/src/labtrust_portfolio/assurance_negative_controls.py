"""
Deterministic negative-control materializers for P7 governance discrimination experiments.

Each case produces a work directory (run artifacts) and pack path for review_assurance_pipeline.
"""
from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import FrozenSet, List, Literal, Tuple

from . import assurance_failure_codes as FC

Expected = Literal["accept", "reject"]


@dataclass(frozen=True)
class NegativeCaseSpec:
    """Specification for one negative (or positive) control."""

    id: str
    family: str
    expected_outcome: Expected
    expected_codes: FrozenSet[str]
    failure_stage_hint: str


def _copy_run(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def _copy_pack(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _load_pack(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_pack(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _strip_disposition_commit_trace(run_dir: Path) -> None:
    """Remove task_end events for disposition_commit (lab PONR) from trace.json in place."""
    tr_path = run_dir / "trace.json"
    tr = json.loads(tr_path.read_text(encoding="utf-8"))
    evs: List[dict] = []
    for ev in tr.get("events", []):
        if ev.get("type") == "task_end":
            name = (ev.get("payload") or {}).get("name", "")
            if name == "disposition_commit":
                continue
        evs.append(ev)
    tr["events"] = evs
    tr_path.write_text(json.dumps(tr, indent=2) + "\n", encoding="utf-8")


def materialize_case(
    repo_root: Path,
    work_root: Path,
    case_id: str,
    base_lab_run: Path,
    base_wh_run: Path,
    base_traffic_run: Path,
    lab_pack: Path,
    warehouse_pack: Path,
    medical_pack: Path,
    seed: int,
) -> Tuple[Path, Path, str, Expected, FrozenSet[str], str]:
    """
    Build a single case under work_root / f\"case_{case_id}_s{seed}\".

    Returns (run_dir, pack_path, scenario_id, expected_outcome, expected_codes, family).
    """
    work = work_root / f"case_{case_id}_s{seed}"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)

    lab_pack_w = work / "pack_lab.json"
    wh_pack_w = work / "pack_wh.json"
    med_pack_w = work / "pack_med.json"
    _copy_pack(lab_pack, lab_pack_w)
    _copy_pack(warehouse_pack, wh_pack_w)
    _copy_pack(medical_pack, med_pack_w)

    run_lab = work / "run_lab"
    run_wh = work / "run_wh"
    run_traffic = work / "run_traffic"
    _copy_run(base_lab_run, run_lab)
    _copy_run(base_wh_run, run_wh)
    _copy_run(base_traffic_run, run_traffic)

    # ---- Positive control (valid lab path) ----
    if case_id == "positive_valid_lab":
        return run_lab, lab_pack_w, "lab_profile_v0", "accept", frozenset(), "positive_control"

    # ---- Family A: pack structure ----
    if case_id == "hazard_missing_control_ids":
        p = work / "bad_pack.json"
        d = _load_pack(lab_pack_w)
        d["hazards"][0]["control_ids"] = []
        _write_pack(p, d)
        return run_lab, p, "lab_profile_v0", "reject", frozenset({FC.CONTROL_REFERENCE_MISSING}), "pack_structure"

    if case_id == "hazard_references_unknown_control":
        p = work / "bad_pack.json"
        d = _load_pack(lab_pack_w)
        d["hazards"][0]["control_ids"] = ["C-001", "C-999"]
        _write_pack(p, d)
        return run_lab, p, "lab_profile_v0", "reject", frozenset({FC.CONTROL_REFERENCE_MISSING}), "pack_structure"

    if case_id == "control_missing_evidence_types":
        p = work / "bad_pack.json"
        d = _load_pack(lab_pack_w)
        for c in d["controls"]:
            if c["id"] == "C-001":
                c["evidence_artifact_types"] = []
        _write_pack(p, d)
        return run_lab, p, "lab_profile_v0", "reject", frozenset({FC.CONTROL_EVIDENCE_TYPES_MISSING}), "pack_structure"

    if case_id == "missing_required_field":
        p = work / "bad_pack.json"
        d = _load_pack(lab_pack_w)
        del d["controls"]
        _write_pack(p, d)
        return run_lab, p, "lab_profile_v0", "reject", frozenset({FC.PACK_SCHEMA_INVALID}), "pack_structure"

    if case_id == "ponr_ids_missing_for_profile":
        p = work / "bad_pack.json"
        d = _load_pack(lab_pack_w)
        for h in d["hazards"]:
            h["ponr_ids"] = []
        _write_pack(p, d)
        return run_lab, p, "lab_profile_v0", "reject", frozenset({FC.PROFILE_PONR_UNCOVERED}), "pack_structure"

    if case_id == "evidence_map_inconsistent":
        p = work / "bad_pack.json"
        d = _load_pack(lab_pack_w)
        d["evidence_map"]["H-001"] = ["C-001"]
        _write_pack(p, d)
        return run_lab, p, "lab_profile_v0", "reject", frozenset({FC.EVIDENCE_MAP_INCONSISTENT}), "pack_structure"

    # ---- Family B: artifact admissibility ----
    if case_id == "missing_trace_file":
        r = work / "run_no_trace"
        _copy_run(base_lab_run, r)
        (r / "trace.json").unlink(missing_ok=True)
        return r, lab_pack_w, "lab_profile_v0", "reject", frozenset({FC.TRACE_MISSING}), "artifact_admissibility"

    if case_id == "missing_bundle_file":
        r = work / "run_no_bundle"
        _copy_run(base_lab_run, r)
        (r / "evidence_bundle.json").unlink(missing_ok=True)
        return r, lab_pack_w, "lab_profile_v0", "reject", frozenset({FC.BUNDLE_MISSING}), "artifact_admissibility"

    if case_id == "trace_schema_invalid":
        r = work / "run_bad_trace"
        _copy_run(base_lab_run, r)
        (r / "trace.json").write_text("{ not json", encoding="utf-8")
        return r, lab_pack_w, "lab_profile_v0", "reject", frozenset({FC.TRACE_SCHEMA_INVALID}), "artifact_admissibility"

    if case_id == "bundle_schema_invalid":
        r = work / "run_bad_bundle"
        _copy_run(base_lab_run, r)
        (r / "evidence_bundle.json").write_text("{}", encoding="utf-8")
        return r, lab_pack_w, "lab_profile_v0", "reject", frozenset({FC.BUNDLE_SCHEMA_INVALID}), "artifact_admissibility"

    if case_id == "trace_truncated":
        r = work / "run_trunc_trace"
        _copy_run(base_lab_run, r)
        t = (r / "trace.json").read_text(encoding="utf-8")
        (r / "trace.json").write_text(t[: max(20, len(t) // 3)], encoding="utf-8")
        return r, lab_pack_w, "lab_profile_v0", "reject", frozenset({FC.TRACE_SCHEMA_INVALID}), "artifact_admissibility"

    if case_id == "bundle_corrupted_field":
        r = work / "run_bad_bundle2"
        _copy_run(base_lab_run, r)
        b = json.loads((r / "evidence_bundle.json").read_text(encoding="utf-8"))
        del b["verification"]
        (r / "evidence_bundle.json").write_text(json.dumps(b), encoding="utf-8")
        return r, lab_pack_w, "lab_profile_v0", "reject", frozenset({FC.BUNDLE_SCHEMA_INVALID}), "artifact_admissibility"

    if case_id == "bundle_broken_trace_hash":
        r = work / "run_bad_bundle_sha"
        _copy_run(base_lab_run, r)
        b = json.loads((r / "evidence_bundle.json").read_text(encoding="utf-8"))
        for art in b.get("artifacts") or []:
            if not isinstance(art, dict):
                continue
            rel = str(art.get("path", ""))
            if rel.endswith("trace.json") or rel == "trace.json":
                art["sha256"] = "0" * 64
        (r / "evidence_bundle.json").write_text(json.dumps(b, indent=2) + "\n", encoding="utf-8")
        return r, lab_pack_w, "lab_profile_v0", "reject", frozenset({FC.PROVENANCE_MISMATCH}), "artifact_admissibility"

    # ---- Family C: scenario consistency ----
    if case_id == "wrong_pack_for_scenario":
        # Warehouse trace but claim lab scenario for review; trace scenario_id is warehouse_v0
        return run_wh, lab_pack_w, "lab_profile_v0", "reject", frozenset({FC.SCENARIO_PACK_MISMATCH}), "scenario_consistency"

    if case_id in ("cross_run_trace_bundle_swap", "stale_bundle_reused"):
        r = work / "run_swap"
        _copy_run(base_lab_run, r)
        other = work / "run_other_seed"
        from labtrust_portfolio.thinslice import run_thin_slice

        other.mkdir(parents=True)
        run_thin_slice(other, seed=seed + 100, scenario_id="lab_profile_v0", drop_completion_prob=0.0)
        shutil.copy2(other / "evidence_bundle.json", r / "evidence_bundle.json")
        shutil.rmtree(other, ignore_errors=True)
        return r, lab_pack_w, "lab_profile_v0", "reject", frozenset({FC.PROVENANCE_MISMATCH}), "scenario_consistency"

    if case_id in ("swapped_scenario_id_in_trace", "trace_from_other_scenario"):
        r = work / "run_wrong_sid"
        _copy_run(base_lab_run, r)
        tr = json.loads((r / "trace.json").read_text(encoding="utf-8"))
        tr["scenario_id"] = "toy_lab_v0"
        (r / "trace.json").write_text(json.dumps(tr, indent=2) + "\n", encoding="utf-8")
        return r, lab_pack_w, "lab_profile_v0", "reject", frozenset({FC.SCENARIO_PACK_MISMATCH}), "scenario_consistency"

    if case_id == "wrong_required_task_name":
        r = work / "run_wrong_ponr_name"
        _copy_run(base_lab_run, r)
        tr = json.loads((r / "trace.json").read_text(encoding="utf-8"))
        for ev in tr.get("events", []):
            if ev.get("type") == "task_end":
                pl = dict(ev.get("payload") or {})
                if pl.get("name") == "disposition_commit":
                    pl["name"] = "disposition_commit_substitute"
                    ev["payload"] = pl
        (r / "trace.json").write_text(json.dumps(tr, indent=2) + "\n", encoding="utf-8")
        return r, lab_pack_w, "lab_profile_v0", "reject", frozenset({FC.PONR_MISSING}), "scenario_consistency"

    # ---- Family D: adversarial / misleading ----
    if case_id == "missing_required_ponr_event":
        r = work / "run_no_ponr_sc"
        _copy_run(base_lab_run, r)
        _strip_disposition_commit_trace(r)
        return r, lab_pack_w, "lab_profile_v0", "reject", frozenset({FC.PONR_MISSING}), "scenario_consistency"

    if case_id == "remove_final_commit_event_keep_structure":
        r = work / "run_no_ponr_adv"
        _copy_run(base_lab_run, r)
        _strip_disposition_commit_trace(r)
        return r, lab_pack_w, "lab_profile_v0", "reject", frozenset({FC.PONR_MISSING}), "adversarial_misleading"

    if case_id == "partial_control_omission":
        p = work / "pack_partial.json"
        d = _load_pack(lab_pack_w)
        for c in d["controls"]:
            if c["id"] == "C-002":
                # Declares an artifact class no run can satisfy (governance-theater style over-claim)
                c["evidence_artifact_types"] = [
                    "trace",
                    "evidence_bundle",
                    "signed_attestation_chain",
                ]
        _write_pack(p, d)
        return run_lab, p, "lab_profile_v0", "reject", frozenset({FC.INCOMPLETE_EVIDENCE}), "adversarial_misleading"

    if case_id == "wellformed_but_incomplete_evidence":
        p = work / "pack_wellformed_incomplete.json"
        d = _load_pack(lab_pack_w)
        for c in d["controls"]:
            if c.get("id") == "C-001":
                c["evidence_artifact_types"] = ["trace", "evidence_bundle", "conformance"]
        _write_pack(p, d)
        return run_lab, p, "lab_profile_v0", "reject", frozenset({FC.INCOMPLETE_EVIDENCE}), "adversarial_misleading"

    if case_id == "manifest_points_to_foreign_artifact":
        r = work / "run_bad_manifest"
        _copy_run(base_lab_run, r)
        rm = json.loads((r / "release_manifest.json").read_text(encoding="utf-8"))
        if rm.get("artifacts"):
            rm["artifacts"][0]["sha256"] = "0" * 64
        (r / "release_manifest.json").write_text(json.dumps(rm, indent=2) + "\n", encoding="utf-8")
        return r, lab_pack_w, "lab_profile_v0", "reject", frozenset({FC.PROVENANCE_MISMATCH}), "adversarial_misleading"

    # ---- Scenario spread additions ----
    if case_id == "warehouse_missing_required_ponr_event":
        r = work / "run_wh_no_ponr"
        _copy_run(base_wh_run, r)
        tr = json.loads((r / "trace.json").read_text(encoding="utf-8"))
        evs: List[dict] = []
        for ev in tr.get("events", []):
            if ev.get("type") == "task_end":
                name = (ev.get("payload") or {}).get("name", "")
                if name == "place":
                    continue
            evs.append(ev)
        tr["events"] = evs
        (r / "trace.json").write_text(json.dumps(tr, indent=2) + "\n", encoding="utf-8")
        return r, wh_pack_w, "warehouse_v0", "reject", frozenset({FC.PONR_MISSING}), "scenario_consistency"

    if case_id == "warehouse_manifest_points_to_foreign_artifact":
        r = work / "run_wh_bad_manifest"
        _copy_run(base_wh_run, r)
        rm = json.loads((r / "release_manifest.json").read_text(encoding="utf-8"))
        if rm.get("artifacts"):
            rm["artifacts"][0]["sha256"] = "0" * 64
        (r / "release_manifest.json").write_text(json.dumps(rm, indent=2) + "\n", encoding="utf-8")
        return r, wh_pack_w, "warehouse_v0", "reject", frozenset({FC.PROVENANCE_MISMATCH}), "adversarial_misleading"

    if case_id == "traffic_wrong_pack_for_scenario":
        # traffic trace reviewed as traffic scenario, but with warehouse assurance pack
        return run_traffic, wh_pack_w, "traffic_v0", "reject", frozenset({FC.SCENARIO_PACK_MISMATCH}), "scenario_consistency"

    if case_id == "traffic_manifest_points_to_foreign_artifact":
        r = work / "run_traffic_bad_manifest"
        _copy_run(base_traffic_run, r)
        rm = json.loads((r / "release_manifest.json").read_text(encoding="utf-8"))
        if rm.get("artifacts"):
            rm["artifacts"][0]["sha256"] = "0" * 64
        (r / "release_manifest.json").write_text(json.dumps(rm, indent=2) + "\n", encoding="utf-8")
        return r, med_pack_w, "traffic_v0", "reject", frozenset({FC.PROVENANCE_MISMATCH}), "adversarial_misleading"

    # ---- Boundary / hard negatives (expected reject, may be accepted) ----
    if case_id == "boundary_under_specified_pack_still_admissible":
        # Drops one critical control while preserving schema and internal map consistency.
        p = work / "pack_boundary_under_specified.json"
        d = _load_pack(lab_pack_w)
        d["hazards"][0]["control_ids"] = ["C-001"]
        d["controls"] = [c for c in d.get("controls", []) if c.get("id") == "C-001"]
        d["evidence_map"]["H-001"] = ["C-001"]
        if "trace" in d["evidence_map"]:
            d["evidence_map"]["trace"] = ["C-001"]
        if "evidence_bundle" in d["evidence_map"]:
            d["evidence_map"]["evidence_bundle"] = ["C-001"]
        _write_pack(p, d)
        return (
            run_lab,
            p,
            "lab_profile_v0",
            "reject",
            frozenset({FC.INCOMPLETE_EVIDENCE}),
            "boundary_cases",
        )

    if case_id == "boundary_locally_consistent_cross_run_lineage":
        # Copies full artifact set from a different seed; local SHA checks pass but external lineage is stale.
        r = work / "run_boundary_lineage"
        _copy_run(base_lab_run, r)
        other = work / "run_boundary_other_seed"
        from labtrust_portfolio.thinslice import run_thin_slice

        other.mkdir(parents=True)
        run_thin_slice(other, seed=seed + 200, scenario_id="lab_profile_v0", drop_completion_prob=0.0)
        for name in ("trace.json", "evidence_bundle.json", "release_manifest.json", "maestro_report.json"):
            shutil.copy2(other / name, r / name)
        shutil.rmtree(other, ignore_errors=True)
        return (
            r,
            lab_pack_w,
            "lab_profile_v0",
            "reject",
            frozenset({FC.PROVENANCE_MISMATCH}),
            "boundary_cases",
        )

    raise KeyError(f"Unknown negative case id: {case_id}")


def all_case_ids(quick: bool = False) -> List[str]:
    """Ordered list of case ids (positive first, then negatives)."""
    core = [
        "positive_valid_lab",
        "hazard_missing_control_ids",
        "hazard_references_unknown_control",
        "control_missing_evidence_types",
        "missing_required_field",
        "ponr_ids_missing_for_profile",
        "evidence_map_inconsistent",
        "missing_trace_file",
        "missing_bundle_file",
        "trace_schema_invalid",
        "bundle_schema_invalid",
        "trace_truncated",
        "bundle_corrupted_field",
        "bundle_broken_trace_hash",
        "wrong_pack_for_scenario",
        "missing_required_ponr_event",
        "remove_final_commit_event_keep_structure",
        "cross_run_trace_bundle_swap",
        "stale_bundle_reused",
        "swapped_scenario_id_in_trace",
        "wrong_required_task_name",
        "partial_control_omission",
        "wellformed_but_incomplete_evidence",
        "manifest_points_to_foreign_artifact",
        "warehouse_missing_required_ponr_event",
        "warehouse_manifest_points_to_foreign_artifact",
        "traffic_wrong_pack_for_scenario",
        "traffic_manifest_points_to_foreign_artifact",
        "boundary_under_specified_pack_still_admissible",
        "boundary_locally_consistent_cross_run_lineage",
    ]
    if quick:
        return [
            "positive_valid_lab",
            "missing_trace_file",
            "missing_required_ponr_event",
            "wrong_pack_for_scenario",
            "hazard_missing_control_ids",
            "cross_run_trace_bundle_swap",
        ]
    return core
