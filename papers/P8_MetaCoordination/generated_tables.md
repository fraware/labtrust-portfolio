# Generated tables for P8 (P8_MetaCoordination)

## From export_meta_tables.py

Regenerate primary (regime_stress_v0): `python scripts/export_meta_tables.py --comparison datasets/runs/meta_eval/comparison.json`  
Secondary scenario: `python scripts/export_meta_tables.py --comparison datasets/runs/meta_eval/scenario_regime_stress_v1/comparison.json`  
After `run_paper_experiments.py --paper P8`, both comparison files exist. The exporter also prints **Collapse outcome interpretation** and **Stress selection** blocks when present.

# Table 1 - Comparison (fixed vs meta vs naive)

Source: comparison.json. Run meta_eval.py --run-naive to regenerate.

| Regime | tasks_completed_mean | collapse_count | regime_switch_count_total |
|--------|---------------------|----------------|---------------------------|
| fixed (Centralized) | 3.40 | 1 | - |
| meta_controller | 3.40 | 1 | 8 |
| naive (fault_threshold=0) | 3.40 | 1 | 8 |

