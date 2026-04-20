# Replay as control-plane assurance evidence for agentic CPS

**Paper ID:** P3_Replay  
**Tag:** core-kernel  
**Board path:** MVP → Eval → Draft  
**Kernel ownership:** trace/replay kernel (trace semantics, replay levels, divergence detection)

**Positioning (freeze):** AI security + CPS assurance venues. The manuscript treats **L0 replay as a machine-checkable assurance primitive** for control-plane evidence: explicit contracts, first-divergence localization, structured diagnostics, evidence-bundle integration—not a generic debugger and not “hashing logs.”

## 1) One-line question

How do we obtain **independently checkable replay evidence** for control-plane claims in agentic CPS—detection and localization of divergence under a declared contract—without overclaiming full-process determinism or physics replay?

## 2) Scope anchors

- Replay is defined in **levels** (L0 control-plane default; L1 control-plane twin contract; L2 aspirational). This avoids non-credible “full determinism” claims.
- The primary guarantee is **nondeterminism detection + localization** relative to a declared replay contract.
- **Real-ingest** traces are **lane-separated** from synthetic traps and field proxies; ingestion notes document mapping and redaction.

## 3) Claims

- **Package novelty (for reviewers):** Not “hashing logs”; the artifact is **replay levels + TRACE contract + per-event commitments + seq-level localization + witness diagnostics + evidence-bundle fields** (see DRAFT novelty paragraph vs RR / log-only).
- **C1:** A CPS-aware trace format plus a determinism contract enables L0 replay with per-event verification and sequence-level localization, evaluated across explicit evidence lanes (synthetic traps, synthetic passes, field-proxy traces, **two real-ingest lanes**) with corpus-space and category-aware reporting.
- **C2:** Hidden nondeterminism is detectable: same trace ≠ same control-plane behavior triggers structured diagnostics; baselines quantify incremental cost of full L0.
- **C3:** Replay supports audit-style reconstruction from diagnostics; **L1** is a **control-plane twin contract** (stub + optional `--l1-twin`), exercised on **multi-seed thin-slice** and on **passing real_ingest** traces—not physics replay.
- **C4:** The toolchain integrates with evidence bundles so replay outcomes are admissible evidence (MADS).

## 4) Outline

1. Motivation: replayability as assurance infrastructure (audit, forensics, reproducible evaluation)
2. Replay levels and nondeterminism budgets (formalized)
3. Trace format: event ontology, commitments, time model
4. Replay engine: L0; baselines (apply-only, final-hash-only); L1 twin path
5. Divergence detection + attribution (witness slices)
6. Evaluation: lane-separated corpus; multi-seed overhead; **multi-point overhead curve**; **L1 cross-family** (seeds + real_ingest)
7. Evidence integration

## 5) Experiment plan

- **Scenarios:**
  - MAESTRO thin-slice (multi-seed family `42–46` for publishable run);
  - trap corpus (nondeterminism, reorder, timestamp reorder, hash mismatch; long-horizon; mixed-failure; benign pass);
  - field-style pass traces (`field_proxy`; not production-representative);
  - **real-ingest:** `real_bucket_example` (template) and `real_bucket_toy_lab_session` (documented redacted export; see `bench/replay/corpus/REAL_BUCKET_TOY_LAB_SESSION.md`).
- **Metrics:**
  - L0 pass/fail per trace; corpus outcome accuracy and Wilson CI;
  - localization at expected seq for seq-labeled traps (Table 1b);
  - `corpus_category`, `corpus_space_summary`;
  - overhead: mean, p95, p99; bootstrap CIs; **overhead_curve** (multi-prefix);
  - **L1:** `l1_twin_summary` with thin-slice `per_seed`, **`real_ingest_traces`**, `all_pass`, timing stats when `--l1-twin` is used.
- **Baselines:** `replay_eval.py`: apply-only; final-hash-only; witness_window=0.
- **Cross-reference:** fault sweeps and recovery metrics belong to P4 (`maestro_fault_sweep`), not P3.

## 6) Artifact checklist

- `kernel/trace/TRACE.v0.1.schema.json`
- `kernel/trace/REPLAY_LEVELS.v0.1.md`
- `datasets/runs/replay_eval/summary.json` (canonical publishable; `schema_version: p3_replay_eval_v0.2`)
- `bench/replay/corpus/` including `real_bucket_*` pairs and ingestion notes
- `scripts/verify_p3_replay_summary.py --strict-curve`
- Camera-ready figures: `scripts/export_p3_paper_figures.py` → `papers/P3_Replay/figures/`

## 7) Kill criteria

- **K1:** cannot define a determinism contract that is both sufficient and practical.
- **K2:** replay depends on hidden simulator internals (not portable).
- **K3:** If replay fidelity cannot be bounded clearly, narrow claims to **detection/localization only** (no strong fidelity guarantee).

## 8) Target venues

**Primary framing:** AI security for cyber-physical and autonomous systems; CPS assurance, safety cases, and audit.

**Example venue families:** USENIX Security, IEEE S&P, CCS, RAID, SafeComp, DSN, EMSOFT (systems + assurance—match scope to control-plane evidence, not physics simulation).

**Not the primary pitch:** generic record/replay debugging (RR-style) as the contribution category.

## 9) Integration contract

- Replay defines trace/replay semantics.
- MAESTRO consumes traces to produce comparable reports.
- MADS consumes replay outputs as admissible evidence.
