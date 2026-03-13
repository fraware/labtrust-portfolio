# Generated tables for P8 (P8_MetaCoordination)

## From export_meta_tables.py

# Table 1 - Comparison (fixed vs meta vs naive)

Source: comparison.json. Run meta_eval.py --run-naive to regenerate.

| Regime | tasks_completed_mean | collapse_count | regime_switch_count_total |
|--------|---------------------|----------------|---------------------------|
| fixed (Centralized) | 3.00 | 1 | - |
| meta_controller | 3.00 | 1 | 6 |
| naive (fault_threshold=0) | 3.00 | - | 6 |

