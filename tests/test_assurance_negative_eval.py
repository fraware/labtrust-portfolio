"""Smoke test for P7 negative-control eval and export."""
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


class TestAssuranceNegativeEval(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["LABTRUST_KERNEL_DIR"] = str(repo_root() / "kernel")

    def test_negative_eval_quick_produces_json(self) -> None:
        env = os.environ.copy()
        pypath = str(repo_root() / "impl" / "src")
        script = repo_root() / "scripts" / "run_assurance_negative_eval.py"
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "out"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--quick",
                    "--out",
                    str(out),
                ],
                cwd=str(repo_root()),
                env={**env, "PYTHONPATH": pypath},
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(proc.returncode, 0, (proc.stdout, proc.stderr))
            p = out / "negative_results.json"
            self.assertTrue(p.exists())
            data = json.loads(p.read_text(encoding="utf-8"))
            self.assertIn("aggregate", data)
            self.assertIn("by_mode", data)
            self.assertIn("by_perturbation", data)
            self.assertIn("rows", data)
            self.assertGreater(len(data["rows"]), 0)
            for m in ("schema_only", "schema_plus_presence", "full_review"):
                self.assertIn(m, data["by_mode"])

    def test_export_negative_tables(self) -> None:
        env = os.environ.copy()
        pypath = str(repo_root() / "impl" / "src")
        neg_json = repo_root() / "datasets" / "runs" / "assurance_eval" / "negative_results.json"
        if not neg_json.exists():
            self.skipTest("negative_results.json not present; run run_assurance_negative_eval.py")
        with tempfile.TemporaryDirectory() as td:
            outd = Path(td) / "tbl"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(repo_root() / "scripts" / "export_p7_negative_tables.py"),
                    "--input",
                    str(neg_json),
                    "--out-dir",
                    str(outd),
                ],
                cwd=str(repo_root()),
                env={**env, "PYTHONPATH": pypath},
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(proc.returncode, 0, (proc.stdout, proc.stderr))
            for name in (
                "p7_ablation_summary.csv",
                "p7_negative_family_summary.csv",
                "p7_failure_reason_breakdown.csv",
                "p7_perturbation_reject_matrix.csv",
                "p7_aggregate_lift_metrics.csv",
                "p7_latency_by_mode.csv",
            ):
                self.assertTrue((outd / name).exists(), name)
