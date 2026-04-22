"""Normalization must remain narrow: remove adapter-only MAESTRO top-level keys only."""

from __future__ import annotations

import json
from pathlib import Path

from labtrust_portfolio.adapters import REPCPSAdapter, run_adapter
from labtrust_portfolio.p0_e4_matrix import MatrixPaths, run_controller_matrix


def test_normalization_diff_contains_only_top_level_removals(tmp_path: Path) -> None:
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
        controller_pairs_jsonl=runs / "p0_e4_controller_pairs.jsonl",
        raw_failure_reasons=runs / "p0_e4_raw_failure_reasons.json",
    )
    run_controller_matrix(
        repo_root=repo,
        scenarios=["toy_lab_v0"],
        controllers=[("rep_cps", REPCPSAdapter())],
        seeds=[1],
        regimes=["baseline"],
        paths=paths,
        run_adapter_fn=run_adapter,
        git_sha=None,
    )
    diff = json.loads(paths.normalization_diff.read_text(encoding="utf-8"))
    for rec in diff.get("records", []):
        assert rec.get("keys_added", []) == []
        assert rec.get("keys_modified", []) == []
        for removed in rec.get("keys_removed", []):
            assert removed.get("reason_code") == "adapter_only_top_level_field"
