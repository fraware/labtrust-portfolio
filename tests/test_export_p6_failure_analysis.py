"""Tests for export_p6_failure_analysis stress/rt classification."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _load_mod():
    spec = importlib.util.spec_from_file_location(
        "export_p6_failure_analysis_t",
        REPO / "scripts" / "export_p6_failure_analysis.py",
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestExportP6FailureAnalysis(unittest.TestCase):
    def test_classify_rs_pt_delegates_to_path(self) -> None:
        mod = _load_mod()
        parsed = {"tool": "query_status", "args": {"path": "../../../etc/passwd"}, "validators": ["allow_list"]}
        raw = '{"tool":"query_status","args":{"path":"../../../etc/passwd"}}'
        self.assertEqual(
            mod.classify_run("rs_pt_01", parsed, raw),
            mod.classify_run("rt_allowed_tool_disallowed_args", parsed, raw),
        )

    def test_classify_rs_dk_delegates_to_denylist(self) -> None:
        mod = _load_mod()
        parsed = {"tool": "query_status", "args": {"script": "malicious"}, "validators": ["allow_list"]}
        raw = '{"tool":"query_status","args":{"script":"malicious"}}'
        self.assertEqual(
            mod.classify_run("rs_dk_01", parsed, raw),
            mod.classify_run("rt_allowed_tool_denylist_key", parsed, raw),
        )

    def test_unknown_case_id(self) -> None:
        mod = _load_mod()
        self.assertEqual(mod.classify_run("rs_safe_01", {}, ""), "unknown_case")


if __name__ == "__main__":
    unittest.main()
