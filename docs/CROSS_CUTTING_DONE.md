# Cross-cutting work: definition of done

When all items below are checked, cross-cutting work is complete and per-paper work can start.

- [x] **Kernel validation** — `scripts/validate_kernel.py` passes and is tested (schema count, VERSION reported).
- [x] **Profile load** — Lab profile loads from `profiles/lab/v0.1/` and is tested; `load-profile` CLI runs in CI.
- [x] **Thin-slice in CI** — Thin-slice runs in CI; outputs validate against kernel schemas; conformance check passes.
- [x] **Release script** — `release-dataset` (CLI or script) produces a valid release from a run; tested and run in CI.
- [x] **Conformance checker** — `check-conformance` implemented and tested (pass on valid run; fail on missing artifact or replay failure).
- [x] **Integration contracts** — `docs/INTEGRATION_CONTRACTS.md` and `docs/CONDITIONAL_TRIGGERS.md` written; README and PORTFOLIO_BOARD link to them.
- [x] **README and docs** — README includes cross-cutting workflow and evaluation pipelines; `docs/VALIDATING_A_RUN.md` describes validate-run flow; `docs/EVALS_RUNBOOK.md` and `docs/EVAL_RESULTS_INTERPRETATION.md` document evals and results.

Per-paper eval scripts (P0–P8) write to `datasets/runs/`; CI runs them in the `conditional-evals` job. Portfolio-level release: `datasets/releases/portfolio_v0.1/` (p0_conformance_summary.json from build_p0_conformance_summary.py). Evidence bundle schema requires `verification_mode`; conformance Tier 2 is conditional on verification_mode for replay. Conditional papers (P2, P5, P6, P8) document trigger proofs in CONDITIONAL_TRIGGERS.md; eval outputs include success_criteria_met.trigger_met. Run the test suite and CI to confirm green.
