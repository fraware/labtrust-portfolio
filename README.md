# LabTrust Portfolio (MADS-CPS + MAESTRO/Replay release train)

This repository is a **portfolio workspace** for a coherent paper + artifact program around
**assurance, reproducibility, and evaluation of large-scale agentic cyber-physical systems (CPS)**.

## What exists today (v0.1)
- `kernel/` — versioned, strict JSON Schemas (placeholders but stable IDs)
- `impl/` — minimal runnable thin-slice pipeline producing: TRACE → MAESTRO report → Replay result → Evidence bundle
- `bench/` — benchmark scaffolding (MAESTRO + Replay)
- `papers/` — paper-by-paper authoring packets (outline, claims, experiments, artifacts, kill-criteria, venues)
- `datasets/` — run and release outputs (policy documented)

## Quickstart
Validate kernel schemas:
```bash
python scripts/validate_kernel.py
```

Run the thin slice end-to-end:
```bash
PYTHONPATH=impl/src python -m labtrust_portfolio run-thinslice --out-dir datasets/runs/demo
```

Run tests:
```bash
PYTHONPATH=impl/src python -m unittest discover -s tests
```

## Design constraint
The **kernel** is the shared spine. Papers may add optional fields, but **breaking changes require a version bump**.
