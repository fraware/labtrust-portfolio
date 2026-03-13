from __future__ import annotations

import argparse
from pathlib import Path
from .thinslice import run_thin_slice
from .profile import load_lab_profile, lab_profile_dir
from .release import release_dataset
from .conformance import check_conformance, write_conformance_artifact
from .replay import replay_trace, replay_trace_with_diagnostics


def main() -> int:
    ap = argparse.ArgumentParser(prog="labtrust_portfolio")
    sub = ap.add_subparsers(dest="cmd", required=True)

    ts = sub.add_parser(
        "run-thinslice",
        help="Run thin-slice TRACE→MAESTRO→Replay→Evidence pipeline",
    )
    ts.add_argument("--out-dir", type=Path, required=True)
    ts.add_argument("--seed", type=int, default=7)
    ts.add_argument("--delay-p95-ms", type=float, default=50.0)
    ts.add_argument("--drop-completion-prob", type=float, default=0.02)

    load_prof = sub.add_parser(
        "load-profile",
        help="Load and validate the lab profile (profiles/lab/v0.1/)",
    )
    load_prof.add_argument(
        "--profile-dir", type=Path, default=None,
        help="Override profile directory",
    )

    release_cmd = sub.add_parser(
        "release-dataset",
        help="Copy a run to datasets/releases/ and write release manifest",
    )
    release_cmd.add_argument(
        "run_dir", type=Path, help="Run directory (contains trace.json, etc.)",
    )
    release_cmd.add_argument(
        "release_id", type=str, help="Release ID (e.g. release_abc123)",
    )
    release_cmd.add_argument(
        "--releases-root",
        type=Path,
        default=None,
        help="Releases root (default: repo datasets/releases)",
    )
    release_cmd.add_argument(
        "--check-contracts",
        action="store_true",
        help="Run contract validator on trace; deny release if any event denied (strict PONR)",
    )

    check_cmd = sub.add_parser(
        "check-conformance",
        help="Check run directory for Tier 1/2 conformance",
    )
    check_cmd.add_argument(
        "run_dir",
        type=Path,
        help="Run directory (contains trace.json, etc.)",
    )

    replay_cmd = sub.add_parser(
        "replay",
        help="Run L0 replay on a trace; exit 0 if ok, 1 if divergence",
    )
    replay_cmd.add_argument(
        "trace_path",
        type=Path,
        nargs="?",
        default=None,
        help="Path to trace.json (or use --run-dir)",
    )
    replay_cmd.add_argument(
        "--run-dir",
        type=Path,
        default=None,
        help="Run directory (trace.json inside); overrides trace_path",
    )
    replay_cmd.add_argument(
        "--diagnostics",
        action="store_true",
        help="Print structured divergence diagnostics",
    )

    args = ap.parse_args()
    if args.cmd == "run-thinslice":
        out = run_thin_slice(
            args.out_dir,
            seed=args.seed,
            delay_p95_ms=args.delay_p95_ms,
            drop_completion_prob=args.drop_completion_prob,
        )
        for k, p in out.items():
            print(f"{k}: {p}")
        return 0
    if args.cmd == "load-profile":
        profile_dir = (
            args.profile_dir
            if hasattr(args, "profile_dir") and args.profile_dir
            else None
        )
        data = load_lab_profile(profile_dir)
        print(f"OK: loaded lab profile from {lab_profile_dir()}")
        for name in ("ponrs", "fault_model", "telemetry_min_fields", "state_types"):
            if name in data:
                val = data[name]
                n = len(val) if isinstance(val, (list, dict)) else 0
                print(f"  {name}: {n} items")
        return 0
    if args.cmd == "release-dataset":
        run_dir = args.run_dir
        release_id = args.release_id
        if getattr(args, "releases_root", None) is not None:
            releases_root = args.releases_root
        else:
            from .profile import find_repo_root
            repo = find_repo_root(Path(__file__).resolve())
            releases_root = repo / "datasets" / "releases"
        check_contracts = getattr(args, "check_contracts", False)
        release_dir, manifest = release_dataset(
            run_dir, release_id, releases_root, check_contracts=check_contracts
        )
        print(f"Release written to {release_dir}")
        print(f"release_id: {manifest['release_id']}")
        return 0
    if args.cmd == "check-conformance":
        result = check_conformance(args.run_dir)
        conformance_path = write_conformance_artifact(args.run_dir)
        print(result.message())
        print(f"conformance.json: {conformance_path}")
        return 0 if result.passed else 1
    if args.cmd == "replay":
        import json
        run_dir = getattr(args, "run_dir", None)
        trace_path = getattr(args, "trace_path", None)
        if run_dir is not None:
            trace_path = run_dir / "trace.json"
        if trace_path is None or not trace_path.exists():
            print("error: need trace_path or --run-dir with trace.json")
            return 1
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        use_diag = getattr(args, "diagnostics", False)
        if use_diag:
            ok, diagnostics = replay_trace_with_diagnostics(trace)
            if ok:
                print("replay ok")
                return 0
            for d in diagnostics:
                print(d.message())
            return 1
        ok, msg = replay_trace(trace)
        print(msg)
        return 0 if ok else 1

    return 1
