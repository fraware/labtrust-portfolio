# P5 Scaling Laws: Trigger decision

**Trigger:** Proceed only after MAESTRO provides multi-scenario datasets sufficient for out-of-sample validation. Otherwise the paper reads as overclaim.

**Decision: GO (research track).** P4 has delivered multiple scenario families and MAESTRO-compatible traces; the publishable P5 grid uses **six** `real_world` scenario ids (no `toy_lab_v0` in that profile), **five** coordination regimes, agent counts **{1,2,4,8}**, and narrow fault labels **`no_drop` / `drop_005`**. Manuscript readiness still depends on **per-protocol** `success_criteria_met.trigger_met` in the frozen `heldout_results.json` files (scenario LOO can be negative while family LOO passes); see `papers/P5_ScalingLaws/DRAFT.md` and [CONDITIONAL_TRIGGERS.md](CONDITIONAL_TRIGGERS.md).

**Dependencies:** P4 (MAESTRO) multi-scenario and multi-architecture runs. Consumes MAESTRO datasets and Replay traces.
