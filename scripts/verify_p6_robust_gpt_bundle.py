#!/usr/bin/env python3
"""
Machine-check the committed P6 robust GPT audit package under datasets/runs/.

Verifies required materializer outputs exist, then runs
``audit_llm_results.py`` against the frozen camera-ready
``red_team_results.json`` for aggregate recomputation (unless
``--skip-audit``).

Usage (from repo root): ``python scripts/verify_p6_robust_gpt_bundle.py``
Or: ``python scripts/verify_p6_robust_gpt_bundle.py --run-dir …/other_bundle``
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_RUN_DIR = REPO / "datasets" / "runs" / "llm_eval_robust_gpt_20260424"
_DEFAULT_CAMERA_READY = REPO / "datasets" / "runs" / "llm_eval_camera_ready_20260424"
DEFAULT_RED_TEAM = _DEFAULT_CAMERA_READY / "red_team_results.json"

# Keep in sync with scripts/p6_robust_gpt_materialize.py outputs (20260424 partial audit).
REQUIRED_FILES_LEGACY = (
    "README.md",
    "MANIFEST.json",
    "ROBUST_GPT_SUMMARY.json",
    "ROBUST_GPT_SUMMARY.md",
    "canonical_independence_audit.json",
    "negative_controls.json",
    "canonical_real_llm_results.json",
    "raw_outputs.jsonl",
    "parsed_outputs.jsonl",
    "per_case_results.csv",
    "per_case_results.json",
    "failure_audit.csv",
    "failure_audit.json",
    "prompt_variant_results.json",
    "parser_interface_results.json",
    "stress_results.json",
    "statistical_summary.json",
    "model_realization_layered_results.csv",
    "paper_table_recommended.csv",
    "paper_wording_recommended.md",
)

# Full paper-oriented bundle (scripts/p6_robust_gpt_full_package.py).
REQUIRED_FILES_FULL = (
    "README.md",
    "MANIFEST.json",
    "ROBUST_GPT_SUMMARY.md",
    "ROBUST_GPT_SUMMARY.json",
    "canonical_results.json",
    "stress_results.json",
    "prompt_variant_results.json",
    "per_trial_results.jsonl",
    "raw_outputs.jsonl",
    "parsed_outputs.jsonl",
    "per_case_results.csv",
    "per_case_results.json",
    "failure_audit.csv",
    "failure_audit.json",
    "model_realization_layered_results.csv",
    "parser_interface_results.json",
    "scoring_consistency.json",
    "canonical_independence_audit.json",
    "negative_controls.json",
    "statistical_summary.json",
    "paper_table_recommended.csv",
    "paper_wording_recommended.md",
    "prompt_template_audit.json",
    "artifact_hashes.json",
)

PAPER_READY_SIGNOFF = "ENGINEERING SIGN-OFF: GPT RESULTS PAPER-READY"
FULL_VARIANTS = (
    "canonical",
    "strict_json",
    "json_schema",
    "adversarial_context",
    "tool_return_injection",
    "unsafe_paraphrase",
    "benign_paraphrase",
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Verify robust GPT materialized bundle + scoring audit",
    )
    ap.add_argument(
        "--run-dir",
        type=Path,
        default=DEFAULT_RUN_DIR,
        help="Materialized bundle directory",
    )
    ap.add_argument(
        "--red-team-results",
        type=Path,
        default=DEFAULT_RED_TEAM,
        help="Source red_team_results.json for audit_llm_results.py recomputation",
    )
    ap.add_argument(
        "--schema",
        choices=("legacy", "full"),
        default="legacy",
        help="legacy=20260424 materializer layout; full=20260425_full export layout",
    )
    ap.add_argument(
        "--require-paper-ready",
        action="store_true",
        help="Fail unless ROBUST_GPT_SUMMARY.md ends with paper-ready sign-off and gates pass",
    )
    ap.add_argument(
        "--skip-audit",
        action="store_true",
        help="Only check file presence (no audit_llm_results subprocess)",
    )
    args = ap.parse_args()
    run_dir = args.run_dir.resolve()
    if not run_dir.is_dir():
        print(f"run_dir is not a directory: {run_dir}", file=sys.stderr)
        return 1

    req = REQUIRED_FILES_FULL if args.schema == "full" else REQUIRED_FILES_LEGACY
    errors: list[str] = []
    for name in req:
        p = run_dir / name
        if not p.is_file():
            errors.append(f"missing required file: {p.relative_to(REPO)}")

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1

    if args.require_paper_ready:
        md = (run_dir / "ROBUST_GPT_SUMMARY.md").read_text(encoding="utf-8").strip().splitlines()
        tail = ""
        for line in reversed(md):
            if line.strip():
                tail = line.strip()
                break
        if tail != PAPER_READY_SIGNOFF:
            print(
                f"--require-paper-ready: last non-empty line must be:\n  {PAPER_READY_SIGNOFF}\n"
                f"got: {tail!r}",
                file=sys.stderr,
            )
            return 1
        if args.schema == "full":
            sc = _load_json(run_dir / "scoring_consistency.json")
            for row in sc.get("rows") or []:
                if not row.get("matches"):
                    print(
                        "--require-paper-ready: scoring_consistency mismatch",
                        row,
                        file=sys.stderr,
                    )
                    return 1
            pv = _load_json(run_dir / "prompt_variant_results.json")
            for mid, per in (pv.get("models") or {}).items():
                for v in FULL_VARIANTS:
                    st = (per.get(v) or {}).get("status")
                    if st != "executed":
                        print(
                            f"--require-paper-ready: prompt variant {v!r} not_executed for {mid}",
                            file=sys.stderr,
                        )
                        return 1
            stress = _load_json(run_dir / "stress_results.json")
            if stress.get("status") != "executed":
                print("--require-paper-ready: stress_results.status must be executed", file=sys.stderr)
                return 1
            neg = _load_json(run_dir / "negative_controls.json")
            for k in (
                "validator_negative_control_detected",
                "parser_negative_control_detected",
                "scoring_negative_control_detected",
                "prompt_variant_negative_control_detected",
                "stress_suite_negative_control_detected",
                "raw_output_missing_negative_control_detected",
            ):
                if not neg.get(k):
                    print(f"--require-paper-ready: negative_controls.{k} must be true", file=sys.stderr)
                    return 1
            ind = _load_json(run_dir / "canonical_independence_audit.json")
            if not ind.get("distinct_response_ids_available"):
                print(
                    "--require-paper-ready: canonical_independence_audit.distinct_response_ids_available",
                    file=sys.stderr,
                )
                return 1
            if ind.get("copy_or_join_bug_detected"):
                print("--require-paper-ready: copy_or_join_bug_detected", file=sys.stderr)
                return 1
            if not ind.get("scoring_reads_model_specific_files"):
                print("--require-paper-ready: scoring_reads_model_specific_files", file=sys.stderr)
                return 1
            red_path = args.red_team_results.resolve()
            if red_path.is_file():
                red = _load_json(red_path)
                for m in red.get("real_llm_models") or []:
                    if m.get("error"):
                        continue
                    mid = str(m.get("model_id", ""))
                    if mid.startswith("gpt-5"):
                        # GPT-5.x must have full per-trial evidence when included.
                        n_raw = sum(
                            1
                            for line in (run_dir / "raw_outputs.jsonl").read_text(encoding="utf-8").splitlines()
                            if line.strip() and json.loads(line).get("model_id") == mid
                        )
                        n_tot = int(m.get("n_runs_total") or 0)
                        if n_tot and n_raw < n_tot:
                            print(
                                f"--require-paper-ready: {mid} included but raw_outputs.jsonl rows {n_raw} < n_runs_total {n_tot}",
                                file=sys.stderr,
                            )
                            return 1

    if args.skip_audit:
        print("verify_p6_robust_gpt_bundle: file checks OK (--skip-audit)")
        return 0

    red = args.red_team_results.resolve()
    if not red.is_file():
        print(f"--red-team-results not a file: {red}", file=sys.stderr)
        return 1

    audit_cmd = [
        sys.executable,
        str(REPO / "scripts" / "audit_llm_results.py"),
        "--run-dir",
        str(run_dir),
        "--red-team-results",
        str(red),
    ]
    if args.schema == "full" and not args.require_paper_ready:
        audit_cmd.append("--ignore-materialized-scoring-when-red-team-ok")
    r = subprocess.run(audit_cmd, cwd=str(REPO))
    if r.returncode != 0:
        return r.returncode
    print("verify_p6_robust_gpt_bundle: OK", run_dir.relative_to(REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
