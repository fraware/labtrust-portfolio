"""Stored raw summary must match JSONL recompute."""

from __future__ import annotations

import json

from labtrust_portfolio.adapters import CentralizedAdapter, run_adapter
from labtrust_portfolio.p0_e4_matrix import MatrixPaths, recompute_raw_summary_from_jsonl, run_controller_matrix


def test_recompute_matches_written_raw_summary(tmp_path: Path) -> None:
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
    run_controller_matrix(
        repo_root=repo,
        scenarios=["toy_lab_v0"],
        controllers=[("centralized", CentralizedAdapter())],
        seeds=[1, 2],
        regimes=["baseline"],
        paths=paths,
        run_adapter_fn=run_adapter,
        git_sha=None,
    )
    disk = json.loads(paths.raw_summary.read_text(encoding="utf-8"))
    disk_rows = disk["rows"]
    again = recompute_raw_summary_from_jsonl(paths.per_seed_jsonl)
    assert len(again) == len(disk_rows)
    for a, b in zip(again, disk_rows, strict=True):
        assert a["regime"] == b["regime"]
        assert a["scenario"] == b["scenario"]
        assert a["controller"] == b["controller"]
        assert abs(a["raw_conformance_rate"] - b["raw_conformance_rate"]) < 1e-9
        assert abs(a["strong_replay_match_rate"] - b["strong_replay_match_rate"]) < 1e-9
        assert abs(a["p95_latency_ms_mean"] - b["p95_latency_ms_mean"]) < 1e-6
