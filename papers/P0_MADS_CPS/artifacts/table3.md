Refresh stamp: 2026-04-22T11:30:15Z

## Table 3a - E3 replay-link (strong)

E3 row uses strong replay fields only (`all_strong_match` required).

| Scenario | Controller | Seeds | Replay match rate | p95 latency mean (95% CI) ms | Conformance rate |
|----------|-------------|-------|-------------------|------------------------------|------------------|
| lab_profile_v0 | thinslice | 20 | 1.00 | 50.37 [40.48, 60.27] | 1.00 |
| toy_lab_v0 | thinslice | 20 | 1.00 | 35.37 [27.11, 43.62] | 1.00 |

## Table 3b - E4 raw vs normalized controller invariance

Replay rate is strong replay from controller-matrix summaries.

| Scenario | Regime | Controller | Seeds | Raw conformance | Normalized conformance | Strong replay | p95 latency mean (95% CI) ms |
|----------|--------|------------|-------|-----------------|------------------------|---------------|------------------------------|
| lab_profile_v0 | baseline | centralized | 20 | 1.00 | 1.00 | 1.00 | 50.37 [40.02, 60.73] |
| lab_profile_v0 | baseline | rep_cps | 20 | 1.00 | 1.00 | 1.00 | 50.37 [40.02, 60.73] |
| lab_profile_v0 | coordination_shock | centralized | 20 | 0.85 | 0.85 | 0.85 | 156.47 [127.09, 185.85] |
| lab_profile_v0 | coordination_shock | rep_cps | 20 | 0.85 | 0.85 | 0.85 | 156.47 [127.09, 185.85] |
| lab_profile_v0 | moderate | centralized | 20 | 1.00 | 1.00 | 1.00 | 39.86 [27.99, 51.74] |
| lab_profile_v0 | moderate | rep_cps | 20 | 1.00 | 1.00 | 1.00 | 39.86 [27.99, 51.74] |
| lab_profile_v0 | stress | centralized | 20 | 0.85 | 0.85 | 0.85 | 66.56 [48.40, 84.71] |
| lab_profile_v0 | stress | rep_cps | 20 | 0.85 | 0.85 | 0.85 | 66.56 [48.40, 84.71] |
| rep_cps_scheduling_v0 | baseline | centralized | 20 | 1.00 | 1.00 | 1.00 | 35.37 [26.73, 44.01] |
| rep_cps_scheduling_v0 | baseline | rep_cps | 20 | 1.00 | 1.00 | 1.00 | 35.37 [26.73, 44.01] |
| rep_cps_scheduling_v0 | coordination_shock | centralized | 20 | 1.00 | 1.00 | 1.00 | 147.25 [117.01, 177.49] |
| rep_cps_scheduling_v0 | coordination_shock | rep_cps | 20 | 1.00 | 1.00 | 1.00 | 0.00 [0.00, 0.00] |
| rep_cps_scheduling_v0 | moderate | centralized | 20 | 1.00 | 1.00 | 1.00 | 34.94 [21.49, 48.40] |
| rep_cps_scheduling_v0 | moderate | rep_cps | 20 | 1.00 | 1.00 | 1.00 | 34.94 [21.49, 48.40] |
| rep_cps_scheduling_v0 | stress | centralized | 20 | 1.00 | 1.00 | 1.00 | 73.62 [48.74, 98.51] |
| rep_cps_scheduling_v0 | stress | rep_cps | 20 | 1.00 | 1.00 | 1.00 | 73.62 [48.74, 98.51] |
| toy_lab_v0 | baseline | centralized | 20 | 1.00 | 1.00 | 1.00 | 35.37 [26.73, 44.01] |
| toy_lab_v0 | baseline | rep_cps | 20 | 1.00 | 1.00 | 1.00 | 35.37 [26.73, 44.01] |
| toy_lab_v0 | coordination_shock | centralized | 20 | 1.00 | 1.00 | 1.00 | 147.25 [117.01, 177.49] |
| toy_lab_v0 | coordination_shock | rep_cps | 20 | 1.00 | 1.00 | 1.00 | 147.25 [117.01, 177.49] |
| toy_lab_v0 | moderate | centralized | 20 | 1.00 | 1.00 | 1.00 | 34.94 [21.49, 48.40] |
| toy_lab_v0 | moderate | rep_cps | 20 | 1.00 | 1.00 | 1.00 | 34.94 [21.49, 48.40] |
| toy_lab_v0 | stress | centralized | 20 | 1.00 | 1.00 | 1.00 | 73.62 [48.74, 98.51] |
| toy_lab_v0 | stress | rep_cps | 20 | 1.00 | 1.00 | 1.00 | 73.62 [48.74, 98.51] |


