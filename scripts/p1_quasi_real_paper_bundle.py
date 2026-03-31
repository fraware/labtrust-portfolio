#!/usr/bin/env python3
"""
Generate P1 quasi-real corpus paper bundle: policy×family metrics, FN analysis,
class metrics, dataset stats, inter-annotator summary, case-study packet,
overhead, main table.

Usage (from repo root):
  PYTHONPATH=impl/src python scripts/p1_quasi_real_paper_bundle.py [--corpus PATH] [--out DIR]
"""
from __future__ import annotations

import importlib.util
import json
import math
import platform
import statistics
import sys
import time
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "impl" / "src"))

from labtrust_portfolio.contracts import (  # noqa: E402
    ALLOW,
    validate,
    apply_event_to_state,
    prepare_replay_state,
    finalize_event_observation,
    build_contract_config_from_trace,
)


def _load_contracts_eval_module():
    path = REPO / "scripts" / "contracts_eval.py"
    spec = importlib.util.spec_from_file_location("contracts_eval_p1_bundle", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CE = _load_contracts_eval_module()

POLICIES: list[tuple[str, object | None]] = [
    ("full_contract", None),
    ("occ_only", CE._occ_only_allows),
    ("lease_only", CE._lease_only_allows),
    ("lock_only", CE._lock_only_allows),
    ("state_machine_only", CE._state_machine_only_allows),
    ("practical_heuristic", CE._practical_heuristic_allows),
    ("timestamp_only", CE._timestamp_only_allows),
    ("ownership_only", CE._ownership_only_allows),
    ("accept_all", CE._accept_all),
    ("naive_lww", CE._naive_lww_allows),
]

FAMILIES = (
    "lab_orchestration_partner_like",
    "simulator_documented_semantics",
    "incident_reconstructed",
)

PAPER_CLASSES = (
    "split_brain",
    "stale_write",
    "reorder_violation",
    "unknown_key",
    "invalid_handover",
)


def _sequence_label(corpus_root: Path, path: Path) -> str:
    return CE._sequence_label(corpus_root, path)


def _family_from_label(seq_label: str) -> str:
    return seq_label.split("/")[0] if "/" in seq_label else "overall"


def _percentile(samples: list[float], p: float) -> float | None:
    if not samples:
        return None
    s = sorted(samples)
    n = len(s)
    if n == 1:
        return round(s[0], 4)
    k = (n - 1) * (p / 100.0)
    f = int(math.floor(k))
    c = min(int(math.ceil(k)), n - 1)
    if f == c:
        return round(s[f], 4)
    return round(s[f] + (s[c] - s[f]) * (k - f), 4)


def _map_annotation_class(fc: str) -> str:
    if fc == "reorder_sensitive_invalidity":
        return "reorder_violation"
    if fc == "admissible":
        return "admissible"
    return fc


def _annotation_for_event(data: dict, event_idx: int) -> dict | None:
    for a in data.get("annotations") or []:
        if a.get("event_idx") == event_idx:
            return a
    return None


def _infer_fn_root_cause(
    state: dict,
    event: dict,
    ann_fc_raw: str,
    paper_fc: str,
    contract_cfg: dict,
) -> tuple[str, str]:
    """Return (predicate_that_failed_to_fire, root_cause_category)."""
    payload = event.get("payload", {})
    key = payload.get("task_id") or payload.get("key") or ""
    writer = payload.get("writer") or event.get("actor", {}).get("id", "")
    ownership = state.get("ownership", {})
    last_ts = state.get("_last_ts", {})
    owner = ownership.get(key)
    prev_ts = last_ts.get(key, -1.0)
    ts = float(event.get("ts", 0.0))

    if paper_fc == "unknown_key":
        if not key or not str(key).strip():
            return ("empty_key", "event schema loss during normalization")
        allowed = contract_cfg.get("allowed_keys")
        if allowed is not None and key not in allowed:
            return (
                "declared_key_scope (out-of-scope key; kernel should deny)",
                "annotation / policy mismatch",
            )
        return (
            "unknown_key_expected_but_key_allowed_by_declared_scope",
            "annotation / policy mismatch",
        )

    if paper_fc == "split_brain":
        if owner is None or owner == writer:
            return (
                "split_brain_non_owner_check (replay state has no conflicting owner vs writer)",
                "missing handover evidence in normalized state",
            )
        return (
            "split_brain_predicate_unmet_despite_annotation",
            "annotation / policy mismatch",
        )

    if paper_fc in ("stale_write", "reorder_violation"):
        if prev_ts <= ts:
            return (
                "temporal_regression_check (prev_ts <= event_ts in replay prefix)",
                "ambiguity in event ordering",
            )
        if ann_fc_raw == "reorder_sensitive_invalidity":
            return (
                "reorder/stale_bundle (contract bundles stale+reorder; gold split finer)",
                "annotation / policy mismatch",
            )
        return ("temporal_checks", "insufficient temporal information")

    if paper_fc == "invalid_handover":
        return ("handover_token_or_metadata", "missing handover evidence in normalized state")

    return ("unspecified_predicate", "other")


def _run_trace_policy(
    data: dict,
    policy_name: str,
    policy_fn,
    evaluation_scope: dict,
) -> tuple[int, int, int, int, int, list[float], bool]:
    """tp, fp, fn, false_denials_on_valid, denials_total, latencies_us, exact_trace_match."""
    state = prepare_replay_state(dict(data["initial_state"]))
    contract_cfg = build_contract_config_from_trace(
        data,
        family_id=data.get("scenario_family_id"),
        evaluation_scope=evaluation_scope,
    )
    events = data["events"]
    expected = data["expected_verdicts"]
    tp = fp = fn = 0
    false_denial = 0
    denials = 0
    latencies: list[float] = []
    for i, ev in enumerate(events):
        t0 = time.perf_counter()
        if policy_name == "full_contract":
            ok = validate(state, ev, contract_cfg).verdict == ALLOW
        else:
            ok = policy_fn(state, ev)
        latencies.append((time.perf_counter() - t0) * 1e6)
        exp = expected[i]
        actual = "allow" if ok else "deny"
        if exp == "deny" and actual == "deny":
            tp += 1
        elif exp == "allow" and actual == "deny":
            fp += 1
            false_denial += 1
        elif exp == "deny" and actual == "allow":
            fn += 1
        if ok:
            state = apply_event_to_state(state, ev)
        else:
            denials += 1
        finalize_event_observation(state, ev)
    exact = fn == 0 and fp == 0
    return tp, fp, fn, false_denial, denials, latencies, exact


def _aggregate_rows(
    corpus_root: Path,
    paths: list[Path],
    family_filter: str | None,
    evaluation_scope: dict,
) -> dict[str, dict]:
    """policy_name -> metrics for filtered paths."""
    out: dict[str, dict] = {}
    for policy_name, policy_fn in POLICIES:
        n_traces = 0
        n_events = 0
        exact_match_traces = 0
        tp = fp = fn = 0
        false_denial = 0
        all_lat: list[float] = []
        for path in paths:
            seq = _sequence_label(corpus_root, path)
            fam = _family_from_label(seq)
            if family_filter and fam != family_filter:
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
            if "events" not in data or "expected_verdicts" not in data:
                continue
            n_traces += 1
            ne = len(data["events"])
            n_events += ne
            tpi, fpi, fni, fd, _dn, lat, ex = _run_trace_policy(
                data, policy_name, policy_fn, evaluation_scope
            )
            tp += tpi
            fp += fpi
            fn += fni
            false_denial += fd
            all_lat.extend(lat)
            if ex:
                exact_match_traces += 1
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
        out[policy_name] = {
            "policy_name": policy_name,
            "trace_family": family_filter or "overall",
            "n_traces": n_traces,
            "n_events": n_events,
            "exact_match_traces": exact_match_traces,
            "exact_match_rate": round(exact_match_traces / n_traces, 4) if n_traces else 0.0,
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "false_denial_count_on_valid_events": false_denial,
            "mean_validation_time_us": round(statistics.mean(all_lat), 4) if all_lat else 0.0,
            "p50_validation_time_us": _percentile(all_lat, 50),
            "p95_validation_time_us": _percentile(all_lat, 95),
            "p99_validation_time_us": _percentile(all_lat, 99),
        }
    return out


def _build_policy_by_family(
    corpus_root: Path, all_paths: list[Path], evaluation_scope: dict
) -> list[dict]:
    rows: list[dict] = []
    for fam in FAMILIES:
        agg = _aggregate_rows(corpus_root, all_paths, fam, evaluation_scope)
        for _k, row in sorted(agg.items()):
            rows.append(row)
    agg_o = _aggregate_rows(corpus_root, all_paths, None, evaluation_scope)
    for _k, row in sorted(agg_o.items()):
        rows.append(row)
    return rows


def _fn_analysis_rows(
    corpus_root: Path, paths: list[Path], evaluation_scope: dict
) -> tuple[list[dict], dict]:
    rows: list[dict] = []
    by_family: dict[str, int] = defaultdict(int)
    by_fc: dict[str, int] = defaultdict(int)
    by_rc: dict[str, int] = defaultdict(int)
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        if "events" not in data or "expected_verdicts" not in data:
            continue
        seq = _sequence_label(corpus_root, path)
        fam = _family_from_label(seq)
        trace_id = path.stem
        state = prepare_replay_state(dict(data["initial_state"]))
        contract_cfg = build_contract_config_from_trace(
            data,
            family_id=data.get("scenario_family_id"),
            evaluation_scope=evaluation_scope,
        )
        events = data["events"]
        expected = data["expected_verdicts"]
        for i, ev in enumerate(events):
            if expected[i] != "deny":
                va = validate(state, ev, contract_cfg)
                if va.verdict == ALLOW:
                    state = apply_event_to_state(state, ev)
                finalize_event_observation(state, ev)
                continue
            v = validate(state, ev, contract_cfg)
            if v.verdict != ALLOW:
                finalize_event_observation(state, ev)
                continue
            ann = _annotation_for_event(data, i) or {}
            ann_fc_raw = ann.get("failure_class", "unknown")
            paper_fc = _map_annotation_class(ann_fc_raw)
            pred, rc = _infer_fn_root_cause(state, ev, ann_fc_raw, paper_fc, contract_cfg)
            rows.append({
                "trace_family": fam,
                "trace_id": trace_id,
                "sequence": seq,
                "event_index": i,
                "expected_failure_class": paper_fc,
                "predicate_that_failed_to_fire": pred,
                "root_cause_category": rc,
                "contract_reason_codes_if_any": v.reason_codes,
            })
            by_family[fam] += 1
            by_fc[paper_fc] += 1
            by_rc[rc] += 1
            finalize_event_observation(state, ev)
            state = apply_event_to_state(state, ev)
    summary = {
        "total_false_negatives": len(rows),
        "by_trace_family": dict(by_family),
        "by_failure_class": dict(by_fc),
        "by_root_cause_category": dict(by_rc),
    }
    return rows, summary


def _advance_contract_replay(state: dict, ev: dict, contract_cfg: dict) -> dict:
    """Advance replay state using full_contract admit/deny (matches contracts_eval)."""
    v = validate(state, ev, contract_cfg)
    if v.verdict == ALLOW:
        state = apply_event_to_state(state, ev)
    finalize_event_observation(state, ev)
    return state


def _class_level_metrics_fixed(
    corpus_root: Path, paths: list[Path], evaluation_scope: dict
) -> dict:
    """
    Class metrics: positive = gold deny with annotation mapped to class.
    Replay state follows full_contract (same as contracts_eval).
    """
    policies = {name: fn for name, fn in POLICIES}
    target_policies = [
        "full_contract",
        "practical_heuristic",
        "occ_only",
        "lease_only",
        "lock_only",
        "state_machine_only",
        "timestamp_only",
        "ownership_only",
    ]
    results = []
    for pname in target_policies:
        pfn = policies[pname]
        by_c = {c: {"tp": 0, "fp": 0, "fn": 0, "npos": 0} for c in PAPER_CLASSES}
        for path in paths:
            data = json.loads(path.read_text(encoding="utf-8"))
            if "events" not in data or "expected_verdicts" not in data:
                continue
            state = prepare_replay_state(dict(data["initial_state"]))
            contract_cfg = build_contract_config_from_trace(
                data,
                family_id=data.get("scenario_family_id"),
                evaluation_scope=evaluation_scope,
            )
            events = data["events"]
            expected = data["expected_verdicts"]
            for i, ev in enumerate(events):
                ann = _annotation_for_event(data, i)
                raw_fc = (ann or {}).get("failure_class", "")
                pfc = _map_annotation_class(raw_fc)
                exp = expected[i]
                if exp != "deny":
                    state = _advance_contract_replay(state, ev, contract_cfg)
                    continue
                if pfc == "admissible":
                    state = _advance_contract_replay(state, ev, contract_cfg)
                    continue
                if pfc not in by_c:
                    state = _advance_contract_replay(state, ev, contract_cfg)
                    continue
                by_c[pfc]["npos"] += 1
                if pname == "full_contract":
                    ok = validate(state, ev, contract_cfg).verdict == ALLOW
                else:
                    ok = pfn(state, ev)
                act = "allow" if ok else "deny"
                if exp == "deny" and act == "deny":
                    by_c[pfc]["tp"] += 1
                elif exp == "allow" and act == "deny":
                    by_c[pfc]["fp"] += 1
                elif exp == "deny" and act == "allow":
                    by_c[pfc]["fn"] += 1
                state = _advance_contract_replay(state, ev, contract_cfg)
        row = {"policy": pname, "by_class": {}}
        for c in PAPER_CLASSES:
            d = by_c[c]
            npos = d["npos"]
            if npos == 0:
                row["by_class"][c] = {
                    "n_positive_events": 0,
                    "tp": 0,
                    "fp": 0,
                    "fn": 0,
                    "precision": None,
                    "recall": None,
                    "f1": None,
                }
                continue
            tp, fp, fn = d["tp"], d["fp"], d["fn"]
            prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
            row["by_class"][c] = {
                "n_positive_events": npos,
                "tp": tp,
                "fp": fp,
                "fn": fn,
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1": round(f1, 4),
            }
        results.append(row)
    b14 = [r for r in results if r["policy"] in ("occ_only", "lease_only", "lock_only", "state_machine_only")]
    best = max(
        b14,
        key=lambda r: sum(
            (x.get("f1") or 0.0) * (x.get("n_positive_events") or 0) for x in r["by_class"].values()
        ),
    )
    return {"class_metrics_by_policy": results, "best_b1_b4_weighted_f1_mass": best["policy"]}


def _trace_family_stats(manifest: dict, corpus_root: Path, paths: list[Path]) -> list[dict]:
    fam_meta = {f["family_id"]: f for f in manifest.get("trace_families", [])}
    out = []
    for fam in FAMILIES:
        fps = [p for p in paths if _family_from_label(_sequence_label(corpus_root, p)) == fam]
        meta = fam_meta.get(fam, {})
        n_tr = len(fps)
        ev_counts = []
        n_invalid_traces = 0
        n_invalid_ev = 0
        n_valid_ev = 0
        pos_only = mixed = 0
        handover_traces = 0
        for p in fps:
            d = json.loads(p.read_text(encoding="utf-8"))
            exp = d.get("expected_verdicts", [])
            ne = len(exp)
            ev_counts.append(ne)
            inv = sum(1 for x in exp if x == "deny")
            val = sum(1 for x in exp if x == "allow")
            n_invalid_ev += inv
            n_valid_ev += val
            if inv > 0:
                n_invalid_traces += 1
            if inv == 0:
                pos_only += 1
            elif val > 0 and inv > 0:
                mixed += 1
            desc = (d.get("description") or "").lower()
            if "handover" in desc:
                handover_traces += 1
        ev_counts.sort()
        mid = len(ev_counts) // 2
        median_ev = ev_counts[mid] if ev_counts else 0
        out.append({
            "trace_family": fam,
            "n_traces": n_tr,
            "total_events": sum(ev_counts),
            "mean_events_per_trace": round(statistics.mean(ev_counts), 4) if ev_counts else 0,
            "median_events_per_trace": median_ev,
            "min_events_per_trace": min(ev_counts) if ev_counts else 0,
            "max_events_per_trace": max(ev_counts) if ev_counts else 0,
            "n_traces_with_at_least_one_invalid_mutation": n_invalid_traces,
            "n_invalid_events_total": n_invalid_ev,
            "n_valid_events_total": n_valid_ev,
            "controllers_involved": meta.get("controllers", []),
            "shared_keyed_resources": meta.get("shared_keyed_resources"),
            "shared_resource_key_type": "payload.task_id (string keys; scope per trace initial_state)",
            "n_traces_positive_control_only_allow": pos_only,
            "n_traces_mixed_valid_invalid": mixed,
            "n_traces_description_mentions_handover": handover_traces,
            "manifest_includes_handover_behavior": meta.get("includes_handover_behavior"),
        })
    return out


def _overhead_detail(
    corpus_root: Path, paths: list[Path], best_b1_b4: str, evaluation_scope: dict
) -> dict:
    policies = [
        "full_contract",
        "practical_heuristic",
        best_b1_b4,
        "timestamp_only",
        "ownership_only",
    ]
    pmap = dict(POLICIES)
    wall0 = time.perf_counter()
    detail = {}
    for pname in policies:
        lat: list[float] = []
        for path in paths:
            data = json.loads(path.read_text(encoding="utf-8"))
            if "events" not in data:
                continue
            state = prepare_replay_state(dict(data["initial_state"]))
            contract_cfg = build_contract_config_from_trace(
                data,
                family_id=data.get("scenario_family_id"),
                evaluation_scope=evaluation_scope,
            )
            pfn = pmap[pname]
            for ev in data["events"]:
                t0 = time.perf_counter()
                if pname == "full_contract":
                    ok = validate(state, ev, contract_cfg).verdict == ALLOW
                else:
                    ok = pfn(state, ev)
                lat.append((time.perf_counter() - t0) * 1e6)
                if ok:
                    state = apply_event_to_state(state, ev)
                finalize_event_observation(state, ev)
        detail[pname] = {
            "mean_validation_time_us": round(statistics.mean(lat), 4) if lat else 0.0,
            "p50_validation_time_us": _percentile(lat, 50),
            "p95_validation_time_us": _percentile(lat, 95),
            "p99_validation_time_us": _percentile(lat, 99),
            "n_event_samples": len(lat),
        }
    wall = time.perf_counter() - wall0
    return {
        "policies": detail,
        "total_wall_clock_sec_for_overhead_sampling": round(wall, 4),
        "hardware_runtime": {
            "platform": platform.platform(),
            "python": sys.version.split()[0],
            "processor": platform.processor() or "unknown",
            "hostname": platform.node(),
        },
    }


def _missed_vs_contract(
    corpus_root: Path, paths: list[Path], baseline_name: str, evaluation_scope: dict
) -> int:
    if baseline_name == "full_contract":
        return 0
    pfn = dict(POLICIES)[baseline_name]
    if pfn is None:
        return 0
    n = 0
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        if "events" not in data:
            continue
        state = prepare_replay_state(dict(data["initial_state"]))
        contract_cfg = build_contract_config_from_trace(
            data,
            family_id=data.get("scenario_family_id"),
            evaluation_scope=evaluation_scope,
        )
        for ev in data["events"]:
            v = validate(state, ev, contract_cfg)
            cdeny = v.verdict != ALLOW
            bok = pfn(state, ev)
            if cdeny and bok:
                n += 1
            if v.verdict == ALLOW:
                state = apply_event_to_state(state, ev)
            finalize_event_observation(state, ev)
    return n


def _pick_case_study_path(
    corpus_root: Path, paths: list[Path], evaluation_scope: dict
) -> Path:
    """Choose a trace where upgraded contract denies at least one event B5 would allow."""
    best_score = -1
    best_path = paths[0] if paths else corpus_root / "lab_orchestration_partner_like" / "trace_01.json"
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        if "events" not in data or "expected_verdicts" not in data:
            continue
        cfg = build_contract_config_from_trace(
            data,
            family_id=data.get("scenario_family_id"),
            evaluation_scope=evaluation_scope,
        )
        state = prepare_replay_state(dict(data["initial_state"]))
        events = data["events"]
        expected = data["expected_verdicts"]
        score = 0
        for i, ev in enumerate(events):
            fv = validate(state, ev, cfg)
            b5 = CE._practical_heuristic_allows(state, ev)
            if fv.verdict != ALLOW and b5:
                score += 5
            if fv.verdict != ALLOW and i < len(expected) and expected[i] == "deny":
                score += 1
            if fv.verdict == ALLOW:
                state = apply_event_to_state(state, ev)
            finalize_event_observation(state, ev)
        if score > best_score:
            best_score = score
            best_path = path
    return best_path


def _case_study_packet_from_path(path: Path, evaluation_scope: dict) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    state = prepare_replay_state(dict(data["initial_state"]))
    contract_cfg = build_contract_config_from_trace(
        data,
        family_id=data.get("scenario_family_id"),
        evaluation_scope=evaluation_scope,
    )
    events = data["events"]
    expected = data["expected_verdicts"]
    rows = []
    for i, ev in enumerate(events):
        pl = ev.get("payload", {})
        key = pl.get("task_id", "")
        writer = pl.get("writer") or ev.get("actor", {}).get("id", "")
        norm = {
            "type": ev.get("type"),
            "ts": ev.get("ts"),
            "actor": ev.get("actor"),
            "payload": ev.get("payload"),
        }
        fv = validate(state, ev, contract_cfg)
        b5 = CE._practical_heuristic_allows(state, ev)
        rows.append({
            "event_index": i,
            "timestamp": ev.get("ts"),
            "writer": writer,
            "key": key,
            "action": ev.get("type"),
            "normalized_event": norm,
            "expected_verdict": expected[i],
            "full_contract_verdict": "allow" if fv.verdict == ALLOW else "deny",
            "full_contract_reason_codes": fv.reason_codes,
            "practical_heuristic_B5_verdict": "allow" if b5 else "deny",
        })
        if fv.verdict == ALLOW:
            state = apply_event_to_state(state, ev)
        finalize_event_observation(state, ev)
    excerpt_idx = [0, 1, 2]
    try:
        rel_trace = path.resolve().relative_to(REPO.resolve()).as_posix()
    except ValueError:
        rel_trace = str(path)
    stem = path.stem
    return {
        "case_study_id": f"auto_selected_{stem}",
        "source_trace": rel_trace,
        "initial_state": data["initial_state"],
        "ordered_events": data["events"],
        "per_event": rows,
        "paper_excerpt_event_indices": excerpt_idx,
        "paper_excerpt_events": [rows[i] for i in excerpt_idx],
        "delivery_only_outcome_note": (
            "If only transport/delivery checks apply, each event can be accepted as "
            "well-formed; coordination invalidity is visible only under ownership + temporal rules."
        ),
        "evaluation_independence_note": (
            "allowed_keys for this replay come from evaluation_scope.json + scenario_family_id "
            "+ initial_state keys only, not from gold verdicts."
        ),
    }


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, default=REPO / "datasets" / "contracts_real")
    ap.add_argument("--out", type=Path, default=REPO / "datasets" / "runs" / "p1_quasi_real_paper")
    args = ap.parse_args()
    corpus_root = args.corpus.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    paths = sorted(p for p in corpus_root.rglob("trace_*.json") if p.is_file())
    manifest = json.loads((corpus_root / "manifest.json").read_text(encoding="utf-8"))

    scope_path = corpus_root / "evaluation_scope.json"
    if not scope_path.is_file():
        raise SystemExit(f"Missing required non-gold scope file: {scope_path}")
    evaluation_scope = json.loads(scope_path.read_text(encoding="utf-8"))

    policy_rows = _build_policy_by_family(corpus_root, paths, evaluation_scope)
    (out / "policy_by_family.json").write_text(
        json.dumps({"schema_version": 1, "rows": policy_rows}, indent=2) + "\n",
        encoding="utf-8",
    )

    fn_rows, fn_summary = _fn_analysis_rows(corpus_root, paths, evaluation_scope)
    (out / "false_negative_analysis.json").write_text(
        json.dumps(
            {"schema_version": 1, "rows": fn_rows, "aggregated_summary": fn_summary},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    class_blob = _class_level_metrics_fixed(corpus_root, paths, evaluation_scope)
    overall_metrics = {r["policy_name"]: r for r in policy_rows if r["trace_family"] == "overall"}
    b14n = ("occ_only", "lease_only", "lock_only", "state_machine_only")
    best_b14_f1 = max(b14n, key=lambda n: overall_metrics.get(n, {}).get("f1") or 0.0)
    class_blob["best_b1_b4_by_overall_quasi_real_f1"] = best_b14_f1
    (out / "class_metrics_quasi_real.json").write_text(
        json.dumps({"schema_version": 1, **class_blob}, indent=2) + "\n",
        encoding="utf-8",
    )

    fam_stats = _trace_family_stats(manifest, corpus_root, paths)
    (out / "trace_family_characterization.json").write_text(
        json.dumps({"schema_version": 1, "families": fam_stats}, indent=2) + "\n",
        encoding="utf-8",
    )

    ia_path = corpus_root / "inter_annotator_agreement.json"
    ia = json.loads(ia_path.read_text(encoding="utf-8")) if ia_path.exists() else {}
    adj = ia.get("adjudication") or {}
    disagreement_categories = [
        k for k in adj if k.startswith("resolved_to_") and isinstance(adj.get(k), int)
    ]
    inter_paper = {
        "dataset_id": ia.get("dataset_id"),
        "number_of_traces_doubly_annotated": ia.get("subset_size_traces"),
        "trace_ids_in_doubly_annotated_subset": ia.get("subset_trace_ids"),
        "number_of_events_doubly_annotated": ia.get("event_level", {}).get("total_events_compared"),
        "event_level_agreement_rate": round(
            1.0 - ia.get("event_level", {}).get("disagreement_rate", 0.0), 4
        ),
        "trace_level_agreement_rate": round(
            1.0 - ia.get("trace_level", {}).get("disagreement_rate", 0.0), 4
        ),
        "event_level_disagreement_rate": ia.get("event_level", {}).get("disagreement_rate"),
        "trace_level_disagreement_rate": ia.get("trace_level", {}).get("disagreement_rate"),
        "disagreement_categories_adjudication": ia.get("adjudication"),
        "disagreement_resolution_keys": disagreement_categories,
        "adjudication_process_reference": "datasets/contracts_real/ANNOTATION_PROTOCOL.md",
        "cohen_kappa": None,
        "cohen_kappa_note": (
            "Per-event paired label contingency tables for annotator A vs B are not stored in "
            "inter_annotator_agreement.json; only aggregate agreement counts are available. "
            "Cohen's kappa can be computed if raw paired verdicts are exported."
        ),
        "gold_labels_for_eval": (
            "Post-adjudication labels are the trace JSON fields expected_verdicts and annotations "
            "in datasets/contracts_real/ (single gold column per event after review_lead adjudication)."
        ),
    }
    (out / "inter_annotator_paper.json").write_text(
        json.dumps({"schema_version": 1, **inter_paper}, indent=2) + "\n",
        encoding="utf-8",
    )

    cs_path = _pick_case_study_path(corpus_root, paths, evaluation_scope)
    cs = _case_study_packet_from_path(cs_path, evaluation_scope)
    (out / "case_study_packet.json").write_text(
        json.dumps({"schema_version": 1, **cs}, indent=2) + "\n",
        encoding="utf-8",
    )

    oh = _overhead_detail(corpus_root, paths, best_b14_f1, evaluation_scope)
    oh["best_b1_b4_included"] = best_b14_f1
    (out / "overhead_quasi_real_by_policy.json").write_text(
        json.dumps({"schema_version": 1, **oh}, indent=2) + "\n",
        encoding="utf-8",
    )

    overall = {r["policy_name"]: r for r in policy_rows if r["trace_family"] == "overall"}
    best_b14 = class_blob["best_b1_b4_by_overall_quasi_real_f1"]
    main_rows = []
    seen_policies: set[str] = set()
    for pname in [
        "full_contract",
        "practical_heuristic",
        best_b14,
        "timestamp_only",
        "ownership_only",
        "occ_only",
        "lease_only",
        "lock_only",
        "state_machine_only",
        "accept_all",
        "naive_lww",
    ]:
        if pname not in overall or pname in seen_policies:
            continue
        seen_policies.add(pname)
        r = overall[pname]
        main_rows.append({
            "policy": pname,
            "exact_trace_match_pct": round(100.0 * r["exact_match_rate"], 2),
            "tp": r["tp"],
            "fp": r["fp"],
            "fn": r["fn"],
            "precision": r["precision"],
            "recall": r["recall"],
            "f1": r["f1"],
            "missed_invalid_events_vs_gold_fn": r["fn"],
            "missed_invalid_events_vs_full_contract": _missed_vs_contract(
                corpus_root, paths, pname, evaluation_scope
            ),
            "false_denials_on_valid_events": r["false_denial_count_on_valid_events"],
        })
    (out / "main_table_quasi_real.json").write_text(
        json.dumps({"schema_version": 1, "rows": main_rows}, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "| policy | exact trace match % | TP | FP | FN | precision | recall | F1 | missed invalid (gold FN) | missed vs full_contract | false denials on valid |",
        "|----------|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in main_rows:
        lines.append(
            f"| {row['policy']} | {row['exact_trace_match_pct']} | {row['tp']} | {row['fp']} | {row['fn']} | "
            f"{row['precision']} | {row['recall']} | {row['f1']} | {row['missed_invalid_events_vs_gold_fn']} | "
            f"{row['missed_invalid_events_vs_full_contract']} | {row['false_denials_on_valid_events']} |"
        )
    (out / "main_table_quasi_real.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({"wrote": str(out), "n_traces": len(paths)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
