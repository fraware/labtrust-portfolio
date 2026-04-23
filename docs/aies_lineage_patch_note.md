# AIES Lineage Patch Note

## Current gap

The retained boundary case `boundary_locally_consistent_cross_run_lineage` can pass when
locally consistent artifacts are assembled without a globally binding run-level lineage
identifier that is checked end-to-end across trace, bundle, and release manifest.

## Minimal closing patch

The smallest viable closure would add a single lineage binding field (for example
`run_lineage_id`) that is:

- emitted into trace and evidence bundle at run creation,
- included in release manifest references,
- required to match in `full_review`.

## Affected code paths

- `impl/src/labtrust_portfolio/assurance_review_pipeline.py`
- `impl/src/labtrust_portfolio/assurance_negative_controls.py`
- relevant run/export scripts that emit manifests
- regression tests for boundary cases and failure reason mapping

## Scope/risk assessment

This touches core artifact schemas and production of existing run outputs, so it is not a
one-day low-risk patch for this AIES packaging sprint.

## Sprint decision

Deferred in this sprint. We keep the boundary limitation explicit in paper-facing exports
and maintain transparent reporting of boundary-case misses.

