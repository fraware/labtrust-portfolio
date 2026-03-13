"""P6 LLM Planning: integration test for red-team eval and adapter latency."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


class TestLLMRedteamEvalIntegration(unittest.TestCase):
    """Run llm_redteam_eval with --run-adapter; assert red_team and latency."""

    def setUp(self) -> None:
        os.environ["LABTRUST_KERNEL_DIR"] = str(repo_root() / "kernel")

    def test_llm_redteam_eval_produces_valid_results(self) -> None:
        env = os.environ.copy()
        pypath = str(repo_root() / "impl" / "src")
        script = repo_root() / "scripts" / "llm_redteam_eval.py"
        with tempfile.TemporaryDirectory() as td:
            out_dir = Path(td) / "llm_eval"
            out_dir.mkdir(parents=True)
            proc = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--out",
                    str(out_dir),
                    "--run-adapter",
                    "--adapter-scenarios",
                    "toy_lab_v0",
                    "--adapter-seeds",
                    "7",
                ],
                cwd=str(repo_root()),
                env={**env, "PYTHONPATH": pypath},
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(
                proc.returncode, 0,
                (proc.stdout, proc.stderr)
            )
            red_path = out_dir / "red_team_results.json"
            self.assertTrue(
                red_path.exists(),
                "red_team_results.json must be produced",
            )
            red = json.loads(red_path.read_text(encoding="utf-8"))
            self.assertIn("run_manifest", red)
            self.assertIn("success_criteria_met", red)
            self.assertTrue(red["success_criteria_met"].get("red_team_all_pass"))
            self.assertTrue(
                red.get("all_block_unsafe_pass"),
                "Red-team must pass (all_block_unsafe_pass true)",
            )
            self.assertGreaterEqual(red.get("n_cases", 0), 5, "Red-team corpus has at least 5 cases")
            self.assertIn("cases", red)
            for c in red["cases"]:
                self.assertIn("expected_block", c)
                self.assertIn("actually_blocked", c)
                self.assertIn("pass", c)
                self.assertTrue(c["pass"], f"Case {c.get('id')} must pass")
            lat_path = out_dir / "adapter_latency.json"
            self.assertTrue(
                lat_path.exists(),
                "adapter_latency.json must be produced when --run-adapter",
            )
            lat = json.loads(lat_path.read_text(encoding="utf-8"))
            self.assertIn("run_manifest", lat)
            self.assertIn("runs", lat)
            self.assertIn("tail_latency_p95_mean_ms", lat)
            self.assertIn("scenarios", lat)
            self.assertIn("seeds", lat)
            self.assertGreater(len(lat["runs"]), 0)
