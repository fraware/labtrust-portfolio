"""Integration test for AIES assurance packaging exports."""
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


class TestAssuranceAiesExports(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["LABTRUST_KERNEL_DIR"] = str(repo_root() / "kernel")

    def test_aies_bundle_exports(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(repo_root() / "impl" / "src")
        run_eval = repo_root() / "scripts" / "run_assurance_eval.py"
        run_neg = repo_root() / "scripts" / "run_assurance_negative_eval.py"
        export_tables = repo_root() / "scripts" / "export_aies_assurance_tables.py"
        export_packet = repo_root() / "scripts" / "export_bounded_review_packet.py"
        export_fig = repo_root() / "scripts" / "export_aies_review_packet_figure.py"

        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "assurance_eval_aies"
            out.mkdir(parents=True)

            p1 = subprocess.run(
                [sys.executable, str(run_eval), "--out", str(out)],
                cwd=str(repo_root()),
                env=env,
                capture_output=True,
                text=True,
                timeout=240,
            )
            self.assertEqual(p1.returncode, 0, (p1.stdout, p1.stderr))

            p2 = subprocess.run(
                [
                    sys.executable,
                    str(run_neg),
                    "--quick",
                    "--submission-mode",
                    "--out",
                    str(out),
                ],
                cwd=str(repo_root()),
                env=env,
                capture_output=True,
                text=True,
                timeout=240,
            )
            self.assertEqual(p2.returncode, 0, (p2.stdout, p2.stderr))

            # Materialize one representative lab_profile_v0 run for packet export.
            sys.path.insert(0, str(repo_root() / "impl" / "src"))
            from labtrust_portfolio.thinslice import run_thin_slice  # noqa: E402

            run_dir = out / "runs" / "lab_profile_v0_seed7"
            run_dir.mkdir(parents=True)
            run_thin_slice(run_dir, seed=7, scenario_id="lab_profile_v0", drop_completion_prob=0.0)

            packet_dir = out / "bounded_review_packet"
            p3 = subprocess.run(
                [
                    sys.executable,
                    str(export_packet),
                    "--run-dir",
                    str(run_dir),
                    "--out",
                    str(packet_dir),
                    "--scenario-id",
                    "lab_profile_v0",
                ],
                cwd=str(repo_root()),
                env=env,
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(p3.returncode, 0, (p3.stdout, p3.stderr))

            p4 = subprocess.run(
                [
                    sys.executable,
                    str(export_tables),
                    "--in",
                    str(out),
                    "--out",
                    str(out / "tables"),
                ],
                cwd=str(repo_root()),
                env=env,
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(p4.returncode, 0, (p4.stdout, p4.stderr))

            p5 = subprocess.run(
                [
                    sys.executable,
                    str(export_fig),
                    "--in",
                    str(packet_dir),
                    "--out",
                    str(out / "figures"),
                ],
                cwd=str(repo_root()),
                env=env,
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(p5.returncode, 0, (p5.stdout, p5.stderr))

            for req in (
                out / "baseline_summary.json",
                out / "institutional_positive_summary.json",
                out / "negative_summary.json",
                out / "RUN_MANIFEST.json",
                out / "README.md",
                out / "tables" / "baseline_table.tex",
                out / "tables" / "portability_table.tex",
                out / "tables" / "negative_ablation_table.tex",
                out / "tables" / "failure_family_table.tex",
                out / "tables" / "negative_failure_families.csv",
                out / "tables" / "negative_failure_reasons.csv",
                out / "proxy_stress_only" / "traffic_medical_proxy_summary.json",
                out / "bounded_review_packet" / "packet_manifest.json",
                out / "figures" / "review_packet_figure.mmd",
            ):
                self.assertTrue(req.exists(), str(req))

            baseline = json.loads((out / "baseline_summary.json").read_text(encoding="utf-8"))
            self.assertEqual(baseline.get("scenario_id"), "lab_profile_v0")
            inst = json.loads(
                (out / "institutional_positive_summary.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                (inst.get("portability_case") or {}).get("scenario_id"),
                "warehouse_v0",
            )

