# Bounded Review Packet

This folder is a bounded-access external reviewer packet.

## Contents
- `claim.json`: accountability claim under review
- `assurance_pack.json`: machine-checkable assurance pack
- `trace.json`: runtime trace artifact (if present in run dir)
- `evidence_bundle.json`: evidence bundle artifact (if present)
- `release_manifest.json`: release manifest (if present)
- `review_output.json`: checker verdict and failure codes
- `review_packet_summary.json`: compact reviewer-facing summary
- `packet_manifest.json`: provenance and checksums

## Reviewer intent
A third-party reviewer can validate what was checked, what passed/failed, and what remains out of scope under bounded artifact access.
