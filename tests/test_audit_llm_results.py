"""Tests for scripts/audit_llm_results.py scoring and CLI contract."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _load_audit_module():
    spec = importlib.util.spec_from_file_location(
        "audit_llm_results_t",
        REPO / "scripts" / "audit_llm_results.py",
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestAuditLlmScoring(unittest.TestCase):
    def test_red_team_scoring_ok(self) -> None:
        mod = _load_audit_module()
        red = {
            "run_manifest": {"real_llm_prompt_variants": ["canonical"]},
            "real_llm_models": [
                {
                    "model_id": "m-a",
                    "n_pass_total": 5,
                    "n_runs_total": 5,
                    "prompt_variants": ["canonical"],
                    "run_manifest": {"real_llm_variant_fingerprint": "fp1"},
                    "cases": [
                        {"case_id": "c1", "prompt_variant": "canonical", "pass_count": 2, "n_runs": 2},
                        {"case_id": "c2", "prompt_variant": "canonical", "pass_count": 3, "n_runs": 3},
                    ],
                }
            ],
        }
        r = mod.audit_scoring_from_red_team(red)
        self.assertTrue(r["scoring_ok"])
        self.assertTrue(r["models"][0]["pass_sum_matches_aggregate"])
        self.assertTrue(r["models"][0]["runs_sum_matches_aggregate"])

    def test_red_team_scoring_mismatch(self) -> None:
        mod = _load_audit_module()
        red = {
            "run_manifest": {"real_llm_prompt_variants": ["canonical"]},
            "real_llm_models": [
                {
                    "model_id": "m-b",
                    "n_pass_total": 99,
                    "n_runs_total": 5,
                    "prompt_variants": ["canonical"],
                    "cases": [
                        {"case_id": "c1", "prompt_variant": "canonical", "pass_count": 2, "n_runs": 2},
                        {"case_id": "c2", "prompt_variant": "canonical", "pass_count": 3, "n_runs": 3},
                    ],
                }
            ],
        }
        r = mod.audit_scoring_from_red_team(red)
        self.assertFalse(r["scoring_ok"])
        self.assertFalse(r["models"][0]["pass_sum_matches_aggregate"])

    def test_prompt_variant_manifest_mismatch(self) -> None:
        mod = _load_audit_module()
        red = {
            "run_manifest": {"real_llm_prompt_variants": ["canonical", "strict_json"]},
            "real_llm_models": [
                {
                    "model_id": "m-c",
                    "n_pass_total": 1,
                    "n_runs_total": 1,
                    "prompt_variants": ["canonical"],
                    "cases": [{"case_id": "c1", "prompt_variant": "canonical", "pass_count": 1, "n_runs": 1}],
                }
            ],
        }
        r = mod.audit_scoring_from_red_team(red)
        self.assertFalse(r["scoring_ok"])
        self.assertFalse(r["models"][0]["prompt_variant_lists_aligned"])

    def test_no_real_llm_models_neutral(self) -> None:
        mod = _load_audit_module()
        r = mod.audit_scoring_from_red_team({"real_llm_models": []})
        self.assertTrue(r["scoring_ok"])
        self.assertIn("note", r)

    def test_materialized_scoring_reads_summary(self) -> None:
        mod = _load_audit_module()
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            (d / "statistical_summary.json").write_text(
                json.dumps(
                    {
                        "scoring_consistency": [
                            {"model_id": "x", "matches_aggregate_to_case_sum": True},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            r = mod.audit_materialized_scoring(d)
            assert r is not None
            self.assertTrue(r["scoring_ok"])

    def test_main_json_exit_zero_on_robust_package(self) -> None:
        """Smoke: default robust package has independence + materialized scoring."""
        mod = _load_audit_module()
        rd = REPO / "datasets" / "runs" / "llm_eval_robust_gpt_20260424"
        if not (rd / "canonical_independence_audit.json").exists():
            self.skipTest("robust package not present")
        argv = [str(REPO / "scripts" / "audit_llm_results.py"), "--run-dir", str(rd), "--json"]
        old = sys.argv
        try:
            sys.argv = argv
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = mod.main()
        finally:
            sys.argv = old
        self.assertEqual(code, 0)
        self.assertIn("overall_scoring_ok", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
