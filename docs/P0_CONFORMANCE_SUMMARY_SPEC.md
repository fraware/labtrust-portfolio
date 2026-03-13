# P0 conformance summary (p0_conformance_summary.json)

Produced by `scripts/build_p0_conformance_summary.py`. Aggregates conformance over all P0 runs (e.g. E3 run dirs under `datasets/runs/e3/<scenario>/seed_<n>/`, E2 redaction demo).

## Schema (informal)

| Field | Type | Description |
|-------|------|-------------|
| version | string | "0.1" |
| source | string | "p0_conformance_summary" |
| runs_count | number | Number of runs aggregated |
| runs | array | One entry per run |
| runs[].run_id | string | Identifier (e.g. e3_toy_lab_v0_seed_1, e2_redaction_demo) |
| runs[].run_dir | string | Relative path to run directory |
| runs[].tier | number | Conformance tier (1, 2, or 3) |
| runs[].pass | boolean | Tier pass/fail |
| runs[].reasons | array of strings | Failure reasons (empty if pass) |

## Location

Written to `datasets/releases/portfolio_v0.1/p0_conformance_summary.json` by default. The portfolio release dir is created if missing.
