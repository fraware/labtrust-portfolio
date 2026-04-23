# AIES 2026 Assurance Sprint

This sprint packages the assurance-pack work for an AIES 2026 submission with the
institutional accountability framing:

- Primary institutional case: `lab_profile_v0`
- Portability case: `warehouse_v0`
- Negative controls retained and exported cleanly
- Traffic/medical proxy retained only under `proxy_stress_only`

## Output root

- `datasets/runs/assurance_eval_aies/`

## Main scripts

- `scripts/run_assurance_eval.py --out datasets/runs/assurance_eval_aies`
- `scripts/run_assurance_negative_eval.py --out datasets/runs/assurance_eval_aies --submission-mode`
- `python -c "from pathlib import Path; from labtrust_portfolio.thinslice import run_thin_slice; d=Path('datasets/runs/assurance_eval_aies/runs/lab_profile_v0_seed7'); d.mkdir(parents=True, exist_ok=True); run_thin_slice(d, seed=7, scenario_id='lab_profile_v0', drop_completion_prob=0.0)"`
- `scripts/export_bounded_review_packet.py --run-dir <run_dir> --out datasets/runs/assurance_eval_aies/bounded_review_packet`
- `scripts/export_aies_assurance_tables.py --in datasets/runs/assurance_eval_aies --out datasets/runs/assurance_eval_aies/tables`
- `scripts/export_aies_review_packet_figure.py --in datasets/runs/assurance_eval_aies/bounded_review_packet --out datasets/runs/assurance_eval_aies/figures`

## Paper-facing outputs

- `baseline_summary.json`
- `institutional_positive_summary.json`
- `negative_summary.json`
- `bounded_review_packet/`
- `tables/baseline_table.tex`
- `tables/portability_table.tex`
- `tables/negative_ablation_table.tex`
- `tables/failure_family_table.tex`
- `tables/negative_failure_families.csv`
- `tables/negative_failure_reasons.csv`
- `figures/review_packet_figure.mmd` (plus png/pdf when renderer is available)
- `RUN_MANIFEST.json`
- `README.md`

## Main-text vs supplement

- Main-text defaults: `lab_profile_v0` and `warehouse_v0` tables.
- Supplement/proxy bucket: `proxy_stress_only/traffic_medical_proxy_summary.json`.

