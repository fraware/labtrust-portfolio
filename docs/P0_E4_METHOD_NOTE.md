# P0 E4 method note (controller matrix)

This note documents how we evaluate **controller-independence** and **replay-link** evidence for P0 E4 after the controller-matrix upgrade.

## Raw versus normalized evaluation

- **Raw (E4a):** After `run_adapter`, we **do not** rewrite `trace.json`, `maestro_report.json`, or the original `evidence_bundle.json` in the raw run directory. Conformance is `check_conformance(raw_dir)` on exactly those artifacts, and `conformance.json` is then rewritten so it matches that outcome (the thin-slice harness may have written an earlier `conformance.json` before an adapter appended adapter-only MAESTRO fields such as `metadata_rep_cps`, which are rejected at Tier 1 by `MAESTRO_REPORT.v0.2` under strict JSON Schema). Replay checks recompute MAESTRO from the stored trace and compare to the stored report.
- **Normalized (E4b):** We **copy** the raw tree to a parallel `datasets/runs/p0_e4_matrix/normalized/...` directory. Normalization is **only** stripping non–MAESTRO_REPORT.v0.2 top-level keys from `maestro_report.json` (for example adapter-only fields such as `metadata_rep_cps`). We then **rebuild** `evidence_bundle.json`, `release_manifest.json`, and `conformance.json` from the copied trace plus the stripped MAESTRO so evidence reflects the normalized MAESTRO honestly (including real schema validation and replay flags).

There is **no** hidden `schema_validation_ok = true` repair on the raw path. Any adapter-only MAESTRO fields must not be counted as “raw conformance success” if they cause schema or replay failures; the normalized path isolates interface-level predicates.

## Replay-match definitions

- **Weak replay match:** `tasks_completed` and `coordination_messages` in recomputed metrics equal the stored MAESTRO metrics (legacy diagnostic).
- **Strong replay match:** Equality of the full MAESTRO **core slice** (`run_outcome`, `metrics`, `safety`, `coordination_efficiency`, `faults`) plus **PONR witness coverage** when the scenario declares PONR tasks (see `conformance.SCENARIO_PONR_TASK_NAMES`): every declared PONR task name must appear as a `task_end` payload in the trace.

Table 3’s E4 rows prefer **strong** replay when `datasets/runs/p0_e4_raw_summary.json` exists (`export_p0_table3.py --e4-raw-summary` default).

## Regimes

Matrix script `scripts/run_p0_e4_controller_matrix.py` runs three named fault envelopes on top of the thin-slice harness (forwarded through adapters into `run_thin_slice`):

| Regime   | Intent |
|----------|--------|
| baseline | No completion drop, no delay faults (deterministic envelope). |
| moderate | Mild `drop_completion_prob` and `delay_fault_prob`, slightly raised `delay_p95_ms`. |
| stress   | Stronger drops/delays plus `reordered_event_fault_prob` and `partial_result_fault_prob`. |

Exact numeric values live in `labtrust_portfolio.p0_e4_matrix.REGIME_FAULT_PARAMS`.

## Do traces differ across controllers?

Answer this using **`datasets/runs/p0_e4_per_seed.jsonl`** and **`datasets/runs/p0_e4_diagnostics.json`**:

- Per-seed lines include `raw_trace_sha256`, `raw_maestro_sha256`, `weak_replay_match`, and `strong_replay_match`.
- Diagnostics include, for each scenario and regime, the **rate** at which the two controllers match on trace / MAESTRO / evidence hashes for the **same seed index**, mean absolute difference in reported p95 latency, and the list of seeds where trace or MAESTRO hashes diverge.

Identical aggregate table rows with divergent hashes indicate **weak metrics**; identical hashes across controllers indicate genuinely identical artifacts under the chosen envelope (or insufficient stress to separate controllers).

## Repair steps

**None** in raw evaluation. Normalized runs only perform declared stripping of adapter-only MAESTRO keys and a full evidence/release rebuild from the copied trace plus stripped MAESTRO. That rebuild may set `schema_validation_ok` from real validation; it is **not** a silent “force true” on raw bundles.

## Commands

```text
PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/run_p0_e4_controller_matrix.py --seeds 30 --scenarios toy_lab_v0,lab_profile_v0 --regimes baseline,moderate,stress --out datasets/runs/p0_e4_controller_matrix.json
python scripts/export_p0_e4_main_table.py --in datasets/runs/p0_e4_raw_summary.json
python scripts/export_p0_e4_diagnostics_table.py --in datasets/runs/p0_e4_diagnostics.json
```

Baseline-only legacy summary (`p0_e4_summary.json`): if `p0_e4_raw_summary.json` already exists from a **multi-regime** matrix run with matching baseline coverage, `run_p0_e4_multi_adapter.py` only rebuilds the legacy JSON and does **not** overwrite the matrix bundle. If the raw summary on disk includes non-baseline regimes but baseline coverage does not match the requested `--seeds`, the script exits with an error instead of clobbering the file.

```text
PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel python scripts/run_p0_e4_multi_adapter.py --seeds 20 --scenarios toy_lab_v0,lab_profile_v0
```
