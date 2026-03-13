# Part 11 Style Audit Trail Alignment (Appendix)

This appendix maps portfolio artifacts (evidence bundle and trace) to expectations derived from **21 CFR Part 11** (Electronic Records; Electronic Signatures). See eCFR: [21 CFR Part 11](https://ecfr.federalregister.gov/current/title-21/chapter-I/subchapter-A/part-11). We do not claim compliance or certification; we show how the same run can support audit expectations.

## Part 11–derived expectations (Subpart B, 11.10)

Each requirement is mapped to an **artifact path** and **field/event** so that compliance is machine-checkable (no prose-only).

| Expectation | Source | Artifact path | Field / event |
|-------------|--------|---------------|----------------|
| Secure, computer-generated, time-stamped audit trail | 11.10(a) | trace.json; evidence_bundle.json | Trace: `events[].ts`, `events[].state_hash_after`, `final_state_hash`. Bundle: `artifacts[].sha256`. |
| Record date and time of operator entries and actions that create, modify, or delete electronic records | 11.10(a) | trace.json | `events[].ts`, `events[].type`, `events[].actor`, `events[].payload` (task_id, name). |
| Record changes shall not obscure previously recorded information | 11.10(a) | trace.json (append-only); evidence_bundle redaction_manifest | Event order and `events[].ts` preserved; redaction replaces payload with `_redacted_ref` only. |
| Audit trail retained for a period at least as long as subject electronic records | 11.10(a) | release_manifest.json | `artifacts[]` (path, sha256); retention enforced at storage layer (deployment policy). |
| Audit trail available for agency review and copying | 11.10(a) | evidence_bundle.json; trace.json | `verification_mode`; `redaction_manifest`; files present and referenced in bundle. |

## Mapping summary

- **Secure, time-stamped:** Trace event `ts`; hashes in `state_hash_after`, `final_state_hash`, and bundle `artifacts[].sha256`.
- **Non-obscuring:** Append-only trace; E2 redaction does not remove event order or timestamps.
- **Operational actions:** Event types (e.g. task_start, task_end, coordination_message, fault_injected) and payloads record what was done, by whom (actor_id), and when (ts).

This alignment supports use of portfolio outputs in environments that follow Part 11–style expectations; it is not a certification or legal opinion.
