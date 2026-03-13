"""Load and validate the lab profile (profiles/lab/v0.1/)."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None  # type: ignore

REQUIRED_FILES = (
    "ponrs.yaml",
    "fault_model.yaml",
    "telemetry_min_fields.yaml",
    "state_types.yaml",
)
REQUIRED_TOP_LEVEL_KEYS = {
    "ponrs.yaml": ("ponrs",),
    "fault_model.yaml": ("fault_classes",),
    "telemetry_min_fields.yaml": ("required_events", "ponr_requirements"),
    "state_types.yaml": ("entities", "authority"),
}


def find_repo_root(start: Path) -> Path:
    p = start.resolve()
    for _ in range(8):
        if (p / "kernel").exists():
            return p
        p = p.parent
    raise RuntimeError("Could not locate repo root containing kernel/")


def lab_profile_dir(version: str = "v0.1") -> Path:
    """Return the path to profiles/lab/<version>/ from repo root."""
    repo = find_repo_root(Path(__file__).resolve())
    return repo / "profiles" / "lab" / version


def load_lab_profile(profile_dir: Path | None = None) -> Dict[str, Any]:
    """
    Load the lab profile from profile_dir (default: profiles/lab/v0.1/).
    Returns a dict with keys: ponrs, fault_model, telemetry_min_fields,
    state_types. Raises if a required file or top-level key is absent.
    """
    if profile_dir is None:
        profile_dir = lab_profile_dir()
    if not profile_dir.is_dir():
        raise FileNotFoundError(f"Profile directory not found: {profile_dir}")

    if yaml is None:
        raise RuntimeError(
            "PyYAML is required for profile loading (pip install pyyaml)"
        )

    result: Dict[str, Any] = {}
    for filename in REQUIRED_FILES:
        path = profile_dir / filename
        if not path.exists():
            raise FileNotFoundError(
                f"Required profile file missing: {path}"
            )
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if data is None:
            data = {}
        required_keys = REQUIRED_TOP_LEVEL_KEYS[filename]
        for key in required_keys:
            if key not in data:
                raise ValueError(
                    f"{filename}: missing required top-level key {key!r}"
                )
        name = filename.replace(".yaml", "")
        result[name] = data
    return result


def get_profile_task_names(profile: Dict[str, Any]) -> list[str]:
    """
    Return task names from the lab profile if defined. For thin-slice
    alignment we use the scenario; extend this when profile has task list.
    Currently returns [] (scenario is source of truth).
    """
    return []
