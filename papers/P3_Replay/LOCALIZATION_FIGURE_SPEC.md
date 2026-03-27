# First-Divergence Localization Figure Spec

This specification defines `figures/p3_first_divergence_timeline.png` for the P3 paper.

## Purpose

Make first-divergence localization visually obvious in under 10 seconds for reviewers.

## Figure concept

- Horizontal event timeline (`seq=0 ... seq=n`)
- Two tracks per event:
  - committed hash (`state_hash_after`)
  - replayed hash
- First mismatch event highlighted at `seq=i*`
- Witness slice band centered on `i*` (e.g., `i*-1` to `i*+1`)
- Post-divergence events visually de-emphasized with label: "not required to establish first contract violation"

## Required annotations

- `i*` marker with text: "first divergence"
- callout with `expected_hash` vs `got_hash`
- short legend:
  - green = hash match
  - red = hash mismatch
  - gray = downstream events

## Data source

- Use one representative trap row from `datasets/runs/replay_eval/summary.json`:
  - prefer `mixed_failure_trap` or `long_horizon_trap`
- Pull witness context from:
  - `per_trace[].witness_slice`
  - `per_trace[].divergence_at_seq`
  - `per_trace[].expected_divergence_at_seq`

## Script integration

- Exported by `python scripts/export_p3_first_divergence_timeline.py`.
- Default asset path: `papers/P3_Replay/figures/p3_first_divergence_timeline.png` with sidecar JSON metadata.
- The figure is now wired into `papers/P3_Replay/DRAFT.tex` via `\IfFileExists{figures/p3_first_divergence_timeline.png}{...}`.

## Caption guidance

Recommended caption:

> First-divergence localization timeline: committed vs replayed state hashes by event sequence. Replay localizes the first contract violation at `seq=i*`; witness context is shown around `i*`, while downstream events are de-emphasized as unnecessary to establish the first violation.
