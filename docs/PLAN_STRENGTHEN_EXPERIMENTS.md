# Plan: Strengthen experiments, simulations, and tests across the portfolio

This document is the single merged plan. It includes **Phases 1–6** (statistical rigor, scenario/fault coverage, corpus expansion, test strengthening, reporting, documentation), **Phase 7** (real LLM evaluation using API keys in `.env`), and **Phase 8** (implementation of Lean formal verification). The scope and "Out of scope" sections reflect that real LLM and formal verification are in scope; only real hardware remains out of scope.

**Implementation status:** Phases 1–8 are implemented. Current state: stats helper and comparison metrics in meta/rep_cps/scaling evals; run_manifest seed_count and LABTRUST_FIXED_SEED; multi-scenario/defaults per plan; P1 contract corpus 54+ sequences (tiered benchmark: micro, meso, stress/adversarial including cross-key interleaving, delayed release/reassignment, concurrent controller races), async stress runner (`contracts_async_stress.py`), enhanced statistical reporting (`excellence_metrics` with per_class_ci95), transport parity with confidence metrics; P3 replay corpus expanded (core traps + long-horizon + mixed-failure + benign pass + two field-style pass families; discovery from `*_trace.json`; `corpus_space_summary` and Table 1b export), P6 expanded suite (15 red-team + 6 confusable deputy + 4 jailbreak-style) with publishable real-LLM full-suite defaults; **P8** publishable dual-scenario (`regime_stress_v0` + `regime_stress_v1`), `--non-vacuous` with `stress_selection_policy`, `collapse_paired_analysis` (McNemar/Wilson), `verify_p8_meta_artifacts.py`, CI verify + v1 smoke; integration/stress tests and W3 test harness; repro_time_p4.py; real-LLM optional in P6; Lean W3 wedge and impl alignment doc. See [EXPERIMENTS_AND_LIMITATIONS.md](EXPERIMENTS_AND_LIMITATIONS.md) and [formal/lean/README.md](../formal/lean/README.md).

**Tier 2 / Raised bar (implemented):**

- **Publishable default:** 20 seeds; sensitivity at 30 seeds. Scripts default to 20; CI keeps reduced seeds for speed.
- **Power and sensitivity:** Comparison evals report difference_ci_width and power_post_hoc (post-hoc power); [sensitivity_seed_sweep.py](../scripts/sensitivity_seed_sweep.py) runs meta_eval (optional `--meta-scenario regime_stress_v0|regime_stress_v1`) or rep_cps_eval at N=10, 20, 30 and writes sensitivity_summary.json. Documented in [EVALS_RUNBOOK.md](EVALS_RUNBOOK.md).
- **Formal verification:** Three Lean wedges: W3 (evidence-bundle verifier; soundness lemmas stated, proofs use sorry pending Std); W1 (Gatekeeper fail-closed, proved); W2 (contract validator determinism, proved). Python test harness aligns impl to W3 spec.
- **Corpora:** Documented expansion protocol ([CORPUS_EXPANSION.md](CORPUS_EXPANSION.md)); run_manifest includes corpus_sequence_count, replay_trap_count, red_team_case_count; optional parameterized generator for contracts ([generate_contract_corpus.py](../scripts/generate_contract_corpus.py)).

---

## Scope and "state of the art" bar

