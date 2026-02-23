# Deterministic Replay (scaffolding)

Replay is treated as a first-class primitive:
- TRACE format is deterministic enough to reconstruct state transitions
- Replay engine validates that the final state hash matches
- Nondeterminism is flagged when replay diverges

Thin-slice replay lives in `impl/src/labtrust_portfolio/replay.py`.
