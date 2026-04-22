# P0 Repro Run (Frozen)

Environment used:

- OS: Windows (PowerShell)
- `PYTHONPATH=impl/src`
- `LABTRUST_KERNEL_DIR=kernel`

Fresh clone used for reproducibility hardening:

- `git clone "c:\Users\mateo\labtrust-portfolio" "c:\Users\mateo\labtrust-portfolio-clean"`
- In clone:
  - `python scripts/replay_link_e3.py --runs 20 --scenarios lab_profile_v0,toy_lab_v0 --standalone-verifier --out datasets/runs/e3_summary.json`
  - `python scripts/run_p0_e4_controller_matrix.py --seeds 20 --scenarios toy_lab_v0,lab_profile_v0,rep_cps_scheduling_v0 --regimes baseline,moderate,stress,coordination_shock --out datasets/runs/p0_e4_controller_matrix.json`

Key fact checks executed:

- E3 strong replay: `all_strong_match == true`
- Baseline raw invariance: baseline `raw_conformance_rate == 1.0` for both controllers
- Divergence regime present: `coordination_shock + rep_cps_scheduling_v0` shows controller separation in diagnostics exports
- Claim matrix guardrail: `raw universal invariance across all regimes` remains `not supported`

Frozen artifact regeneration in working repo (for committed outputs):

- `python scripts/replay_link_e3.py --runs 20 --scenarios lab_profile_v0,toy_lab_v0 --standalone-verifier --out datasets/runs/e3_summary.json`
- `python scripts/run_p0_e4_controller_matrix.py --seeds 20 --scenarios toy_lab_v0,lab_profile_v0,rep_cps_scheduling_v0 --regimes baseline,moderate,stress,coordination_shock --out datasets/runs/p0_e4_controller_matrix.json`

Paper-facing exports:

- `python scripts/export_p0_table3.py --e3 datasets/runs/e3_summary.json --e4-raw-summary datasets/runs/p0_e4_raw_summary.json --e4-normalized-summary datasets/runs/p0_e4_normalized_summary.json`
- `python scripts/export_p0_e4_controller_divergence_table.py`
- `python scripts/export_p0_e4_claim_matrix.py`

Reviewer-facing test bundle:

- `python -m pytest tests/test_p0_e4_raw_preservation.py tests/test_p0_e4_summary_recompute.py tests/test_p0_e4_strong_replay_equivalence.py tests/test_p0_e4_zero_latency_semantics.py -q`
