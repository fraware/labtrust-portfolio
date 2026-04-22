"""Normalization records removals with reason codes and remains narrow."""

from __future__ import annotations

from labtrust_portfolio.p0_e4_matrix import strip_maestro_to_v02


def test_strip_maestro_records_adapter_key() -> None:
    before = {
        "version": "0.2",
        "run_id": "r1",
        "scenario_id": "toy_lab_v0",
        "run_outcome": "success_safe",
        "metrics": {"tasks_completed": 4, "coordination_messages": 0},
        "safety": {},
        "coordination_efficiency": {},
        "faults": {},
        "notes": "n",
        "metadata_rep_cps": True,
    }
    after, removed = strip_maestro_to_v02(before)
    assert "metadata_rep_cps" not in after
    assert any(x.get("key") == "metadata_rep_cps" for x in removed)
    assert all(x.get("reason_code") == "adapter_only_top_level_field" for x in removed)


def test_strip_maestro_no_added_or_modified_keys() -> None:
    before = {
        "version": "0.2",
        "run_id": "r1",
        "scenario_id": "toy_lab_v0",
        "run_outcome": "success_safe",
        "metrics": {"tasks_completed": 4, "coordination_messages": 0},
        "safety": {},
        "coordination_efficiency": {},
        "faults": {},
        "notes": "n",
    }
    after, removed = strip_maestro_to_v02(before)
    assert removed == []
    assert set(after.keys()) == set(before.keys())
    for k in before:
        assert after[k] == before[k]
