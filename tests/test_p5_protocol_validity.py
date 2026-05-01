"""P5: strict protocol semantics over frozen heldout_results.json bundles."""
from __future__ import annotations

import json
import unittest
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _heldout_paths() -> list[Path]:
    r = repo_root() / "datasets" / "runs"
    return [
        r / "scaling_eval" / "heldout_results.json",
        r / "scaling_eval_family" / "heldout_results.json",
        r / "scaling_eval_regime" / "heldout_results.json",
        r / "scaling_eval_agent_count" / "heldout_results.json",
        r / "scaling_eval_fault" / "heldout_results.json",
    ]


class TestP5ProtocolValidity(unittest.TestCase):
    def test_each_protocol_strict_nulling_and_trigger_consistency(self) -> None:
        """If any fold lacks regression_mae, overall is null and trigger is false."""
        for path in _heldout_paths():
            if not path.exists():
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
            folds = data.get("held_out_results") or []
            missing = [f for f in folds if f.get("regression_mae") is None]
            overall_reg = data.get("overall_regression_mae")
            sc = data.get("success_criteria_met") or {}
            trig = sc.get("trigger_met")

            if missing:
                self.assertIsNone(
                    overall_reg,
                    f"{path}: overall_regression_mae must be null when folds missing regression",
                )
                self.assertFalse(
                    trig,
                    f"{path}: trigger_met must be false when any fold lacks regression",
                )
                labels = sc.get("regression_missing_fold_labels") or []
                self.assertGreater(
                    len(labels),
                    0,
                    f"{path}: missing folds must be recorded in regression_missing_fold_labels",
                )
                self.assertTrue(
                    data.get("regression_skipped_reason"),
                    f"{path}: missing folds require regression_skipped_reason (strict nulling)",
                )
                self.assertIs(
                    sc.get("regression_protocol_valid"),
                    False,
                    f"{path}: invalid regression protocol must set regression_protocol_valid false",
                )
            else:
                self.assertIsNotNone(
                    overall_reg,
                    f"{path}: finite folds imply numeric overall regression MAE",
                )
                # Trigger aligns with admissible booleans (oracle excluded).
                beat_g = sc.get("beat_global_mean_out_of_sample")
                beat_f = sc.get("beat_feature_baseline_out_of_sample")
                beat_r = sc.get("beat_regime_baseline_out_of_sample")
                self.assertIsInstance(beat_g, bool)
                self.assertIsInstance(beat_f, bool)
                self.assertIsInstance(beat_r, bool)
                expected = bool(beat_g and beat_f and beat_r)
                self.assertEqual(
                    trig,
                    expected,
                    f"{path}: trigger_met must match AND of admissible beats "
                    f"(got trig={trig} beats={beat_g},{beat_f},{beat_r})",
                )

            for fold in folds:
                self.assertIn("regression_mae", fold)
                self.assertIn(
                    "test_collapse_brier_train_prevalence",
                    fold,
                    f"{path}: each fold should export exploratory collapse Brier",
                )

            ci_lo = data.get("overall_regression_mae_ci95_lower")
            ci_hi = data.get("overall_regression_mae_ci95_upper")
            if overall_reg is not None:
                self.assertIsNotNone(ci_lo)
                self.assertIsNotNone(ci_hi)
            if overall_reg is None and sc.get("regression_protocol_valid") is not False:
                reason = data.get("regression_skipped_reason")
                self.assertTrue(
                    reason,
                    f"{path}: null overall regression requires regression_skipped_reason",
                )

    def test_generated_tables_notes_strict_nulling_when_present(self) -> None:
        gt = repo_root() / "papers" / "P5_ScalingLaws" / "generated_tables.md"
        if not gt.exists():
            self.skipTest("generated_tables.md not present")
        text = gt.read_text(encoding="utf-8")
        for path in _heldout_paths():
            if not path.exists():
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("overall_regression_mae") is not None:
                continue
            reason = data.get("regression_skipped_reason")
            if not reason:
                continue
            # Exporter should surface skip reason for reviewers (footnote-style).
            self.assertIn(
                "Regression skip / strict nulling",
                text,
                "generated_tables.md should document strict nulling when regression is absent",
            )
            break


if __name__ == "__main__":
    unittest.main()
