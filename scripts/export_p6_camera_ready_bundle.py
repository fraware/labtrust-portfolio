#!/usr/bin/env python3
"""
Generate P6 camera-ready manifest and table-ready CSV/JSON artifacts.
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN_DIR = REPO_ROOT / "datasets" / "runs" / "llm_eval"


def _read_json(path: Path, required: bool = True) -> dict:
    if not path.exists():
        if required:
            raise FileNotFoundError(f"Required artifact missing: {path}")
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_csv(path: Path, rows: list[dict], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k) for k in columns})


def _git_commit() -> str | None:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
        ).strip()
        return out
    except Exception:
        return None


def _manifest(run_dir: Path) -> dict:
    red = _read_json(run_dir / "red_team_results.json")
    base = _read_json(run_dir / "baseline_comparison.json", required=False)
    adapter = _read_json(run_dir / "adapter_latency.json", required=False)
    models = []
    if red.get("real_llm_models"):
        models = [
            m.get("model_id")
            for m in red["real_llm_models"]
            if m.get("model_id")
        ]
    elif red.get("real_llm", {}).get("model_id"):
        models = [red["real_llm"]["model_id"]]

    prompt_hash = None
    if red.get("real_llm_models"):
        for m in red["real_llm_models"]:
            prompt_hash = (m.get("run_manifest") or {}).get("prompt_template_hash")
            if prompt_hash:
                break
    elif red.get("real_llm", {}).get("run_manifest"):
        prompt_hash = red["real_llm"]["run_manifest"].get("prompt_template_hash")

    rm = red.get("run_manifest", {})
    return {
        "run_id": run_dir.name,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_commit": _git_commit(),
        "policy_version": rm.get("policy_version"),
        "evaluator_version": rm.get("evaluator_version"),
        "schema_version": "typed_plan.0.1",
        "models": models,
        "scenarios": adapter.get(
            "scenarios", base.get("run_manifest", {}).get("scenarios", [])
        ),
        "seeds": adapter.get("seeds", base.get("run_manifest", {}).get("seeds", [])),
        "prompt_template_hash": prompt_hash,
        "results": {
            "synthetic_suite": str(run_dir / "red_team_results.json"),
            "llm_runs": str(run_dir / "red_team_results.json"),
            "adapter_latency": (
                str(run_dir / "adapter_latency.json")
                if (run_dir / "adapter_latency.json").exists()
                else None
            ),
            "baselines": (
                str(run_dir / "baseline_comparison.json")
                if (run_dir / "baseline_comparison.json").exists()
                else None
            ),
            "replay": (
                str(run_dir / "replay_denials.json")
                if (run_dir / "replay_denials.json").exists()
                else None
            ),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Export P6 camera-ready artifact bundle."
    )
    ap.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    args = ap.parse_args()
    run_dir = args.run_dir

    red = _read_json(run_dir / "red_team_results.json")
    conf = _read_json(run_dir / "confusable_deputy_results.json")
    base_tool = _read_json(run_dir / "baseline_comparison.json", required=False)
    base_args = _read_json(run_dir / "baseline_comparison_args.json", required=False)
    base_benign = _read_json(run_dir / "baseline_benign.json", required=False)
    adapter = _read_json(run_dir / "adapter_latency.json", required=False)
    denial = _read_json(run_dir / "denial_trace_stats.json", required=False)

    exports = run_dir / "tables"
    exports.mkdir(parents=True, exist_ok=True)

    _write_csv(
        exports / "direct_typed_step_suite_cases.csv",
        red.get("cases", []),
        [
            "id",
            "description",
            "expected_block",
            "actually_blocked",
            "pass",
            "attribution",
        ],
    )
    _write_csv(
        exports / "jailbreak_suite_cases.csv",
        red.get("jailbreak_style", {}).get("cases", []),
        [
            "id",
            "description",
            "expected_block",
            "actually_blocked",
            "pass",
            "attribution",
        ],
    )
    _write_csv(
        exports / "confusable_deputy_cases.csv",
        conf.get("confusable_deputy_cases", []),
        [
            "id",
            "description",
            "expected_block",
            "actually_blocked",
            "pass",
            "attribution",
        ],
    )
    baseline_cols = [
        "scenario_id",
        "seed",
        "gated_denials",
        "weak_denials",
        "ungated_denials",
        "gated_tasks_completed",
        "weak_tasks_completed",
        "ungated_tasks_completed",
    ]
    if base_tool:
        _write_csv(
            exports / "baseline_tool_level_rows.csv",
            base_tool.get("rows", []),
            baseline_cols,
        )
    if base_args:
        _write_csv(
            exports / "baseline_argument_level_rows.csv",
            base_args.get("rows", []),
            baseline_cols,
        )
    if base_benign:
        _write_csv(
            exports / "benign_probe_rows.csv",
            base_benign.get("rows", []),
            baseline_cols,
        )
    if adapter:
        _write_csv(
            exports / "latency_per_run.csv",
            adapter.get("runs", []),
            [
                "scenario_id",
                "seed",
                "task_latency_ms_p95",
                "wall_sec",
                "denials_count",
                "tasks_completed",
            ],
        )

    manifest = _manifest(run_dir)
    (run_dir / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    if denial:
        (exports / "denial_trace_stats.json").write_text(
            json.dumps(denial, indent=2) + "\n", encoding="utf-8"
        )
    (exports / "llm_aggregate.json").write_text(
        json.dumps(
            {
                "red_team": red.get("excellence_metrics", {}),
                "confusable_deputy": conf.get("excellence_metrics", {}),
                "jailbreak_style": red.get("jailbreak_style", {}).get(
                    "denial_by_layer", {}
                ),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote bundle to {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
