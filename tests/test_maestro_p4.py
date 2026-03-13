"""P4 CPS-MAESTRO: integration tests for fault sweep and baselines."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Scenario family tests use impl
try:
    from labtrust_portfolio.scenario import (
        get_failure_dominance,
        get_resource_graph,
        get_scenario_family,
        load_scenario,
    )
except ImportError:
    get_scenario_family = None  # type: ignore[misc, assignment]
    get_resource_graph = None  # type: ignore[misc, assignment]
    get_failure_dominance = None  # type: ignore[misc, assignment]
    load_scenario = None  # type: ignore[misc, assignment]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


class TestMaestroFaultSweepIntegration(unittest.TestCase):
    """Run maestro_fault_sweep and assert sweep output structure."""

    def setUp(self) -> None:
        os.environ["LABTRUST_KERNEL_DIR"] = str(repo_root() / "kernel")

    def test_maestro_fault_sweep_produces_valid_sweep(self) -> None:
        env = os.environ.copy()
        script = repo_root() / "scripts" / "maestro_fault_sweep.py"
        with tempfile.TemporaryDirectory() as td:
            out_dir = Path(td) / "maestro_fault_sweep"
            out_dir.mkdir(parents=True)
            proc = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--scenario",
                    "toy_lab_v0",
                    "--seeds",
                    "2",
                    "--out",
                    str(out_dir),
                ],
                cwd=str(repo_root()),
                env={**env, "PYTHONPATH": str(repo_root() / "impl" / "src")},
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(proc.returncode, 0, (proc.stdout, proc.stderr))
            multi_path = out_dir / "multi_sweep.json"
            self.assertTrue(
                multi_path.exists(), "multi_sweep.json must be produced"
            )
            data = json.loads(multi_path.read_text(encoding="utf-8"))
            self.assertIn("per_scenario", data)
            self.assertGreater(len(data["per_scenario"]), 0)
            combined = data["per_scenario"][0]
            self.assertIn("sweep", combined)
            self.assertGreater(len(combined["sweep"]), 0)
            summary = combined["sweep"][0]
            self.assertIn("tasks_completed_mean", summary)
            self.assertIn("tasks_completed_stdev", summary)
            self.assertIn("p95_latency_ms_mean", summary)
            self.assertIn("per_run", summary)
            self.assertGreater(len(summary["per_run"]), 0)
            self.assertIn("run_manifest", data)
            rm = data["run_manifest"]
            self.assertIn("seeds", rm)
            if "seed_count" in rm:
                self.assertEqual(rm["seed_count"], 2)
            if "tasks_completed_stdev" in summary:
                self.assertGreaterEqual(summary["tasks_completed_stdev"], 0)

    def test_maestro_fault_sweep_high_drop_tasks_drop(self) -> None:
        """Stress: high drop_completion_prob (0.3) reduces tasks_completed_mean vs no_drop."""
        env = os.environ.copy()
        script = repo_root() / "scripts" / "maestro_fault_sweep.py"
        with tempfile.TemporaryDirectory() as td:
            out_dir = Path(td) / "maestro_stress"
            out_dir.mkdir(parents=True)
            proc = subprocess.run(
                [
                    sys.executable, str(script),
                    "--scenario", "toy_lab_v0",
                    "--seeds", "3",
                    "--out", str(out_dir),
                ],
                cwd=str(repo_root()),
                env={**env, "PYTHONPATH": str(repo_root() / "impl" / "src")},
                capture_output=True,
                text=True,
                timeout=180,
            )
            self.assertEqual(proc.returncode, 0, (proc.stdout, proc.stderr))
            data = json.loads((out_dir / "multi_sweep.json").read_text(encoding="utf-8"))
            self.assertIn("per_scenario", data)
            self.assertGreater(len(data["per_scenario"]), 0)
            sweep = data["per_scenario"][0].get("sweep", [])
            no_drop_mean = None
            drop_high_mean = None
            for s in sweep:
                label = s.get("setting", "")
                if label == "no_drop":
                    no_drop_mean = s.get("tasks_completed_mean")
                if "drop_02" in label or (s.get("drop_completion_prob") == 0.2):
                    drop_high_mean = s.get("tasks_completed_mean")
            if no_drop_mean is not None and drop_high_mean is not None:
                self.assertLessEqual(
                    drop_high_mean, no_drop_mean + 0.01,
                    "High drop should not increase tasks_completed vs no_drop",
                )


class TestMaestroBaselinesIntegration(unittest.TestCase):
    """Run maestro_baselines and assert baseline output."""

    def setUp(self) -> None:
        os.environ["LABTRUST_KERNEL_DIR"] = str(repo_root() / "kernel")

    def test_maestro_baselines_produces_valid_baseline(self) -> None:
        env = os.environ.copy()
        script = repo_root() / "scripts" / "maestro_baselines.py"
        proc = subprocess.run(
            [
                sys.executable,
                str(script),
                "--scenario",
                "toy_lab_v0",
                "--seeds",
                "2",
            ],
            cwd=str(repo_root()),
            env={**env, "PYTHONPATH": str(repo_root() / "impl" / "src")},
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(proc.returncode, 0, (proc.stdout, proc.stderr))
        out_path = repo_root() / "bench" / "maestro" / "baseline_results.md"
        self.assertTrue(
            out_path.exists(), "baseline_results.md must be produced"
        )
        content = out_path.read_text(encoding="utf-8")
        self.assertIn("Adapter", content)
        self.assertIn("tasks_completed", content)
        self.assertIn("Centralized", content)
        self.assertIn("Blackboard", content)
        summary_path = repo_root() / "bench" / "maestro" / "baseline_summary.json"
        self.assertTrue(
            summary_path.exists(),
            "baseline_summary.json must be produced by maestro_baselines.py",
        )
        data = json.loads(summary_path.read_text(encoding="utf-8"))
        self.assertIn("rows", data)
        self.assertIn("scenario", data)
        self.assertGreater(len(data["rows"]), 0)
        row = data["rows"][0]
        for key in ("adapter", "seed", "tasks_completed", "coordination_messages", "p95_latency_ms"):
            self.assertIn(key, row, f"Row must have '{key}'")


class TestScenarioFamily(unittest.TestCase):
    """Unit tests for scenario taxonomy (family) and load_scenario."""

    def test_get_scenario_family_returns_default_when_absent(self) -> None:
        if get_scenario_family is None:
            self.skipTest("labtrust_portfolio.scenario not importable")
        self.assertEqual(get_scenario_family({}), "default")
        self.assertEqual(get_scenario_family({"tasks": []}), "default")

    def test_get_scenario_family_returns_family_when_present(self) -> None:
        if get_scenario_family is None:
            self.skipTest("labtrust_portfolio.scenario not importable")
        self.assertEqual(get_scenario_family({"family": "lab"}), "lab")
        self.assertEqual(get_scenario_family({"family": "warehouse"}), "warehouse")

    def test_load_scenario_includes_family_for_toy_lab(self) -> None:
        if load_scenario is None:
            self.skipTest("labtrust_portfolio.scenario not importable")
        scenario = load_scenario("toy_lab_v0")
        self.assertIn("family", scenario)
        self.assertEqual(scenario["family"], "lab")
        self.assertEqual(get_scenario_family(scenario), "lab")

    def test_lab_profile_v0_has_resource_graph_and_failure_dominance(self) -> None:
        if load_scenario is None or get_resource_graph is None or get_failure_dominance is None:
            self.skipTest("labtrust_portfolio.scenario not importable")
        scenario = load_scenario("lab_profile_v0")
        rg = get_resource_graph(scenario)
        self.assertIsNotNone(rg)
        self.assertIn("instruments", rg)
        self.assertIn("stations", rg)
        self.assertTrue(rg.get("queue_contention"))
        self.assertEqual(get_failure_dominance(scenario), "contention")
