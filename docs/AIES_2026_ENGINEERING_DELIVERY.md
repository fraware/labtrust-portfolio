# AIES 2026 Engineering Delivery

## what was changed

- Added bounded external review packet export:
  - `scripts/export_bounded_review_packet.py`
- Added AIES-focused assurance table/summary exporter:
  - `scripts/export_aies_assurance_tables.py`
- Added AIES review-packet figure exporter:
  - `scripts/export_aies_review_packet_figure.py`
- Added sprint documentation:
  - `docs/AIES_2026_ASSURANCE_SPRINT.md`
  - `docs/aies_lineage_patch_note.md`
- Added fast integration coverage:
  - `tests/test_assurance_aies_exports.py`
- Generated AIES bundle under:
  - `datasets/runs/assurance_eval_aies/`

## what commands reproduce it

```bash
export PYTHONPATH=impl/src
export LABTRUST_KERNEL_DIR=kernel

python scripts/run_assurance_eval.py --out datasets/runs/assurance_eval_aies
python scripts/run_assurance_negative_eval.py --out datasets/runs/assurance_eval_aies --submission-mode
python -c "from pathlib import Path; from labtrust_portfolio.thinslice import run_thin_slice; d=Path('datasets/runs/assurance_eval_aies/runs/lab_profile_v0_seed7'); d.mkdir(parents=True, exist_ok=True); run_thin_slice(d, seed=7, scenario_id='lab_profile_v0', drop_completion_prob=0.0)"
python scripts/export_bounded_review_packet.py --run-dir datasets/runs/assurance_eval_aies/runs/lab_profile_v0_seed7 --out datasets/runs/assurance_eval_aies/bounded_review_packet --scenario-id lab_profile_v0
python scripts/export_aies_assurance_tables.py --in datasets/runs/assurance_eval_aies --out datasets/runs/assurance_eval_aies/tables
python scripts/export_aies_review_packet_figure.py --in datasets/runs/assurance_eval_aies/bounded_review_packet --out datasets/runs/assurance_eval_aies/figures
```

## what metrics changed relative to prior assurance eval

- This sprint does not change checker semantics; it repackages outputs for AIES framing.
- Main textual emphasis moved to:
  - baseline institutional row (`lab_profile_v0`)
  - portability row (`warehouse_v0`)
- Traffic/medical proxy moved to:
  - `proxy_stress_only/traffic_medical_proxy_summary.json`

## whether the lineage patch was attempted

- Feasibility was analyzed and documented.
- Patch was not implemented in this sprint due to cross-cutting schema/runtime impact.
- See: `docs/aies_lineage_patch_note.md`.

## what main-text artifacts are now ready

- `datasets/runs/assurance_eval_aies/baseline_summary.json`
- `datasets/runs/assurance_eval_aies/institutional_positive_summary.json`
- `datasets/runs/assurance_eval_aies/negative_summary.json`
- `datasets/runs/assurance_eval_aies/tables/baseline_table.tex`
- `datasets/runs/assurance_eval_aies/tables/portability_table.tex`
- `datasets/runs/assurance_eval_aies/tables/negative_ablation_table.tex`
- `datasets/runs/assurance_eval_aies/tables/failure_family_table.tex`
- `datasets/runs/assurance_eval_aies/figures/review_packet_figure.mmd`

