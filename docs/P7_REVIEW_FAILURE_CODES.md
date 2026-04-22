# P7 review failure codes (stable identifiers)

These codes appear in `review_assurance_run.py` / `assurance_review_pipeline` JSON output and in `negative_results.json` rows. They support **failure localization** (Q3: attribution) for governance-evidence discrimination experiments.

| Code | Meaning |
|------|---------|
| `PACK_SCHEMA_INVALID` | Pack JSON fails schema or structural rules. |
| `CONTROL_REFERENCE_MISSING` | Hazard references missing or unknown control id. |
| `CONTROL_EVIDENCE_TYPES_MISSING` | Control has empty `evidence_artifact_types`. |
| `PROFILE_PONR_UNCOVERED` | Profile `ponrs.yaml` id not present on any hazard `ponr_ids`. |
| `EVIDENCE_MAP_INCONSISTENT` | `evidence_map` entry for a hazard omits a declared control. |
| `TRACE_MISSING` | `trace.json` absent when required. |
| `BUNDLE_MISSING` | `evidence_bundle.json` absent when required. |
| `MAESTRO_MISSING` | `maestro_report.json` absent when required. |
| `RELEASE_MANIFEST_MISSING` | `release_manifest.json` absent when required. |
| `TRACE_SCHEMA_INVALID` | Trace present but not valid JSON or fails trace schema. |
| `BUNDLE_SCHEMA_INVALID` | Bundle present but fails evidence-bundle schema. |
| `PONR_MISSING` | Required PONR-aligned task names absent from trace for scenario. |
| `SCENARIO_PACK_MISMATCH` | Trace `scenario_id` does not match declared review scenario. |
| `PROVENANCE_MISMATCH` | Bundle or release manifest SHA256 does not match file on disk. |
| `INCOMPLETE_EVIDENCE` | Control declares artifact types not all present in the run. |
| `UNKNOWN_REVIEW_FAILURE` | Catch-all for unexpected validation errors. |

**Non-claim:** Codes describe mechanical checks only, not legal sufficiency or regulatory compliance.
