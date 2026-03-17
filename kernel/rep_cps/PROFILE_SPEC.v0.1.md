# REP-CPS Profile Spec v0.1

## Scope

Timing-aware, authenticated sensitivity-sharing profile for CPS coordination. Shared variables influence scheduling/actuation only through explicit safety gates (MADS-compatible).

## Message schemas and windowing

- **Variables:** Typed coordination variables (e.g. load, availability, priority) identified by name; values are numeric or bounded enums. Schema: `REP_CPS_PROFILE.v0.1.schema.json` property `variables` (array of variable names).
- **Windowing:** Updates are valid within a time window (e.g. max age in seconds); stale updates are discarded. Rate limits (updates per variable per second) cap influence. Profile property `rate_limits`: `max_updates_per_sec`, `max_age_sec`.

## Rate limits and provenance

- **Rate limits:** Each variable has a maximum update rate; aggregator rejects or throttles excess. Prevents burst dominance.
- **Provenance:** Each update carries source identity (agent_id) and timestamp. Auth layer verifies identity; replay of old updates is rejected (timestamp within window, monotonic or nonce). Profile property `auth`: `require_provenance`, `reject_replay`.

## Threat model

- **Byzantine agents:** A subset of agents may send arbitrary values. Aggregation must bound their influence (e.g. robust to up to f faulty agents).
- **Sybils:** Multiple fake identities; mitigated by authenticated channels and rate limits per identity.
- **Spoofing:** Impersonation; mitigated by auth hooks (signature or attested identity).
- **Replay:** Old messages replayed; mitigated by timestamps/nonces and windowing.

## Robust aggregation

- **Aggregation:** Function that combines updates from multiple agents into a single value per variable. Robust form: e.g. trimmed mean, median, or Byzantine-resistant rule (e.g. discard extreme quartiles). Profile property `aggregation`: `method` (e.g. "trimmed_mean", "median"), `trim_fraction` (for trimmed mean). In the evaluated harness, robust aggregation reduces observed compromise-induced bias relative to naive averaging; acceptance test: with f compromised agents sending extremes, aggregate bias is reduced vs naive mean.

## Safety-gate integration

- **Safety gate:** Protocol state (aggregated variables) does not directly actuate. It feeds into a Gatekeeper/Monitor that checks MADS admissibility (evidence, conformance) before any actuation or PONR transition. Profile property `safety_gate`: `mads_tier_required` (e.g. 2), `gate_before_actuation`.

## Reference implementation

- **Aggregator:** `impl` module `rep_cps.aggregate()` with rate limiting and robust aggregation.
- **Attack harness:** `rep_cps.compromised_updates()` or harness that injects Byzantine-style updates for testing.
- **MAESTRO adapter:** Adapter that runs a scenario while executing the REP-CPS protocol (aggregation steps, safety-gate check) and produces TRACE + MAESTRO_REPORT.
