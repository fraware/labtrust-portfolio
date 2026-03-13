# Kernel Changelog

Breaking changes to kernel schemas or semantics require a schema version bump and an entry here.

## Version bump rule

- **Breaking change:** Any change that invalidates existing valid instances or changes the meaning of a field. Update the schema `$id` version segment (e.g. `v0.1` → `v0.2`), add an entry below, and update `kernel/VERSION` if the kernel version is bumped.
- **Non-breaking:** Additive changes (new optional fields, new schemas) may be documented here without a version bump.

## v0.1 (current)

- Initial kernel: TRACE, MAESTRO_REPORT, EVIDENCE_BUNDLE, RELEASE_MANIFEST, COORD_CONTRACT, REP_CPS_PROFILE, TYPED_PLAN, ASSURANCE_PACK.
- Supporting docs: VERIFICATION_MODES.v0.1.md, REPLAY_LEVELS.v0.1.md, OPC_UA_LADS_MAPPING.v0.1.md.
