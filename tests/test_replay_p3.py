"""Tests for P3 Replay: CLI, divergence diagnostics, trace corpus, real eval launch."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


class TestReplayDiagnostics(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["LABTRUST_KERNEL_DIR"] = str(repo_root() / "kernel")

    def test_nondeterminism_trap_diverges(self) -> None:
        from labtrust_portfolio.replay import replay_trace_with_diagnostics

        corpus_dir = repo_root() / "bench" / "replay" / "corpus"
        trace_path = corpus_dir / "nondeterminism_trap_trace.json"
        self.assertTrue(trace_path.exists())
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        ok, diagnostics = replay_trace_with_diagnostics(trace)
        self.assertFalse(ok)
        self.assertGreater(len(diagnostics), 0)
        self.assertEqual(diagnostics[0].seq, 0)


class TestReplayCorpus(unittest.TestCase):
    """Corpus trace + expected file; assert replay outcome matches."""

    def setUp(self) -> None:
        os.environ["LABTRUST_KERNEL_DIR"] = str(repo_root() / "kernel")

    def test_corpus_nondeterminism_trap(self) -> None:
        from labtrust_portfolio.replay import replay_trace_with_diagnostics

        corpus_dir = repo_root() / "bench" / "replay" / "corpus"
        trace_path = corpus_dir / "nondeterminism_trap_trace.json"
        expected_path = corpus_dir / "nondeterminism_trap_expected.json"
        self.assertTrue(trace_path.exists())
        self.assertTrue(expected_path.exists())
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        expected = json.loads(expected_path.read_text(encoding="utf-8"))
        ok, diagnostics = replay_trace_with_diagnostics(trace)
        self.assertEqual(ok, expected["expected_replay_ok"])
        if not ok and diagnostics:
            self.assertEqual(
                diagnostics[0].seq,
                expected.get("expected_divergence_at_seq", 0),
            )

    def test_corpus_reorder_trap(self) -> None:
        from labtrust_portfolio.replay import replay_trace_with_diagnostics

        corpus_dir = repo_root() / "bench" / "replay" / "corpus"
        trace_path = corpus_dir / "reorder_trap_trace.json"
        expected_path = corpus_dir / "reorder_trap_expected.json"
        self.assertTrue(trace_path.exists())
        self.assertTrue(expected_path.exists())
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        expected = json.loads(expected_path.read_text(encoding="utf-8"))
        ok, diagnostics = replay_trace_with_diagnostics(trace)
        self.assertEqual(ok, expected["expected_replay_ok"])
        if not ok and diagnostics:
            self.assertEqual(
                diagnostics[0].seq,
                expected.get("expected_divergence_at_seq", 1),
            )

    def test_corpus_timestamp_reorder_trap(self) -> None:
        from labtrust_portfolio.replay import replay_trace_with_diagnostics

        corpus_dir = repo_root() / "bench" / "replay" / "corpus"
        trace_path = corpus_dir / "timestamp_reorder_trap_trace.json"
        expected_path = corpus_dir / "timestamp_reorder_trap_expected.json"
        self.assertTrue(trace_path.exists())
        self.assertTrue(expected_path.exists())
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        expected = json.loads(expected_path.read_text(encoding="utf-8"))
        ok, diagnostics = replay_trace_with_diagnostics(trace)
        self.assertEqual(ok, expected["expected_replay_ok"])
        if not ok and diagnostics:
            self.assertEqual(
                diagnostics[0].seq,
                expected.get("expected_divergence_at_seq", 1),
            )

    def test_corpus_hash_mismatch_trap(self) -> None:
        from labtrust_portfolio.replay import replay_trace_with_diagnostics

        corpus_dir = repo_root() / "bench" / "replay" / "corpus"
        trace_path = corpus_dir / "hash_mismatch_trap_trace.json"
        expected_path = corpus_dir / "hash_mismatch_trap_expected.json"
        self.assertTrue(trace_path.exists())
        self.assertTrue(expected_path.exists())
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        expected = json.loads(expected_path.read_text(encoding="utf-8"))
        ok, diagnostics = replay_trace_with_diagnostics(trace)
        self.assertEqual(ok, expected["expected_replay_ok"])
        if not ok and diagnostics:
            self.assertEqual(
                diagnostics[0].seq,
                expected.get("expected_divergence_at_seq", 1),
            )

    def test_corpus_field_style_pass(self) -> None:
        from labtrust_portfolio.replay import replay_trace_with_diagnostics

        corpus_dir = repo_root() / "bench" / "replay" / "corpus"
        trace_path = corpus_dir / "field_style_pass_trace.json"
        expected_path = corpus_dir / "field_style_pass_expected.json"
        self.assertTrue(trace_path.exists())
        self.assertTrue(expected_path.exists())
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        expected = json.loads(expected_path.read_text(encoding="utf-8"))
        ok, diagnostics = replay_trace_with_diagnostics(trace)
        self.assertEqual(ok, expected["expected_replay_ok"])
        self.assertTrue(ok)
        self.assertEqual(diagnostics, [])

    def test_corpus_long_horizon_trap(self) -> None:
        from labtrust_portfolio.replay import replay_trace_with_diagnostics

        corpus_dir = repo_root() / "bench" / "replay" / "corpus"
        trace_path = corpus_dir / "long_horizon_trap_trace.json"
        expected_path = corpus_dir / "long_horizon_trap_expected.json"
        self.assertTrue(trace_path.exists())
        self.assertTrue(expected_path.exists())
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        expected = json.loads(expected_path.read_text(encoding="utf-8"))
        ok, diagnostics = replay_trace_with_diagnostics(trace)
        self.assertEqual(ok, expected["expected_replay_ok"])
        if not ok and diagnostics:
            self.assertEqual(
                diagnostics[0].seq,
                expected.get("expected_divergence_at_seq"),
            )

    def test_corpus_mixed_failure_trap(self) -> None:
        from labtrust_portfolio.replay import replay_trace_with_diagnostics

        corpus_dir = repo_root() / "bench" / "replay" / "corpus"
        trace_path = corpus_dir / "mixed_failure_trap_trace.json"
        expected_path = corpus_dir / "mixed_failure_trap_expected.json"
        self.assertTrue(trace_path.exists())
        self.assertTrue(expected_path.exists())
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        expected = json.loads(expected_path.read_text(encoding="utf-8"))
        ok, diagnostics = replay_trace_with_diagnostics(trace)
        self.assertEqual(ok, expected["expected_replay_ok"])
        if not ok and diagnostics:
            self.assertEqual(
                diagnostics[0].seq,
                expected.get("expected_divergence_at_seq"),
            )

    def test_corpus_benign_perturbation_pass(self) -> None:
        from labtrust_portfolio.replay import replay_trace_with_diagnostics

        corpus_dir = repo_root() / "bench" / "replay" / "corpus"
        trace_path = corpus_dir / "benign_perturbation_pass_trace.json"
        expected_path = corpus_dir / "benign_perturbation_pass_expected.json"
        self.assertTrue(trace_path.exists())
        self.assertTrue(expected_path.exists())
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        expected = json.loads(expected_path.read_text(encoding="utf-8"))
        ok, diagnostics = replay_trace_with_diagnostics(trace)
        self.assertEqual(ok, expected["expected_replay_ok"])
        self.assertTrue(ok)
        self.assertEqual(diagnostics, [])

    def test_corpus_field_style_pass_variant_b(self) -> None:
        from labtrust_portfolio.replay import replay_trace_with_diagnostics

        corpus_dir = repo_root() / "bench" / "replay" / "corpus"
        trace_path = corpus_dir / "field_style_pass_variant_b_trace.json"
        expected_path = corpus_dir / "field_style_pass_variant_b_expected.json"
        self.assertTrue(trace_path.exists())
        self.assertTrue(expected_path.exists())
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        expected = json.loads(expected_path.read_text(encoding="utf-8"))
        ok, diagnostics = replay_trace_with_diagnostics(trace)
        self.assertEqual(ok, expected["expected_replay_ok"])
        self.assertTrue(ok)
        self.assertEqual(diagnostics, [])


class TestReplayBaselines(unittest.TestCase):
    """Baselines: apply-only (no hash) and final-hash-only."""

    def setUp(self) -> None:
        os.environ["LABTRUST_KERNEL_DIR"] = str(repo_root() / "kernel")

    def test_apply_only_runs(self) -> None:
        from labtrust_portfolio.replay import replay_trace_apply_only

        corpus_dir = repo_root() / "bench" / "replay" / "corpus"
        trace = json.loads(
            (corpus_dir / "nondeterminism_trap_trace.json").read_text(
                encoding="utf-8"
            )
        )
        replay_trace_apply_only(trace)

    def test_final_hash_only_no_localization(self) -> None:
        from labtrust_portfolio.replay import replay_trace_final_hash_only

        corpus_dir = repo_root() / "bench" / "replay" / "corpus"
        trace = json.loads(
            (corpus_dir / "reorder_trap_trace.json").read_text(encoding="utf-8")
        )
        ok, diagnostics = replay_trace_final_hash_only(trace)
        self.assertFalse(ok)
        if diagnostics:
            self.assertEqual(diagnostics[0].seq, -1)


class TestReplayL1Stub(unittest.TestCase):
    """L1 stub: valid twin config passes, missing/invalid config fails."""

    def setUp(self) -> None:
        os.environ["LABTRUST_KERNEL_DIR"] = str(repo_root() / "kernel")

    def test_l1_stub_succeeds_with_valid_config(self) -> None:
        from labtrust_portfolio.thinslice import run_thin_slice
        from labtrust_portfolio.replay import replay_l1_stub
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td)
            run_thin_slice(run_dir, seed=1, drop_completion_prob=0.0)
            trace_path = run_dir / "trace.json"
            trace = json.loads(trace_path.read_text(encoding="utf-8"))
            corpus_dir = repo_root() / "bench" / "replay" / "corpus"
            twin_config = corpus_dir / "twin_config.json"
            self.assertTrue(twin_config.exists())
            ok, msg = replay_l1_stub(trace, twin_config)
            self.assertTrue(ok, msg)
            self.assertIn("L1 stub ok", msg)

    def test_l1_stub_fails_when_config_missing(self) -> None:
        from labtrust_portfolio.thinslice import run_thin_slice
        from labtrust_portfolio.replay import replay_l1_stub
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td)
            run_thin_slice(run_dir, seed=1, drop_completion_prob=0.0)
            trace_path = run_dir / "trace.json"
            trace = json.loads(trace_path.read_text(encoding="utf-8"))
            missing_config = Path(td) / "nonexistent_twin_config.json"
            self.assertFalse(missing_config.exists())
            ok, msg = replay_l1_stub(trace, missing_config)
            self.assertFalse(ok)
            self.assertIn("not found", msg)

    def test_l1_stub_fails_when_config_invalid(self) -> None:
        from labtrust_portfolio.thinslice import run_thin_slice
        from labtrust_portfolio.replay import replay_l1_stub
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td)
            run_thin_slice(run_dir, seed=1, drop_completion_prob=0.0)
            trace_path = run_dir / "trace.json"
            trace = json.loads(trace_path.read_text(encoding="utf-8"))
            bad_config = Path(td) / "bad_twin_config.json"
            bad_config.write_text("{ invalid json", encoding="utf-8")
            ok, msg = replay_l1_stub(trace, bad_config)
            self.assertFalse(ok)
            self.assertIn("invalid", msg)

    def test_l1_stub_fails_when_config_missing_required_key(self) -> None:
        from labtrust_portfolio.thinslice import run_thin_slice
        from labtrust_portfolio.replay import replay_l1_stub
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td)
            run_thin_slice(run_dir, seed=1, drop_completion_prob=0.0)
            trace_path = run_dir / "trace.json"
            trace = json.loads(trace_path.read_text(encoding="utf-8"))
            no_build_hash = Path(td) / "partial_config.json"
            no_build_hash.write_text('{"env_seed": 1}', encoding="utf-8")
            ok, msg = replay_l1_stub(trace, no_build_hash)
            self.assertFalse(ok)
            self.assertIn("missing required key", msg)


class TestReplayEvalIntegration(unittest.TestCase):
    """Real launch: run replay_eval script and assert summary structure and invariants."""

    def setUp(self) -> None:
        os.environ["LABTRUST_KERNEL_DIR"] = str(repo_root() / "kernel")

    def test_replay_eval_produces_valid_summary(self) -> None:
        env = os.environ.copy()
        script = repo_root() / "scripts" / "replay_eval.py"
        with tempfile.TemporaryDirectory() as td:
            out_path = Path(td) / "summary.json"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--out",
                    str(out_path),
                    "--overhead-runs",
                    "2",
                    "--overhead-curve",
                    "--bootstrap-reps",
                    "50",
                ],
                cwd=str(repo_root()),
                env={**env, "PYTHONPATH": str(repo_root() / "impl" / "src")},
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(proc.returncode, 0, (proc.stdout, proc.stderr))
            self.assertTrue(out_path.exists(), "summary.json must be produced")
            summary = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertTrue(summary.get("replay_eval"))
            self.assertIn("run_manifest", summary)
            self.assertIn("success_criteria_met", summary)
            self.assertTrue(summary["success_criteria_met"].get("fidelity_pass"))
            self.assertTrue(
                summary.get("fidelity_pass"),
                "Thin-slice replay must pass",
            )
            self.assertTrue(
                summary.get("l1_stub_ok"),
                "L1 stub must pass with twin_config.json",
            )
            self.assertIn("replay_level", summary)
            self.assertIn(summary["replay_level"], ("L0", "L1"))
            self.assertIn("nondeterminism_budget", summary)
            self.assertIn("L0", summary["nondeterminism_budget"])
            self.assertIn("divergence_localization_confidence", summary)
            self.assertGreaterEqual(
                summary["divergence_localization_confidence"], 0.0
            )
            self.assertLessEqual(summary["divergence_localization_confidence"], 1.0)
            self.assertIn("overhead_stats", summary)
            self.assertIn("n_replays", summary["overhead_stats"])
            self.assertIn("mean_ms", summary["overhead_stats"])
            self.assertIn("p99_ms", summary["overhead_stats"])
            self.assertEqual(
                summary["overhead_stats"].get("percentile_method"),
                "linear_hf7",
            )
            self.assertEqual(summary.get("schema_version"), "p3_replay_eval_v0.2")
            self.assertIn("baseline_overhead", summary)
            bo = summary["baseline_overhead"]
            self.assertIsNotNone(bo)
            self.assertIn("apply_only_no_hash", bo)
            self.assertIn("final_hash_only", bo)
            curve = summary.get("overhead_curve") or []
            self.assertGreaterEqual(
                len(curve),
                2,
                "overhead_curve should have multiple prefix sizes",
            )
            self.assertIn("p95_replay_ci95_lower_ms", curve[0])
            self.assertTrue(
                summary["success_criteria_met"].get("corpus_expected_outcomes_met")
            )
            corpus = summary.get("corpus_divergence_detected", [])
            names = {r["name"] for r in corpus}
            self.assertIn("nondeterminism_trap", names)
            self.assertIn("reorder_trap", names)
            self.assertIn("timestamp_reorder_trap", names)
            self.assertIn("hash_mismatch_trap", names)
            self.assertIn("long_horizon_trap", names)
            self.assertIn("mixed_failure_trap", names)
            per_names = {r["name"] for r in summary.get("per_trace", [])}
            self.assertIn("field_style_pass", per_names)
            self.assertIn("benign_perturbation_pass", per_names)
            self.assertIn("field_style_pass_variant_b", per_names)
            self.assertIn("corpus_space_summary", summary)
            for r in corpus:
                if r["name"] == "nondeterminism_trap":
                    self.assertEqual(r["divergence_at_seq"], 0)
                elif r["name"] in ("reorder_trap", "timestamp_reorder_trap"):
                    self.assertEqual(r["divergence_at_seq"], 1)
                elif r["name"] == "hash_mismatch_trap":
                    self.assertEqual(r["divergence_at_seq"], 1)
                elif r["name"] == "long_horizon_trap":
                    self.assertEqual(r["divergence_at_seq"], 20)
                elif r["name"] == "mixed_failure_trap":
                    self.assertEqual(r["divergence_at_seq"], 2)


class TestReplayCLI(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["LABTRUST_KERNEL_DIR"] = str(repo_root() / "kernel")

    def test_replay_maestro_trace_passes(self) -> None:
        from labtrust_portfolio.thinslice import run_thin_slice
        from labtrust_portfolio.replay import replay_trace
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td)
            run_thin_slice(run_dir, seed=1, drop_completion_prob=0.0)
            trace_path = run_dir / "trace.json"
            trace = json.loads(trace_path.read_text(encoding="utf-8"))
            ok, _ = replay_trace(trace)
            self.assertTrue(ok)
