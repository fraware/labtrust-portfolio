# assurance_eval_aies

AIES 2026 paper-facing assurance artifact bundle.

## Main-text artifacts
- `baseline_summary.json` (primary institutional baseline: lab_profile_v0)
- `institutional_positive_summary.json` (lab + warehouse portability)
- `negative_summary.json` (ablation/family/failure summaries)
- `tables/baseline_table.tex`, `tables/portability_table.tex`
- `tables/negative_ablation_table.tex`, `tables/failure_family_table.tex`

## Supplement / proxy bucket
- `proxy_stress_only/traffic_medical_proxy_summary.json`

## Repro commands
```bash
export PYTHONPATH=impl/src
export LABTRUST_KERNEL_DIR=kernel
python scripts/run_assurance_eval.py --out datasets/runs/assurance_eval_aies
python scripts/run_assurance_negative_eval.py --out datasets/runs/assurance_eval_aies --submission-mode
python -c "from pathlib import Path; from labtrust_portfolio.thinslice import run_thin_slice; d=Path('datasets/runs/assurance_eval_aies/runs/lab_profile_v0_seed7'); d.mkdir(parents=True, exist_ok=True); run_thin_slice(d, seed=7, scenario_id='lab_profile_v0', drop_completion_prob=0.0)"
python scripts/export_bounded_review_packet.py --run-dir datasets/runs/assurance_eval_aies/runs/lab_profile_v0_seed7 --out datasets/runs/assurance_eval_aies/bounded_review_packet --scenario-id lab_profile_v0 --submission-mode
python scripts/export_aies_assurance_tables.py --in datasets/runs/assurance_eval_aies --out datasets/runs/assurance_eval_aies/tables
python scripts/export_aies_review_packet_figure.py --in datasets/runs/assurance_eval_aies/bounded_review_packet --out datasets/runs/assurance_eval_aies/figures
```

See `RUN_MANIFEST.json` for provenance and checksums.
