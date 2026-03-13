# L1 Twin Replay Design (v0.1)

## Goal

Replay control plane (L0) and reproduce key environment transitions in a simulator with declared fidelity. L1 requires twin configuration identity and a mapping from observed sensor events to the twin observation interface.

## Twin configuration identity

A twin config file (e.g. `twin_config.json` or `twin_config.yaml`) must capture:

- **build_hash:** Identity of the twin/simulator build (e.g. git commit or version).
- **model_params:** Key model parameters that affect outcomes (e.g. noise scales, dynamics).
- **env_seed:** Environment randomization seed so that the same L0 trace + config yields reproducible twin behavior.

## Mapping from trace to twin

- L0 trace events (especially tool calls, state transitions) are the input to the twin.
- Sensor events or observations that are logged in the trace (or referenced by content hash) map to the twin’s observation interface: each observation type has a corresponding twin API or input channel.
- The minimal L1 path: given L0 trace + twin_config, run L0 replay first; if it passes, the same event sequence is then replayed in the twin with the given config and seeds. Divergence in the twin (e.g. different state after N steps) is reported with the same diagnostic structure as L0 (seq, expected vs got).

## Minimal implementation (stub)

A minimal L1 path in the repo: (1) accept L0 trace + twin config path; (2) run L0 replay; (3) if L0 passes, validate that twin config exists and has required keys (build_hash, env_seed); (4) optionally run a no-op “twin replay” step that does not yet execute a real simulator but returns success when config is valid. This proves the contract: L1 is L0 + twin config + future simulator hook.

## Nondeterminism budget for L1

L1 tolerates environment stochasticity that is controlled by env_seed and model_params. Divergence is acceptable only within declared tolerance (e.g. distributional); otherwise the run is non-replayable at L1.
