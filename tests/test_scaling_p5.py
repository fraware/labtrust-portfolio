"""P5 Scaling: integration test and unit tests for scaling module."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SRC = str(_ROOT / "impl" / "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

try:
    from labtrust_portfolio.scaling import (
        build_dataset_from_runs,
        build_scaling_holdout_folds,
        fit_linear_predictor,
        fit_scaling_exponent,
        predict_baseline_mean,
        predict_by_scenario,
    )
except ImportError:
    build_dataset_from_runs = None
    build_scaling_holdout_folds = None
    fit_linear_predictor = None
    fit_scaling_exponent = None
    predict_baseline_mean = None
    predict_by_scenario = None


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


class TestScalingHeldoutEvalIntegration(unittest.TestCase):
    """Run multiscenario_runs then scaling_heldout_eval; assert output."""

    def setUp(self) -> None:
        os.environ["LABTRUST_KERNEL_DIR"] = str(repo_root() / "kernel")

    def test_scaling_heldout_eval_produces_valid_heldout_results(self) -> None:
        env = os.environ.copy()
        pypath = str(repo_root() / "impl" / "src")
        gen_script = repo_root() / "scripts" / "generate_multiscenario_runs.py"
        eval_script = repo_root() / "scripts" / "scaling_heldout_eval.py"
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            runs_dir = base / "multiscenario_runs"
            out_dir = base / "scaling_eval"
            proc_gen = subprocess.run(
                [
                    sys.executable,
                    str(gen_script),
                    "--out",
                    str(runs_dir),
                    "--seeds",
                    "2",
                    "--coordination-grid",
                    "--p5-lite",
                    "--clean",
                    "--profile",
                    "core",
                    "--scenarios",
                    "toy_lab_v0,lab_profile_v0,warehouse_v0",
                ],
                cwd=str(repo_root()),
                env={**env, "PYTHONPATH": pypath},
                capture_output=True,
                text=True,
                timeout=900,
            )
            self.assertEqual(
                proc_gen.returncode, 0,
                (proc_gen.stdout, proc_gen.stderr)
            )
            proc_eval = subprocess.run(
                [
                    sys.executable,
                    str(eval_script),
                    "--runs-dir",
                    str(runs_dir),
                    "--out",
                    str(out_dir),
                ],
                cwd=str(repo_root()),
                env={**env, "PYTHONPATH": pypath},
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertEqual(
                proc_eval.returncode, 0,
                (proc_eval.stdout, proc_eval.stderr)
            )
            results_path = out_dir / "heldout_results.json"
            self.assertTrue(
                results_path.exists(),
                "heldout_results.json must be produced",
            )
            data = json.loads(results_path.read_text(encoding="utf-8"))
            self.assertIn("held_out_results", data)
            self.assertIn("overall_baseline_mae", data)
            self.assertIn("overall_feat_baseline_mae", data)
            self.assertIn("admissible_baselines", data)
            self.assertIn("oracle_baselines", data)
            self.assertIn("total_rows", data)
            self.assertIn("scenario_ids", data)
            self.assertGreater(len(data["held_out_results"]), 0)
            self.assertGreater(data["total_rows"], 0)
            self.assertGreaterEqual(
                len(data["scenario_ids"]), 2,
                "Need at least 2 scenarios for held-out eval",
            )
            self.assertIn(
                "overall_baseline_mae_ci95_lower", data,
                "Summary must include 95% CI for baseline MAE",
            )
            self.assertIn(
                "overall_feat_baseline_mae_ci95_lower", data,
                "Summary must include 95% CI for feat baseline MAE",
            )
            self.assertIn(
                "scaling_fit", data,
                "Summary must include scaling_fit (exploratory exponent)",
            )
            self.assertIn("run_manifest", data)
            rm = data["run_manifest"]
            self.assertIn("script", rm)
            self.assertIn("coordination_regimes", rm)
            self.assertIn("agent_counts", rm)
            self.assertGreaterEqual(len(data["held_out_results"]), 2, "held_out_results length >= 2")
            self.assertIn("success_criteria_met", data)
            sc = data["success_criteria_met"]
            self.assertIn("beat_global_mean_out_of_sample", sc)
            self.assertIn("beat_feature_baseline_out_of_sample", sc)
            self.assertIn("beat_regime_baseline_out_of_sample", sc)
            self.assertIn("trigger_met", sc)
            self.assertIsInstance(sc.get("beat_global_mean_out_of_sample"), bool)
            self.assertIsInstance(sc.get("trigger_met"), bool)
            first = data["held_out_results"][0]
            self.assertLessEqual(
                first["oracle_per_scenario_baseline_mae"] + 1e-6,
                first["admissible_per_scenario_train_mae"] + 1e-6,
                "Oracle per-scenario MAE should be <= admissible train-only (leakage helps)",
            )
            if "overall_baseline_mae_ci95_lower" in data and "overall_baseline_mae_ci95_upper" in data:
                self.assertLessEqual(
                    data["overall_baseline_mae_ci95_lower"],
                    data.get("overall_baseline_mae", 0) + 0.01,
                )
                self.assertGreaterEqual(
                    data["overall_baseline_mae_ci95_upper"],
                    data.get("overall_baseline_mae", 0) - 0.01,
                )
            first = data["held_out_results"][0]
            self.assertIn(
                "regression_mae", first,
                "Each held-out result must include regression_mae",
            )
            self.assertIn(
                "test_collapse_rate", first,
                "Each held-out result must include test_collapse_rate",
            )
            export_script = repo_root() / "scripts" / "export_scaling_tables.py"
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
                timeout=10,
            )
            self.assertEqual(
                proc_exp.returncode, 0,
                "export_scaling_tables must succeed on eval output",
            )
            sens_dir = base / "sensitivity_sweep"
            proc_sens = subprocess.run(
                [
                    sys.executable,
                    str(repo_root() / "scripts" / "scaling_sensitivity_sweep.py"),
                    "--runs-dir",
                    str(runs_dir),
                    "--out-dir",
                    str(sens_dir),
                    "--caps",
                    "1,2",
                ],
                cwd=str(repo_root()),
                env={**env, "PYTHONPATH": pypath},
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(proc_sens.returncode, 0, (proc_sens.stdout, proc_sens.stderr))
            self.assertTrue((sens_dir / "scaling_sensitivity.json").exists())
            rec_path = base / "recommendation_eval.json"
            proc_rec = subprocess.run(
                [
                    sys.executable,
                    str(repo_root() / "scripts" / "scaling_recommend_eval.py"),
                    "--runs-dir",
                    str(runs_dir),
                    "--out",
                    str(rec_path),
                ],
                cwd=str(repo_root()),
                env={**env, "PYTHONPATH": pypath},
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(proc_rec.returncode, 0, (proc_rec.stdout, proc_rec.stderr))
            self.assertTrue(rec_path.exists())


class TestScalingModule(unittest.TestCase):
    """Unit tests for scaling.py: regression, scaling exponent, collapse."""

    def setUp(self) -> None:
        os.environ["LABTRUST_KERNEL_DIR"] = str(repo_root() / "kernel")

    def test_fit_linear_predictor_returns_predictor(self) -> None:
        if fit_linear_predictor is None:
            self.skipTest("scaling module not importable")
        rows = [
            {"num_tasks": 3, "num_faults": 1, "response": {"tasks_completed": 3}},
            {"num_tasks": 4, "num_faults": 0, "response": {"tasks_completed": 4}},
            {"num_tasks": 5, "num_faults": 1, "response": {"tasks_completed": 5}},
        ]
        pred = fit_linear_predictor(rows, "tasks_completed")
        self.assertIsNotNone(pred)
        out = pred({"num_tasks": 4, "num_faults": 0})
        self.assertIsInstance(out, (int, float))

    def test_fit_linear_predictor_empty_returns_none(self) -> None:
        if fit_linear_predictor is None:
            self.skipTest("scaling module not importable")
        self.assertIsNone(fit_linear_predictor([], "tasks_completed"))

    def test_fit_scaling_exponent_returns_dict(self) -> None:
        if fit_scaling_exponent is None:
            self.skipTest("scaling module not importable")
        rows = [
            {"num_tasks": 2, "response": {"tasks_completed": 2}},
            {"num_tasks": 3, "response": {"tasks_completed": 3}},
            {"num_tasks": 4, "response": {"tasks_completed": 4}},
        ]
        out = fit_scaling_exponent(rows, "tasks_completed", "num_tasks")
        self.assertIsInstance(out, dict)
        if out:
            self.assertIn("scaling_exponent", out)
            self.assertIn("scaling_r2", out)

    def test_fit_scaling_exponent_insufficient_data_returns_empty(self) -> None:
        if fit_scaling_exponent is None:
            self.skipTest("scaling module not importable")
        rows = [{"num_tasks": 1, "response": {"tasks_completed": 1}}]
        out = fit_scaling_exponent(rows, "tasks_completed", "num_tasks")
        self.assertEqual(out, {})

    def test_build_dataset_adds_collapse(self) -> None:
        if build_dataset_from_runs is None:
            self.skipTest("scaling module not importable")
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            run_dir = base / "s1" / "no_drop" / "seed_1"
            run_dir.mkdir(parents=True)
            trace = {"scenario_id": "toy_lab_v0", "seed": 1, "events": []}
            report = {
                "metrics": {"tasks_completed": 1, "coordination_messages": 0},
                "faults": {"recovery_ok": True, "fault_injected": False},
            }
            (run_dir / "trace.json").write_text(
                json.dumps(trace), encoding="utf-8"
            )
            (run_dir / "maestro_report.json").write_text(
                json.dumps(report), encoding="utf-8"
            )
            rows = build_dataset_from_runs(base)
        self.assertEqual(len(rows), 1)
        self.assertIn("collapse", rows[0])
        self.assertTrue(rows[0]["collapse"])  # tasks_completed 1 < 2
        self.assertIn("scenario_family", rows[0])
        self.assertIn("coordination_tax_proxy", rows[0])
        self.assertIn("error_amplification_proxy", rows[0])
        self.assertIn("coordination_tax_proxy", rows[0].get("response", {}))
        self.assertEqual(rows[0].get("agent_count"), 1)
        self.assertEqual(rows[0].get("coordination_regime"), "centralized")

    def test_regime_bundle_prefitted_predictors_match(self) -> None:
        if fit_linear_predictor is None:
            self.skipTest("scaling module not importable")
        from labtrust_portfolio.scaling import (
            DEFAULT_FEATURE_COLS_P5,
            regime_recommendation_bundle,
        )

        feats = list(DEFAULT_FEATURE_COLS_P5)
        train_rows = []
        for i in range(20):
            train_rows.append({
                "num_tasks": 3 + (i % 4),
                "num_faults": 1,
                "tool_density": 0.4,
                "agent_count": 2,
                "regime_id": 1.0,
                "hierarchy_depth": 2,
                "fan_out": 2,
                "queue_contention_index": 0.3,
                "shared_state_contention": 0.2,
                "response": {
                    "tasks_completed": float(i),
                    "collapse_probability": 0.05 + i * 0.01,
                },
                "scenario_id": "lab_profile_v0",
                "coordination_regime": "centralized",
            })
        template = dict(train_rows[5])
        pred_tc = fit_linear_predictor(train_rows, "tasks_completed", feats)
        pred_cp = fit_linear_predictor(
            train_rows, "collapse_probability", feats,
        )
        self.assertIsNotNone(pred_tc)
        self.assertIsNotNone(pred_cp)
        b1 = regime_recommendation_bundle(train_rows, template, agent_count=2)
        b2 = regime_recommendation_bundle(
            train_rows,
            template,
            agent_count=2,
            fitted_tasks_predictor=pred_tc,
            fitted_collapse_predictor=pred_cp,
        )
        self.assertEqual(b1["recommended_regime"], b2["recommended_regime"])
        self.assertEqual(len(b1["per_regime"]), len(b2["per_regime"]))
        for p, q in zip(b1["per_regime"], b2["per_regime"]):
            self.assertEqual(p["regime"], q["regime"])
            self.assertAlmostEqual(
                p["pred_tasks_completed"], q["pred_tasks_completed"], places=5,
            )
            self.assertAlmostEqual(
                p["pred_collapse_probability"],
                q["pred_collapse_probability"],
                places=5,
            )


class TestScalingBaselines(unittest.TestCase):
    """Oracle vs admissible predict_by_scenario semantics."""

    def test_predict_by_scenario_fallback(self) -> None:
        if predict_by_scenario is None or predict_baseline_mean is None:
            self.skipTest("scaling not importable")
        train = [
            {
                "scenario_id": "A",
                "response": {"tasks_completed": 10},
            },
        ]
        g = predict_baseline_mean(train, "tasks_completed")
        self.assertEqual(
            predict_by_scenario(train, "B", "tasks_completed", fallback=g),
            g,
        )


class TestScalingHoldoutFolds(unittest.TestCase):
    def test_regime_folds_need_two_regimes(self) -> None:
        if build_scaling_holdout_folds is None:
            self.skipTest("scaling not importable")
        from labtrust_portfolio.scaling import extract_features_from_scenario

        rows = [
            {
                "scenario_id": "s1",
                "scenario_family": "lab",
                "coordination_regime": "centralized",
                "agent_count": 1,
                "response": {"tasks_completed": 1},
            },
        ]
        _mode, folds = build_scaling_holdout_folds(
            list(rows), "regime", extract_features_from_scenario,
        )
        self.assertEqual(folds, [])
