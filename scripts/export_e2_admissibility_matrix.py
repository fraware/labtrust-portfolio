#!/usr/bin/env python3
"""
Export E2 redaction admissibility matrix for the draft. Rows: admissibility condition.
Columns: full trace vs redacted trace. Cells: checkable (yes/no) or N/A.
Usage: python scripts/export_e2_admissibility_matrix.py
"""
from __future__ import annotations

def main() -> int:
    lines = [
        "## E2 Redaction admissibility matrix",
        "",
        "| Admissibility condition | Full trace | Redacted trace |",
        "|-------------------------|------------|----------------|",
        "| schema_validation_ok    | yes        | yes            |",
        "| integrity_ok (hashes)    | yes        | yes            |",
        "| replay_ok (L0/L1)       | yes        | no (audit-only)|",
        "| PONR coverage           | yes        | N/A (structure only) |",
        "",
        "Redacted trace preserves event order, timestamps, and state_hash_after; payloads are "
        "replaced by content-addressed refs. Replay is not run on redacted trace (replay expects "
        "full payloads). See kernel/mads/VERIFICATION_MODES.v0.1.md.",
    ]
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
