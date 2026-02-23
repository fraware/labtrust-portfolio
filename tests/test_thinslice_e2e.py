from __future__ import annotations

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
            outs = run_thin_slice(out_dir, seed=42, delay_p95_ms=30.0, drop_completion_prob=0.0)

            for k in ["trace","maestro_report","evidence_bundle","release_manifest"]:
                self.assertTrue(outs[k].exists(), f"missing {k}")

            import json
            ev = json.loads((out_dir / "evidence_bundle.json").read_text(encoding="utf-8"))
            self.assertTrue(ev["verification"]["replay_ok"], "replay should succeed when drop_completion_prob=0.0")
            self.assertTrue(ev["verification"]["schema_validation_ok"], "schemas should validate")

if __name__ == "__main__":
    unittest.main()
