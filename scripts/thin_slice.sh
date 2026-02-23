#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${1:-datasets/runs/$(date -u +%Y%m%dT%H%M%SZ)_thin_slice}"
mkdir -p "$OUT_DIR"

PYTHONPATH=impl/src python -m labtrust_portfolio run-thinslice --out-dir "$OUT_DIR"
echo "Wrote thin-slice artifacts to: $OUT_DIR"
