"""Tests for P1 Contracts: validator, corpus driver, failure-class sequences, real eval launch."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from labtrust_portfolio.contracts import (
    validate,
    apply_event_to_state,
    prepare_replay_state,
    finalize_event_observation,
    build_contract_config_from_trace,
    load_evaluation_scope,
    ContractVerdict,
    ALLOW,
    REASON_REORDER,
    REASON_STALE_WRITE,
    REASON_SPLIT_BRAIN,
    REASON_UNKNOWN_KEY,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _corpus_dir() -> Path:
    return _repo_root() / "bench" / "contracts" / "corpus"


def _replay_trace_expect_match(data: dict, path_label: str = "") -> ContractVerdict:
    state = prepare_replay_state(dict(data["initial_state"]))
    cfg = build_contract_config_from_trace(data)
    events = data["events"]
    expected = data["expected_verdicts"]
    assert len(events) == len(expected), f"{path_label}: events/verdicts length mismatch"
    verdict = ContractVerdict(verdict=ALLOW, reason_codes=[])
    for i, ev in enumerate(events):
        verdict = validate(state, ev, cfg)
        assert verdict.verdict == expected[i], (
            f"{path_label} event {i}: expected {expected[i]}, got {verdict.verdict}"
        )
        if verdict.verdict == ALLOW:
            state = apply_event_to_state(state, ev)
        finalize_event_observation(state, ev)
    return verdict


def test_corpus_driver_each_file() -> None:
    """Load each corpus JSON; for each event validate and apply; assert verdicts match."""
    corpus_dir = _corpus_dir()
    if not corpus_dir.exists():
        return
    for path in sorted(corpus_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if "events" not in data or "expected_verdicts" not in data:
            continue
        _replay_trace_expect_match(data, path.name)


def test_corpus_good_sequence() -> None:
    path = _corpus_dir() / "good_sequence.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    _replay_trace_expect_match(data, "good_sequence")


def test_corpus_split_brain() -> None:
    path = _corpus_dir() / "split_brain_sequence.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    events = data["events"]
    verdict = _replay_trace_expect_match(data, "split_brain_sequence")
    assert REASON_SPLIT_BRAIN in verdict.reason_codes or not events


def test_corpus_stale_write() -> None:
    path = _corpus_dir() / "stale_write_sequence.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    events = data["events"]
    expected = data["expected_verdicts"]
    verdict = _replay_trace_expect_match(data, "stale_write_sequence")
    if events and expected[0] == "deny":
        assert REASON_STALE_WRITE in verdict.reason_codes


def test_corpus_reorder() -> None:
    path = _corpus_dir() / "reorder_sequence.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    events = data["events"]
    expected = data["expected_verdicts"]
    verdict = _replay_trace_expect_match(data, "reorder_sequence")
    if events and expected[-1] == "deny":
        assert REASON_REORDER in verdict.reason_codes
        assert REASON_STALE_WRITE in verdict.reason_codes


def test_non_gold_evaluation_scope_unknown_key_incident_trace() -> None:
    """allowed_keys from evaluation_scope.json only (no gold); unknown_* not in registry."""
    path = (
        _repo_root()
        / "datasets"
        / "contracts_real"
        / "incident_reconstructed"
        / "trace_04.json"
    )
    if not path.exists():
        return
    scope_path = _repo_root() / "datasets" / "contracts_real" / "evaluation_scope.json"
    scope = load_evaluation_scope(scope_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    cfg = build_contract_config_from_trace(
        data,
        family_id=data.get("scenario_family_id"),
        evaluation_scope=scope,
    )
    assert "unknown_4" not in cfg.get("allowed_keys", ())
    state = prepare_replay_state(dict(data["initial_state"]))
    events = data["events"]
    last_verdict = ContractVerdict(verdict=ALLOW, reason_codes=[])
    for i, ev in enumerate(events):
        last_verdict = validate(state, ev, cfg)
        exp = data["expected_verdicts"][i]
        assert last_verdict.verdict == exp, f"event {i}: expected {exp}, got {last_verdict.verdict}"
        if last_verdict.verdict == ALLOW:
            state = apply_event_to_state(state, ev)
        finalize_event_observation(state, ev)
    assert REASON_UNKNOWN_KEY in last_verdict.reason_codes


def test_corpus_unsafe_lww() -> None:
    path = _corpus_dir() / "unsafe_lww_sequence.json"
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    events = data["events"]
    expected = data["expected_verdicts"]
    verdict = _replay_trace_expect_match(data, "unsafe_lww_sequence")
    if events and expected[-1] == "deny":
        assert REASON_REORDER in verdict.reason_codes
        assert REASON_STALE_WRITE in verdict.reason_codes


class TestContractsEvalIntegration(unittest.TestCase):
    """Real launch: run contracts_eval script and assert eval.json structure and invariants."""

    def test_contracts_eval_produces_valid_eval(self) -> None:
        env = os.environ.copy()
        script = _repo_root() / "scripts" / "contracts_eval.py"
        with tempfile.TemporaryDirectory() as td:
            out_dir = Path(td) / "contracts_eval"
            out_dir.mkdir(parents=True)
            proc = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--out",
                    str(out_dir),
                ],
                cwd=str(_repo_root()),
                env={**env, "PYTHONPATH": str(_repo_root() / "impl" / "src")},
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertEqual(proc.returncode, 0, (proc.stdout, proc.stderr))
            eval_path = out_dir / "eval.json"
            self.assertTrue(eval_path.exists(), "eval.json must be produced")
            data = json.loads(eval_path.read_text(encoding="utf-8"))
            self.assertTrue(data.get("corpus_eval"))
            self.assertIn("run_manifest", data)
            self.assertIn("success_criteria_met", data)
            self.assertTrue(data["success_criteria_met"].get("all_detection_ok"))
            self.assertIn("sequences", data)
            self.assertGreater(len(data["sequences"]), 0)
            for seq in data["sequences"]:
                self.assertIn("detection_ok", seq)
                self.assertTrue(
                    seq["detection_ok"],
                    f"Sequence {seq.get('sequence')} must have detection_ok true",
                )
            self.assertIn("violations_denied_with_validator", data)
            self.assertIn("baseline_timestamp_only_denials", data)
            self.assertIn("baseline_timestamp_only_missed", data)
            # Verdict-vector correctness: detection_ok is per-event match, not just denial count
            for seq in data["sequences"]:
                self.assertIn("detection_ok", seq)
                if "actual_verdicts" in seq and "expected_verdicts" not in seq:
                    pass  # actual_verdicts present for debugging
            # Event-level latency and CI
            self.assertIn("latency_percentiles_us", data)
            lp = data["latency_percentiles_us"]
            self.assertIn("event_level_n", lp)
            self.assertIn("median_ci95", lp)
            self.assertIn("p95_ci95", lp)
            self.assertIn("p99_ci95", lp)
            # Detection metrics include F1
            self.assertIn("detection_metrics", data)
            self.assertIn("f1", data["detection_metrics"])
            self.assertIn("detection_metrics_by_class", data)
            self.assertIsInstance(data["detection_metrics_by_class"], dict)
            self.assertGreater(len(data["detection_metrics_by_class"]), 0)
            ab = data.get("ablation", {})
            for key in (
                "full_contract",
                "timestamp_only",
                "ownership_only",
                "occ_only",
                "lease_only",
                "lock_only",
                "accept_all",
                "naive_lww",
            ):
                self.assertIn(key, ab, f"ablation must include {key}")
            # Run manifest includes script_version and corpus_fingerprint
            rm = data["run_manifest"]
            self.assertIn("script_version", rm)
            self.assertIn("corpus_fingerprint", rm)


class TestContractsVerdictVectorCorrectness(unittest.TestCase):
    """Regression: detection_ok must be exact per-event verdict match, not denial count."""

    def test_detection_ok_false_when_one_verdict_wrong(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            corpus_dir = Path(td) / "corpus"
            corpus_dir.mkdir()
            # One sequence: two events, both allow
            path = corpus_dir / "one_sequence.json"
            path.write_text(
                json.dumps({
                    "description": "Two allows",
                    "initial_state": {"ownership": {}, "_last_ts": {}},
                    "events": [
                        {"type": "task_start", "ts": 1.0, "actor": {"id": "agent_1"}, "payload": {"task_id": "t1", "writer": "agent_1"}},
                        {"type": "task_end", "ts": 2.0, "actor": {"id": "agent_1"}, "payload": {"task_id": "t1", "writer": "agent_1"}},
                    ],
                    "expected_verdicts": ["allow", "deny"],  # second should be allow; wrong
                }),
                encoding="utf-8",
            )
            script = _repo_root() / "scripts" / "contracts_eval.py"
            out_dir = Path(td) / "out"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--out",
                    str(out_dir),
                    "--corpus",
                    str(corpus_dir),
                ],
                cwd=str(_repo_root()),
                env={**os.environ, "PYTHONPATH": str(_repo_root() / "impl" / "src")},
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(proc.returncode, 0)
            data = json.loads((out_dir / "eval.json").read_text(encoding="utf-8"))
            self.assertFalse(data["success_criteria_met"]["all_detection_ok"])
            self.assertEqual(len(data["sequences"]), 1)
            self.assertFalse(data["sequences"][0]["detection_ok"])


class TestContractsScaleTest(unittest.TestCase):
    """P1 scale-test: contracts_eval --scale-test with small scale-events for speed."""

    def test_contracts_scale_test_produces_scale_test_json(self) -> None:
        env = os.environ.copy()
        script = _repo_root() / "scripts" / "contracts_eval.py"
        with tempfile.TemporaryDirectory() as td:
            out_dir = Path(td) / "contracts_eval"
            out_dir.mkdir(parents=True)
            proc = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--out",
                    str(out_dir),
                    "--scale-test",
                    "--scale-events",
                    "1000",
                ],
                cwd=str(_repo_root()),
                env={**env, "PYTHONPATH": str(_repo_root() / "impl" / "src")},
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertEqual(proc.returncode, 0, (proc.stdout, proc.stderr))
            scale_path = out_dir / "scale_test.json"
            self.assertTrue(scale_path.exists(), "scale_test.json must be produced")
            data = json.loads(scale_path.read_text(encoding="utf-8"))
            self.assertIn("run_manifest", data)
            self.assertEqual(data["run_manifest"].get("script"), "contracts_eval.py")
            self.assertIn("time_per_write_us", data)
            self.assertIn("scale_test_events", data["run_manifest"])
            self.assertEqual(data["run_manifest"]["scale_test_events"], 1000)


class TestP1AppendixTexExport(unittest.TestCase):
    """export_p1_appendix_tex.py produces valid LaTeX from eval-shaped JSON."""

    def test_export_appendix_tex_writes_longtable(self) -> None:
        script = _repo_root() / "scripts" / "export_p1_appendix_tex.py"
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            eval_path = td_path / "eval.json"
            eval_path.write_text(
                json.dumps({
                    "sequences": [
                        {"sequence": "good_sequence", "detection_ok": True, "denials": 0},
                        {"sequence": "split_brain_sequence", "detection_ok": True, "denials": 1},
                    ],
                    "run_manifest": {
                        "script_version": "v0.test",
                        "corpus_fingerprint": "abc123",
                        "corpus_sequence_count": 2,
                    },
                }),
                encoding="utf-8",
            )
            out_path = td_path / "out.tex"
            proc = subprocess.run(
                [sys.executable, str(script), "--eval", str(eval_path), "--out", str(out_path)],
                cwd=str(_repo_root()),
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(proc.returncode, 0, (proc.stdout, proc.stderr))
            tex = out_path.read_text(encoding="utf-8")
            self.assertIn("\\begin{longtable}", tex)
            self.assertIn("good\\_sequence", tex)
            self.assertIn("v0.test", tex)
