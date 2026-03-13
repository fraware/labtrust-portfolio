"""
P5 Scaling: feature extraction from scenario + trace, dataset builder, minimal predictor.
Task features (depth, tool density, scenario); response (tasks_completed, p95, etc.).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .scenario import load_scenario, get_scenario_task_names


def extract_features_from_scenario(scenario_id: str) -> Dict[str, Any]:
    """Extract task features from scenario YAML: num_tasks, scenario_id, task_names, tool_density, fault_density, sequential_depth_proxy, resource_coupling_index."""
    try:
        scenario = load_scenario(scenario_id)
        names = get_scenario_task_names(scenario)
        num_tasks = len(names)
        num_faults = len(scenario.get("faults", []))
        rg = scenario.get("resource_graph") or {}
        instruments = rg.get("instruments") or []
        stations = rg.get("stations") or []
        num_instruments = len(instruments)
        num_stations = len(stations)
        num_resources = num_instruments + num_stations
        tool_density = num_tasks / max(1, num_resources) if num_resources else float(num_tasks)
        fault_density = num_faults / max(1, num_tasks)
        sequential_depth_proxy = num_tasks
        resource_coupling_index = num_resources
        return {
            "scenario_id": scenario_id,
            "num_tasks": num_tasks,
            "task_names": names,
            "num_faults": num_faults,
            "tool_density": tool_density,
            "fault_density": fault_density,
            "sequential_depth_proxy": sequential_depth_proxy,
            "resource_coupling_index": resource_coupling_index,
        }
    except (FileNotFoundError, ValueError):
        return {
            "scenario_id": scenario_id,
            "num_tasks": 0,
            "task_names": [],
            "num_faults": 0,
            "tool_density": 0.0,
            "fault_density": 0.0,
            "sequential_depth_proxy": 0,
            "resource_coupling_index": 0,
        }


def extract_features_from_trace(trace: Dict[str, Any]) -> Dict[str, Any]:
    """Extract from trace: event_count, scenario_id, seed."""
    events = trace.get("events", [])
    return {
        "scenario_id": trace.get("scenario_id", ""),
        "seed": trace.get("seed", 0),
        "event_count": len(events),
    }


def extract_response_from_report(report: Dict[str, Any]) -> Dict[str, Any]:
    """Extract response variables from MAESTRO report."""
    m = report.get("metrics", {})
    faults = report.get("faults", {})
    return {
        "tasks_completed": m.get("tasks_completed", 0),
        "coordination_messages": m.get("coordination_messages", 0),
        "task_latency_ms_p95": m.get("task_latency_ms_p95", 0.0),
        "recovery_ok": faults.get("recovery_ok", True),
        "fault_injected": faults.get("fault_injected", False),
    }


# Collapse threshold: tasks_completed below this or recovery_ok False counts as collapse.
COLLAPSE_TASKS_THRESHOLD = 2


def build_dataset_from_runs(runs_dir: Path) -> List[Dict[str, Any]]:
    """
    Build modeling table from run directories: each run has trace.json and
    maestro_report.json. Returns list of rows with features + response.
    Adds derived 'collapse' (True if tasks_completed < threshold or not recovery_ok).
    """
    rows = []
    for run_path in runs_dir.rglob("trace.json"):
        report_path = run_path.parent / "maestro_report.json"
        if not report_path.exists():
            continue
        trace = json.loads(run_path.read_text(encoding="utf-8"))
        report = json.loads(report_path.read_text(encoding="utf-8"))
        scenario_id = trace.get("scenario_id", "")
        feats = extract_features_from_scenario(scenario_id)
        feats.update(extract_features_from_trace(trace))
        response = extract_response_from_report(report)
        feats["response"] = response
        tc = response.get("tasks_completed", 0)
        recovery_ok = response.get("recovery_ok", True)
        feats["collapse"] = (
            tc < COLLAPSE_TASKS_THRESHOLD or not recovery_ok
        )
        rows.append(feats)
    return rows


def predict_baseline_mean(rows: List[Dict[str, Any]], target: str = "tasks_completed") -> float:
    """Baseline predictor: mean of target in training rows."""
    if not rows:
        return 0.0
    vals = [r.get("response", {}).get(target, 0) for r in rows]
    return sum(vals) / len(vals)


def predict_by_scenario(
    rows: List[Dict[str, Any]],
    scenario_id: str,
    target: str = "tasks_completed",
) -> float:
    """Predict for scenario: mean of target among rows with same scenario_id."""
    subset = [r for r in rows if r.get("scenario_id") == scenario_id]
    return predict_baseline_mean(subset, target)


def predict_prior_model(row: Dict[str, Any], target: str = "tasks_completed") -> float:
    """
    Prior coordination model: predict tasks_completed from num_tasks only
    (simple upper-bound heuristic: completion cannot exceed num_tasks).
    Used as a baseline from coordination literature (task-count scaling).
    """
    if target != "tasks_completed":
        return 0.0
    num_tasks = row.get("num_tasks", 0) or 0
    num_faults = row.get("num_faults", 0) or 0
    # Heuristic: completed ≈ num_tasks * (1 - small penalty per fault)
    penalty = min(0.2, 0.05 * num_faults)
    return max(0.0, float(num_tasks) * (1.0 - penalty))


def _ols_fit(
    rows: List[Dict[str, Any]],
    target: str,
    feature_cols: List[str],
) -> Any:
    """
    Closed-form OLS: beta = (X'X)^{-1} X'y.
    Returns (coefs, intercept) or None if singular/empty.
    """
    if not rows or not feature_cols:
        return None
    y_vals = [r.get("response", {}).get(target, 0) for r in rows]
    X_rows = []
    for r in rows:
        row = [1.0]  # intercept column
        for col in feature_cols:
            row.append(float(r.get(col, 0)))
        X_rows.append(row)
    n = len(X_rows)
    k = len(feature_cols) + 1
    if n < k:
        return None
    # X @ beta = y; X is n x k, y is n x 1. beta = (X'X)^{-1} X' y
    X = X_rows
    y = y_vals
    # X'X (k x k)
    XtX = [[0.0] * k for _ in range(k)]
    for i in range(k):
        for j in range(k):
            XtX[i][j] = sum(X[row][i] * X[row][j] for row in range(n))
    # X'y (k x 1)
    Xty = [sum(X[row][i] * y[row] for row in range(n)) for i in range(k)]
    # Invert XtX (simple 2x2 or 3x3; for larger use numpy if available)
    try:
        inv = _invert_2x2_or_3x3(XtX)
        if inv is None:
            return None
        beta = [sum(inv[i][j] * Xty[j] for j in range(k)) for i in range(k)]
        return (beta[1:], beta[0])  # coefs, intercept
    except Exception:
        return None


def _invert_2x2_or_3x3(M: List[List[float]]) -> Any:
    """Invert 2x2 or 3x3 matrix; returns None if singular."""
    size = len(M)
    if size == 2:
        a, b, c, d = M[0][0], M[0][1], M[1][0], M[1][1]
        det = a * d - b * c
        if abs(det) < 1e-12:
            return None
        return [[d / det, -b / det], [-c / det, a / det]]
    if size == 3:
        # 3x3 inverse via cofactors
        a, b, c = M[0][0], M[0][1], M[0][2]
        d, e, f = M[1][0], M[1][1], M[1][2]
        g, h, i = M[2][0], M[2][1], M[2][2]
        det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
        if abs(det) < 1e-12:
            return None
        inv = [
            [(e * i - f * h) / det, (c * h - b * i) / det, (b * f - c * e) / det],
            [(f * g - d * i) / det, (a * i - c * g) / det, (c * d - a * f) / det],
            [(d * h - e * g) / det, (b * g - a * h) / det, (a * e - b * d) / det],
        ]
        return inv
    return None


def fit_linear_predictor(
    rows: List[Dict[str, Any]],
    target: str = "tasks_completed",
    feature_cols: List[str] = None,
) -> Any:
    """
    Fit linear model on rows; feature_cols default ["num_tasks", "num_faults"].
    Tries full feature set first; falls back to num_tasks-only if singular or n < k
    so that fewer rows are required (n >= 2). Returns a callable predict(feature_dict)
    -> float, or None if fit failed.
    """
    if feature_cols is None:
        feature_cols = ["num_tasks", "num_faults"]
    result = _ols_fit(rows, target, feature_cols)
    used_cols = feature_cols
    if result is None and feature_cols != ["num_tasks"]:
        result = _ols_fit(rows, target, ["num_tasks"])
        used_cols = ["num_tasks"]
    if result is None:
        return None
    coefs, intercept = result

    def predict(feat: Dict[str, Any]) -> float:
        val = intercept
        for i, col in enumerate(used_cols):
            val += coefs[i] * float(feat.get(col, 0))
        return val

    return predict


def fit_tree_stump_predictor(
    rows: List[Dict[str, Any]],
    target: str = "tasks_completed",
    feature_col: str = "num_tasks",
) -> Any:
    """
    Stump baseline: split on feature_col at median; return callable predict(feat) -> float
    that returns mean of target for the branch (left = feat <= median, right = feat > median).
    Returns None if insufficient rows (< 2).
    """
    vals = [r.get(feature_col, 0) for r in rows]
    targets = [r.get("response", {}).get(target, 0) for r in rows]
    if len(rows) < 2:
        return None
    import statistics
    med = statistics.median(vals)
    left_y = [t for v, t in zip(vals, targets) if v <= med]
    right_y = [t for v, t in zip(vals, targets) if v > med]
    mean_left = sum(left_y) / len(left_y) if left_y else 0.0
    mean_right = sum(right_y) / len(right_y) if right_y else 0.0

    def predict(feat: Dict[str, Any]) -> float:
        x = float(feat.get(feature_col, 0))
        return mean_left if x <= med else mean_right

    return predict


def fit_scaling_exponent(
    rows: List[Dict[str, Any]],
    target: str = "tasks_completed",
    feature: str = "num_tasks",
) -> Dict[str, Any]:
    """
    Exploratory power-law fit: log(target) ~ log(feature).
    Returns dict with scaling_exponent, scaling_r2, n_used; or empty if fit failed.
    Uses only rows where both target and feature are > 0.
    """
    y_vals = []
    x_vals = []
    for r in rows:
        y = r.get("response", {}).get(target, 0)
        x = float(r.get(feature, 0))
        if y is not None and x > 0 and y > 0:
            y_vals.append(y)
            x_vals.append(x)
    if len(y_vals) < 2:
        return {}
    import math
    log_y = [math.log(y) for y in y_vals]
    log_x = [math.log(x) for x in x_vals]
    n = len(log_y)
    mean_ly = sum(log_y) / n
    mean_lx = sum(log_x) / n
    ss_xx = sum((lx - mean_lx) ** 2 for lx in log_x)
    ss_xy = sum((lx - mean_lx) * (ly - mean_ly) for lx, ly in zip(log_x, log_y))
    if ss_xx < 1e-12:
        return {}
    slope = ss_xy / ss_xx
    intercept_ly = mean_ly - slope * mean_lx
    ss_yy = sum((ly - mean_ly) ** 2 for ly in log_y)
    ss_res = sum(
        (ly - intercept_ly - slope * lx) ** 2
        for lx, ly in zip(log_x, log_y)
    )
    r2 = 1.0 - (ss_res / ss_yy) if ss_yy > 1e-12 else 0.0
    return {
        "scaling_exponent": slope,
        "scaling_r2": r2,
        "n_used": n,
    }
