"""E4 raw path must not strip adapter MAESTRO fields; normalization only under normalized/."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.mark.parametrize("controller", ["centralized", "rep_cps"])
def test_raw_maestro_unstripped_after_matrix(controller: str, tmp_path: Path) -> None:
    from labtrust_portfolio.adapters import CentralizedAdapter, REPCPSAdapter, run_adapter
    from labtrust_portfolio.p0_e4_matrix import MatrixPaths, run_controller_matrix

    repo = tmp_path / "repo"
    repo.mkdir()
    runs = tmp_path / "runs"
    root = runs / "p0_e4_matrix"
    paths = MatrixPaths(
        repo_root=repo,
        runs_parent=runs,
        raw_runs_root=root / "raw",
        norm_runs_root=root / "normalized",
        per_seed_jsonl=runs / "p0_e4_per_seed.jsonl",
        raw_summary=runs / "p0_e4_raw_summary.json",
        normalized_summary=runs / "p0_e4_normalized_summary.json",
        normalization_diff=runs / "p0_e4_normalization_diff.json",
        controller_matrix=runs / "p0_e4_controller_matrix.json",
        diagnostics=runs / "p0_e4_diagnostics.json",
    )
    adapters = [
        ("centralized", CentralizedAdapter()),
        ("rep_cps", REPCPSAdapter()),
    ]
    ctrl = next(a for a in adapters if a[0] == controller)[1]
    run_controller_matrix(
        repo_root=repo,
        scenarios=["toy_lab_v0"],
        controllers=[(controller, ctrl)],
        seeds=[1],
        regimes=["baseline"],
        paths=paths,
        run_adapter_fn=run_adapter,
        git_sha=None,
    )
    raw_maestro = paths.raw_runs_root / "baseline" / "toy_lab_v0" / controller / "seed_1" / "maestro_report.json"
    data = json.loads(raw_maestro.read_text(encoding="utf-8"))
    if controller == "rep_cps":
        assert data.get("metadata_rep_cps") is True
    norm_maestro = paths.norm_runs_root / "baseline" / "toy_lab_v0" / controller / "seed_1" / "maestro_report.json"
    nd = json.loads(norm_maestro.read_text(encoding="utf-8"))
    assert "metadata_rep_cps" not in nd
