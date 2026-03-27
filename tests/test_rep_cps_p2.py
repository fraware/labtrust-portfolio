"""P2 REP-CPS: unit tests for aggregate; integration tests for real eval and adapter runs."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "impl" / "src"))

from labtrust_portfolio.rep_cps import aggregate


class TestRepCpsAggregate(unittest.TestCase):
    """Unit tests for aggregate() rate_limit and max_age_sec."""

    def test_aggregate_rate_limit_drops_excess_per_agent(self) -> None:
        """With rate_limit=1, only the latest update per agent is kept."""
        updates = [
            {"variable": "load", "value": 0.3, "ts": 0.0, "agent_id": "a1"},
            {"variable": "load", "value": 0.5, "ts": 0.1, "agent_id": "a1"},
            {"variable": "load", "value": 0.4, "ts": 0.0, "agent_id": "a2"},
        ]
        no_limit = aggregate("load", updates, method="mean")
        with_limit = aggregate("load", updates, method="mean", rate_limit=1)
        self.assertAlmostEqual(no_limit, 0.4)
        self.assertAlmostEqual(with_limit, 0.45)

    def test_aggregate_max_age_drops_old_updates(self) -> None:
        """With max_age_sec, updates older than (current_ts - max_age_sec) are dropped."""
        updates = [
            {"variable": "load", "value": 1.0, "ts": 0.0, "agent_id": "a1"},
            {"variable": "load", "value": 2.0, "ts": 1.0, "agent_id": "a2"},
        ]
        no_age = aggregate("load", updates, method="mean")
        with_age = aggregate(
            "load", updates, method="mean",
            max_age_sec=0.5, current_ts=1.5
        )
        self.assertAlmostEqual(no_age, 1.5)
        self.assertAlmostEqual(with_age, 2.0)


class TestRepCpsEvalIntegration(unittest.TestCase):
    """Real launch: run rep_cps_eval script and assert summary structure and invariants."""

    def test_rep_cps_eval_produces_valid_summary(self) -> None:
        env = os.environ.copy()
        env["LABTRUST_KERNEL_DIR"] = str(REPO / "kernel")
        script = REPO / "scripts" / "rep_cps_eval.py"
        with tempfile.TemporaryDirectory() as td:
            out_dir = Path(td) / "rep_cps_eval"
            out_dir.mkdir(parents=True)
            proc = subprocess.run(
                [
                    sys.executable, str(script), "--out", str(out_dir),
                    "--seeds", "1,2", "--scenarios", "toy_lab_v0", "--delay-sweep", "0.05",
                ],
                cwd=str(REPO),
                env={**env, "PYTHONPATH": str(REPO / "impl" / "src")},
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(proc.returncode, 0, (proc.stdout, proc.stderr))
            summary_path = out_dir / "summary.json"
            self.assertTrue(summary_path.exists(), "summary.json must be produced")
            summary = json.loads(summary_path.read_text(encoding="utf-8"))

            self.assertIn("aggregation_under_compromise", summary)
            agg = summary["aggregation_under_compromise"]
            self.assertLess(
                agg["bias_robust"], agg["bias_naive"],
                "Robust aggregation must have lower bias than naive under compromise",
            )
            self.assertIn("rate_limit_windowing", summary)
            self.assertTrue(
                summary["rate_limit_windowing"]["rate_limit_windowing_exercised"]
            )
            self.assertEqual(summary.get("aggregation_steps"), 1)

            self.assertIn("profile_ablation", summary)
            ablation = summary["profile_ablation"]
            self.assertIsInstance(ablation, list)
            self.assertGreater(len(ablation), 0)
            variant_names = [r.get("variant") for r in ablation]
            self.assertIn("full_profile", variant_names)
            self.assertIn("no_robust_aggregation", variant_names)

            self.assertIn("resilience_envelope", summary)
            env_res = summary["resilience_envelope"]
            self.assertIn("safe_operating_region_n_compromised_max", env_res)
            self.assertIn("failure_boundary_n_compromised", env_res)
            self.assertIn("magnitude_sweep", summary)
            self.assertIn("trim_fraction_sweep", summary)

            self.assertIn("latency_cost", summary)
            lc = summary["latency_cost"]
            self.assertIn("wall_sec_rep_cps_mean", lc)
            self.assertIn("policy_overhead_vs_centralized_ms_rep_cps", lc)

            self.assertIn("freshness_replay_evidence", summary)
            self.assertIn("sybil_vs_spoofing_evidence", summary)
            self.assertIn("messaging_sim", summary)
            self.assertIn("dynamic_aggregation_series", summary)
            dyn = summary["dynamic_aggregation_series"]
            self.assertIn("trim_bias_drift_area", dyn)
            self.assertIn("trim_bias_persistence_ticks_gt_1", dyn)
            self.assertEqual(dyn.get("temporal_series_kind"), "offline_synthetic_harness")
            self.assertIn("scheduling_dependent_eval", summary)
            self.assertIn("offline_comparator_baselines", summary)
            ocb = summary["offline_comparator_baselines"]
            self.assertIn("honest_range_clamped_bias_vs_honest_trimmed", ocb)
            self.assertIn("comparator_classes", ocb)
            self.assertIn("aggregation_variants", summary)
            for v in summary["aggregation_variants"]:
                self.assertIn("beats_naive_mean", v)

            self.assertIn("run_manifest", summary)
            rm = summary["run_manifest"]
            self.assertIn("seeds", rm)
            self.assertEqual(len(rm["seeds"]), 2, "run_manifest.seeds length must match --seeds 1,2")
            if "seed_count" in rm:
                self.assertEqual(rm["seed_count"], 2)
            self.assertIn("rep_cps_tasks_completed_mean", summary)
            if "rep_cps_tasks_completed_stdev" in summary:
                self.assertGreaterEqual(summary["rep_cps_tasks_completed_stdev"], 0)
            if "rep_cps_tasks_completed_ci95" in summary:
                ci = summary["rep_cps_tasks_completed_ci95"]
                self.assertEqual(len(ci), 2)
                self.assertLessEqual(ci[0], summary["rep_cps_tasks_completed_mean"])
                self.assertGreaterEqual(ci[1], summary["rep_cps_tasks_completed_mean"])
            self.assertIn("success_criteria_met", summary)
            sc = summary["success_criteria_met"]
            self.assertTrue(sc.get("adapter_parity"), "adapter_parity must hold (REP-CPS == centralized)")
            self.assertTrue(sc.get("robust_beats_naive"), "robust_beats_naive must hold under compromise")
            self.assertIn("adapter_runs", summary)
            self.assertEqual(len(summary["adapter_runs"]), 2)
            self.assertIn("rep_cps_tasks_completed_mean", summary)
            self.assertIn("rep_cps_naive_tasks_completed_mean", summary)
            self.assertIn("rep_cps_unsecured_tasks_completed_mean", summary)
            self.assertIn("rep_cps_unsecured_aggregate_load_mean", summary)
            self.assertIsNotNone(summary["rep_cps_unsecured_aggregate_load_mean"])
            self.assertGreater(
                summary["rep_cps_unsecured_aggregate_load_mean"], 1.0,
                "Unsecured (with compromised updates) should yield high aggregate",
            )
            # Per-scenario summary (when multiple scenarios)
            if "per_scenario" in summary:
                per_scenario = summary["per_scenario"]
                self.assertIsInstance(per_scenario, list)
                for ps in per_scenario:
                    self.assertIn("scenario_id", ps)
                    if "rep_cps_tasks_mean" in ps:
                        self.assertIsInstance(ps["rep_cps_tasks_mean"], (int, float))
            # Excellence metrics (comparison statistics when adapter runs exist)
            if "excellence_metrics" in summary:
                excellence = summary["excellence_metrics"]
                if "difference_mean" in excellence:
                    self.assertIsInstance(excellence["difference_mean"], (int, float))
                if "difference_ci95" in excellence:
                    ci = excellence["difference_ci95"]
                    self.assertIsInstance(ci, list)
                    self.assertEqual(len(ci), 2)
                if "paired_t_p_value" in excellence and excellence["paired_t_p_value"] is not None:
                    self.assertIsInstance(excellence["paired_t_p_value"], (int, float))
                    self.assertGreaterEqual(excellence["paired_t_p_value"], 0.0)
                    self.assertLessEqual(excellence["paired_t_p_value"], 1.0)


class TestRepCpsSchedulingScenario(unittest.TestCase):
    """Scheduling-dependent scenario: REP preserves tasks vs naive under spoof stress."""

    def test_scheduling_scenario_rep_beats_naive_tasks(self) -> None:
        env = os.environ.copy()
        env["LABTRUST_KERNEL_DIR"] = str(REPO / "kernel")
        script = REPO / "scripts" / "rep_cps_eval.py"
        with tempfile.TemporaryDirectory() as td:
            out_dir = Path(td) / "rep_cps_eval"
            out_dir.mkdir(parents=True)
            proc = subprocess.run(
                [
                    sys.executable, str(script), "--out", str(out_dir),
                    "--seeds", "7,8", "--scenarios", "rep_cps_scheduling_v0",
                    "--delay-sweep", "0.05",
                ],
                cwd=str(REPO),
                env={**env, "PYTHONPATH": str(REPO / "impl" / "src")},
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(proc.returncode, 0, (proc.stdout, proc.stderr))
            summary = json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))
            sched = summary.get("scheduling_dependent_eval")
            self.assertIsNotNone(sched)
            self.assertTrue(sched.get("rep_beats_naive_tasks"))
            self.assertGreater(sched.get("rep_cps_tasks_mean", 0), sched.get("naive_in_loop_tasks_mean", 0))
            sc = summary["success_criteria_met"]
            self.assertTrue(sc.get("scheduling_scenario_task_divergence"))
            # Verify per_scenario includes scheduling scenario
            if "per_scenario" in summary:
                sched_scenarios = [ps for ps in summary["per_scenario"] if ps.get("scenario_id") == "rep_cps_scheduling_v0"]
                self.assertGreater(len(sched_scenarios), 0, "per_scenario should include rep_cps_scheduling_v0")


class TestRepCpsAdapterRealRun(unittest.TestCase):
    """Real run: REPCPSAdapter and CentralizedAdapter on real scenario; assert outputs."""

    def test_rep_cps_adapter_real_run_vs_centralized(self) -> None:
        os.environ["LABTRUST_KERNEL_DIR"] = str(REPO / "kernel")
        from labtrust_portfolio.adapters.rep_cps_adapter import REPCPSAdapter
        from labtrust_portfolio.adapters.centralized import CentralizedAdapter
        from labtrust_portfolio.adapters.base import run_adapter

        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            rep_dir = out / "rep_cps"
            cen_dir = out / "centralized"
            rep_dir.mkdir(parents=True)
            cen_dir.mkdir(parents=True)

            rep_result = run_adapter(
                REPCPSAdapter(), "toy_lab_v0", rep_dir, seed=7,
                delay_fault_prob=0.0, drop_completion_prob=0.0,
            )
            cen_result = run_adapter(
                CentralizedAdapter(), "toy_lab_v0", cen_dir, seed=7,
                delay_fault_prob=0.0, drop_completion_prob=0.0,
            )

            self.assertTrue(rep_result.trace.get("metadata", {}).get("rep_cps"))
            self.assertIn("rep_cps_aggregate_load", rep_result.trace.get("metadata", {}))
            self.assertTrue(rep_result.trace["metadata"].get("rep_cps_safety_gate_ok"))
            self.assertIn("tasks_completed", rep_result.maestro_report.get("metrics", {}))
            self.assertIn("tasks_completed", cen_result.maestro_report.get("metrics", {}))

            rep_tasks = rep_result.maestro_report["metrics"]["tasks_completed"]
            cen_tasks = cen_result.maestro_report["metrics"]["tasks_completed"]
            self.assertEqual(
                rep_tasks, cen_tasks,
                "Same seed and scenario: REP-CPS and Centralized must complete same tasks",
            )


class TestRepCpsMultiScenario(unittest.TestCase):
    """Multi-scenario eval: verify per_scenario summary and drop_completion_prob sweep support."""

    def test_multi_scenario_produces_per_scenario_summary(self) -> None:
        """When multiple scenarios are run, per_scenario summary should be present."""
        env = os.environ.copy()
        env["LABTRUST_KERNEL_DIR"] = str(REPO / "kernel")
        script = REPO / "scripts" / "rep_cps_eval.py"
        with tempfile.TemporaryDirectory() as td:
            out_dir = Path(td) / "rep_cps_eval"
            out_dir.mkdir(parents=True)
            proc = subprocess.run(
                [
                    sys.executable, str(script), "--out", str(out_dir),
                    "--seeds", "1,2", "--scenarios", "toy_lab_v0,lab_profile_v0",
                    "--delay-sweep", "0.05",
                ],
                cwd=str(REPO),
                env={**env, "PYTHONPATH": str(REPO / "impl" / "src")},
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(proc.returncode, 0, (proc.stdout, proc.stderr))
            summary = json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))
            # When multiple scenarios, per_scenario should be present
            if len(summary.get("scenario_ids", [])) > 1:
                self.assertIn("per_scenario", summary)
                per_scenario = summary["per_scenario"]
                self.assertIsInstance(per_scenario, list)
                self.assertGreaterEqual(len(per_scenario), 2)
                scenario_ids = [ps.get("scenario_id") for ps in per_scenario]
                self.assertIn("toy_lab_v0", scenario_ids)
                self.assertIn("lab_profile_v0", scenario_ids)
                for ps in per_scenario:
                    self.assertIn("naive_in_loop_tasks_mean", ps)
                    self.assertIn("unsecured_tasks_mean", ps)

    def test_drop_sweep_support(self) -> None:
        """Verify drop_completion_prob_sweep is recorded in run_manifest when used."""
        env = os.environ.copy()
        env["LABTRUST_KERNEL_DIR"] = str(REPO / "kernel")
        script = REPO / "scripts" / "rep_cps_eval.py"
        with tempfile.TemporaryDirectory() as td:
            out_dir = Path(td) / "rep_cps_eval"
            out_dir.mkdir(parents=True)
            proc = subprocess.run(
                [
                    sys.executable, str(script), "--out", str(out_dir),
                    "--seeds", "1", "--scenarios", "toy_lab_v0",
                    "--delay-sweep", "0.05", "--drop-sweep", "0.01,0.02",
                ],
                cwd=str(REPO),
                env={**env, "PYTHONPATH": str(REPO / "impl" / "src")},
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(proc.returncode, 0, (proc.stdout, proc.stderr))
            summary = json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))
            rm = summary.get("run_manifest", {})
            if "drop_completion_prob_sweep" in rm:
                drop_sweep = rm["drop_completion_prob_sweep"]
                self.assertIsInstance(drop_sweep, list)
                self.assertIn(0.01, drop_sweep)
                self.assertIn(0.02, drop_sweep)

    def test_gate_threshold_sweep_support(self) -> None:
        """Verify gate_threshold_sweep_results is emitted for scheduling scenario."""
        env = os.environ.copy()
        env["LABTRUST_KERNEL_DIR"] = str(REPO / "kernel")
        script = REPO / "scripts" / "rep_cps_eval.py"
        with tempfile.TemporaryDirectory() as td:
            out_dir = Path(td) / "rep_cps_eval"
            out_dir.mkdir(parents=True)
            proc = subprocess.run(
                [
                    sys.executable, str(script), "--out", str(out_dir),
                    "--seeds", "1,2", "--scenarios", "rep_cps_scheduling_v0",
                    "--delay-sweep", "0.05", "--drop-sweep", "0.02",
                    "--gate-threshold-sweep", "1.5,2.0,2.5",
                ],
                cwd=str(REPO),
                env={**env, "PYTHONPATH": str(REPO / "impl" / "src")},
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(proc.returncode, 0, (proc.stdout, proc.stderr))
            summary = json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))
            self.assertIn("gate_threshold_sweep_results", summary)
            rows = summary["gate_threshold_sweep_results"]
            self.assertIsInstance(rows, list)
            self.assertGreaterEqual(len(rows), 3)
            first = rows[0]
            self.assertIn("safety_gate_max_load", first)
            self.assertIn("rep_cps_gate_deny_rate", first)
            self.assertIn("rep_beats_naive_tasks", first)
