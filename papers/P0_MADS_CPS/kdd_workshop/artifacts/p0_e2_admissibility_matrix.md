## Table 2 ù E2 admissibility matrix

| Predicate | Full mode | Evaluator mode | Regulator mode | Public/redacted mode |
|-----------|-----------|----------------|----------------|----------------------|
| schema_validation_ok | yes | yes | yes | yes |
| integrity_ok (hashes) | yes | yes | yes | yes |
| replay_ok (L0/L1) | yes | yes (full trace); no (redacted) | yes (full); no (redacted) | no (redacted); N/A (public, replay not required) |
| PONR coverage | yes | yes (full); N/A (redacted, structure only) | yes (full); N/A (redacted) | N/A (redacted) |

Full mode: all artifacts present and unredacted; all predicates checkable. Evaluator and regulator: when trace is redacted, payloads are content-addressed refs; replay is not run, so replay_ok is false; schema and integrity remain checkable. Public/redacted: when redacted, same as evaluator redacted; when public and unredacted, replay is not required by mode so replay_ok may be N/A. See kernel/mads/VERIFICATION_MODES.v0.1.md.
