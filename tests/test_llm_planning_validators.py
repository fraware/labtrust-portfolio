"""Unit tests for P6 llm_planning validators (allow_list, safe_args, ponr_gate, privilege)."""
from __future__ import annotations

import unittest

from labtrust_portfolio.llm_planning import (
    CONFUSABLE_DEPUTY_CASES,
    JAILBREAK_STYLE_CASES,
    RED_TEAM_CASES,
    ponr_gate_check,
    validate_plan_step_with_attribution,
)


ALLOWED = ["query_status", "submit_result"]


class TestPonrGate(unittest.TestCase):
    def test_blocks_bypass_key(self) -> None:
        step = {
            "seq": 0,
            "tool": "submit_result",
            "args": {"task_id": "t1", "bypass_safety_gate": True},
            "validators": ["allow_list", "ponr_gate"],
        }
        ok, viol = ponr_gate_check(step)
        self.assertFalse(ok)
        self.assertTrue(any("bypass_safety_gate" in v for v in viol))

    def test_admits_safe_submit(self) -> None:
        step = {
            "seq": 0,
            "tool": "submit_result",
            "args": {"task_id": "t1", "value": 0.0},
            "validators": ["allow_list", "ponr_gate"],
        }
        ok, viol = ponr_gate_check(step)
        self.assertTrue(ok)
        self.assertEqual(viol, [])


class TestSyntheticSuites(unittest.TestCase):
    def test_red_team_all_expected_match_validator(self) -> None:
        for c in RED_TEAM_CASES:
            with self.subTest(case_id=c["id"]):
                allowed, _reasons, _attr = validate_plan_step_with_attribution(
                    c["step"], ALLOWED
                )
                blocked = not allowed
                self.assertEqual(blocked, c["expected_block"], msg=c["id"])

    def test_confusable_all_expected(self) -> None:
        for c in CONFUSABLE_DEPUTY_CASES:
            with self.subTest(case_id=c["id"]):
                allowed, _reasons, _attr = validate_plan_step_with_attribution(
                    c["step"], ALLOWED
                )
                blocked = not allowed
                self.assertEqual(blocked, c["expected_block"], msg=c["id"])

    def test_jailbreak_all_expected(self) -> None:
        for c in JAILBREAK_STYLE_CASES:
            with self.subTest(case_id=c["id"]):
                allowed, _reasons, _attr = validate_plan_step_with_attribution(
                    c["step"], ALLOWED
                )
                blocked = not allowed
                self.assertEqual(blocked, c["expected_block"], msg=c["id"])

    def test_red_team_minimum_size(self) -> None:
        self.assertGreaterEqual(len(RED_TEAM_CASES), 15)
        self.assertGreaterEqual(len(CONFUSABLE_DEPUTY_CASES), 6)
        self.assertGreaterEqual(len(JAILBREAK_STYLE_CASES), 4)


if __name__ == "__main__":
    unittest.main()
