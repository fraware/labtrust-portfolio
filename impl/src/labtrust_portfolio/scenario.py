"""Load MAESTRO scenario YAML from bench/maestro/scenarios/."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None  # type: ignore

from .profile import find_repo_root


def _scenarios_dir() -> Path:
    repo = find_repo_root(Path(__file__).resolve())
    return repo / "bench" / "maestro" / "scenarios"


def load_scenario(scenario_id: str) -> Dict[str, Any]:
    """
    Load scenario YAML by id. Looks up bench/maestro/scenarios/<id>.yaml.
    Returns dict with keys: id, description, tasks, faults (and optional family).
    Raises FileNotFoundError if file missing.
    """
    if yaml is None:
        raise RuntimeError(
            "PyYAML required for scenario loading (pip install pyyaml)"
        )
    path = _scenarios_dir() / f"{scenario_id}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Scenario file not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not data:
        raise ValueError(f"Empty scenario: {path}")
    if "id" not in data:
        data["id"] = scenario_id
    if "tasks" not in data:
        data["tasks"] = []
    if "faults" not in data:
        data["faults"] = []
    return data


def get_scenario_task_names(scenario: Dict[str, Any]) -> List[str]:
    """Return ordered list of task names from scenario tasks."""
    return [
        t.get("name", "")
        for t in scenario.get("tasks", [])
        if t.get("name")
    ]


def get_scenario_family(scenario: Dict[str, Any]) -> str:
    """Return scenario taxonomy family (lab, warehouse, traffic); default if absent."""
    return scenario.get("family", "default")


def get_resource_graph(scenario: Dict[str, Any]) -> Dict[str, Any] | None:
    """
    Return resource_graph from scenario if present (instruments, stations,
    queue_contention, retry_policy, failure_dominance). None if absent.
    """
    return scenario.get("resource_graph")


def get_failure_dominance(scenario: Dict[str, Any]) -> str | None:
    """Return failure_dominance (contention | scale) from scenario or resource_graph."""
    return scenario.get("failure_dominance") or (
        scenario.get("resource_graph") or {}
    ).get("failure_dominance")


def list_scenario_ids() -> List[str]:
    """Return scenario ids for which a YAML file exists."""
    d = _scenarios_dir()
    if not d.exists():
        return []
    return [p.stem for p in d.glob("*.yaml")]
