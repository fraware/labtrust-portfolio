#!/usr/bin/env python3
"""
Generate paper artifacts: check eval outputs exist, run export scripts (tables),
run Figure 0 and Figure 1 scripts, and write generated tables to
papers/Px_*/generated_tables.md. Does not modify DRAFT.md.

Usage (from repo root):
  PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/generate_paper_artifacts.py [--paper P0|P1|...|P8|all] [--skip-eval-check]
  --paper: paper ID or "all" (default: all).
  --skip-eval-check: run export/figure scripts even if eval outputs are missing (some may print "Run X first").
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUNS = REPO / "datasets" / "runs"
SCRIPTS = REPO / "scripts"
FIGURES = REPO / "docs" / "figures"

# Paper ID -> (folder_name, required_eval_paths, export_commands, figure0_script, figure1_script)
# required_eval_paths: list of Paths that should exist (or script prints helpful message)
# export_commands: list of (script_name, [args]) e.g. ("export_e3_table.py", [])
# figure scripts: script name only; script writes to docs/figures/
PAPER_CONFIG = {
    "P0": (
        "P0_MADS-CPS",
        [RUNS / "e3_summary.json", RUNS / "e2_redaction_demo" / "trace_redacted.json"],
        [("export_e3_table.py", []), ("export_e2_admissibility_matrix.py", [])],
        "export_p0_assurance_pipeline.py",
        "plot_e3_latency.py",
    ),
    "P1": (
        "P1_Contracts",
        [RUNS / "contracts_eval" / "eval.json"],
        [("export_contracts_corpus_table.py", [])],
        "export_p1_contract_flow.py",
        "plot_contracts_scale.py",
    ),
    "P2": (
        "P2_REP-CPS",
        [RUNS / "rep_cps_eval" / "summary.json"],
        [],  # Tables from summary.json manually or no dedicated export
        "export_p2_rep_profile_diagram.py",
        "plot_rep_cps_summary.py",
    ),
    "P3": (
        "P3_Replay",
        [RUNS / "replay_eval" / "summary.json"],
        [],  # Table content from summary
        "export_p3_replay_levels_diagram.py",
        "plot_replay_overhead.py",
    ),
    "P4": (
        "P4_CPS-MAESTRO",
        [
            RUNS / "maestro_fault_sweep" / "multi_sweep.json",
            REPO / "bench" / "maestro" / "baseline_summary.json",
        ],
        [("export_maestro_tables.py", [])],
        "export_p4_maestro_flow.py",
        "plot_maestro_recovery.py",
    ),
    "P5": (
        "P5_ScalingLaws",
        [RUNS / "scaling_eval" / "heldout_results.json"],
        [("export_scaling_tables.py", [])],
        "export_p5_baseline_hierarchy.py",
        "plot_scaling_mae.py",
    ),
    "P6": (
        "P6_LLMPlanning",
        [RUNS / "llm_eval" / "red_team_results.json"],
        [("export_llm_redteam_table.py", [])],
        "export_p6_firewall_flow.py",
        "plot_llm_adapter_latency.py",
    ),
    "P7": (
        "P7_StandardsMapping",
        [RUNS / "assurance_eval" / "results.json"],
        [("export_assurance_tables.py", [])],
        "export_p7_mapping_flow.py",
        "export_assurance_gsn.py",  # Figure 1 for P7
    ),
    "P8": (
        "P8_MetaCoordination",
        [RUNS / "meta_eval" / "comparison.json"],
        [("export_meta_tables.py", [])],
        "export_p8_meta_diagram.py",
        "plot_meta_collapse.py",
    ),
}


def env() -> dict:
    e = os.environ.copy()
    e.setdefault("LABTRUST_KERNEL_DIR", str(REPO / "kernel"))
    e.setdefault("PYTHONPATH", str(REPO / "impl" / "src"))
    return e


def run_capture(cmd: list[str], timeout: int = 120) -> tuple[bool, str]:
    """Run command; return (success, stdout+stderr)."""
    try:
        r = subprocess.run(
            cmd,
            cwd=str(REPO),
            env=env(),
            timeout=timeout,
            capture_output=True,
            text=True,
        )
        out = (r.stdout or "") + (r.stderr or "")
        return r.returncode == 0, out
    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception as ex:
        return False, str(ex)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Generate paper artifacts: check evals, run exports, run figure scripts, write generated_tables.md"
    )
    ap.add_argument(
        "--paper",
        default="all",
        help="Paper ID (P0..P8) or 'all'",
    )
    ap.add_argument(
        "--skip-eval-check",
        action="store_true",
        help="Do not require eval outputs to exist; run export/figure scripts anyway",
    )
    args = ap.parse_args()

    papers = list(PAPER_CONFIG.keys()) if args.paper == "all" else [args.paper]
    if args.paper != "all" and args.paper not in PAPER_CONFIG:
        print(f"Unknown paper: {args.paper}. Use P0..P8 or all.")
        return 1

    for pid in papers:
        config = PAPER_CONFIG[pid]
        folder, required_paths, export_cmds, fig0, fig1 = config
        paper_dir = REPO / "papers" / folder
        if not paper_dir.exists():
            print(f"Skip {pid}: papers/{folder} not found.")
            continue

        print(f"\n=== {pid} {folder} ===")

        # 1. Check eval outputs
        missing = [] if args.skip_eval_check else [p for p in required_paths if not p.exists()]
        if missing:
            print(f"  Missing eval outputs (run eval first):")
            for p in missing:
                print(f"    - {p.relative_to(REPO)}")
            print(f"  See docs/PAPER_GENERATION_WORKFLOW.md for commands.")
            if not args.skip_eval_check:
                print("  Skipping export step (run with --skip-eval-check to run anyway).")
        else:
            print("  Eval outputs present.")

        # 2. Run export scripts, write to generated_tables.md (skip if missing and not --skip-eval-check)
        table_lines = [f"# Generated tables for {pid} ({folder})", ""]
        any_export = False
        run_exports = args.skip_eval_check or not missing
        for script_name, script_args in export_cmds:
            if not run_exports:
                continue
            script_path = SCRIPTS / script_name
            if not script_path.exists():
                print(f"  Skip export: {script_name} not found.")
                continue
            ok, out = run_capture([sys.executable, str(script_path)] + script_args)
            if ok and out.strip():
                table_lines.append(f"## From {script_name}")
                table_lines.append("")
                table_lines.extend(out.rstrip().split("\n"))
                table_lines.append("")
                any_export = True
            else:
                print(f"  Export {script_name}: no output or failed (run eval first?)")
        if any_export:
            out_file = paper_dir / "generated_tables.md"
            out_file.write_text("\n".join(table_lines) + "\n", encoding="utf-8")
            print(f"  Wrote {out_file.relative_to(REPO)}")

        # 3. Figure 0
        fig0_path = SCRIPTS / fig0
        if fig0_path.exists():
            ok, _ = run_capture([sys.executable, str(fig0_path)])
            print(f"  Figure 0 ({fig0}): {'OK' if ok else 'FAILED'}")
        else:
            print(f"  Figure 0: {fig0} not found")

        # 4. Figure 1 (P7 uses export_assurance_gsn with --out)
        fig1_path = SCRIPTS / fig1
        if fig1_path.exists():
            cmd = [sys.executable, str(fig1_path)]
            if pid == "P7" and "export_assurance_gsn" in fig1:
                cmd.extend(["--out", str(FIGURES / "p7_gsn.mmd")])
            ok, _ = run_capture(cmd)
            print(f"  Figure 1 ({fig1}): {'OK' if ok else 'FAILED'}")
        else:
            print(f"  Figure 1: {fig1} not found")

    print("\nDone. Paste from papers/Px_*/generated_tables.md into DRAFT.md as needed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
