"""
W3 Evidence bundle: test that impl output satisfies the same conditions as Lean W3 spec.
Labtrust formal/lean Labtrust.W3 defines: required artifact paths, SHA256 format,
verification.schema_validation_ok, verification.replay_ok. This test asserts the impl
evidence bundle (or a minimal one) meets those conditions so the Lean spec aligns with impl.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

# W3 conditions (mirror formal/lean/Labtrust/W3EvidenceBundle.lean)
REQUIRED_PATHS = ["trace.json", "maestro_report.json", "evidence_bundle.json"]


def valid_sha256_format(h: str) -> bool:
    """64-char hex (W3 validSha256Format)."""
    return len(h) == 64 and all(c in "0123456789abcdef" for c in h.lower())


def has_required_artifacts(artifacts: list[dict]) -> bool:
    """All required paths present (W3 hasRequiredArtifacts)."""
    paths = {a.get("path", "").split("/")[-1] for a in artifacts}
    return all(p in paths for p in REQUIRED_PATHS)


def all_hashes_valid_format(artifacts: list[dict]) -> bool:
    """Every artifact has valid SHA256 (W3 allHashesValidFormat)."""
    return all(valid_sha256_format(a.get("sha256", "")) for a in artifacts)


def verify_bundle(bundle: dict) -> tuple[bool, list[str]]:
    """W3-style verify: OK iff required present, hashes valid, verification flags true."""
    reasons = []
    artifacts = bundle.get("artifacts", [])
    if not has_required_artifacts(artifacts):
        missing = [p for p in REQUIRED_PATHS if not any(p in str(a.get("path", "")) for a in artifacts)]
        reasons.append(f"missing required artifacts: {missing}")
    if not all_hashes_valid_format(artifacts):
        reasons.append("invalid SHA256 format in artifacts")
    ver = bundle.get("verification", {})
    if not ver.get("schema_validation_ok", False):
        reasons.append("schema_validation_ok is false")
    if not ver.get("replay_ok", False):
        reasons.append("replay_ok is false")
    return (len(reasons) == 0, reasons)


class TestW3EvidenceBundleConditions(unittest.TestCase):
    """Assert impl evidence bundle satisfies W3 spec conditions."""

    def test_verify_bundle_ok_when_complete(self) -> None:
        """A complete bundle (required paths, valid hashes, verification ok) passes."""
        bundle = {
            "version": "0.1",
            "run_id": "test",
            "kernel_version": "0.1",
            "artifacts": [
                {"path": "trace.json", "sha256": "a" * 64, "schema_id": "https://example.org/trace"},
                {"path": "maestro_report.json", "sha256": "b" * 64, "schema_id": "https://example.org/maestro"},
                {"path": "evidence_bundle.json", "sha256": "c" * 64, "schema_id": "https://example.org/evidence"},
            ],
            "verification": {"schema_validation_ok": True, "replay_ok": True, "replay_diagnostics": ""},
        }
        ok, reasons = verify_bundle(bundle)
        self.assertTrue(ok, reasons)
        self.assertEqual(reasons, [])

    def test_verify_bundle_fail_when_missing_artifact(self) -> None:
        """Missing a required path fails."""
        bundle = {
            "version": "0.1",
            "run_id": "test",
            "kernel_version": "0.1",
            "artifacts": [
                {"path": "trace.json", "sha256": "a" * 64, "schema_id": "x"},
            ],
            "verification": {"schema_validation_ok": True, "replay_ok": True, "replay_diagnostics": ""},
        }
        ok, reasons = verify_bundle(bundle)
        self.assertFalse(ok)
        self.assertTrue(any("missing" in r for r in reasons))

    def test_impl_build_evidence_bundle_produces_w3_compatible_bundle(self) -> None:
        """build_evidence_bundle produces artifacts with valid SHA256 and structure."""
        try:
            from labtrust_portfolio.evidence import build_evidence_bundle
        except ImportError:
            self.skipTest("labtrust_portfolio.evidence not available")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "trace.json").write_text('{"version":"0.1","events":[]}')
            (root / "maestro_report.json").write_text('{"metrics":{}}')
            artifacts = [root / "trace.json", root / "maestro_report.json"]
            schema_ids = ["https://example.org/trace", "https://example.org/maestro"]
            bundle = build_evidence_bundle(
                "run1", "0.1", artifacts, schema_ids,
                schema_validation_ok=True, replay_ok=True, replay_diag="",
            )
            self.assertIn("artifacts", bundle)
            self.assertIn("verification", bundle)
            self.assertTrue(all_hashes_valid_format(bundle["artifacts"]))
            self.assertTrue(bundle["verification"]["schema_validation_ok"])
            self.assertTrue(bundle["verification"]["replay_ok"])
            # W3 requiredPaths includes evidence_bundle.json; impl may build from 2 artifacts
            # So we only assert hashes and verification; required paths check is for full bundle.
            self.assertEqual(len(bundle["artifacts"]), 2)
