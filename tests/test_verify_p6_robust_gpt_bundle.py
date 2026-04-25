"""Smoke test for verify_p6_robust_gpt_bundle.py."""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


class TestVerifyP6RobustGptBundle(unittest.TestCase):
    def test_verify_default_bundle(self) -> None:
        rd = REPO / "datasets" / "runs" / "llm_eval_robust_gpt_20260424"
        if not (rd / "MANIFEST.json").exists():
            self.skipTest("robust bundle not present")
        r = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "verify_p6_robust_gpt_bundle.py")],
            cwd=str(REPO),
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 0, msg=r.stderr + r.stdout)

    def test_verify_skip_audit_bad_dir(self) -> None:
        r = subprocess.run(
            [
                sys.executable,
                str(REPO / "scripts" / "verify_p6_robust_gpt_bundle.py"),
                "--run-dir",
                str(REPO / "datasets" / "runs" / "nonexistent_robust_dir_xyz"),
                "--skip-audit",
            ],
            cwd=str(REPO),
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
