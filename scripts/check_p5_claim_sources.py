#!/usr/bin/env python3
"""
Fail loudly if P5 frozen artifacts contradict the NeurIPS claim lock or if prose upgrades
exploratory / negative results into prohibited universal claims.

Loads:
  papers/P5_ScalingLaws/claim_sources.yaml (optional but recommended)
  Canonical JSON under datasets/runs/
Scans:
  papers/P5_ScalingLaws/DRAFT.md, README.md, AUTHORING_PACKET.md
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None


def _load_json(p: Path) -> dict[str, Any]:
    return json.loads(p.read_text(encoding="utf-8"))


PROSE_SCAN_FILES = [
    REPO / "papers" / "P5_ScalingLaws" / "DRAFT.md",
    REPO / "papers" / "P5_ScalingLaws" / "README.md",
    REPO / "papers" / "P5_ScalingLaws" / "AUTHORING_PACKET.md",
    REPO / "papers" / "P5_ScalingLaws" / "claims.yaml",
]

TIER_D_PATTERNS = [
    re.compile(r"\bwe establish\b.*\b(cps )?scaling laws?\b", re.IGNORECASE | re.DOTALL),
    re.compile(r"\bestablishes (a |)(general |)(cps )?scaling laws?\b", re.IGNORECASE),
    re.compile(r"\bpredict(s|ed|ing)? held-out scenarios robustly\b", re.IGNORECASE),
    re.compile(r"\brecommender selects optimal\b", re.IGNORECASE),
    re.compile(r"\barchitecture-selection mechanism\b", re.IGNORECASE),
    re.compile(r"\bdecision authority\b", re.IGNORECASE),
    re.compile(r"\boracle baselines? are valid baselines\b", re.IGNORECASE),
    re.compile(r"\boracle baselines? as (valid|appropriate)\b", re.IGNORECASE),
    re.compile(r"\bmore agents always hurt\b", re.IGNORECASE),
    re.compile(r"\brobustly estimate(?:s|d)? collapse\b", re.IGNORECASE),
    re.compile(r"\bscaling laws? (are |is )?established\b", re.IGNORECASE),
    re.compile(r"\bestablished (a |)(general |)(cps )?scaling laws?\b", re.IGNORECASE),
]

DEPLOYMENT_RERECOMMEND_RE = re.compile(
    r"\b(recommends|selects optimal|architecture-selection mechanism|decision authority)\b",
    re.IGNORECASE,
)


def _scan_prose() -> list[str]:
    errors: list[str] = []
    for path in PROSE_SCAN_FILES:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(REPO)
        for rx in TIER_D_PATTERNS:
            if rx.search(text):
                errors.append(f"{rel}: prose matches prohibited pattern {rx.pattern!r}")
        for m in DEPLOYMENT_RERECOMMEND_RE.finditer(text):
            start = max(0, m.start() - 200)
            end = min(len(text), m.end() + 200)
            window = text[start:end].lower()
            if "exploratory" in window or "not deployment-ready" in window:
                continue
            errors.append(
                f"{rel}: '{m.group(0)}' without nearby 'exploratory' or 'not deployment-ready'",
            )
    return errors


def _assert_protocol(path: Path, label: str) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"Missing {label}: {path}"]
    data = _load_json(path)
    folds = data.get("held_out_results") or []
    missing = [f for f in folds if f.get("regression_mae") is None]
    overall_reg = data.get("overall_regression_mae")
    sc = data.get("success_criteria_met") or {}
    trig = sc.get("trigger_met")
    if missing:
        if overall_reg is not None:
            errors.append(f"{label}: null regression folds but overall_regression_mae is not null")
        if trig is True:
            errors.append(f"{label}: null regression folds but trigger_met is true")
    else:
        if overall_reg is None and sc.get("regression_protocol_valid", True):
            errors.append(f"{label}: all folds finite but overall_regression_mae is null")
    return errors


def main() -> int:
    scenario_p = REPO / "datasets" / "runs" / "scaling_eval" / "heldout_results.json"
    family_p = REPO / "datasets" / "runs" / "scaling_eval_family" / "heldout_results.json"
    rec_p = REPO / "datasets" / "runs" / "scaling_recommend" / "recommendation_eval.json"
    tables_p = REPO / "papers" / "P5_ScalingLaws" / "generated_tables.md"

    errors: list[str] = []
    errors.extend(_scan_prose())

    if not scenario_p.exists():
        errors.append(f"Missing scenario heldout: {scenario_p}")
        print("\n".join(errors) or "ok")
        return 1

    scenario = _load_json(scenario_p)
    scenario_sc = scenario.get("success_criteria_met") or {}
    if scenario_sc.get("trigger_met") is not False:
        errors.append("scenario-heldout: expected success_criteria_met.trigger_met == false")
    reg_mae = scenario.get("overall_regression_mae")
    feat_mae = scenario.get("overall_feat_baseline_mae")
    if reg_mae is not None and feat_mae is not None:
        if not (reg_mae > feat_mae - 1e-9):
            errors.append(
                "scenario-heldout: regression MAE should exceed num-tasks bucket MAE on freeze",
            )

    if family_p.exists():
        family = _load_json(family_p)
        fsc = family.get("success_criteria_met") or {}
        if fsc.get("trigger_met") is not True:
            errors.append("family-heldout: expected success_criteria_met.trigger_met == true")
        r2 = family.get("overall_regression_mae")
        f2 = family.get("overall_feat_baseline_mae")
        if r2 is not None and f2 is not None and not (r2 < f2 - 1e-9):
            errors.append(
                "family-heldout: regression should beat num-tasks bucket MAE on freeze",
            )

    def _trigger_independent_of_oracle(path: Path, label: str) -> list[str]:
        """trigger_met must follow admissible AND only, never oracle."""
        out: list[str] = []
        if not path.exists():
            return out
        d = _load_json(path)
        sc = d.get("success_criteria_met") or {}
        trig = sc.get("trigger_met")
        adm = bool(
            sc.get("beat_global_mean_out_of_sample")
            and sc.get("beat_feature_baseline_out_of_sample")
            and sc.get("beat_regime_baseline_out_of_sample"),
        )
        if sc.get("regression_protocol_valid", True) and trig is not None:
            if bool(trig) != adm:
                out.append(
                    f"{label}-heldout: trigger_met must equal AND of admissible beats "
                    f"(oracle excluded; got trigger={trig} admissible_and={adm})",
                )
        return out

    for p, lbl in (
        (scenario_p, "scenario"),
        (family_p, "family"),
        (
            REPO / "datasets" / "runs" / "scaling_eval_regime" / "heldout_results.json",
            "regime",
        ),
        (
            REPO / "datasets" / "runs" / "scaling_eval_agent_count" / "heldout_results.json",
            "agent_count",
        ),
        (
            REPO / "datasets" / "runs" / "scaling_eval_fault" / "heldout_results.json",
            "fault",
        ),
    ):
        errors.extend(_assert_protocol(p, lbl))
        errors.extend(_trigger_independent_of_oracle(p, lbl))

    sec = scenario.get("secondary_targets") or {}
    tax = sec.get("coordination_tax_proxy") or {}
    err_amp = sec.get("error_amplification_proxy") or {}
    treg = tax.get("overall_regression_mae")
    ereg = err_amp.get("overall_regression_mae")
    if (
        treg is not None
        and ereg is not None
        and not (treg < ereg - 1e-9)
    ):
        errors.append(
            "secondary_targets: coordination_tax_proxy should be more predictable "
            "(lower MAE) than error_amplification_proxy on freeze",
        )

    tax_sc = tax.get("success_criteria_met") or {}
    if scenario_sc.get("trigger_met") is False and tax_sc.get("trigger_met") is not True:
        errors.append(
            "scenario-heldout freeze: expect coordination_tax_proxy secondary trigger_met "
            "true while tasks_completed trigger is false",
        )
    if scenario_sc.get("trigger_met") is True and tax_sc.get("trigger_met") is not True:
        errors.append(
            "unexpected: tasks_completed trigger_met true but coordination_tax_proxy "
            "secondary trigger false",
        )

    if rec_p.exists():
        rec = _load_json(rec_p)
        if rec.get("claim_status") != "exploratory":
            errors.append("recommendation_eval: claim_status must be 'exploratory'")
        if rec.get("deployment_claim_allowed") is not False:
            errors.append(
                "recommendation_eval: deployment_claim_allowed must be false",
            )
        if rec.get("reason") != "low regime-selection accuracy under frozen evaluation":
            errors.append(
                "recommendation_eval: reason must match frozen exploratory disclosure",
            )

    if tables_p.exists():
        gt = tables_p.read_text(encoding="utf-8")
        has_tasks = ("Δ tasks 1→8" in gt) or ("d tasks 1->8" in gt)
        has_tax = ("Δ coordination tax 1→8" in gt) or ("d coord. tax 1->8" in gt)
        if not has_tasks or not has_tax:
            errors.append(
                "generated_tables.md must include title-grounding columns "
                "for both tasks and coordination tax deltas",
            )
        if "## Main Table 4" in gt and (
            "much more predictable than throughput" not in gt.lower()
            or "error amplification" not in gt.lower()
        ):
            errors.append(
                "generated_tables.md Main Table 4 must state coordination tax predictability "
                "vs throughput and error amplification (regenerate export_scaling_tables.py)",
            )
        if "scaling_fit=exploratory" not in gt.lower() and "exploratory log-log scaling fit" not in gt.lower():
            errors.append("generated_tables.md should label scaling_fit as exploratory")
        if "Collapse prevalence" not in gt or "Brier score" not in gt:
            errors.append(
                "generated_tables.md appendix must include collapse prevalence + Brier columns",
            )
    else:
        errors.append(f"Missing {tables_p}")

    cs_yaml = REPO / "papers" / "P5_ScalingLaws" / "claim_sources.yaml"
    if cs_yaml.exists() and yaml is not None:
        raw = yaml.safe_load(cs_yaml.read_text(encoding="utf-8")) or {}
        if raw.get("claims", {}).get("grid_size", {}).get("value") != scenario.get("total_rows"):
            errors.append(
                "claim_sources.yaml grid_size.value must match heldout total_rows",
            )

    if errors:
        print("check_p5_claim_sources FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("check_p5_claim_sources: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
