"""Tests for robust GPT audit materializer and stress case corpus."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


class TestP6RobustGptMaterialize(unittest.TestCase):
    def test_stress_cases_validate_and_count(self) -> None:
        p = REPO / "datasets" / "cases" / "p6_real_llm_stress_cases.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        cases = data.get("cases", [])
        self.assertGreaterEqual(len(cases), 35)
        from labtrust_portfolio.llm_planning import validate_plan_step

        allowed = ["query_status", "submit_result"]
        for c in cases:
            step = c["step"]
            exp = c["expected_block"]
            ok, _ = validate_plan_step(step, allowed)
            blocked = not ok
            self.assertEqual(
                blocked,
                exp,
                msg=f"{c['id']}: validator blocked={blocked} expected_block={exp}",
            )

    def test_materialize_independence_verdict(self) -> None:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "p6_robust_gpt_materialize",
            REPO / "scripts" / "p6_robust_gpt_materialize.py",
        )
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        red = json.loads(
            (REPO / "datasets" / "runs" / "llm_eval_camera_ready_20260424" / "red_team_results.json").read_text(
                encoding="utf-8"
            )
        )
        ind = mod.build_independence_audit(red)
        self.assertTrue(ind.get("distinct_model_ids"))
        self.assertTrue(ind.get("same_denominator"))
        self.assertEqual(ind.get("verdict"), "independent_runs_confirmed")


if __name__ == "__main__":
    unittest.main()
