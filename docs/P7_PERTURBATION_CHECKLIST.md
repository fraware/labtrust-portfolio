# P7 negative perturbations — checklist vs empirical brief

Implementation: `impl/src/labtrust_portfolio/assurance_negative_controls.py` (`perturbation_id` = `case_id`). Eval order: `all_case_ids()`.

## Family A — pack structure

| Brief name | `perturbation_id` | Status |
|------------|-------------------|--------|
| hazard with no control_ids | `hazard_missing_control_ids` | implemented |
| hazard references nonexistent control | `hazard_references_unknown_control` | implemented |
| control with empty evidence_artifact_types | `control_missing_evidence_types` | implemented |
| pack missing required top-level field | `missing_required_field` | implemented |
| profile PONR IDs not on hazards | `ponr_ids_missing_for_profile` | implemented |
| evidence map inconsistent with declared controls | `evidence_map_inconsistent` | implemented |

## Family B — artifact admissibility

| Brief name | `perturbation_id` | Status |
|------------|-------------------|--------|
| missing trace | `missing_trace_file` | implemented |
| missing bundle | `missing_bundle_file` | implemented |
| malformed / invalid trace JSON | `trace_schema_invalid` | implemented |
| invalid bundle vs schema | `bundle_schema_invalid` | implemented |
| truncated trace JSON | `trace_truncated` | implemented |
| required bundle field removed | `bundle_corrupted_field` | implemented |
| broken trace hash in bundle | `bundle_broken_trace_hash` | implemented |

## Family C — scenario consistency

| Brief name | `perturbation_id` | Status |
|------------|-------------------|--------|
| wrong pack for scenario / run | `wrong_pack_for_scenario` | implemented |
| trace missing required PONR task | `missing_required_ponr_event` | implemented (strips `disposition_commit`) |
| trace from other scenario (wrong scenario_id) | `trace_from_other_scenario` | **merged into eval suite** — same materialization as `swapped_scenario_id_in_trace`; only `swapped_scenario_id_in_trace` appears in `all_case_ids()` to avoid duplicate rows. `materialize_case(..., "trace_from_other_scenario", ...)` is still supported. |
| wrong required task name (misnamed PONR) | `wrong_required_task_name` | implemented |
| trace from run A + bundle from run B | `cross_run_trace_bundle_swap` | implemented |
| valid trace + stale bundle from other seed | `stale_bundle_reused` | **merged** with `cross_run_trace_bundle_swap` (same swap-from-alt-seed materialization; kept as separate id for brief traceability) |

## Family D — adversarial / misleading

| Brief name | `perturbation_id` | Status |
|------------|-------------------|--------|
| remove final commitment event, structure valid | `remove_final_commit_event_keep_structure` | implemented (same strip as `missing_required_ponr_event`; family D vs C) |
| release manifest mismatched artifact SHA | `manifest_points_to_foreign_artifact` | implemented |
| partial / impossible control evidence claim | `partial_control_omission` | implemented |
| well-formed artifacts, pack over-claims evidence | `wellformed_but_incomplete_evidence` | implemented (pack adds `conformance` type; reviewer `evidence_present` does not treat it as satisfied) |

## Positive control

| Role | `perturbation_id` |
|------|-------------------|
| valid lab path | `positive_valid_lab` |

## Notes

- **Merged / duplicate semantics:** `stale_bundle_reused` and `cross_run_trace_bundle_swap` share the same swap-from-alternate-seed implementation but remain separate `perturbation_id` rows for brief traceability. `trace_from_other_scenario` is not duplicated in `all_case_ids()` (see Family C table).
- **Failure codes:** [docs/P7_REVIEW_FAILURE_CODES.md](P7_REVIEW_FAILURE_CODES.md).
