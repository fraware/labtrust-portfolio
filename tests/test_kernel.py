"""Tests for kernel validation and schema loading."""
from __future__ import annotations

import os
import subprocess
import unittest
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


class TestValidateKernelScript(unittest.TestCase):
    """Test scripts/validate_kernel.py exits 0 and reports expected schema count."""

    def test_validate_kernel_exits_zero(self) -> None:
        script = repo_root() / "scripts" / "validate_kernel.py"
        self.assertTrue(script.exists(), "validate_kernel.py must exist")
        result = subprocess.run(
            [os.environ.get("PYTHON", "python"), str(script)],
            cwd=repo_root(),
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0, f"stdout={result.stdout!r} stderr={result.stderr!r}")

    def test_validate_kernel_reports_schema_count(self) -> None:
        script = repo_root() / "scripts" / "validate_kernel.py"
        result = subprocess.run(
            [os.environ.get("PYTHON", "python"), str(script)],
            cwd=repo_root(),
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0)
        kernel = repo_root() / "kernel"
        expected_count = len(list(kernel.rglob("*.schema.json")))
        self.assertIn(f"{expected_count} schemas validated", result.stdout)
        self.assertIn("VERSION=", result.stdout)


class TestSchemaLoading(unittest.TestCase):
    """Test that impl can load each kernel schema used by the thin-slice pipeline."""

    def setUp(self) -> None:
        kernel_dir = repo_root() / "kernel"
        os.environ["LABTRUST_KERNEL_DIR"] = str(kernel_dir.resolve())

    def test_load_release_train_schemas(self) -> None:
        from labtrust_portfolio.schema import load_schema

        schemas = [
            "trace/TRACE.v0.1.schema.json",
            "eval/MAESTRO_REPORT.v0.1.schema.json",
            "mads/EVIDENCE_BUNDLE.v0.1.schema.json",
            "policy/RELEASE_MANIFEST.v0.1.schema.json",
        ]
        for relpath in schemas:
            with self.subTest(relpath=relpath):
                schema = load_schema(relpath)
                self.assertIn("$schema", schema)
                self.assertIn("$id", schema)
                self.assertIn("type", schema)
