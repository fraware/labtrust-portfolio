# P5 final reproduction log (fill after a clean run)

Record the environment used for the NeurIPS artifact freeze. **Do not** edit committed JSON numbers by hand; regenerate via the pipeline below.

## 1. Portfolio validation

```bash
export PYTHONPATH=impl/src
export LABTRUST_KERNEL_DIR=kernel

python scripts/validate_kernel.py
python -m unittest discover -s tests
```

PowerShell:

```powershell
$env:PYTHONPATH = "impl/src"
$env:LABTRUST_KERNEL_DIR = "kernel"
python scripts/validate_kernel.py
python -m unittest discover -s tests
```

## 2. P5 paper pipeline

```bash
PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel \
  python scripts/run_paper_experiments.py --paper P5
```

Piecemeal refresh (large grids): regenerate each `heldout_results.json` without dumping JSON to stdout:

```bash
PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/scaling_heldout_eval.py \
  --runs-dir datasets/runs/multiscenario_runs --out datasets/runs/scaling_eval \
  --holdout-mode scenario --quiet
# repeat with --out …/scaling_eval_family --holdout-mode family, etc.
```

Then refresh tables:

```bash
PYTHONPATH=impl/src python scripts/export_scaling_tables.py \
  --results datasets/runs/scaling_eval/heldout_results.json \
  --family-results datasets/runs/scaling_eval_family/heldout_results.json \
  --regime-results datasets/runs/scaling_eval_regime/heldout_results.json \
  --agent-results datasets/runs/scaling_eval_agent_count/heldout_results.json \
  --fault-results datasets/runs/scaling_eval_fault/heldout_results.json \
  --recommend-results datasets/runs/scaling_recommend/recommendation_eval.json \
  --sensitivity-results datasets/runs/sensitivity_sweep/scaling_sensitivity.json \
  --regime-agent-summary datasets/runs/scaling_summary/regime_agent_summary.json \
  --out papers/P5_ScalingLaws/generated_tables.md
```

## 3. Success criteria (paths must exist and be non-empty)

- `datasets/runs/multiscenario_runs/` (directory)
- `datasets/runs/scaling_eval/heldout_results.json`
- `datasets/runs/scaling_eval_family/heldout_results.json`
- `datasets/runs/scaling_eval_regime/heldout_results.json`
- `datasets/runs/scaling_eval_agent_count/heldout_results.json`
- `datasets/runs/scaling_eval_fault/heldout_results.json`
- `datasets/runs/sensitivity_sweep/scaling_sensitivity.json`
- `datasets/runs/scaling_recommend/recommendation_eval.json`
- `datasets/runs/scaling_summary/regime_agent_summary.json`
- `papers/P5_ScalingLaws/generated_tables.md`

## 4. Record here after success

**Interpretation (two SHAs).** Cite **`git rev-parse HEAD` below** as the **artifact freeze bundle** (committed JSON + `generated_tables.md` + `p5_artifact_hashes.txt` + LaTeX tables). Each `heldout_results.json` also embeds **`run_manifest.commit`**, which records **`git rev-parse HEAD` at the instant `scaling_heldout_eval.py` wrote that file** (here the parent commit of the bundle — portfolio code without the artifact commit). For NeurIPS reproducibility, reviewers should **check out the artifact bundle commit**; the embedded field documents which code revision produced the numeric sweep.

| Field | Value |
|-------|--------|
| Artifact bundle commit (`git rev-parse HEAD` at freeze) | `3a7d4f0b17c86cde219852f59dbd36a68b45efb0` |
| Embedded `run_manifest.commit` (eval-time HEAD; parent of bundle) | `ede2b361620270bbaf5e4e343ce6a6c3c2834217` |
| `python --version` | Python 3.13.11 |
| OS | Microsoft Windows 11 Home; Version 10.0.26200 |

**Commands executed for this log entry (repo root, PowerShell):**

1. `python scripts/validate_kernel.py`
2. `$env:PYTHONPATH='impl/src'; $env:LABTRUST_KERNEL_DIR='kernel'; python -m unittest discover -s tests -q`
3. Held-out regeneration (five modes): `python scripts/scaling_heldout_eval.py --runs-dir datasets/runs/multiscenario_runs --out datasets/runs/<dir> --holdout-mode <scenario|family|regime|agent_count|fault_setting> --quiet`
4. `$env:PYTHONPATH='impl/src'; python scripts/export_scaling_tables.py --out papers/P5_ScalingLaws/generated_tables.md --out-tex-dir papers/P5_ScalingLaws/neurips2026/tables_tex`
5. `python scripts/hash_p5_artifacts.py`
6. `python scripts/check_p5_claim_sources.py`

**Git tag:** `neurips2026-p5-freeze-v1` points at the commit that contains this filled log (docs-only follow-up commit after the artifact bundle).

## 5. Artifact hashes (cross-platform)

From repo root:

```bash
python scripts/hash_p5_artifacts.py --out papers/P5_ScalingLaws/p5_artifact_hashes.txt
```

This writes **repo-relative** paths (`datasets/runs/...`) and SHA-256 digests so Linux CI and Windows clones produce the same manifest for identical file contents. Commit `p5_artifact_hashes.txt` with the freeze and refresh it whenever canonical JSON under `datasets/runs/` at depth ≤2 changes (`tests/test_p5_submission_readiness.py` enforces presence).

## 6. Claim-source gate

```bash
python scripts/check_p5_claim_sources.py
```
