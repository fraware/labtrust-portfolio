#!/usr/bin/env python3
"""Copy a run to datasets/releases/<release_id>/ and write release manifest.

Usage (from repo root):
  PYTHONPATH=impl/src python scripts/release_dataset.py <run_dir> <release_id>
  PYTHONPATH=impl/src python -m labtrust_portfolio release-dataset <run_dir> <release_id>
"""
from __future__ import annotations

import sys
from pathlib import Path

# Allow running script without installing package
repo = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo / "impl" / "src"))

from labtrust_portfolio.cli import main

if __name__ == "__main__":
    sys.argv = ["labtrust_portfolio", "release-dataset"] + sys.argv[1:]
    raise SystemExit(main())
