"""P7 Standards Mapping: integration test and unit tests for assurance eval."""
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


class TestAssuranceEvalIntegration(unittest.TestCase):
    """Run run_assurance_eval with --out temp; assert results and export script."""

    def setUp(self) -> None:
        os.environ["LABTRUST_KERNEL_DIR"] = str(repo_root() / "kernel")

    def test_assurance_eval_produces_valid_results(self) -> None:
        env = os.environ.copy()
        pypath = str(repo_root() / "impl" / "src")
        script = repo_root() / "scripts" / "run_assurance_eval.py"
        with tempfile.TemporaryDirectory() as td:
            out_dir = Path(td) / "assurance_eval"
            out_dir.mkdir(parents=True)
            proc = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--out",
                    str(out_dir),
                ],
                cwd=str(repo_root()),
                env={**env, "PYTHONPATH": pypath},
                capture_output=True,
                text=True,
                timeout=180,
            )
            self.assertEqual(
                proc.returncode, 0,
                (proc.stdout, proc.stderr)
            )
            results_path = out_dir / "results.json"
            self.assertTrue(
                results_path.exists(),
                "results.json must be produced under --out",
            )
            data = json.loads(results_path.read_text(encoding="utf-8"))
            self.assertIn("run_manifest", data)
            self.assertIn("success_criteria_met", data)
            self.assertTrue(data["success_criteria_met"].get("mapping_ok"))
            self.assertTrue(data["success_criteria_met"].get("ponr_coverage_ok"))
            self.assertIn("mapping_check", data)
            mc = data["mapping_check"]
            self.assertTrue(mc.get("ok"), "mapping_check.ok must be true")
            self.assertTrue(
                mc.get("ponr_coverage_ok"),
                "mapping_check.ponr_coverage_ok must be true",
            )
            self.assertIn("review", data)
            self.assertIn("reviews", data)
            review = data["review"]
            self.assertTrue(
                review.get("exit_ok"),
                "review.exit_ok must be true",
            )
            self.assertIn("evidence_bundle_ok", review)
            self.assertIn("trace_ok", review)
            self.assertIn("controls_covered", review)
            self.assertGreater(
                len(review.get("controls_covered", [])), 0,
                "controls_covered must be non-empty",
            )
            self.assertIn(
                "ponr_coverage", review,
                "review must include ponr_coverage (SOTA metric)",
            )
            pc = review.get("ponr_coverage") or {}
            self.assertIn("ratio", pc)
            self.assertIn(
                "disposition_commit",
                pc.get("required_task_names", []),
                "primary Table 1 review must be lab_profile_v0 with disposition_commit",
            )
            self.assertIn(
                "control_coverage_ratio", review,
                "review must include control_coverage_ratio (SOTA metric)",
            )
            self.assertIn(
                "lab_profile_v0", data["reviews"],
                "reviews must include lab_profile_v0 (kernel PONR scenario)",
            )
            lab_review = data["reviews"]["lab_profile_v0"]
            lab_pc = lab_review.get("ponr_coverage") or {}
            self.assertIn(
                "disposition_commit",
                lab_pc.get("required_task_names", []),
                "lab_profile_v0 must require disposition_commit (kernel PONR)",
            )
            export_script = repo_root() / "scripts" / "export_assurance_tables.py"
            proc_exp = subprocess.run(
                [
                    sys.executable,
                    str(export_script),
                    "--results",
                    str(results_path),
                ],
                cwd=str(repo_root()),
                env={**env, "PYTHONPATH": pypath},
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(
                proc_exp.returncode, 0,
                "export_assurance_tables.py must succeed on results.json",
            )


class TestAssuranceMappingCheck(unittest.TestCase):
    """Unit tests for check_assurance_mapping (schema + PONR coverage)."""

    def setUp(self) -> None:
        os.environ["LABTRUST_KERNEL_DIR"] = str(repo_root() / "kernel")

    def test_check_assurance_mapping_exits_zero_and_outputs_json(self) -> None:
        env = os.environ.copy()
        pypath = str(repo_root() / "impl" / "src")
        script = repo_root() / "scripts" / "check_assurance_mapping.py"
        proc = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(repo_root()),
            env={**env, "PYTHONPATH": pypath},
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(proc.returncode, 0, (proc.stdout, proc.stderr))
        lines = [l.strip() for l in (proc.stdout or "").strip().splitlines()]
        json_line = None
        for line in lines:
            if line.startswith("{"):
                json_line = line
                break
        self.assertIsNotNone(json_line, "stdout must contain a JSON line")
        data = json.loads(json_line)
        self.assertTrue(data.get("mapping_ok"), "mapping_ok must be true")
        self.assertTrue(
            data.get("ponr_coverage_ok"),
            "ponr_coverage_ok must be true",
        )


class TestAuditBundle(unittest.TestCase):
    """Auditor walk-through script: mapping + PONR + optional run review."""

    def setUp(self) -> None:
        os.environ["LABTRUST_KERNEL_DIR"] = str(repo_root() / "kernel")

    def test_audit_bundle_mapping_and_ponr_pass(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(repo_root() / "impl" / "src")
        script = repo_root() / "scripts" / "audit_bundle.py"
        proc = subprocess.run(
            [sys.executable, str(script), "--json-only"],
            cwd=str(repo_root()),
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(proc.returncode, 0, (proc.stdout, proc.stderr))
        lines = [l.strip() for l in (proc.stdout or "").strip().splitlines()]
        json_line = lines[-1] if lines else ""
        self.assertTrue(json_line.startswith("{"), "output must contain JSON")
        data = json.loads(json_line)
        self.assertEqual(
            data.get("mapping_completeness"), "pass",
            "mapping_completeness must be pass",
        )
        self.assertEqual(
            data.get("ponr_coverage"), "pass",
            "ponr_coverage must be pass",
        )

    def test_audit_bundle_with_run_dir(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(repo_root() / "impl" / "src")
        env["LABTRUST_KERNEL_DIR"] = str(repo_root() / "kernel")
        sys.path.insert(0, str(repo_root() / "impl" / "src"))
        script = repo_root() / "scripts" / "audit_bundle.py"
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td)
            from labtrust_portfolio.thinslice import run_thin_slice  # noqa: E402
            run_thin_slice(run_dir, seed=1, drop_completion_prob=0.0)
            proc = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--run-dir",
                    str(run_dir),
                    "--scenario-id",
                    "toy_lab_v0",
                    "--json-only",
                ],
                cwd=str(repo_root()),
                env=env,
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertEqual(proc.returncode, 0, (proc.stdout, proc.stderr))
            lines = [l.strip() for l in (proc.stdout or "").strip().splitlines()]
            json_line = lines[-1] if lines else "{}"
            self.assertTrue(json_line.startswith("{"))
            data = json.loads(json_line)
            self.assertEqual(data.get("mapping_completeness"), "pass")
            self.assertEqual(data.get("ponr_coverage"), "pass")
            self.assertTrue(data.get("review_exit_ok"), "review must pass on valid run dir")


class TestScenarioPackCompatibility(unittest.TestCase):
    """full_review must reject scenarios outside pack-declared compatibility."""

    def setUp(self) -> None:
        os.environ["LABTRUST_KERNEL_DIR"] = str(repo_root() / "kernel")

    def test_full_review_rejects_incompatible_scenario_pack(self) -> None:
        sys.path.insert(0, str(repo_root() / "impl" / "src"))
        from labtrust_portfolio.assurance_review_pipeline import review_assurance_pipeline  # noqa: E402
        from labtrust_portfolio.thinslice import run_thin_slice  # noqa: E402

        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td) / "run_traffic"
            run_dir.mkdir(parents=True)
            run_thin_slice(run_dir, seed=7, scenario_id="traffic_v0", drop_completion_prob=0.0)

            wh_pack = repo_root() / "profiles" / "warehouse" / "v0.1" / "assurance_pack_instantiation.json"
            out = review_assurance_pipeline(
                run_dir,
                wh_pack,
                "traffic_v0",
                "full_review",
                profile_dir=repo_root() / "profiles" / "medical_v0.1",
                repo_root=repo_root(),
            )
            self.assertFalse(out.get("exit_ok"), out)
            self.assertIn("SCENARIO_PACK_MISMATCH", out.get("failure_reason_codes") or [])
