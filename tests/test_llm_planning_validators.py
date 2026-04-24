"""Unit tests for P6 llm_planning validators (allow_list, safe_args, ponr_gate, privilege)."""
from __future__ import annotations

import unittest

from labtrust_portfolio.llm_planning import (
    CONFUSABLE_DEPUTY_CASES,
    JAILBREAK_STYLE_CASES,
    MockToolExecutor,
    RED_TEAM_CASES,
    StepDecision,
    safe_args_check,
    validate_plan,
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


class TestTypedPlanValidation(unittest.TestCase):
    def test_duplicate_seq_denied(self) -> None:
        plan = {
            "version": "0.1",
            "plan_id": "p1",
            "steps": [
                {"seq": 0, "tool": "query_status", "args": {}, "validators": ["allow_list"]},
                {"seq": 0, "tool": "submit_result", "args": {}, "validators": ["allow_list"]},
            ],
        }
        ok, errs = validate_plan(plan)
        self.assertFalse(ok)
        self.assertTrue(any("duplicate sequence identifiers" in e for e in errs))

    def test_non_monotone_seq_denied(self) -> None:
        plan = {
            "version": "0.1",
            "plan_id": "p2",
            "steps": [
                {"seq": 1, "tool": "query_status", "args": {}, "validators": ["allow_list"]},
                {"seq": 0, "tool": "submit_result", "args": {}, "validators": ["allow_list"]},
            ],
        }
        ok, errs = validate_plan(plan)
        self.assertFalse(ok)
        self.assertTrue(any("monotone increasing" in e for e in errs))


class TestSafeArgsHardening(unittest.TestCase):
    def test_recursive_deny_key_is_blocked(self) -> None:
        step = {
            "seq": 0,
            "tool": "query_status",
            "args": {"payload": {"nested": {"script": "evil"}}},
            "validators": ["allow_list", "safe_args"],
        }
        ok, violations = safe_args_check(step)
        self.assertFalse(ok)
        self.assertTrue(any("deny-list key 'script'" in v for v in violations))

    def test_normalized_path_traversal_is_blocked(self) -> None:
        step = {
            "seq": 0,
            "tool": "query_status",
            "args": {"output_path": "reports\\..\\..\\secrets.txt"},
            "validators": ["allow_list", "safe_args"],
        }
        ok, violations = safe_args_check(step)
        self.assertFalse(ok)
        self.assertTrue(any("path traversal" in v for v in violations))


class TestMockToolExecutor(unittest.TestCase):
    def test_denied_disallowed_tool_not_executed(self) -> None:
        step = {"seq": 0, "tool": "execute_system", "args": {"cmd": "rm -rf"}, "validators": ["allow_list"]}
        allowed, reasons, _ = validate_plan_step_with_attribution(step, ALLOWED)
        ex = MockToolExecutor()
        ex.execute_if_allowed(step, StepDecision(allowed=allowed, reasons=reasons))
        self.assertEqual(len(ex.executed), 0)
        self.assertEqual(len(ex.denied), 1)

    def test_denied_unsafe_args_not_executed(self) -> None:
        step = {
            "seq": 1,
            "tool": "query_status",
            "args": {"path": "../../../etc/passwd"},
            "validators": ["allow_list", "safe_args"],
        }
        allowed, reasons, _ = validate_plan_step_with_attribution(step, ALLOWED)
        ex = MockToolExecutor()
        ex.execute_if_allowed(step, StepDecision(allowed=allowed, reasons=reasons))
        self.assertEqual(len(ex.executed), 0)
        self.assertEqual(len(ex.denied), 1)

    def test_allowed_safe_step_is_executed(self) -> None:
        step = {"seq": 0, "tool": "query_status", "args": {}, "validators": ["allow_list"]}
        allowed, reasons, _ = validate_plan_step_with_attribution(step, ALLOWED)
        ex = MockToolExecutor()
        ex.execute_if_allowed(step, StepDecision(allowed=allowed, reasons=reasons))
        self.assertEqual(len(ex.executed), 1)
        self.assertEqual(len(ex.denied), 0)

    def test_ungated_mode_executes_unsafe_step(self) -> None:
        step = {"seq": 0, "tool": "execute_system", "args": {"cmd": "rm -rf"}, "validators": ["allow_list"]}
        ex = MockToolExecutor()
        ex.execute_if_allowed(step, StepDecision(allowed=True, reasons=["mock ungated"]))
        self.assertEqual(len(ex.executed), 1)
        self.assertEqual(len(ex.denied), 0)


if __name__ == "__main__":
    unittest.main()
