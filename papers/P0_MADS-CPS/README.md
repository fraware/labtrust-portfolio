# MADS-CPS: A Machine-Checkable Minimum Assurance Bar for Agentic Cyber-Physical Workflows

P0 defines a machine-checkable minimum assurance bar for agentic CPS: conformance tiers (E1), restricted auditability and redaction (E2), replay-link (E3), and algorithm-independence (E4). Draft and claim table: [DRAFT.md](DRAFT.md), [claims.yaml](claims.yaml). Tables and figures: [VISUALS_PER_PAPER.md](../docs/VISUALS_PER_PAPER.md), [RESULTS_PER_PAPER.md](../docs/RESULTS_PER_PAPER.md). Outline: [AUTHORING_PACKET.md](AUTHORING_PACKET.md).

**Central claim.** A minimum assurance bar for agentic CPS can be defined in terms of machine-checkable evidence obligations and conformance predicates, independently of the internal decision policy, and verified by third parties under both full and restricted audit modes. MADS-CPS is not a replacement for risk frameworks, safety cases, or regulatory quality systems; it is a machine-checkable evidence substrate that can support them.

**E1 (Conformance corpus):** Build a challenge set of run directories (missing artifact, schema-invalid, hash mismatch, replay mismatch, missing PONR event, etc.). The conformance checker (`labtrust_portfolio check-conformance`) is run on each; Table 1 reports case ID, fault injected, expected tier, observed tier, and agreement. See `scripts/build_p0_conformance_corpus.py` and `scripts/export_e1_corpus_table.py` (or equivalent).

**E2 (Restricted auditability):** Run `python scripts/e2_redaction_demo.py --out datasets/runs/e2_redaction_demo`. Produces `trace_redacted.json` and `evidence_bundle_redacted.json`. The verification-mode admissibility matrix (Table 2) has four columns: full, evaluator, regulator, public/redacted. Under redaction, a subset of admissibility checks (schema, integrity) remains; replay_ok is not checkable. See `kernel/mads/VERIFICATION_MODES.v0.1.md` and `scripts/export_e2_admissibility_matrix.py`.

**E3 (Replay link):** An independent verifier (standalone script or subprocess) recomputes the evaluation report from the trace. Run `python scripts/produce_p0_e3_release.py --runs 20` (with LABTRUST_KERNEL_DIR and PYTHONPATH set). Produces runs under `datasets/runs/e3/<scenario>/seed_<n>/`, `e3_summary.json`, and optionally the release. Table 3 (with E4) reports replay match rate, latency mean and 95% CI, and conformance rate. See `scripts/export_e3_table.py`, `scripts/plot_e3_latency.py`.

**E4 (Algorithm-independence):** At least two adapters (e.g. centralized, REP-CPS or retry-heavy) produce the same artifact interface for the same scenario. The same conformance checker is run; conformance depends on artifacts and declared envelope, not controller identity. Results feed into Table 3.

Conformance check: `labtrust_portfolio check-conformance <run_dir>`. See `docs/VALIDATING_A_RUN.md` and `impl/src/labtrust_portfolio/conformance.py`. Results summary: [datasets/runs/RUN_RESULTS_SUMMARY.md](../datasets/runs/RUN_RESULTS_SUMMARY.md).
