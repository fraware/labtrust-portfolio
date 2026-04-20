# LabTrust Kernel

The kernel is the shared spine of the portfolio: versioned JSON Schemas and supporting documents that define the only stable interfaces across papers.

## Artifacts

### JSON Schemas (under `kernel/**/*.schema.json`)

| Schema | Path | Description |
|--------|------|-------------|
| TRACE | trace/TRACE.v0.1.schema.json | Execution trace format for replay and evaluation |
| MAESTRO_REPORT | eval/MAESTRO_REPORT.v0.1.schema.json; eval/MAESTRO_REPORT.v0.2.schema.json | Benchmark evaluation report (v0.1 legacy; **v0.2** adds recovery timing, safety block, coordination efficiency, run_outcome) |
| EVIDENCE_BUNDLE | mads/EVIDENCE_BUNDLE.v0.1.schema.json | Admissible evidence bundle for verification |
| RELEASE_MANIFEST | policy/RELEASE_MANIFEST.v0.1.schema.json | Release artifact manifest |
| COORD_CONTRACT | contracts/COORD_CONTRACT.v0.1.schema.json | Coordination contract schema |
| REP_CPS_PROFILE | rep_cps/REP_CPS_PROFILE.v0.1.schema.json | REP-CPS protocol profile |
| TYPED_PLAN | llm_runtime/TYPED_PLAN.v0.1.schema.json | Typed plan schema for LLM runtime |
| ASSURANCE_PACK | assurance_pack/ASSURANCE_PACK.v0.1.schema.json | Assurance pack template |

### Supporting documents

- `mads/VERIFICATION_MODES.v0.1.md` — Verification postures (public vs restricted auditability).
- `trace/REPLAY_LEVELS.v0.1.md` — Replay fidelity levels (L0/L1/L2).
- `interop/OPC_UA_LADS_MAPPING.v0.1.md` — OPC UA LADS interop mapping.

### Version file

- `VERSION` — Current kernel version (e.g. 0.1).

## Version bump process

1. Update the schema `$id` version segment (e.g. `v0.1` → `v0.2`) for any changed schema.
2. Update `kernel/VERSION` if releasing a new kernel version.
3. Add an entry to [CHANGELOG.md](CHANGELOG.md) describing the breaking change.

Validate the kernel from the repo root:

```bash
python scripts/validate_kernel.py
```
