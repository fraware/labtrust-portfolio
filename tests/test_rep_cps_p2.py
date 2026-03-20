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