- **Real LLM:** In scope. API keys live in [`.env`](../.env) at repo root (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENHANDS_API_KEY`). Scripts load them via `python-dotenv` (or equivalent); `.env` is in `.gitignore` and must never be committed. P6 and any other paper that benefits from LLM-backed evaluation will support an optional real-LLM mode.
- **Real hardware:** Out of scope. Physical execution remains thin-slice simulation only; document in EXPERIMENTS_AND_LIMITATIONS.
- **Formal verification:** In scope. At least one Lean wedge from [formal/lean/README.md](../formal/lean/README.md) will be implemented so that selected kernels have machine-checked proofs; multiple papers (P0, P1, P3) can reference the same wedge where applicable.

---

## Current weaknesses (summary)

The portfolio already documents many limitations in DRAFTs (synthetic traces, thin-slice only, toy scenarios, no real hardware). The main actionable weaknesses are:

- **Statistical rigor (addressed):** Previously 10 seeds was the bar; now publishable default is 20. Formal tests (t-test, bootstrap), effect-size, and power/sensitivity are implemented (see Tier 2 above).
- **Scenario and fault coverage:** Single-scenario defaults (P0 E3: toy_lab_v0; P2: one scenario in many runs); P5 multiscenario uses only 2–3 fault settings; **P8** minimal/CI runs can still be vacuous on collapse, but publishable `run_paper_experiments.py --paper P8` uses `--non-vacuous` and dual stress scenarios (see [EVALS_RUNBOOK.md](EVALS_RUNBOOK.md) P8).
- **Corpus and case diversity (addressed):** P1: 54+ contract sequences (tiered: positive controls, split-brain, stale/reorder, boundary, long-horizon, adversarial including cross-key interleaving, delayed release/reassignment, concurrent controller races; see bench/contracts/BENCHMARK_SPEC.v0.1.md); async stress testing with delay/skew/reorder sweeps; P3: replay corpus includes core traps (nondeterminism, reorder, timestamp_reorder, hash_mismatch), expanded traps (long_horizon, mixed_failure), benign perturbation pass, two field-style pass traces, plus thin-slice row in eval; `export_replay_corpus_table.py` emits Table 1 + Table 1b; P6: 15 red-team + 6 confusable deputy + 4 jailbreak-style cases (plus adaptive suite).
- **Test depth:** Integration tests use minimal seeds (1,2 or 2) and single scenario; no variance/CI assertions; no property-based or targeted stress tests beyond one P8 stress test.
- **Reporting gaps:** Regression MAE in P5 is computed but Table 2 shows "—"; effect size vs baseline not consistently in summary JSONs; no repro wall-clock or claim-confidence in artifacts.
- **Reproducibility and sensitivity:** No documented fixed RNG seed (e.g. LABTRUST_CI_SEED) used consistently; no sensitivity sweeps (e.g. seed range, fault-intensity) to show result stability.
- **Real LLM available:** P6 supports real-LLM full-suite runs (`--real-llm --real-llm-runs N --real-llm-suite full`) with per-case and overall Wilson intervals.
- **Formal proofs (addressed):** W3 evidence-bundle verifier implemented in Lean; see [formal/lean/README.md](../formal/lean/README.md) and `tests/test_w3_evidence_bundle.py`.

---

## Phase 1: Statistical rigor and reporting (portfolio-wide)

**Goal:** Every comparison (A vs B) has a reproducible effect measure and, where applicable, a simple significance check.

1. **Add a small stats helper and wire it into evals**
   - Add `impl/src/labtrust_portfolio/stats.py` (or `scripts/common_stats.py`) with:
     - `paired_t_test(a_list, b_list)` → t_stat, p_value, dof (for paired seeds).
     - `bootstrap_ci_difference(a_list, b_list, n_bootstrap=1000, ci=0.95)` → (lower, upper) for difference of means.
     - `effect_size_mean_diff(a_list, b_list)` → raw difference and, if useful, Cohen's d.
   - Extend eval summary schemas and scripts so that when two conditions are compared (e.g. fixed vs meta, robust vs naive, baseline vs model), the summary JSON includes:
     - `excellence_metrics.difference_mean`, `excellence_metrics.difference_ci95` (bootstrap or analytical),
     - optional `excellence_metrics.paired_t_p_value`, `excellence_metrics.alpha` (e.g. 0.05).
   - **Evals to update first:** [scripts/meta_eval.py](../scripts/meta_eval.py) (fixed vs meta), [scripts/rep_cps_eval.py](../scripts/rep_cps_eval.py) (robust vs naive), [scripts/scaling_heldout_eval.py](../scripts/scaling_heldout_eval.py) (baseline vs feature/regression). Document in [REPORTING_STANDARD.md](REPORTING_STANDARD.md) and [STANDARDS_OF_EXCELLENCE.md](STANDARDS_OF_EXCELLENCE.md) that these fields are the standard for "comparison" results.

2. **Publishable seed count and optional high-N mode**
   - Keep 10 as the default publishable minimum; add an optional `--seeds 20` or `--seeds 30` to key evals (e.g. meta_eval, rep_cps_eval, maestro_fault_sweep, scaling_heldout_eval) and document: "For sensitivity or rebuttals, re-run with --seeds 20."
   - In run_manifest, always record the exact seed list and seed count so reviewers can see N.

3. **Fixed RNG seed for reproducibility**
   - Document and use a single env var (e.g. `LABTRUST_FIXED_SEED`) that all stochastic scripts read when set; run_manifest still records the seeds used. Prefer seeding at process start so that "same seed list + same script" yields bit-identical traces where the pipeline is deterministic. Update [REPORTING_STANDARD.md](REPORTING_STANDARD.md) and [EVALS_RUNBOOK.md](EVALS_RUNBOOK.md).

---

## Phase 2: Scenario and fault coverage

**Goal:** Multi-scenario and multi-fault evals are the default for publishable tables where the paper makes a general claim.

4. **P0 E3 multi-scenario by default for publishable**
   - [scripts/produce_p0_e3_release.py](../scripts/produce_p0_e3_release.py): change default `--scenarios` from `toy_lab_v0` to `toy_lab_v0,lab_profile_v0` (or all 5), and document "Minimal: toy_lab_v0; publishable: toy_lab_v0,lab_profile_v0 (or more)."
   - Ensure [scripts/replay_link_e3.py](../scripts/replay_link_e3.py) and export scripts support per_scenario variance table and CI; DRAFT Table 1 (or a second table) can show per-scenario mean/stdev/CI.

5. **P2 REP-CPS multi-scenario and delay sweep**
   - Default or publishable: run rep_cps_eval with `--scenarios toy_lab_v0,lab_profile_v0` and `--delay-sweep 0,0.05,0.1,0.2` so tables and figures reflect more than one scenario and multiple delay levels. Document in DRAFT and runbook.

6. **P4 MAESTRO fault and scenario breadth**
   - [scripts/maestro_fault_sweep.py](../scripts/maestro_fault_sweep.py): add an optional `--all-scenarios` that runs over all 5 scenarios (toy_lab_v0, lab_profile_v0, warehouse_v0, traffic_v0, regime_stress_v0); keep default as current 2 for CI/speed. Add one more fault setting if useful (e.g. higher drop prob) so recovery curve has a clear trend.

7. **P5 multiscenario runs: regime_stress and fault-mix**
   - [scripts/generate_multiscenario_runs.py](../scripts/generate_multiscenario_runs.py): include `regime_stress_v0` in the scenario list when present; ensure `--fault-mix` is the recommended default for publishable. Add a third fault setting (e.g. delay or combined) so train/test diversity is higher.

8. **P8 non-vacuous collapse** *(largely implemented)*
   - Publishable path: `meta_collapse_sweep.py` + `meta_eval.py --non-vacuous` with matching `--scenario`; `run_manifest.stress_selection_policy` records the rule; `run_paper_experiments.py --paper P8` runs v0 and v1. Stress presets `--stress-preset high|very_high` exist. Remaining gap (optional): separate calibration vs evaluation seed lists; fixed RetryHeavy-as-baseline runs if the draft claims “best fixed” beyond Centralized.

---

## Phase 3: Corpus and case expansion

**Goal:** Larger, documented corpora and red-team sets so claims are not tied to a handful of hand-crafted cases.

9. **P1 Contracts corpus**
   - Add 2–3 new corpus sequences (e.g. multi-writer contention, edge-case timestamps) under [bench/contracts/corpus/](../bench/contracts/corpus/); keep JSON schema and naming convention. Document in [bench/contracts/README.md](../bench/contracts/README.md). Ensure contracts_eval and export scripts iterate over all corpus files so new sequences appear in tables.

10. **P3 Replay corpus** *(done: expanded corpus + space metrics)*
    - Checked-in pairs under [bench/replay/corpus/](../bench/replay/corpus/) include long-horizon and mixed-failure traps, benign pass, second field-style pass; regenerate JSON via [generate_p3_replay_corpus_traces.py](../scripts/generate_p3_replay_corpus_traces.py) when needed. `replay_eval.py` reports `divergence_localization_confidence`, `corpus_space_summary`, and per-trace localization/size fields; `verify_p3_replay_summary.py` enforces presence of space summary on corpus rows.

11. **P6 Red-team and confusable deputy**
    - Implemented: expanded suite in [impl/src/labtrust_portfolio/llm_planning.py](../impl/src/labtrust_portfolio/llm_planning.py) with additional red-team, confusable deputy, jailbreak-style, and ponr_gate-oriented cases; docs/eval now state total counts from artifacts.

---

## Phase 4: Test strengthening

**Goal:** Integration tests assert on variance/CI when N>=2; add a small set of stress and sensitivity tests.

12. **Integration tests: assert on variance and manifest**
    - For each paper's integration test that runs an eval script (P2, P4, P5, P6, P7, P8): when the test uses 2+ seeds, add assertions that the summary contains run_manifest with the correct seed count and that mean/stdev (or CI) fields are present and numerically plausible (e.g. stdev >= 0, CI lower <= mean <= CI upper). See [tests/test_rep_cps_p2.py](../tests/test_rep_cps_p2.py), [tests/test_maestro_p4.py](../tests/test_maestro_p4.py), etc.

13. **Stress and sensitivity tests**
    - **P4:** Add a test that runs fault sweep with a high drop_completion_prob (e.g. 0.3) and asserts tasks_completed_mean drops vs no_drop.
    - **P5:** Add a test that runs held-out eval with at least 3 scenarios and asserts beat_baseline or trigger_met is present and held_out_results length >= 2.
    - **P8:** Existing collapse-threshold stress test + `verify_p8_meta_artifacts` + `regime_stress_v1` smoke; optional follow-up: hermetic non-vacuous integration test (heavier) asserting `stress_selection_policy` and `collapse_paired_analysis` (note `meta_reduces_collapse` = non-inferior counts, not strict improvement).
    - **P1:** Add a test that runs contracts_eval with --scale-test (small scale-events for speed, e.g. 1000) and asserts scale_test.json exists and has run_manifest and time_per_write_us (or equivalent).

14. **CI evals: align with publishable defaults where feasible**
    - In [.github/workflows/ci.yml](../.github/workflows/ci.yml): keep reduced seeds for speed, but use 2 scenarios for P0 E3 when possible (e.g. toy_lab_v0,lab_profile_v0 with 5 runs each), and ensure P8 meta_collapse_sweep uses at least 2 drop_probs and 3 seeds so the artifact is non-empty and structure is validated.

---

## Phase 5: Reporting and export fixes

**Goal:** Every table in the draft is filled from scripts; effect size and regression where defined are visible.

15. **P5 regression MAE in export and DRAFT**
    - In [scripts/export_scaling_tables.py](../scripts/export_scaling_tables.py) (or equivalent): ensure regression MAE is read from heldout_results and printed in Table 2 when present (fit_linear_predictor can return None for small N; document when regression is skipped). Update [papers/P5_ScalingLaws/DRAFT.md](../papers/P5_ScalingLaws/DRAFT.md) so the Regression row is either populated or explicitly "N/A (e.g. insufficient train rows)."

16. **Effect size in summary JSONs**
    - Add to excellence_metrics (or equivalent) in the relevant evals: improvement_pct or baseline_margin for P2 (bias reduction), P4 (recovery vs no_drop), P5 (MAE reduction vs global mean), P8 (collapse reduction). Document in [STANDARDS_OF_EXCELLENCE.md](STANDARDS_OF_EXCELLENCE.md) and in each paper's "How to read" in [RESULTS_PER_PAPER.md](RESULTS_PER_PAPER.md).

17. **Repro time and claim confidence (optional but recommended)**
    - Add a one-off script or CI step that runs the minimal repro for one paper (e.g. P4) and records wall-clock time; document "Repro time: under 20 min" in that paper's DRAFT or in a central repro manifest. In claims.yaml, add optional `evidence.confidence` (high/medium/low) per claim as in STANDARDS_OF_EXCELLENCE.

---

## Phase 6: Documentation and scope

**Goal:** One place that summarizes "what is strong" vs "what is intentionally limited" so reviewers and future work know the bar.

18. **Experiments and limitations summary doc**
    - Add [docs/EXPERIMENTS_AND_LIMITATIONS.md](EXPERIMENTS_AND_LIMITATIONS.md) (or extend [EVAL_RESULTS_INTERPRETATION.md](EVAL_RESULTS_INTERPRETATION.md)) with:
      - **What we do:** 20 seeds (publishable default), run manifest, variance/CI, multi-scenario where applicable, statistical tests for comparisons, expanded corpora, optional real LLM (Phase 7), formal verification (Phase 8).
      - **What we do not do (and why):** No real hardware; thin-slice only for physical execution; no formal verification of full system or LLM planner; threat model and fault set are bounded. Reference each paper's Limitations section.
    - Link from README and PORTFOLIO_BOARD so "strengthened experiments" and "known limitations" are easy to find.

---

## Phase 7: Real LLM evaluation (P6 and related)

**Goal:** Support real LLM calls for plan generation and/or red-team-style prompts; API keys from `.env`; results reproducible and documented.

1. **Env and dependency**
   - Add `python-dotenv` (or equivalent) to project deps; document in README that `.env` at repo root is required for real-LLM mode.
   - In any script that calls an LLM API, load `.env` from repo root and read `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENHANDS_API_KEY`; fail gracefully with a clear message if real-LLM is requested but keys are missing.

2. **Real-LLM mode in P6**
   - Add an optional path in the P6 pipeline that calls a real model (e.g. OpenAI or Anthropic) to:
     - **Option A:** Generate a typed plan (or tool-call sequence) for a given scenario; run the existing validator on the model output; record allow/deny and, if applicable, latency.
     - **Option B:** Run red-team prompts (e.g. "Suggest a plan step that might try to use a disallowed tool") and check that the validator blocks the resulting step.
   - Prefer one provider and one model (e.g. OpenAI gpt-4o-mini) for reproducibility; document model and temperature in run_manifest. Optional: support a second provider for comparison.
   - Output: extend `red_team_results.json` or add `llm_real_plan_results.json` with run_manifest (model_id, provider, temperature, scenario_ids, seeds), pass/fail per run, and latency. Do not log raw API keys or full prompt/response in artifacts.

3. **Adapter and eval script**
   - Extend [impl/src/labtrust_portfolio/adapters/llm_planning_adapter.py](../impl/src/labtrust_portfolio/adapters/llm_planning_adapter.py) (or add a separate "real LLM" adapter) so that when real-LLM mode is enabled and keys are present, it requests a plan from the API, then runs the same validator and trace/report pipeline. Keep synthetic mode as default so CI and keyless runs still work.
   - [scripts/llm_redteam_eval.py](../scripts/llm_redteam_eval.py): add a flag (e.g. `--real-llm`) that enables the real-LLM path; when set, load `.env`, call the chosen API, and merge results into the existing JSON output with a clear `real_llm_used: true` and model id in run_manifest.

4. **Documentation and limitations**
   - In [docs/EXPERIMENTS_AND_LIMITATIONS.md](EXPERIMENTS_AND_LIMITATIONS.md) (or equivalent): state that **real LLM is in scope**; API keys are in `.env`; real-LLM mode is optional and used for P6 (and any future paper that needs it). Document that thin-slice and synthetic plans remain the default for CI and keyless environments.
   - In [papers/P6_LLMPlanning/DRAFT.md](../papers/P6_LLMPlanning/DRAFT.md): update the Limitations / comparison table to "Real LLM: supported when `.env` keys are set; synthetic-only by default." Remove or soften "No real LLM in v0.1" where it is no longer accurate.

---

## Phase 8: Lean formal verification (state of the art)

**Goal:** Implement at least one Lean wedge from [formal/lean/README.md](../formal/lean/README.md) so that selected portfolio kernels have machine-checked proofs; set up structure for further wedges (W1, W2, W4).

1. **Lean project structure**
   - Under [formal/lean/](../formal/lean/), create a Lean 4 project (e.g. `lakefile.toml`, `LeanProject.lean` or equivalent) so that `lake build` (or `leanproject build`) succeeds. Add a short README section on how to build and run the proofs.

2. **W3 — Evidence bundle verifier (first wedge)**
   - Encode the evidence-bundle verifier spec as Lean definitions: required artifact presence, schema validity checks, and hash/signature (or checksum) verification assumptions. Match the semantics described in the kernel (e.g. [kernel/mads/EVIDENCE_BUNDLE](../kernel/mads/) and related docs).
   - Prove soundness lemmas: e.g. "If the verifier returns OK, then tampering is detectable under the stated cryptographic assumptions." Keep assumptions explicit (e.g. collision resistance, integrity of artifact hashes).
   - Add a small test harness: either extract the spec (e.g. as a list of conditions) for a Python test that checks the implementation against the same conditions, or document how the Lean spec aligns with [impl](../impl/) so that future work can bind the proof to the code.

3. **W1 and/or W2 (next wedges)**
   - **W1 — Gatekeeper/PONR (P0):** Encode fail-closed and "no Tier T2/T3 actuation without recorded authorization" as Lean predicates; prove the stated invariants under the assumed model of transitions. Reference in P0 DRAFT and claims (e.g. "Gatekeeper kernel has formal model in formal/lean/").
   - **W2 — Contract validator (P1):** Encode ownership/lease and valid transition rules; prove determinism of verdicts given the same event stream. Reference in P1 DRAFT and claims.
   - Order can be W3 → W1 → W2 (or W2 before W1) depending on effort; at least one full wedge (definitions + proofs + harness or doc) completes "implement real Lean proofs."

4. **Documentation**
   - Update [formal/lean/README.md](../formal/lean/README.md) to state which wedges are implemented (e.g. "W3 implemented; W1 in progress") and how to build and run. In [docs/EXPERIMENTS_AND_LIMITATIONS.md](EXPERIMENTS_AND_LIMITATIONS.md), add a "Formal verification" subsection: which kernels are formally specified and proved, and what is not (e.g. "We do not verify the autonomous lab end-to-end or the LLM planner's correctness").

---

## Out of scope (by design)

- **Real hardware:** Remains out of scope; thin-slice and simulation are the supported execution model. Document in EXPERIMENTS_AND_LIMITATIONS.
- **Real LLM:** In scope (Phase 7). API keys in `.env`; optional real-LLM mode for P6 and related evals; documented in EXPERIMENTS_AND_LIMITATIONS.
- **Full formal verification:** In scope (Phase 8). At least one Lean wedge (W3, then W1/W2) is implemented; formal/lean/README.md and EXPERIMENTS_AND_LIMITATIONS document what is proved and what is not.
- **New papers or new kernels:** Focus is improving experiments and tests for existing P0–P8 pipelines and artifacts.

---

## Implementation order (suggested)

| Priority | Item | Dependencies |
|----------|------|--------------|
| 1 | Phase 1.1 – stats helper + wire into 2–3 evals | None |
| 2 | Phase 4.12 – integration tests assert manifest/variance | None |
| 3 | Phase 5.15 – P5 regression in export and DRAFT | None |
| 4 | Phase 1.3 – fixed RNG seed doc and usage | None |
| 5 | Phase 2.4 – P0 E3 multi-scenario default | None |
| 6 | Phase 2.8 – P8 stress preset / non-vacuous doc | None |
| 7 | Phase 3.9–3.11 – corpus/case expansion (P1, P3, P6) | Corpus files |
| 8 | Phase 4.13 – stress/sensitivity tests | Phase 1.1 helpful |
| 9 | Phase 2.5–2.7 – P2/P4/P5 scenario and fault breadth | Optional for CI |
| 10 | Phase 5.16–5.17, Phase 6.18 – reporting and doc | After evals updated |
| 11 | Phase 7 – Real LLM (env, adapter, --real-llm, doc) | P6 eval/adapter stable |
| 12 | Phase 8 – Lean (project, W3, then W1/W2, doc) | Can run in parallel |

---

## Summary

- **Phases 1–6:** Statistical rigor, scenario/fault coverage, corpus expansion, test strengthening, reporting fixes, and EXPERIMENTS_AND_LIMITATIONS documentation.
- **Phase 7 (Real LLM):** Use `.env` at repo root for API keys; add optional real-LLM mode to P6 eval and adapter; document in EXPERIMENTS_AND_LIMITATIONS that real LLM is in scope.
- **Phase 8 (Lean):** Implement real Lean proofs (W3 first, then W1/W2) under `formal/lean/` so that at least one kernel has machine-checked proofs and each affected paper can claim formal verification where applicable.
- **Out of scope:** Only real hardware remains out of scope; real LLM and formal verification are part of the plan.
