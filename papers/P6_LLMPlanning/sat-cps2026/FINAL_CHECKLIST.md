# SaT-CPS 2026 P6 -- Final acceptance checklist

Paper is ready for submission only when all items are true.

## Narrative and venue fit

- [ ] **Title** reads as CPS security / runtime enforcement for tool invocation (not a generic LLM leaderboard paper).
- [ ] **Abstract** states the synthetic primary result (15/15 red-team, 6/6 confusable, 4/4 jailbreak-style in the released suite) and the cited **OpenAI real-LLM** numbers with exact denominator from run_manifest (camera-ready snapshot `llm_eval_camera_ready_20260424`: gpt-4.1-mini and gpt-4.1 each 75/75, Wilson [95.1, 100.0], N=3 runs/case, 25 cases/model).
- [ ] If the abstract mentions **Prime Inference** or four models, it **labels the run separately** (N=3, 39 trials/model, different output dir) and does not imply the same experiment as OpenAI N=5.
- [ ] **Introduction** places the trust boundary early: planner output is untrusted until the firewall admits it.
- [ ] **Threat model** lists assets, adversarial leverage, trust assumptions, non-goals, and includes the summary table.
- [ ] **Discussion** uses **containment** language only; no banned words from SUBMISSION_STANDARD.md.

## Evidence blocks (A--D)

- [ ] **Block A:** Synthetic suite is clearly primary validator evidence; cites `red_team_results.json`, `confusable_deputy_results.json`.
- [ ] **Block B:** Real-LLM denominator, Wilson CI, and **failure-case** discussion (argument-level rows); cites OpenAI run manifest fields (`model_id`, `n_runs_per_case`, `prompt_template_hash` where applicable).
- [ ] **Block C:** Adapter latency, denial counts, optional **latency decomposition** (`--latency-decomposition`); denial-trace **case study** (execute_system or equivalent).
- [ ] **Block D:** Tool-level and argument-level baselines honestly framed; optional **benign** false-positive line if cited (`baseline_benign.json`).

## Figures, format, compliance

- [ ] **Figure 1 (decision path):** Regenerated via `export_p6_firewall_flow.py`; readable in PDF.
- [ ] **Figure 2 (adapter latency):** Only if space allows; tied to `adapter_latency.json`.
- [ ] **ACM proceedings** format, **10-page** cap including references.
- [ ] **Authors and affiliations** per workshop CFP.

## Reproducibility and artifact integrity

- [ ] Every table number in the camera-ready draft maps to a file under the cited canonical run directory (current default: `datasets/runs/llm_eval_camera_ready_20260424/`; Prime or supplementary runs must use clearly named alternate dirs).
- [ ] `run_manifest` fields are consistent with the text (`timestamp_iso`, `evaluator_version`, `policy_version`; real-LLM: `prompt_template_hash` where written).
- [ ] Appendix or supplementary: `export_p6_artifact_hashes.py` + `export_p6_reproducibility_table.py` run on the **same** directory cited in the paper.
- [ ] Machine integrity gate passes: `python scripts/verify_p6_camera_ready_bundle.py` (CI + local pre-submit).
- [ ] Optional deep-dive exports (if referenced): `export_p6_layer_attribution.py`, `export_p6_failure_analysis.py`, `export_p6_cross_model_heatmap.py`, `export_p6_latency_decomposition.py`.

## Optional extended experiments (6--12)

- [ ] Any claim about concurrency, capture-off ablation, storage, cost, policy sweep, replanning, or adaptive suite is backed by the corresponding `p6_*.json` artifact and script name in EXPERIMENTS_RUNBOOK.md.

## Process

- [ ] After submission (or before), run **Review 1--3** from REVIEW_PROTOCOL.md and record sign-off.

See **SUBMISSION_STANDARD.md** (five axes), **EXPERIMENTS_RUNBOOK.md** (commands), **README.md** (evidence tiers), **claims_satcps.yaml** (C1--C4).
