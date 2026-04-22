# Generated tables for P8 (P8_MetaCoordination)

## From export_meta_tables.py

# Table 1 - Comparison (fixed vs meta vs naive)

Source: comparison.json. Run meta_eval.py --run-naive to regenerate.

| Regime | tasks_completed_mean | collapse_count | regime_switch_count_total |
|--------|---------------------|----------------|---------------------------|
| fixed (Centralized) | 2.70 | 1 | - |
| meta_controller | 3.45 | 0 | 8 |
| naive (fault_threshold=0) | 3.85 | 0 | 17 |

## Recovery latency proxy and explicit safety counts

`time_to_recovery_ms_mean` is from MAESTRO metrics on the evaluated regime.

| Arm | time_to_recovery_ms_mean | ponr_violation_count_total | safety_violation_count_total |
|-----|---------------------------|------------------------------|------------------------------|
| fixed (Centralized) | - | 0 | 0 |
| meta_controller | 106.04 | 0 | 0 |

## Collapse outcome interpretation (paired seeds)

- **Non-inferior on counts (meta <= fixed):** `meta_non_worse_collapse` = True
- **Strict improvement (meta < fixed):** `meta_strictly_reduces_collapse` = True
- **McNemar (discordant pairs only) p (two-sided):** 1.0
- **Wilson 95% CI - fixed collapse rate:** [0.008881, 0.236136]
- **Wilson 95% CI - meta collapse rate:** [0.0, 0.16113]

## Stress selection (non-vacuous runs)

- **rule_id:** `largest_drop_prob_with_any_collapse`
- **chosen_drop_completion_prob:** 0.35
- **source:** `datasets/runs/meta_eval/collapse_sweep.json`

