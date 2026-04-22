# P7 — Standards Mapping (Assurance Pack)

P7 argues for a **traceable, mechanically checkable** mapping from hazards to controls to evidence artifacts and audit traces, using a structured assurance pack (`hazards`, `controls`, `evidence_map`), schema validation, mapping completeness checks, and **scripted review** (PONR-aligned task coverage where defined per scenario, plus control coverage). **No certification or compliance claim:** translation layer and audit-support tooling only.

## Publishable evidence (committed)

| Artifact | Role |
|----------|------|
| `datasets/runs/assurance_eval/results.json` | Baseline: `mapping_check`, Table 1 primary review (`lab_profile_v0` / `disposition_commit`), `reviews`, scenario-matched `per_profile`, `run_manifest` |
| `datasets/runs/assurance_eval/robust_results.json` | Robust matrix: 400 runs, `aggregate`, `by_scenario`, `real_world_proxy`, `rows`, `run_manifest` (20 seeds, scenario↔profile alignment + proxy note) |
| `datasets/runs/assurance_eval/negative_results.json` | Negative controls + ablations: `aggregate` (rates, lift vs baselines, `governance_evidence_discrimination_accuracy`), `by_mode`, `by_family`, `by_scenario`, `by_perturbation`, `rows` with `failure_reason_codes` ([P7_REVIEW_FAILURE_CODES.md](../../docs/P7_REVIEW_FAILURE_CODES.md)) |
| `papers/P7_StandardsMapping/p7_*.csv` | Tables 4–6 + supplements from `export_p7_negative_tables.py`: family summary, ablation summary, failure breakdown, `p7_perturbation_reject_matrix.csv`, `p7_aggregate_lift_metrics.csv`, `p7_latency_by_mode.csv`, `p7_negative_by_scenario.csv`, `p7_boundary_case_summary.csv`, `p7_submission_manifest_redacted.json`, `p7_generation_metadata.json` |
| `docs/figures/p7_mapping_flow.mmd` | Figure 0 source (Mermaid) |
| `docs/figures/p7_gsn.mmd` | Figure 1 source (GSN-lite) |
| `docs/figures/p7_mapping_flow.png`, `.pdf` | Camera-ready Figure 0 |
| `docs/figures/p7_gsn.png`, `.pdf` | Camera-ready Figure 1 |
| `docs/figures/p7_review_stages.mmd` | Figure 2 source — review-stage decision flow (`full_review` path) |
| `docs/figures/p7_review_stages.png`, `.pdf` | Camera-ready Figure 2 (committed when rendered; regenerate via `render_p7_mermaid_figures.py`) |
| `papers/P7_StandardsMapping/generated_tables.md` | Index for Tables 1–6 (CSV paths + links to checklist); Tables 1–3 markdown from `export_assurance_tables.py` when exported to that path |

## One-shot regeneration (repo root)

Set `PYTHONPATH=impl/src` and `LABTRUST_KERNEL_DIR=kernel` for eval scripts.

```bash
python scripts/run_assurance_eval.py --out datasets/runs/assurance_eval
python scripts/run_assurance_robust_eval.py --out datasets/runs/assurance_eval
python scripts/run_assurance_negative_eval.py --out datasets/runs/assurance_eval --submission-mode
python scripts/export_p7_mapping_flow.py
python scripts/export_assurance_gsn.py --out docs/figures/p7_gsn.mmd
python scripts/export_assurance_tables.py --results datasets/runs/assurance_eval/results.json
python scripts/export_p7_negative_tables.py --input datasets/runs/assurance_eval/negative_results.json --submission-mode
python scripts/render_p7_mermaid_figures.py
```

Validate: `python scripts/check_assurance_mapping.py`; `python scripts/audit_bundle.py --json-only`; `tests/test_assurance_p7.py`; `tests/test_assurance_negative_eval.py` (includes CSV↔JSON consistency checks for `by_mode`, `by_family`, and aggregate lift fields).

## Profiles

- `profiles/lab/v0.1/assurance_pack_instantiation.json`
- `profiles/warehouse/v0.1/assurance_pack_instantiation.json`
- `profiles/medical_v0.1/assurance_pack_instantiation.json`

## Related docs

- Standards mapping methodology and clause tables: [docs/P7_STANDARDS_MAPPING.md](../../docs/P7_STANDARDS_MAPPING.md)
- Robust protocol and success criteria: [docs/P7_ROBUST_EXPERIMENT_PLAN.md](../../docs/P7_ROBUST_EXPERIMENT_PLAN.md)
- Independent review checklist: [docs/P7_REVIEW_CHECKLIST.md](../../docs/P7_REVIEW_CHECKLIST.md)
- Stable failure codes: [docs/P7_REVIEW_FAILURE_CODES.md](../../docs/P7_REVIEW_FAILURE_CODES.md)
- Perturbation ids vs empirical brief: [docs/P7_PERTURBATION_CHECKLIST.md](../../docs/P7_PERTURBATION_CHECKLIST.md)
- Auditor feedback protocol: [docs/P7_AUDITOR_FEEDBACK_PROTOCOL.md](../../docs/P7_AUDITOR_FEEDBACK_PROTOCOL.md)
- Runbook (commands, CI): [docs/EVALS_RUNBOOK.md](../../docs/EVALS_RUNBOOK.md)
- Results interpretation: [docs/RESULTS_PER_PAPER.md](../../docs/RESULTS_PER_PAPER.md#p7--standards-mapping-assurance-pack)

## Paper files

- Draft: `DRAFT.md`
- Claims: `claims.yaml`
- Authoring packet: `AUTHORING_PACKET.md`
- Phase 3 gate: `PHASE3_PASSED.md`

## Automation

`scripts/run_paper_experiments.py --paper P7` runs baseline + robust eval (non-quick mode uses 20-seed robust matrix).
