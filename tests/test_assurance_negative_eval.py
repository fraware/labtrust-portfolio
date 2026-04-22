"""Smoke test for P7 negative-control eval and export."""
from __future__ import annotations

import json
import os
import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


class TestAssuranceNegativeEval(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["LABTRUST_KERNEL_DIR"] = str(repo_root() / "kernel")

    def test_negative_eval_quick_produces_json(self) -> None:
        env = os.environ.copy()
        pypath = str(repo_root() / "impl" / "src")
        script = repo_root() / "scripts" / "run_assurance_negative_eval.py"
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "out"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--quick",
                    "--submission-mode",
                    "--out",
                    str(out),
                ],
                cwd=str(repo_root()),
                env={**env, "PYTHONPATH": pypath},
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(proc.returncode, 0, (proc.stdout, proc.stderr))
            p = out / "negative_results.json"
            self.assertTrue(p.exists())
            data = json.loads(p.read_text(encoding="utf-8"))
            self.assertIn("aggregate", data)
            self.assertIn("by_mode", data)
            self.assertIn("by_scenario", data)
            self.assertIn("by_perturbation", data)
            self.assertIn("rows", data)
            self.assertGreater(len(data["rows"]), 0)
            self.assertEqual(data.get("run_manifest", {}).get("repo_root"), "<redacted>")
            for m in ("schema_only", "schema_plus_presence", "full_review"):
                self.assertIn(m, data["by_mode"])
            # Regression: schema_only must still false-accept at least one invalid case.
            self.assertGreater(
                float(data["by_mode"]["schema_only"]["false_accept_rate"] or 0.0),
                0.0,
            )
            # Regression: known full-review rejections remain enforced.
            by_pid = {x["perturbation_id"]: x for x in data.get("by_perturbation", [])}
            prov = by_pid["cross_run_trace_bundle_swap"]["by_mode"]["full_review"]
            self.assertFalse(bool(prov["review_exit_ok"]))
            self.assertIn("PROVENANCE_MISMATCH", prov["failure_reason_codes"])
            ponr = by_pid["missing_required_ponr_event"]["by_mode"]["full_review"]
            self.assertFalse(bool(ponr["review_exit_ok"]))
            self.assertIn("PONR_MISSING", ponr["failure_reason_codes"])

    def test_export_negative_tables(self) -> None:
        env = os.environ.copy()
        pypath = str(repo_root() / "impl" / "src")
        neg_json = repo_root() / "datasets" / "runs" / "assurance_eval" / "negative_results.json"
        if not neg_json.exists():
            self.skipTest("negative_results.json not present; run run_assurance_negative_eval.py")
        with tempfile.TemporaryDirectory() as td:
            outd = Path(td) / "tbl"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(repo_root() / "scripts" / "export_p7_negative_tables.py"),
                    "--input",
                    str(neg_json),
                    "--out-dir",
                    str(outd),
                    "--submission-mode",
                ],
                cwd=str(repo_root()),
                env={**env, "PYTHONPATH": pypath},
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(proc.returncode, 0, (proc.stdout, proc.stderr))
            for name in (
                "p7_ablation_summary.csv",
                "p7_negative_family_summary.csv",
                "p7_failure_reason_breakdown.csv",
                "p7_perturbation_reject_matrix.csv",
                "p7_aggregate_lift_metrics.csv",
                "p7_latency_by_mode.csv",
                "p7_negative_by_scenario.csv",
                "p7_boundary_case_summary.csv",
                "p7_submission_manifest_redacted.json",
                "p7_generation_metadata.json",
            ):
                self.assertTrue((outd / name).exists(), name)

    def test_export_csvs_consistent_with_negative_results_json(self) -> None:
        env = os.environ.copy()
        pypath = str(repo_root() / "impl" / "src")
        script_eval = repo_root() / "scripts" / "run_assurance_negative_eval.py"
        script_export = repo_root() / "scripts" / "export_p7_negative_tables.py"
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "eval"
            proc_eval = subprocess.run(
                [
                    sys.executable,
                    str(script_eval),
                    "--quick",
                    "--submission-mode",
                    "--out",
                    str(out),
                ],
                cwd=str(repo_root()),
                env={**env, "PYTHONPATH": pypath},
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(proc_eval.returncode, 0, (proc_eval.stdout, proc_eval.stderr))
            neg_json = out / "negative_results.json"
            self.assertTrue(neg_json.exists())
            data = json.loads(neg_json.read_text(encoding="utf-8"))
            proc_export = subprocess.run(
                [
                    sys.executable,
                    str(script_export),
                    "--input",
                    str(neg_json),
                    "--out-dir",
                    str(out),
                    "--submission-mode",
                ],
                cwd=str(repo_root()),
                env={**env, "PYTHONPATH": pypath},
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertEqual(proc_export.returncode, 0, (proc_export.stdout, proc_export.stderr))

            # 1) p7_ablation_summary.csv == by_mode
            with (out / "p7_ablation_summary.csv").open("r", encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f))
            by_mode = data["by_mode"]
            self.assertEqual({r["review_mode"] for r in rows}, set(by_mode.keys()))
            for r in rows:
                m = by_mode[r["review_mode"]]
                self.assertEqual(float(r["valid_accept_rate"]), float(m["valid_accept_rate"]))
                self.assertEqual(float(r["invalid_reject_rate"]), float(m["invalid_reject_rate"]))
                self.assertEqual(float(r["false_accept_rate"]), float(m["false_accept_rate"]))
                self.assertEqual(float(r["false_reject_rate"]), float(m["false_reject_rate"]))
                self.assertEqual(float(r["localization_accuracy"]), float(m["localization_accuracy"]))

            # 2) p7_negative_family_summary.csv == by_family
            with (out / "p7_negative_family_summary.csv").open("r", encoding="utf-8", newline="") as f:
                fam_rows = list(csv.DictReader(f))
            by_family = {
                k: v
                for k, v in (data.get("by_family") or {}).items()
                if k != "positive_control"
            }
            self.assertEqual({r["failure_family"] for r in fam_rows}, set(by_family.keys()))
            for r in fam_rows:
                fam = r["failure_family"]
                src = by_family[fam]
                self.assertEqual(int(r["n_negative_cases"]), int(src["n"]))
                self.assertEqual(float(r["reject_rate"]), float(src["reject_rate_on_negatives"]))
                self.assertEqual(float(r["localization_accuracy"]), float(src["localization_accuracy"]))

            # 3) p7_aggregate_lift_metrics.csv == aggregate
            with (out / "p7_aggregate_lift_metrics.csv").open("r", encoding="utf-8", newline="") as f:
                agg_rows = list(csv.DictReader(f))
            self.assertEqual(len(agg_rows), 1)
            agg_csv = agg_rows[0]
            agg_json = data["aggregate"]
            for key in (
                "n_valid",
                "n_invalid",
                "governance_evidence_discrimination_accuracy",
                "invalid_reject_lift_full_minus_schema_only",
                "false_accept_drop_full_vs_schema_only",
                "localization_accuracy_lift_full_minus_schema_only",
                "invalid_reject_lift_full_minus_schema_plus_presence",
            ):
                if key in ("n_valid", "n_invalid"):
                    self.assertEqual(int(agg_csv[key]), int(agg_json[key]))
                else:
                    self.assertEqual(float(agg_csv[key]), float(agg_json[key]))
