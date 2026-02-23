# Datasets policy

- `datasets/runs/` are **mutable** working directories (local runs, scratch outputs).
- `datasets/releases/` are **immutable** release snapshots (content-addressed or stamped with release IDs).

Both directories are ignored by default in `.gitignore`, except `.gitkeep` placeholders.

If you publish a dataset, publish **a release manifest** + **evidence bundle** referencing the exact artifacts and hashes.
