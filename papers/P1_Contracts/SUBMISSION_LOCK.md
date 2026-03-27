# P1 Submission Lock

This checklist freezes the exact manuscript-evidence mapping for submission builds.

## 1) Claim-to-evidence matrix

| Claim | Manuscript anchor | Artifact fields/files | Caveat language |
|---|---|---|---|
| C1 Detection and denial on benchmark | `DRAFT.tex` RQ1/RQ2/RQ3, `tab:summary`, `tab:comparators`, `tab:classmetrics`, `fig:heatmap` | `datasets/runs/contracts_eval/eval.json` (`success_criteria_met.all_detection_ok`, `ablation`, `detection_metrics_by_class`) | Benchmark-backed evidence; not field guarantee |
| C2 Trace-derivability and auditability | `DRAFT.tex` Definitions + Scope + Discussion | `impl/src/labtrust_portfolio/contracts.py`, `docs/P1_TRACE_DERIVABILITY.md`, `formal/lean/Labtrust/W2Contract.lean` | No privileged hidden state claim is at artifact boundary |
| C3 Transport-boundary parity | `DRAFT.tex` RQ5 `tab:parity`, `fig:flow` | `datasets/runs/contracts_eval/transport_parity.json` (`parity_ok_all`, `per_sequence`, `parity_confidence`) | Boundary semantics only; no live transport equivalence |
| C4 Overhead and stress characterization | `DRAFT.tex` RQ4/RQ6 `fig:latency`, `fig:scale`, `fig:stress` | `eval.json` (`latency_percentiles_us`), `scale_test.json`, `stress_results.json` | Single-process evaluated setting; stress is sensitivity analysis |

## 2) Camera-ready lock checklist

- [ ] Freeze one run directory and keep `run_manifest.script_version`, `run_manifest.corpus_fingerprint`, `run_manifest.corpus_sequence_count`.
- [ ] Regenerate all visuals and appendix artifacts from the frozen run:
  - `python scripts/generate_paper_artifacts.py --paper P1`
  - `python scripts/export_p1_appendix_tex.py --eval datasets/runs/contracts_eval/eval.json`
- [ ] Confirm no placeholders remain in `DRAFT.tex` (`\IfFileExists` fallbacks should not be active in final build).
- [ ] Confirm table/figure references in `claims.yaml` match final labels in the compiled paper.
- [ ] Re-run P1 tests:
  - `python -m pytest tests/test_contracts_p1.py -q`

## 3) Blind-review pass

- [ ] Keep anonymous author block in `DRAFT.tex` if venue is double blind.
- [ ] Avoid self-identifying language in acknowledgements, artifact notes, or appendix prose.
- [ ] Remove internal/proprietary references not needed for reproduction.

## 4) Reviewer-objection quick map

- **Weak baselines:** Explicitly framed as proxy comparators for boundary ingredient isolation.
- **Synthetic benchmark:** Addressed by anti-circular labeling governance and full per-sequence appendix.
- **Transport overclaim:** Restricted to boundary parity with explicit non-goals.
- **Insufficient formal proof:** Determinism alignment noted with Lean; admitted-prefix theorem is a sketch.
- **Stress overclaim:** Presented as sensitivity characterization, not deployment guarantee.

