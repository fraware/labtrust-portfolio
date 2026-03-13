"""Tests for lab profile loading and scenario alignment."""
from __future__ import annotations

import os
import unittest
from pathlib import Path

# Scenario task names used by thin-slice (single source of truth for this test)
THINSLICE_TASK_NAMES = ["receive_sample", "centrifuge", "analyze", "report_results"]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


class TestProfileLoader(unittest.TestCase):
    """Test that the lab profile loads and has required structure."""

    def setUp(self) -> None:
        self.profile_dir = repo_root() / "profiles" / "lab" / "v0.1"

    def test_profile_dir_exists(self) -> None:
        self.assertTrue(self.profile_dir.is_dir(), f"Profile dir should exist: {self.profile_dir}")

    def test_load_lab_profile_succeeds(self) -> None:
        from labtrust_portfolio.profile import load_lab_profile
        data = load_lab_profile(self.profile_dir)
        self.assertIn("ponrs", data)
        self.assertIn("fault_model", data)
        self.assertIn("telemetry_min_fields", data)
        self.assertIn("state_types", data)

    def test_profile_ponrs_has_list(self) -> None:
        from labtrust_portfolio.profile import load_lab_profile
        data = load_lab_profile(self.profile_dir)
        ponrs = data["ponrs"]["ponrs"]
        self.assertIsInstance(ponrs, list)
        self.assertGreater(len(ponrs), 0)
        self.assertIn("id", ponrs[0])

    def test_profile_fault_model_has_classes(self) -> None:
        from labtrust_portfolio.profile import load_lab_profile
        data = load_lab_profile(self.profile_dir)
        classes = data["fault_model"]["fault_classes"]
        self.assertIsInstance(classes, list)
        self.assertGreater(len(classes), 0)


class TestScenarioAlignment(unittest.TestCase):
    """Test that MAESTRO scenario toy_lab_v0 is consistent with thin-slice expectations."""

    def test_scenario_file_exists(self) -> None:
        scenario_path = repo_root() / "bench" / "maestro" / "scenarios" / "toy_lab_v0.yaml"
        self.assertTrue(scenario_path.exists(), f"Scenario should exist: {scenario_path}")

    def test_scenario_tasks_match_thinslice(self) -> None:
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML required for scenario load")
        scenario_path = repo_root() / "bench" / "maestro" / "scenarios" / "toy_lab_v0.yaml"
        data = yaml.safe_load(scenario_path.read_text(encoding="utf-8"))
        self.assertIsNotNone(data)
        self.assertIn("tasks", data)
        task_names = [t["name"] for t in data["tasks"]]
        self.assertEqual(task_names, THINSLICE_TASK_NAMES, "Scenario tasks must match thin-slice task list")
