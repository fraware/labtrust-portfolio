# Generated tables for P7 (P7_StandardsMapping)

**How to read:** run_assurance_eval runs over three profiles (lab v0.1, warehouse v0.1, medical v0.1); results.json includes per_profile. Standards mapping: [docs/P7_STANDARDS_MAPPING.md](../../docs/P7_STANDARDS_MAPPING.md). Regenerate: `python scripts/run_assurance_eval.py --out datasets/runs/assurance_eval` then `python scripts/export_assurance_tables.py --results datasets/runs/assurance_eval/results.json`.

## From export_assurance_tables.py

# Table 1 — Mapping and review results

| mapping_check_ok | ponr_coverage_ok | review_exit_ok | ponr_events_count | ponr_coverage_ratio | control_coverage_ratio |
|------------------|------------------|---------------|-------------------|---------------------|-------------------------|
| yes | yes | yes | 4 | 1.00 | 1.00 |

# Table 2 — Per-scenario review (kernel PONR)

| scenario_id | exit_ok | ponr_coverage_ratio | control_coverage_ratio |
|-------------|---------|---------------------|-------------------------|
| lab_profile_v0 | yes | 1.00 | 1.00 |
| toy_lab_v0 | yes | 1.00 | 1.00 |

