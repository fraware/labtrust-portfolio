"""Guardrails: E4 scripts must not reintroduce hidden evidence patching on the raw path."""

from __future__ import annotations

from pathlib import Path


def test_multi_adapter_script_has_no_schema_ok_bypass() -> None:
    repo = Path(__file__).resolve().parents[1]
    text = (repo / "scripts" / "run_p0_e4_multi_adapter.py").read_text(encoding="utf-8")
    assert "schema_validation_ok" not in text
    assert "_fix_evidence" not in text
    assert "_align_maestro" not in text


def test_matrix_module_has_no_forced_schema_true_patch() -> None:
    repo = Path(__file__).resolve().parents[1]
    text = (repo / "impl" / "src" / "labtrust_portfolio" / "p0_e4_matrix.py").read_text(encoding="utf-8")
    assert '["schema_validation_ok"] = True' not in text
