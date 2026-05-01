"""Minimal CI gate: canonical P5 artifacts and headline trigger semantics."""
from __future__ import annotations

import json
import unittest
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


class TestP5SubmissionReadiness(unittest.TestCase):
    def test_canonical_paths_exist(self) -> None:
        root = repo_root()
        paths = [
            root / "datasets" / "runs" / "scaling_eval" / "heldout_results.json",
            root / "datasets" / "runs" / "scaling_eval_family" / "heldout_results.json",
            root / "datasets" / "runs" / "scaling_eval_regime" / "heldout_results.json",
            root / "datasets" / "runs" / "scaling_eval_agent_count" / "heldout_results.json",
            root / "datasets" / "runs" / "scaling_eval_fault" / "heldout_results.json",
            root / "datasets" / "runs" / "sensitivity_sweep" / "scaling_sensitivity.json",
            root / "datasets" / "runs" / "scaling_recommend" / "recommendation_eval.json",
            root / "datasets" / "runs" / "scaling_summary" / "regime_agent_summary.json",
            root / "papers" / "P5_ScalingLaws" / "generated_tables.md",
        ]
        missing = [str(p) for p in paths if not p.exists()]
        self.assertFalse(missing, "Missing canonical artifacts:\n" + "\n".join(missing))

    def test_multiscenario_runs_dir_when_present(self) -> None:
        """Bulk runs directory is gitignored; require it only when reproducing locally."""
        p = repo_root() / "datasets" / "runs" / "multiscenario_runs"
        if not p.exists():
            self.skipTest("multiscenario_runs/ absent (expected in CI without bulk checkout)")
        self.assertTrue(p.is_dir())

    def test_grid_manifest_dimensions(self) -> None:
        main_p = repo_root() / "datasets" / "runs" / "scaling_eval" / "heldout_results.json"
        data = json.loads(main_p.read_text(encoding="utf-8"))
        self.assertEqual(data.get("total_rows"), 7200)
        rm = data.get("run_manifest") or {}
        self.assertEqual(len(rm.get("scenario_ids") or []), 6)
        self.assertEqual(len(rm.get("coordination_regimes") or []), 5)
        self.assertEqual(len(rm.get("agent_counts") or []), 4)
        self.assertEqual(len(rm.get("fault_setting_labels") or []), 2)
        seeds = rm.get("seeds") or []
        self.assertEqual(len(seeds), 30)

    def test_coordination_tax_secondary_trigger_stricter_than_primary(self) -> None:
        """Secondary coordination-tax block can trigger while primary throughput does not."""
        scen = json.loads(
            (
                repo_root() / "datasets" / "runs" / "scaling_eval" / "heldout_results.json"
            ).read_text(encoding="utf-8"),
        )
        primary = (scen.get("success_criteria_met") or {}).get("trigger_met")
        tax_trig = (
            (scen.get("secondary_targets") or {})
            .get("coordination_tax_proxy", {})
            .get("success_criteria_met", {})
            .get("trigger_met")
        )
        self.assertFalse(primary)
        self.assertTrue(tax_trig)

    def test_oracle_baseline_not_trigger_gate(self) -> None:
        """trigger_met is defined only from admissible beats; oracle is separate."""
        scen = json.loads(
            (
                repo_root() / "datasets" / "runs" / "scaling_eval" / "heldout_results.json"
            ).read_text(encoding="utf-8"),
        )
        sc = scen.get("success_criteria_met") or {}
        self.assertIn("beat_oracle_per_scenario_baseline", sc)
        self.assertIn("beat_feature_baseline_out_of_sample", sc)
        self.assertEqual(
            sc.get("trigger_met"),
            bool(
                sc.get("beat_global_mean_out_of_sample")
                and sc.get("beat_feature_baseline_out_of_sample")
                and sc.get("beat_regime_baseline_out_of_sample"),
            ),
        )

    def test_scenario_family_headline_triggers(self) -> None:
        scen = json.loads(
            (
                repo_root() / "datasets" / "runs" / "scaling_eval" / "heldout_results.json"
            ).read_text(encoding="utf-8"),
        )
        fam = json.loads(
            (
                repo_root()
                / "datasets"
                / "runs"
                / "scaling_eval_family"
                / "heldout_results.json"
            ).read_text(encoding="utf-8"),
        )
        self.assertFalse((scen.get("success_criteria_met") or {}).get("trigger_met"))
        self.assertTrue((fam.get("success_criteria_met") or {}).get("trigger_met"))

    def test_recommendation_claim_status(self) -> None:
        rec_p = repo_root() / "datasets" / "runs" / "scaling_recommend" / "recommendation_eval.json"
        rec = json.loads(rec_p.read_text(encoding="utf-8"))
        self.assertEqual(rec.get("claim_status"), "exploratory")
        self.assertIs(rec.get("deployment_claim_allowed"), False)

    def test_regime_agent_summary_complete_matrix(self) -> None:
        p = repo_root() / "datasets" / "runs" / "scaling_summary" / "regime_agent_summary.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        by_pair: dict[tuple[str, str], set[int]] = {}
        for e in data.get("group_summary") or []:
            fam = str(e.get("scenario_family", ""))
            reg = str(e.get("coordination_regime", ""))
            ac = int(e.get("agent_count", 0) or 0)
            by_pair.setdefault((fam, reg), set()).add(ac)
        expected_rows = sum(
            1
            for acs in by_pair.values()
            if 1 in acs and 8 in acs
        )
        deltas = data.get("high_vs_low_agent_count_deltas") or []
        self.assertEqual(
            len(deltas),
            expected_rows,
            "Every family×regime with agent 1 and 8 must have a high-vs-low delta row",
        )

    def test_generated_tables_not_stale(self) -> None:
        root = repo_root()
        gt = root / "papers" / "P5_ScalingLaws" / "generated_tables.md"
        src = root / "datasets" / "runs" / "scaling_eval" / "heldout_results.json"
        self.assertGreaterEqual(
            gt.stat().st_mtime + 0.5,
            src.stat().st_mtime,
            "Regenerate generated_tables.md after updating scaling_eval JSON",
        )

    def test_p5_artifact_hash_manifest(self) -> None:
        """Freeze discipline: repo-relative SHA256 manifest (run hash_p5_artifacts.py after artifact changes)."""
        p = repo_root() / "papers" / "P5_ScalingLaws" / "p5_artifact_hashes.txt"
        self.assertTrue(p.exists(), "Missing p5_artifact_hashes.txt — run scripts/hash_p5_artifacts.py")
        text = p.read_text(encoding="utf-8").strip()
        self.assertTrue(text, "p5_artifact_hashes.txt is empty")
        norm = text.replace("\\", "/")
        self.assertIn(
            "datasets/runs/scaling_eval/heldout_results.json",
            norm,
            "Manifest must include scenario-heldout JSON",
        )
        self.assertNotRegex(
            norm,
            r"\b[A-Z]:/",
            "Manifest paths must be repo-relative (fix scripts/hash_p5_artifacts.py)",
        )


if __name__ == "__main__":
    unittest.main()
