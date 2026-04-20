#!/usr/bin/env python3
"""
Generate paper artifacts: check eval outputs exist, run export scripts (tables),
run paper figure scripts, and write generated tables to
papers/Px_*/generated_tables.md. Does not modify DRAFT.md.
P3 uses scripts/export_p3_paper_figures.py to populate papers/P3_Replay/figures/.

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
        [
            RUNS / "e3_summary.json",
            RUNS / "p0_e4_summary.json",
            RUNS / "p0_conformance_corpus" / "corpus_manifest.json",
            RUNS / "e2_redaction_demo" / "trace_redacted.json",
        ],
        [
            ("export_e1_corpus_table.py", []),
            ("export_e2_admissibility_matrix.py", []),
            ("export_e3_table.py", []),
            ("export_p0_table3.py", []),
        ],
        "export_p0_assurance_pipeline.py",
        "export_p0_tier_lattice.py",
    ),
    "P1": (
        "P1_Contracts",
        [RUNS / "contracts_eval" / "eval.json"],
        [
            ("export_contracts_corpus_table.py", []),
            ("export_p1_appendix_tex.py", []),
        ],
        "export_p1_contract_flow.py",
        "plot_contracts_scale.py",
    ),
    "P2": (
        "P2_REP-CPS",
        [RUNS / "rep_cps_eval" / "summary.json"],
        # export_rep_cps_tables.py writes papers/P2_REP-CPS/generated_tables.md directly (no stdout table body)
        [],
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
    # Child scripts print UTF-8 table titles (em dash, etc.); required on Windows.
    e.setdefault("PYTHONIOENCODING", "utf-8")
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
            encoding="utf-8",
            errors="replace",
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
        if pid == "P0":
            _p0_repro = (
                "Regenerate from repo root (`PYTHONPATH=impl/src`, "
                "`LABTRUST_KERNEL_DIR=kernel`): "
                "`python scripts/generate_paper_artifacts.py --paper P0`."
            )
            _p0_maestro = (
                "Tier 1 includes `maestro_report.json` validation against "
                "`kernel/eval/MAESTRO_REPORT.v0.2.schema.json`."
            )
            table_lines.extend([_p0_repro, "", _p0_maestro, ""])
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

        # 3–4. Figures (P3: single bundle into papers/P3_Replay/figures/)
        if pid == "P3":
            pack = SCRIPTS / "export_p3_paper_figures.py"
            if pack.exists():
                okp, _ = run_capture([sys.executable, str(pack)])
                print(
                    f"  P3 paper figures (export_p3_paper_figures.py): "
                    f"{'OK' if okp else 'FAILED'}"
                )
            else:
                print("  P3: export_p3_paper_figures.py not found")
        else:
            fig0_path = SCRIPTS / fig0
            if fig0_path.exists():
                ok, _ = run_capture([sys.executable, str(fig0_path)])
                print(f"  Figure 0 ({fig0}): {'OK' if ok else 'FAILED'}")
            else:
                print(f"  Figure 0: {fig0} not found")

            fig1_path = SCRIPTS / fig1
            if fig1_path.exists():
                cmd = [sys.executable, str(fig1_path)]
                if pid == "P7" and "export_assurance_gsn" in fig1:
                    cmd.extend(["--out", str(FIGURES / "p7_gsn.mmd")])
                ok, _ = run_capture(cmd)
                print(f"  Figure 1 ({fig1}): {'OK' if ok else 'FAILED'}")
            else:
                print(f"  Figure 1: {fig1} not found")

            if pid == "P0":
                for extra in ("export_p0_redaction_figure.py", "plot_e3_latency.py"):
                    ep = SCRIPTS / extra
                    if ep.exists():
                        okx, _ = run_capture([sys.executable, str(ep)])
                        print(f"  P0 extra ({extra}): {'OK' if okx else 'FAILED'}")
                    else:
                        print(f"  P0 extra: {extra} not found")

            if pid == "P1":
                for extra in ("render_p1_flow_figure.py", "plot_p1_paper_figures.py"):
                    ep = SCRIPTS / extra
                    if ep.exists():
                        okx, _ = run_capture([sys.executable, str(ep)])
                        print(f"  P1 extra ({extra}): {'OK' if okx else 'FAILED'}")
                    else:
                        print(f"  P1 extra: {extra} not found")

        if pid == "P2":
            fig2_path = SCRIPTS / "plot_rep_cps_gate_threshold.py"
            if fig2_path.exists():
                ok2, _ = run_capture([sys.executable, str(fig2_path)])
                print(f"  Figure 2 (plot_rep_cps_gate_threshold.py): {'OK' if ok2 else 'FAILED'}")
            else:
                print("  Figure 2: plot_rep_cps_gate_threshold.py not found")
            fig3_path = SCRIPTS / "plot_rep_cps_dynamics.py"
            if fig3_path.exists():
                ok3, _ = run_capture([sys.executable, str(fig3_path)])
                print(f"  Figure 3 (plot_rep_cps_dynamics.py): {'OK' if ok3 else 'FAILED'}")
            else:
                print("  Figure 3: plot_rep_cps_dynamics.py not found")
            fig4_path = SCRIPTS / "plot_rep_cps_latency.py"
            if fig4_path.exists():
                ok4, _ = run_capture([sys.executable, str(fig4_path)])
                print(f"  Figure 4 (plot_rep_cps_latency.py): {'OK' if ok4 else 'FAILED'}")
            else:
                print("  Figure 4: plot_rep_cps_latency.py not found")
            exp = SCRIPTS / "export_rep_cps_tables.py"
            if exp.exists() and (args.skip_eval_check or not missing):
                okt, _ = run_capture([sys.executable, str(exp)])
                print(f"  Tables (export_rep_cps_tables.py): {'OK' if okt else 'FAILED'}")

    print("\nDone. Paste from papers/Px_*/generated_tables.md into DRAFT.md as needed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
