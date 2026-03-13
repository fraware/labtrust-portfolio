"""Tests for conformance checker."""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


class TestConformanceChecker(unittest.TestCase):
    """Test conformance checker Tier 1 and Tier 2."""

    def setUp(self) -> None:
        os.environ["LABTRUST_KERNEL_DIR"] = str(
            (repo_root() / "kernel").resolve()
        )

    def test_valid_run_passes(self) -> None:
        from labtrust_portfolio.thinslice import run_thin_slice
        from labtrust_portfolio.conformance import check_conformance

        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td)
            run_thin_slice(run_dir, seed=99, drop_completion_prob=0.0)
            result = check_conformance(run_dir)
            self.assertTrue(result.passed, result.message())
            self.assertGreaterEqual(result.tier, 2)

    def test_missing_artifact_fails(self) -> None:
        from labtrust_portfolio.thinslice import run_thin_slice
        from labtrust_portfolio.conformance import check_conformance

        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td)
            run_thin_slice(run_dir, seed=1, drop_completion_prob=0.0)
            (run_dir / "maestro_report.json").unlink()
            result = check_conformance(run_dir)
            self.assertFalse(result.passed)
            self.assertIn("missing artifact", result.message())

    def test_replay_fail_fails_tier2(self) -> None:
        from labtrust_portfolio.thinslice import run_thin_slice
        from labtrust_portfolio.conformance import check_conformance

        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td)
            run_thin_slice(run_dir, seed=1, drop_completion_prob=0.0)
            trace_path = run_dir / "trace.json"
            trace = json.loads(trace_path.read_text(encoding="utf-8"))
            if trace["events"]:
                trace["events"][0]["state_hash_after"] = "a" * 64
            trace_path.write_text(json.dumps(trace, indent=2))
            ev_path = run_dir / "evidence_bundle.json"
            ev = json.loads(ev_path.read_text(encoding="utf-8"))
            ev["verification"]["replay_ok"] = False
            ev_path.write_text(json.dumps(ev, indent=2))
            result = check_conformance(run_dir)
            self.assertFalse(result.passed)
            self.assertIn("replay", result.message().lower())
