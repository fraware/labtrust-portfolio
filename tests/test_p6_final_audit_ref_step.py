"""Reference-step resolution for P6 final audit bundle (stress rs_* ids)."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


class TestP6FinalAuditRefStep(unittest.TestCase):
    def tearDown(self) -> None:
        for k in ("export_p6_final_audit_bundle_rs", "export_p6_final_audit_bundle_rs2"):
            sys.modules.pop(k, None)

    def _load_mod(self, name: str):
        spec = importlib.util.spec_from_file_location(
            name,
            REPO / "scripts" / "export_p6_final_audit_bundle.py",
        )
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
        return mod

    def test_ref_step_rs_safe(self) -> None:
        mod = self._load_mod("export_p6_final_audit_bundle_rs")
        step = mod._ref_step_for_case("rs_safe_01")
        self.assertEqual(step.get("tool"), "query_status")
        self.assertIn("allow_list", step.get("validators") or [])

    def test_ref_step_unknown_rs_empty(self) -> None:
        mod = self._load_mod("export_p6_final_audit_bundle_rs2")
        self.assertEqual(mod._ref_step_for_case("rs_nonexistent_xyz_999"), {})


if __name__ == "__main__":
    unittest.main()
