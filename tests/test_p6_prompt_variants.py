"""Unit tests for P6 real-LLM prompt variant helpers."""
from __future__ import annotations

import unittest
from pathlib import Path

from labtrust_portfolio.p6_prompt_variants import (
    PROMPT_VARIANT_NAMES,
    TYPED_STEP_JSON_SCHEMA,
    build_real_llm_user_prompt,
    openai_json_schema_response_format,
    parse_prompt_variant_list,
)


class TestP6PromptVariants(unittest.TestCase):
    def test_parse_default_and_order(self) -> None:
        self.assertEqual(parse_prompt_variant_list(None), ["canonical"])
        self.assertEqual(parse_prompt_variant_list(""), ["canonical"])
        self.assertEqual(
            parse_prompt_variant_list("strict_json,canonical"),
            ["strict_json", "canonical"],
        )

    def test_parse_dedup(self) -> None:
        self.assertEqual(
            parse_prompt_variant_list("canonical,canonical,json_schema"),
            ["canonical", "json_schema"],
        )

    def test_parse_unknown_raises(self) -> None:
        with self.assertRaises(ValueError):
            parse_prompt_variant_list("not_a_variant")

    def test_build_unknown_variant_raises(self) -> None:
        step = {"tool": "query_status", "args": {}}
        with self.assertRaises(ValueError):
            build_real_llm_user_prompt("rt_empty_tool", step, "nope")

    def test_json_schema_prompt_includes_three_keys(self) -> None:
        step = {"tool": "query_status", "args": {}, "validators": ["allow_list"]}
        p = build_real_llm_user_prompt("rt_empty_tool", step, "json_schema")
        self.assertIn("validators", p)
        self.assertIn('"tool"', p)

    def test_openai_response_format_shape(self) -> None:
        rf = openai_json_schema_response_format()
        self.assertEqual(rf.get("type"), "json_schema")
        self.assertIn("json_schema", rf)
        self.assertEqual(rf["json_schema"].get("name"), "typed_plan_step")
        self.assertTrue(rf["json_schema"].get("strict"))

    def test_typed_step_schema_required(self) -> None:
        req = set(TYPED_STEP_JSON_SCHEMA.get("required", []))
        self.assertTrue({"tool", "args", "validators"}.issubset(req))

    def test_all_names_parse_roundtrip(self) -> None:
        s = ",".join(PROMPT_VARIANT_NAMES)
        got = parse_prompt_variant_list(s)
        self.assertEqual(got, list(PROMPT_VARIANT_NAMES))


class TestCrossModelSummaryKeys(unittest.TestCase):
    def test_composite_case_variant_key(self) -> None:
        import importlib.util

        root = Path(__file__).resolve().parents[1]
        spec = importlib.util.spec_from_file_location(
            "llm_redteam_eval_xs",
            root / "scripts" / "llm_redteam_eval.py",
        )
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        m1 = {
            "model_id": "m1",
            "cases": [{"case_id": "c1", "prompt_variant": "canonical", "n_runs": 10, "pass_count": 10}],
        }
        m2 = {
            "model_id": "m2",
            "cases": [{"case_id": "c1", "prompt_variant": "canonical", "n_runs": 10, "pass_count": 5}],
        }
        cross = mod._compute_cross_model_summary([m1, m2])
        assert cross is not None
        self.assertIn("c1|canonical", cross["per_case_pass_rates"])

    def test_variant_split_same_case_id(self) -> None:
        import importlib.util

        root = Path(__file__).resolve().parents[1]
        spec = importlib.util.spec_from_file_location(
            "llm_redteam_eval_xs2",
            root / "scripts" / "llm_redteam_eval.py",
        )
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        m1 = {
            "model_id": "m1",
            "cases": [
                {"case_id": "c1", "prompt_variant": "canonical", "n_runs": 1, "pass_count": 1},
                {"case_id": "c1", "prompt_variant": "strict_json", "n_runs": 1, "pass_count": 0},
            ],
        }
        m2 = {
            "model_id": "m2",
            "cases": [
                {"case_id": "c1", "prompt_variant": "canonical", "n_runs": 1, "pass_count": 1},
                {"case_id": "c1", "prompt_variant": "strict_json", "n_runs": 1, "pass_count": 1},
            ],
        }
        cross = mod._compute_cross_model_summary([m1, m2])
        assert cross is not None
        self.assertIn("c1|canonical", cross["per_case_pass_rates"])
        self.assertIn("c1|strict_json", cross["per_case_pass_rates"])


if __name__ == "__main__":
    unittest.main()
