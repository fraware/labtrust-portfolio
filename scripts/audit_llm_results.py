#!/usr/bin/env python3
"""
Audit helpers for real-LLM run directories and red_team_results.json.

Examples:
  python scripts/audit_llm_results.py --run-dir datasets/runs/llm_eval_robust_gpt_20260424
  python scripts/audit_llm_results.py --run-dir datasets/runs/my_eval \\
      --red-team-results datasets/runs/my_eval/red_team_results.json --json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def audit_scoring_from_red_team(red: dict[str, Any]) -> dict[str, Any]:
    """
    Recompute per-model sums from real_llm_models[].cases[] and compare to aggregates.
    Each cases[] row is one (case_id, prompt_variant) slice with pass_count / n_runs.
    """
    models_out: list[dict[str, Any]] = []
    any_fail = False
    top_rm = red.get("run_manifest") or {}
    top_pv = top_rm.get("real_llm_prompt_variants")
    models = red.get("real_llm_models") or []
    successful = [m for m in models if not m.get("error")]
    if not successful:
        return {
            "models": [],
            "scoring_ok": True,
            "note": "no successful real_llm_models to score",
        }

    for m in models:
        if m.get("error"):
            models_out.append(
                {
                    "model_id": m.get("model_id"),
                    "skipped": True,
                    "error": m.get("error"),
                }
            )
            continue
        mid = str(m.get("model_id", ""))
        cases = m.get("cases") or []
        sum_pc = sum(int(c.get("pass_count", 0)) for c in cases)
        sum_nr = sum(int(c.get("n_runs", 0) or 0) for c in cases)
        npt = m.get("n_pass_total")
        nrt = m.get("n_runs_total")
        mv_pv = m.get("prompt_variants")
        rm = m.get("run_manifest") or {}
        rm_fp = rm.get("real_llm_variant_fingerprint")
        pass_ok = sum_pc == npt if npt is not None else True
        runs_ok = sum_nr == nrt if nrt is not None else True
        pv_ok = True
        if top_pv is not None and mv_pv is not None and list(top_pv) != list(mv_pv):
            pv_ok = False
        row = {
            "model_id": mid,
            "sum_pass_count": sum_pc,
            "n_pass_total": npt,
            "pass_sum_matches_aggregate": pass_ok,
            "sum_case_n_runs": sum_nr,
            "n_runs_total": nrt,
            "runs_sum_matches_aggregate": runs_ok,
            "n_case_variant_rows": len(cases),
            "model_prompt_variants": mv_pv,
            "top_manifest_prompt_variants": top_pv,
            "prompt_variant_lists_aligned": pv_ok,
            "real_llm_variant_fingerprint": rm_fp,
        }
        if not pass_ok or not runs_ok or not pv_ok:
            any_fail = True
        models_out.append(row)
    return {"models": models_out, "scoring_ok": not any_fail}


def audit_materialized_scoring(run_dir: Path) -> dict[str, Any] | None:
    """Use statistical_summary.json scoring_consistency when present (materializer output)."""
    p = run_dir / "statistical_summary.json"
    if not p.is_file():
        return None
    data = _load_json(p)
    try:
        src = str(p.relative_to(REPO)).replace("\\", "/")
    except ValueError:
        src = str(p)
    checks = data.get("scoring_consistency")
    if checks is None:
        return None
    rows: list[dict[str, Any]] = []
    ok = True
    if not checks:
        return {"source": src, "rows": [], "scoring_ok": True, "note": "empty scoring_consistency list"}
    for c in checks:
        m = bool(c.get("matches_aggregate_to_case_sum", True))
        rows.append(
            {
                "model_id": c.get("model_id"),
                "matches_aggregate_to_case_sum": m,
            }
        )
        if not m:
            ok = False
    return {"source": src, "rows": rows, "scoring_ok": ok and bool(rows)}


def audit_independence(run_dir: Path) -> dict[str, Any] | None:
    p = run_dir / "canonical_independence_audit.json"
    if not p.is_file():
        return None
    data = _load_json(p)
    return {
        "verdict": data.get("verdict"),
        "distinct_model_ids": data.get("distinct_model_ids"),
        "same_denominator": data.get("same_denominator"),
        "distinct_response_ids_available": data.get("distinct_response_ids_available"),
        "cross_model_aligned_trials_with_stored_raw": (data.get("raw_output_hash_comparison") or {}).get(
            "cross_model_aligned_trials_with_stored_raw"
        ),
    }


def audit_robust_summary(run_dir: Path) -> dict[str, Any] | None:
    p = run_dir / "ROBUST_GPT_SUMMARY.json"
    if not p.is_file():
        return None
    data = _load_json(p)
    return {
        "engineering_sign_off": data.get("engineering_sign_off"),
        "n_blockers": len(data.get("blockers") or []),
        "blockers": data.get("blockers") or [],
    }


def run_materializer(red_team: Path | None, out_dir: Path | None) -> int:
    cmd = [sys.executable, str(REPO / "scripts" / "p6_robust_gpt_materialize.py")]
    if red_team is not None:
        cmd += ["--red-team-results", str(red_team)]
    if out_dir is not None:
        cmd += ["--out-dir", str(out_dir)]
    r = subprocess.run(cmd, cwd=str(REPO))
    return r.returncode


def main() -> int:
    ap = argparse.ArgumentParser(description="Audit LLM eval run directory (independence + scoring).")
    ap.add_argument(
        "--run-dir",
        type=Path,
        default=REPO / "datasets" / "runs" / "llm_eval_robust_gpt_20260424",
        help="Directory with canonical_independence_audit.json (and optional statistical_summary.json)",
    )
    ap.add_argument(
        "--red-team-results",
        type=Path,
        default=None,
        metavar="PATH",
        help="Optional path to red_team_results.json for exact scoring recomputation (recommended for scratch --out dirs)",
    )
    ap.add_argument(
        "--rematerialize",
        action="store_true",
        help="Re-run p6_robust_gpt_materialize.py into --run-dir before auditing",
    )
    ap.add_argument(
        "--materialize-red-team",
        type=Path,
        default=None,
        metavar="PATH",
        help="With --rematerialize: pass --red-team-results to the materializer (default: canonical camera-ready JSON)",
    )
    ap.add_argument(
        "--json",
        action="store_true",
        help="Print one JSON object to stdout (for CI)",
    )
    args = ap.parse_args()
    run_dir = args.run_dir.resolve()

    if args.rematerialize:
        m_red = args.materialize_red_team
        if m_red is None:
            m_red = REPO / "datasets" / "runs" / "llm_eval_camera_ready_20260424" / "red_team_results.json"
        rc = run_materializer(m_red.resolve(), run_dir)
        if rc != 0:
            return rc

    report: dict[str, Any] = {"run_dir": str(run_dir)}

    ind = audit_independence(run_dir)
    report["independence"] = ind
    if ind is None and not args.json:
        print("Missing", run_dir / "canonical_independence_audit.json", file=sys.stderr)
        print("Hint: python scripts/p6_robust_gpt_materialize.py --out-dir", run_dir, file=sys.stderr)

    mat = audit_materialized_scoring(run_dir)
    report["materialized_scoring"] = mat

    red_path = args.red_team_results
    if red_path is None:
        candidate = run_dir / "red_team_results.json"
        if candidate.is_file():
            red_path = candidate
    red_audit: dict[str, Any] | None = None
    if red_path is not None and red_path.is_file():
        red = _load_json(red_path.resolve())
        red_audit = audit_scoring_from_red_team(red)
        report["red_team_results_path"] = str(red_path)
        report["red_team_scoring"] = red_audit

    summ = audit_robust_summary(run_dir)
    report["robust_summary"] = summ

    scoring_ok = True
    if mat is not None and not mat.get("scoring_ok", True):
        scoring_ok = False
    if red_audit is not None and not red_audit.get("scoring_ok", True):
        scoring_ok = False

    report["overall_scoring_ok"] = scoring_ok
    report["exit_recommendation"] = 0 if scoring_ok else 1

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        if ind:
            print("independence.verdict:", ind.get("verdict"))
            print("independence.distinct_model_ids:", ind.get("distinct_model_ids"))
            print("independence.response_ids_available:", ind.get("distinct_response_ids_available"))
        if mat:
            print("materialized scoring_consistency ok:", mat.get("scoring_ok"))
            for r in mat.get("rows") or []:
                print(" ", r.get("model_id"), "matches_aggregate_to_case_sum:", r.get("matches_aggregate_to_case_sum"))
        if red_audit:
            print("red_team_results recomputation ok:", red_audit.get("scoring_ok"))
            for r in red_audit.get("models") or []:
                if r.get("skipped"):
                    print(" ", r.get("model_id"), "ERROR", r.get("error"))
                    continue
                print(
                    " ",
                    r.get("model_id"),
                    "pass",
                    r.get("sum_pass_count"),
                    "/",
                    r.get("n_pass_total"),
                    "runs",
                    r.get("sum_case_n_runs"),
                    "/",
                    r.get("n_runs_total"),
                    "pv_aligned",
                    r.get("prompt_variant_lists_aligned"),
                )
        if summ:
            print("ROBUST_GPT_SUMMARY blockers:", summ.get("n_blockers"))

    if ind is None and mat is None and red_audit is None:
        return 1
    return 0 if scoring_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
