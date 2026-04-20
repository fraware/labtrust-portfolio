from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path


class TestThinSliceE2E(unittest.TestCase):
    def test_thinslice_outputs_and_replay(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        os.environ["LABTRUST_KERNEL_DIR"] = str((repo / "kernel").resolve())

        from labtrust_portfolio.thinslice import run_thin_slice

        with tempfile.TemporaryDirectory() as td:
            out_dir = Path(td)
            outs = run_thin_slice(
                out_dir, seed=42, delay_p95_ms=30.0, drop_completion_prob=0.0
            )
            for k in [
                "trace", "maestro_report", "evidence_bundle", "release_manifest"
            ]:
                self.assertTrue(outs[k].exists(), f"missing {k}")

            import json
            ev = json.loads(
                (out_dir / "evidence_bundle.json").read_text(encoding="utf-8")
            )
            self.assertTrue(
                ev["verification"]["replay_ok"],
                "replay should succeed when drop_completion_prob=0.0",
            )
            self.assertTrue(
                ev["verification"]["schema_validation_ok"],
                "schemas should validate",
            )

    def test_release_dataset_from_run(self) -> None:
        """Release script copies run to releases/ and produces valid manifest."""
        repo = Path(__file__).resolve().parents[1]
        os.environ["LABTRUST_KERNEL_DIR"] = str((repo / "kernel").resolve())
        from labtrust_portfolio.thinslice import run_thin_slice
        from labtrust_portfolio.release import release_dataset

        with tempfile.TemporaryDirectory() as run_td:
            with tempfile.TemporaryDirectory() as rel_td:
                run_dir = Path(run_td)
                run_thin_slice(run_dir, seed=1, drop_completion_prob=0.0)
                release_id = "test_release_1"
                release_dir, manifest = release_dataset(
                    run_dir, release_id, Path(rel_td)
                )
                self.assertEqual(manifest["release_id"], release_id)
                for name in (
                    "trace.json",
                    "maestro_report.json",
                    "evidence_bundle.json",
                    "release_manifest.json",
                    "conformance.json",
                ):
                    self.assertTrue(
                        (release_dir / name).exists(),
                        f"release should contain {name}",
                    )

    def test_release_denied_when_tier2_fails(self) -> None:
        """Baseline: with MADS gate, release is denied when conformance fails Tier 2."""
        repo = Path(__file__).resolve().parents[1]
        os.environ["LABTRUST_KERNEL_DIR"] = str((repo / "kernel").resolve())
        from labtrust_portfolio.thinslice import run_thin_slice
        from labtrust_portfolio.release import release_dataset

        with tempfile.TemporaryDirectory() as run_td:
            with tempfile.TemporaryDirectory() as rel_td:
                run_dir = Path(run_td)
                run_thin_slice(run_dir, seed=1, drop_completion_prob=0.0)
                # Corrupt evidence bundle so Tier 2 fails (replay_ok false)
                eb_path = run_dir / "evidence_bundle.json"
                eb = json.loads(eb_path.read_text(encoding="utf-8"))
                eb["verification"]["replay_ok"] = False
                eb_path.write_text(json.dumps(eb, indent=2), encoding="utf-8")
                with self.assertRaises(ValueError) as ctx:
                    release_dataset(run_dir, "test_release_denied", Path(rel_td))
                self.assertIn("Tier 2", str(ctx.exception))
                self.assertIn("Release denied", str(ctx.exception))

    def test_gatekeeper_denies_when_contract_invalid(self) -> None:
        """Gatekeeper denies release when trace has contract violation (e.g. reorder)."""
        repo = Path(__file__).resolve().parents[1]
        os.environ["LABTRUST_KERNEL_DIR"] = str((repo / "kernel").resolve())
        sys_path = str(repo / "impl" / "src")
        if sys_path not in __import__("sys").path:
            __import__("sys").path.insert(0, sys_path)
        from labtrust_portfolio.gatekeeper import allow_release, check_contracts_on_trace
        from labtrust_portfolio.replay import apply_event
        from labtrust_portfolio.trace import state_hash
        from labtrust_portfolio.release import release_dataset
        from labtrust_portfolio.thinslice import run_thin_slice

        with tempfile.TemporaryDirectory() as run_td:
            with tempfile.TemporaryDirectory() as rel_td:
                run_dir = Path(run_td)
                state = {"tasks": {}, "coord_msgs": 0}
                ev1 = {
                    "type": "task_start",
                    "ts": 2.0,
                    "actor": {"kind": "agent", "id": "agent_1"},
                    "payload": {"task_id": "t1", "name": "a"},
                }
                state = apply_event(state, ev1)
                h1 = state_hash(state)
                ev2 = {
                    "type": "task_end",
                    "ts": 1.0,
                    "actor": {"kind": "tool", "id": "device_1"},
                    "payload": {"task_id": "t1", "name": "a"},
                }
                state = apply_event(state, ev2)
                h2 = state_hash(state)
                trace = {
                    "version": "0.1",
                    "run_id": "gatekeeper_test",
                    "scenario_id": "toy_lab_v0",
                    "seed": 1,
                    "start_time_utc": "2020-01-01T00:00:00Z",
                    "events": [
                        {**ev1, "seq": 0, "state_hash_after": h1},
                        {**ev2, "seq": 1, "state_hash_after": h2},
                    ],
                    "final_state_hash": h2,
                }
                (run_dir / "trace.json").write_text(
                    json.dumps(trace, indent=2), encoding="utf-8"
                )
                contract_ok, reason = check_contracts_on_trace(run_dir / "trace.json")
                self.assertFalse(contract_ok, "reorder trace must fail contract check")
                run_thin_slice(run_dir, seed=99, drop_completion_prob=0.0)
                (run_dir / "trace.json").write_text(
                    json.dumps(trace, indent=2), encoding="utf-8"
                )
                self.assertFalse(
                    allow_release(run_dir, check_contracts=True),
                    "allow_release must deny when contract invalid",
                )
                with self.assertRaises(ValueError):
                    release_dataset(run_dir, "test_contract_denied", Path(rel_td))


class TestE2Redaction(unittest.TestCase):
    """E2: Restricted auditability — redacted payloads, structure preserved."""

    def setUp(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        os.environ["LABTRUST_KERNEL_DIR"] = str((repo / "kernel").resolve())

    def test_redacted_trace_preserves_structure(self) -> None:
        from labtrust_portfolio.thinslice import run_thin_slice
        from labtrust_portfolio.evidence import redact_trace_payloads
        from labtrust_portfolio.schema import validate

        with tempfile.TemporaryDirectory() as td:
            out_dir = Path(td)
            run_thin_slice(out_dir, seed=1, drop_completion_prob=0.0)
            trace_path = out_dir / "trace.json"
            trace = json.loads(trace_path.read_text(encoding="utf-8"))
            redacted = redact_trace_payloads(trace)
            self.assertEqual(len(redacted["events"]), len(trace["events"]))
            for i, ev in enumerate(redacted["events"]):
                self.assertEqual(ev["type"], trace["events"][i]["type"])
                self.assertEqual(ev["seq"], trace["events"][i]["seq"])
                self.assertIn("payload", ev)
                self.assertIn("_redacted_ref", ev["payload"])
            validate(redacted, "trace/TRACE.v0.1.schema.json")

    def test_redacted_bundle_validates(self) -> None:
        from labtrust_portfolio.thinslice import run_thin_slice
        from labtrust_portfolio.evidence import (
            redact_trace_payloads,
            build_evidence_bundle,
        )
        from labtrust_portfolio.schema import validate

        with tempfile.TemporaryDirectory() as td:
            out_dir = Path(td)
            run_thin_slice(out_dir, seed=2, drop_completion_prob=0.0)
            trace = json.loads((out_dir / "trace.json").read_text(encoding="utf-8"))
            redacted_trace = redact_trace_payloads(trace)
            redacted_path = out_dir / "trace_redacted.json"
            redacted_path.write_text(
                json.dumps(redacted_trace, indent=2), encoding="utf-8"
            )
            artifacts = [
                redacted_path,
                out_dir / "maestro_report.json",
            ]
            schema_ids = [
                "https://example.org/labtrust/kernel/trace/TRACE.v0.1",
                "https://example.org/labtrust/kernel/eval/MAESTRO_REPORT.v0.2",
            ]
            bundle = build_evidence_bundle(
                run_id=trace["run_id"],
                kernel_version="0.1",
                artifacts=artifacts,
                schema_ids=schema_ids,
                schema_validation_ok=True,
                replay_ok=True,
                replay_diag="redacted run",
            )
            validate(bundle, "mads/EVIDENCE_BUNDLE.v0.1.schema.json")
            self.assertEqual(len(bundle["artifacts"]), 2)


if __name__ == "__main__":
    unittest.main()
