"""Conformance checker: Tier pass/fail for a run directory."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Set

from .replay import replay_trace
from .schema import validate

# Scenario -> task names that are PONR-aligned (must appear as task_end in trace for Tier 3).
# lab_profile_v0: disposition_commit (PONR-B); toy_lab_v0 has no PONR tasks in scope.
SCENARIO_PONR_TASK_NAMES: Dict[str, List[str]] = {
    "lab_profile_v0": ["disposition_commit"],
    "toy_lab_v0": [],
}

REQUIRED_ARTIFACTS = {
    "trace.json": "trace/TRACE.v0.1.schema.json",
    "maestro_report.json": "eval/MAESTRO_REPORT.v0.1.schema.json",
    "evidence_bundle.json": "mads/EVIDENCE_BUNDLE.v0.1.schema.json",
    "release_manifest.json": "policy/RELEASE_MANIFEST.v0.1.schema.json",
}


@dataclass
class ConformanceResult:
    """Result of conformance check."""

    passed: bool
    tier: int
    failures: List[str] = field(default_factory=list)

    def message(self) -> str:
        if self.passed:
            return f"Tier {self.tier} PASS"
        return f"Tier {self.tier} FAIL: " + "; ".join(self.failures)

    def to_dict(self) -> Dict[str, Any]:
        """Structured dict for conformance.json artifact (E1)."""
        return {
            "tier": self.tier,
            "pass": self.passed,
            "reasons": list(self.failures),
        }


def _ponr_task_names_in_trace(trace: Dict[str, Any]) -> Set[str]:
    """Return set of task names that appear in task_end events in the trace."""
    found: Set[str] = set()
    for ev in trace.get("events", []):
        if ev.get("type") == "task_end" and "payload" in ev:
            name = ev["payload"].get("name")
            if isinstance(name, str):
                found.add(name)
    return found


def check_conformance(run_dir: Path) -> ConformanceResult:
    """
    Check conformance of a run directory. Tier 1: all artifacts present and
    validate against kernel schemas. Tier 2: Tier 1 + replay_ok and
    schema_validation_ok in evidence bundle. Tier 3: Tier 2 + PONR coverage
    (trace contains task_end for each PONR-aligned task required by scenario).
    """
    run_dir = run_dir.resolve()
    failures: List[str] = []
    trace_obj: Dict[str, Any] = {}
    evidence_obj: Dict[str, Any] = {}

    for name, schema_relpath in REQUIRED_ARTIFACTS.items():
        path = run_dir / name
        if not path.exists():
            failures.append(f"missing artifact: {name}")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            failures.append(f"{name}: invalid JSON or read error: {e}")
            continue
        if name == "trace.json":
            trace_obj = data
        if name == "evidence_bundle.json":
            evidence_obj = data
        try:
            validate(data, schema_relpath)
        except Exception as e:
            failures.append(f"{name}: schema validation failed: {e}")

    if failures:
        return ConformanceResult(passed=False, tier=1, failures=failures)

    # Tier 1 passed (all present and valid)
    replay_ok = True
    if trace_obj:
        replay_ok, _ = replay_trace(trace_obj)
    verification = evidence_obj.get("verification", {})
    schema_ok = verification.get("schema_validation_ok", False)
    bundle_replay_ok = verification.get("replay_ok", False)
    verification_mode = evidence_obj.get("verification_mode", "evaluator")
    replay_required = verification_mode != "public"  # public bundles are verifiable but not required replayable
    if not schema_ok:
        failures.append("evidence_bundle.verification.schema_validation_ok=false")
    if replay_required and not replay_ok:
        failures.append("replay of trace failed (state hash mismatch)")
    if replay_required and not bundle_replay_ok:
        failures.append("evidence_bundle.verification.replay_ok=false")

    if failures:
        return ConformanceResult(passed=False, tier=2, failures=failures)

    # Tier 2 passed; check Tier 3 (PONR coverage)
    scenario_id = trace_obj.get("scenario_id") or "toy_lab_v0"
    required_ponr_tasks = SCENARIO_PONR_TASK_NAMES.get(
        scenario_id, SCENARIO_PONR_TASK_NAMES.get("toy_lab_v0", [])
    )
    if required_ponr_tasks:
        in_trace = _ponr_task_names_in_trace(trace_obj)
        missing = [t for t in required_ponr_tasks if t not in in_trace]
        if missing:
            return ConformanceResult(
                passed=False,
                tier=3,
                failures=[f"PONR coverage: trace missing task_end for: {', '.join(missing)}"],
            )
    return ConformanceResult(passed=True, tier=3, failures=[])


def write_conformance_artifact(run_dir: Path) -> Path:
    """
    Run conformance check and write conformance.json under run_dir.
    Returns path to conformance.json. Use for E1 artifact.
    """
    result = check_conformance(run_dir)
    out_path = run_dir / "conformance.json"
    out_path.write_text(
        json.dumps(result.to_dict(), indent=2) + "\n",
        encoding="utf-8",
    )
    return out_path
