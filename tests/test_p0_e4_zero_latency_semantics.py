"""Zero p95 latency in E4 must be intentional semantics, not accidental."""

from __future__ import annotations

import json
from pathlib import Path

from labtrust_portfolio.adapters import (
    CentralizedAdapter,
    REPCPSAdapter,
    run_adapter,
)
from labtrust_portfolio.p0_e4_matrix import MatrixPaths, run_controller_matrix


def test_zero_latency_only_when_no_tasks_completed(tmp_path: Path) -> None:
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
        scenarios=["rep_cps_scheduling_v0"],
        controllers=[
            ("centralized", CentralizedAdapter()),
            ("rep_cps", REPCPSAdapter()),
        ],
        seeds=[1, 2, 3],
        regimes=["coordination_shock"],
        paths=paths,
        run_adapter_fn=run_adapter,
        git_sha=None,
    )

    for line in paths.per_seed_jsonl.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        p95 = float(row.get("task_latency_ms_p95") or 0.0)
        tasks_completed = int(row.get("tasks_completed") or 0)
        if p95 == 0.0:
            assert (
                tasks_completed == 0
            ), (
                "Unexpected zero p95 latency with "
                f"tasks_completed={tasks_completed}: {row}"
            )
