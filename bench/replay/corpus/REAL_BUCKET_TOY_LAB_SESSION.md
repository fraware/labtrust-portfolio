# Real ingest: `real_bucket_toy_lab_session`

## Source system class

TRACE emitted by the LabTrust thin-slice harness (`labtrust_portfolio.thinslice.run_thin_slice`) on a developer workstation, scenario `toy_lab_v0`, as part of the E2 redaction demo pipeline (`scripts/e2_redaction_demo.py`). This is a real execution of the control-plane trace generator, not a hand-authored synthetic corpus trap.

## Mapping to TRACE

Events were already in TRACE v0.1 shape (`events[]` with `seq`, `ts`, `type`, `actor`, `payload`, `state_hash_after`). No structural transformation beyond copying the export into the corpus and freezing it as a lane.

## Redaction

- `run_id` replaced with `run_redacted_for_publication` (opaque placeholder). No hostnames or user paths were present in the JSON.

## Preserved fields

Full event sequence, timestamps, actor identifiers (`scheduler`, `agent_1`, `lab_device_1`, `supervisor`), task identifiers, and all `state_hash_after` values as produced by the harness.

## `state_hash_after`

Native: computed by the harness state machine (`state_hash(state)` after each event), not reconstructed post hoc.

## Expected outcome

Pass-only: `expected_replay_ok: true`. No `expected_divergence_at_seq` (not used for seq-grounded localization claims on this lane).
