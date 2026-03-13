"""P8 Meta-Coordination: integration test and unit tests for meta_eval and meta_controller."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Import after path setup for meta_controller unit tests
def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def repo_root() -> Path:
    return _repo_root()


class TestMetaController(unittest.TestCase):
    """Unit tests for decide_switch and regime_switch_event (formal switch criterion)."""

    def setUp(self) -> None:
        sys.path.insert(0, str(_repo_root() / "impl" / "src"))
        from labtrust_portfolio import meta_controller as mc
        self.mc = mc

    def test_decide_switch_to_fallback_when_fault_count_exceeds_threshold(self) -> None:
        out = self.mc.decide_switch(
            "centralized", fault_count=3, latency_p95_ms=50.0,
            fault_threshold=2, latency_threshold_ms=200.0,
        )
        self.assertEqual(out, "fallback")

    def test_decide_switch_to_fallback_when_latency_exceeds_threshold(self) -> None:
        out = self.mc.decide_switch(
            "centralized", fault_count=0, latency_p95_ms=250.0,
            fault_threshold=2, latency_threshold_ms=200.0,
        )
        self.assertEqual(out, "fallback")

    def test_decide_switch_no_switch_when_below_thresholds(self) -> None:
        out = self.mc.decide_switch(
            "centralized", fault_count=1, latency_p95_ms=100.0,
            fault_threshold=2, latency_threshold_ms=200.0,
        )
        self.assertIsNone(out)

    def test_decide_switch_revert_to_centralized_when_in_fallback_and_low(self) -> None:
        out = self.mc.decide_switch(
            "fallback", fault_count=0, latency_p95_ms=80.0,
            fault_threshold=2, latency_threshold_ms=200.0,
        )
        self.assertEqual(out, "centralized")

    def test_decide_switch_naive_zero_threshold_switches_on_any_fault(self) -> None:
        out = self.mc.decide_switch(
            "centralized", fault_count=1, latency_p95_ms=50.0,
            fault_threshold=0, latency_threshold_ms=200.0,
        )
        self.assertEqual(out, "fallback")

    def test_regime_switch_event_has_required_fields(self) -> None:
        ev = self.mc.regime_switch_event(
            seq=1, ts=1.0, from_regime="centralized",
            to_regime="fallback", reason="fault_threshold", state_hash_after="abc",
        )
        self.assertEqual(ev["type"], "regime_switch")
        self.assertIn("payload", ev)
        self.assertEqual(ev["payload"]["from_regime"], "centralized")
        self.assertEqual(ev["payload"]["to_regime"], "fallback")
        self.assertEqual(ev["payload"]["reason"], "fault_threshold")
        self.assertEqual(ev["actor"]["id"], "meta_controller")


class TestMetaEvalIntegration(unittest.TestCase):
    """Run meta_eval with --out temp and --run-naive; assert comparison.json."""


    def setUp(self) -> None:
        os.environ["LABTRUST_KERNEL_DIR"] = str(repo_root() / "kernel")

    def test_meta_eval_produces_valid_comparison(self) -> None:
        env = os.environ.copy()
        pypath = str(repo_root() / "impl" / "src")
        script = repo_root() / "scripts" / "meta_eval.py"
        with tempfile.TemporaryDirectory() as td:
            out_dir = Path(td) / "meta_eval"
            out_dir.mkdir(parents=True)
            proc = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--out",
                    str(out_dir),
                    "--run-naive",
                    "--fault-threshold",
                    "0",
                    "--seeds",
                    "1,2,3",
                ],
                cwd=str(repo_root()),
                env={**env, "PYTHONPATH": pypath},
                capture_output=True,
                text=True,
                timeout=180,
            )
            self.assertEqual(
                proc.returncode, 0,
                (proc.stdout, proc.stderr)
            )
            comparison_path = out_dir / "comparison.json"
            self.assertTrue(
                comparison_path.exists(),
                "comparison.json must be produced under --out",
            )
            data = json.loads(comparison_path.read_text(encoding="utf-8"))
            self.assertIn("fixed", data)
            self.assertIn("meta_controller", data)
            self.assertIn("naive_switch_baseline", data)
            self.assertIn("meta_reduces_collapse", data)
            self.assertIn("no_safety_regression", data)
            self.assertIn("run_manifest", data)
            rm = data["run_manifest"]
            self.assertIn("seeds", rm)
            self.assertEqual(len(rm["seeds"]), 3, "run_manifest.seeds length must match --seeds 1,2,3")
            if "seed_count" in rm:
                self.assertEqual(rm["seed_count"], 3)
            fix = data["fixed"]
            meta = data["meta_controller"]
            if "tasks_completed_ci95" in fix and len(fix["tasks_completed_ci95"]) == 2:
                lo, hi = fix["tasks_completed_ci95"]
                self.assertLessEqual(lo, fix["tasks_completed_mean"])
                self.assertGreaterEqual(hi, fix["tasks_completed_mean"])
            if "tasks_completed_ci95" in meta and len(meta["tasks_completed_ci95"]) == 2:
                lo, hi = meta["tasks_completed_ci95"]
                self.assertLessEqual(lo, meta["tasks_completed_mean"])
                self.assertGreaterEqual(hi, meta["tasks_completed_mean"])
            self.assertIn("success_criteria_met", data)
            sc = data["success_criteria_met"]
            self.assertTrue(sc.get("no_safety_regression"), "no_safety_regression must hold")
            self.assertTrue(sc.get("meta_reduces_collapse"), "meta_reduces_collapse must hold")
            self.assertIn("collapse_definition", data)
            self.assertIn("per_seed", data["fixed"])
            self.assertIn("per_seed", data["meta_controller"])
            self.assertGreater(
                len(data["fixed"]["per_seed"]), 0,
                "fixed.per_seed must be non-empty",
            )
            naive = data["naive_switch_baseline"]
            total_switches = naive.get("regime_switch_count_total", 0)
            self.assertGreaterEqual(
                total_switches, 1,
                "With fault_threshold=0, regime_switch_count_total >= 1",
            )
            self.assertTrue(
                data.get("no_safety_regression"),
                "meta must not regress vs fixed (>= 90% of fixed tasks_completed)",
            )
            self.assertTrue(
                data.get("meta_reduces_collapse"),
                "meta collapse_count must be <= fixed collapse_count",
            )
            export_script = repo_root() / "scripts" / "export_meta_tables.py"
            export_proc = subprocess.run(
                [
                    sys.executable,
                    str(export_script),
                    "--comparison",
                    str(comparison_path),
                ],
                cwd=str(repo_root()),
                env={**env, "PYTHONPATH": pypath},
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(
                export_proc.returncode, 0,
                "export_meta_tables.py must succeed on comparison.json",
            )

    def test_meta_eval_stress_collapse_threshold_exercises_collapse_metric(self) -> None:
        """Run with higher collapse threshold so collapse_count can be non-zero."""
        env = os.environ.copy()
        pypath = str(repo_root() / "impl" / "src")
        script = repo_root() / "scripts" / "meta_eval.py"
        with tempfile.TemporaryDirectory() as td:
            out_dir = Path(td) / "meta_eval_stress"
            out_dir.mkdir(parents=True)
            proc = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--out",
                    str(out_dir),
                    "--collapse-threshold",
                    "4",
                    "--seeds",
                    "1,2",
                ],
                cwd=str(repo_root()),
                env={**env, "PYTHONPATH": pypath},
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(proc.returncode, 0, (proc.stdout, proc.stderr))
            data = json.loads((out_dir / "comparison.json").read_text(encoding="utf-8"))
            self.assertIn("fixed", data)
            self.assertIn("meta_controller", data)
            self.assertIn("collapse_definition", data)
            self.assertTrue(
                "tasks_completed < 4" in data.get("collapse_definition", ""),
                "collapse_definition must reflect threshold 4",
            )
            self.assertIn("meta_reduces_collapse", data)
            self.assertIn("no_safety_regression", data)

    def test_meta_eval_stress_preset_asserts_meta_reduces_collapse(self) -> None:
        """Run with --stress-preset high; assert meta_reduces_collapse when collapse can occur."""
        env = os.environ.copy()
        pypath = str(repo_root() / "impl" / "src")
        script = repo_root() / "scripts" / "meta_eval.py"
        with tempfile.TemporaryDirectory() as td:
            out_dir = Path(td) / "meta_eval_stress_high"
            out_dir.mkdir(parents=True)
            proc = subprocess.run(
                [
                    sys.executable, str(script),
                    "--out", str(out_dir),
                    "--stress-preset", "high",
                    "--seeds", "1,2,3",
                    "--collapse-threshold", "4",
                ],
                cwd=str(repo_root()),
                env={**env, "PYTHONPATH": pypath, "LABTRUST_KERNEL_DIR": str(repo_root() / "kernel")},
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(proc.returncode, 0, (proc.stdout, proc.stderr))
            data = json.loads((out_dir / "comparison.json").read_text(encoding="utf-8"))
            self.assertIn("meta_reduces_collapse", data)
            self.assertTrue(
                data["meta_reduces_collapse"],
                "Meta collapse count must be <= fixed collapse count",
            )
