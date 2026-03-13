# Experiments and Limitations

This document summarizes what the portfolio evaluation does (strengthened experiments) and what it does not do (intentional scope limits). See [PLAN_STRENGTHEN_EXPERIMENTS.md](PLAN_STRENGTHEN_EXPERIMENTS.md) for the full improvement plan and [REPORTING_STANDARD.md](REPORTING_STANDARD.md) for publishable result requirements.

## What we do

- **Sample size and run manifest:** Minimum 20 seeds for publishable tables (10 allowed for minimal/CI); run manifest in each summary JSON records seeds, seed_count, scenario(s), fault settings, and script. Use 30 for sensitivity. See [REPORTING_STANDARD.md](REPORTING_STANDARD.md).
- **Statistics:** Mean, stdev, 95% CI (t-interval or bootstrap) when n >= 2; p95/p99 where applicable (latency, replay overhead).
- **Comparison stats and power:** When two conditions are compared (fixed vs meta, robust vs naive, baseline vs feature), summary JSONs include excellence_metrics: difference_mean, difference_ci95, difference_ci_width, optional paired_t_p_value, power_post_hoc, alpha. Implemented in meta_eval, rep_cps_eval, scaling_heldout_eval via `labtrust_portfolio.stats`. Optional sensitivity sweep at N=10, 20, 30 via `scripts/sensitivity_seed_sweep.py`.
- **Multi-scenario and fault coverage:** Publishable defaults use multiple scenarios (e.g. toy_lab_v0, lab_profile_v0) and fault sweeps where the paper makes a general claim; P4 supports --all-scenarios and includes RetryHeavy adapter (architecturally distinct from Centralized/Blackboard); P5 uses --fault-mix; P8 supports --stress-preset high and very_high, and optional --fallback-adapter retry_heavy for two-regime comparison; P7 runs over three assurance profiles (lab, warehouse, medical). P2 multi-step aggregation reports convergence (steps_to_convergence, convergence_achieved_rate) when --aggregation-steps > 1; Table 4 via export_rep_cps_convergence_table.py.
- **Expanded corpora:** P1 contracts: 7 corpus sequences (bench/contracts/README.md); P3 replay: corpus traps from bench/replay/corpus (e.g. nondeterminism, reorder, timestamp_reorder, hash_mismatch_trap); L1 stub and L1 twin (--l1-twin: deterministic re-run of control-plane state machine); L2 aspirational with design subsection (REPLAY_LEVELS); full corpus table: export_replay_corpus_table.py; P6: 8 red-team, 4 confusable deputy, and jailbreak-style cases (impl/.../llm_planning.py); validator v0.2 (allow_list + safe_args). **Corpus expansion:** Documented protocol for adding contract sequences, replay traps, and red-team/confusable deputy cases; run_manifest records corpus size (corpus_sequence_count, replay_trap_count, red_team_case_count, confusable_deputy_case_count). Optional parameterized generator: `scripts/generate_contract_corpus.py` (N-writer contention). See [CORPUS_EXPANSION.md](CORPUS_EXPANSION.md).
- **Reproducibility:** LABTRUST_FIXED_SEED (env) can be set so stochastic steps (e.g. bootstrap) use a fixed seed; run_manifest still records the seeds used per run. Same seed list + same script yields bit-identical traces where the pipeline is deterministic.
- **Real LLM (optional):** When .env at repo root contains API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.), P6 and related evals support an optional real-LLM mode (e.g. --real-llm) for plan generation or red-team prompts. Synthetic plans remain the default for CI and keyless environments. See Phase 7 in PLAN_STRENGTHEN_EXPERIMENTS.md.
- **Formal verification:** At least one Lean wedge (W3 evidence-bundle verifier; then W1 Gatekeeper/PONR, W2 contract validator) is implemented under formal/lean/ so selected kernels have machine-checked proofs. See formal/lean/README.md and Phase 8 in PLAN_STRENGTHEN_EXPERIMENTS.md.

## What we do not do (and why)

- **Real hardware:** Physical execution is out of scope. All execution is thin-slice simulation (synthetic traces, MAESTRO adapters, replay from trace). Documented in each paper's Limitations where relevant.
- **Full-system formal verification:** We do not verify the autonomous lab end-to-end or the LLM planner's correctness. We verify selected kernels (evidence bundle, gatekeeper, contract validator) as Lean wedges; see formal/lean/README.md.
- **Unbounded threat model:** Fault sets and red-team cases are fixed corpora; we do not claim coverage of all possible attacks or faults. Threat model and fault set are bounded and stated in the papers.
- **Certification claims:** Standards-mapping (P7) is a translation layer only; no certification claim. Other papers state containment, reproducibility, and evidence quality. **Per-paper limitations:** Scope and overclaim checks are stated in each paper's Limitations section: `papers/P0_MADS-CPS/DRAFT.md` through `papers/P8_MetaCoordination/DRAFT.md` (search for "Limitations").

## Formal verification (what is proved)

- **Implemented wedges:** See [formal/lean/README.md](../formal/lean/README.md) for which wedges are implemented and how to build (`lake build` from `formal/lean/`). **W1 (Gatekeeper):** fail-closed theorems proved in `Labtrust/W1Gatekeeper.lean`. **W2 (contract validator):** determinism proved in `Labtrust/W2Contract.lean`. **W3 (evidence bundle verifier):** required artifact presence, schema validity, hash format; soundness lemmas in `Labtrust/W3EvidenceBundle.lean` (proofs use sorry pending Std). Python test harness `tests/test_w3_evidence_bundle.py` aligns impl to W3 spec.
- **Not proved:** End-to-end system correctness; LLM planner output correctness; physical device behavior.

## References

- Reporting: [REPORTING_STANDARD.md](REPORTING_STANDARD.md), [STANDARDS_OF_EXCELLENCE.md](STANDARDS_OF_EXCELLENCE.md).
- Per-paper limitations: papers/P0_MADS-CPS/DRAFT.md through papers/P8_MetaCoordination/DRAFT.md (Limitations sections).
- Strengthen plan: [PLAN_STRENGTHEN_EXPERIMENTS.md](PLAN_STRENGTHEN_EXPERIMENTS.md).
