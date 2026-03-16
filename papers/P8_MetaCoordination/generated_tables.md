# Generated tables for P8 (P8_MetaCoordination)

**How to read:** P8 contributes auditability (regime_switch in trace with reason) and PONR invariance; when non-vacuous, meta reduces collapse; with --fallback-adapter retry_heavy, two real coordination algorithms are compared. Table 1: fixed vs meta vs naive from comparison.json; run meta_eval.py --run-naive (publishable: --non-vacuous, optionally --fallback-adapter retry_heavy).

## From export_meta_tables.py

# Table 1 - Comparison (fixed vs meta vs naive)

Source: comparison.json. Run meta_eval.py --run-naive to regenerate.

| Regime | tasks_completed_mean | collapse_count | regime_switch_count_total |
|--------|---------------------|----------------|---------------------------|
| fixed (Centralized) | 3.00 | 1 | - |
| meta_controller | 3.00 | 1 | 6 |
| naive (fault_threshold=0) | 3.00 | - | 6 |

