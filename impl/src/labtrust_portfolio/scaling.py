"""
P5 Scaling: feature extraction from scenario + trace, dataset builder, minimal predictor.
Task features (depth, tool density, scenario); response (tasks_completed, p95, etc.).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .coordination_profile import VALID_REGIMES, counterfactual_profile_row
from .scenario import get_scenario_family, get_scenario_task_names, load_scenario

TRACE_META_KEYS = (
    "fault_setting_label",
    "agent_count",
    "coordination_regime",
    "coordination_topology",
    "hierarchy_depth",
    "fan_out",
    "handoff_factor",
    "shared_state_contention",
    "deadline_tightness",
    "critical_path_length",
    "branching_factor",
    "queue_contention_index",
    "regime_fault_interaction",
    "regime_id",
)

DEFAULT_FEATURE_COLS_P5 = [
    "num_tasks",
    "num_faults",
    "tool_density",
    "agent_count",
    "regime_id",
    "hierarchy_depth",
    "fan_out",
    "queue_contention_index",
    "shared_state_contention",
]


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
    """Extract from trace: event_count, scenario_id, seed, P5 coordination metadata."""
    events = trace.get("events", [])
    out: Dict[str, Any] = {
        "scenario_id": trace.get("scenario_id", ""),
        "seed": trace.get("seed", 0),
        "event_count": len(events),
    }
    meta = trace.get("metadata") or {}
    for k in TRACE_META_KEYS:
        if k in meta:
            out[k] = meta[k]
    if "fault_setting_label" not in out:
        out["fault_setting_label"] = "unknown"
    if "agent_count" not in out:
        out["agent_count"] = 1
    if "coordination_regime" not in out:
        out["coordination_regime"] = "centralized"
    if "regime_id" not in out:
        out["regime_id"] = 0
    return out


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


def enrich_row_derived_metrics(row: Dict[str, Any]) -> None:
    """
    In-place: coordination_tax_proxy (messages per completed task) and
    error_amplification_proxy (p95 latency per task slot) for P5 narrative and secondary targets.
    """
    resp = row.get("response") or {}
    tc = int(resp.get("tasks_completed", 0) or 0)
    tc_denom = max(1, tc)
    cm = int(resp.get("coordination_messages", 0) or 0)
    p95 = float(resp.get("task_latency_ms_p95", 0) or 0.0)
    nt = max(1, int(row.get("num_tasks", 0) or 0))
    row["coordination_tax_proxy"] = float(cm) / float(tc_denom)
    row["error_amplification_proxy"] = p95 / float(nt)


def scenario_family_for_id(scenario_id: str) -> str:
    """Taxonomy family from scenario YAML (lab, warehouse, traffic, ...); 'unknown' if missing."""
    try:
        return get_scenario_family(load_scenario(scenario_id))
    except (FileNotFoundError, ValueError, RuntimeError, OSError):
        return "unknown"


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
        feats["scenario_family"] = scenario_family_for_id(scenario_id)
        enrich_row_derived_metrics(feats)
        feats["collapse_probability"] = 1.0 if feats.get("collapse") else 0.0
        feats["response"]["coordination_tax_proxy"] = feats["coordination_tax_proxy"]
        feats["response"]["error_amplification_proxy"] = feats["error_amplification_proxy"]
        feats["response"]["collapse_probability"] = feats["collapse_probability"]
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
    fallback: float | None = None,
) -> float:
    """Predict for scenario: mean of target among rows with same scenario_id."""
    subset = [r for r in rows if r.get("scenario_id") == scenario_id]
    if not subset:
        if fallback is not None:
            return float(fallback)
        return 0.0
    return predict_baseline_mean(subset, target)


def predict_train_regime_baseline(
    train_rows: List[Dict[str, Any]],
    regime: str,
    target: str,
    global_fallback: float,
) -> float:
    """Train-only mean for coordination_regime; admissible baseline."""
    sub = [r for r in train_rows if r.get("coordination_regime") == regime]
    if not sub:
        return float(global_fallback)
    return predict_baseline_mean(sub, target)


def predict_train_agent_band_baseline(
    train_rows: List[Dict[str, Any]],
    agent_count: Any,
    target: str,
    global_fallback: float,
) -> float:
    """Train-only mean for same agent_count; admissible when agent_count is not leaked from test."""
    try:
        ac = int(agent_count)
    except (TypeError, ValueError):
        return float(global_fallback)
    sub = [r for r in train_rows if int(r.get("agent_count", 1) or 1) == ac]
    if not sub:
        return float(global_fallback)
    return predict_baseline_mean(sub, target)


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
    # Adaptive ridge on feature columns only (not intercept): stabilizes LOO OLS when
    # train composition leaves X'X ill-conditioned or test points extrapolate (e.g.
    # rare scenario ids under leave-one-scenario-out). Apply only for richer P5 vectors.
    if len(feature_cols) >= 6:
        tr_feat = sum(XtX[i][i] for i in range(1, k))
        lam = 1e-4 * (tr_feat / float(k - 1))
        if lam > 0.0:
            for i in range(1, k):
                XtX[i][i] += lam
    # X'y (k x 1)
    Xty = [sum(X[row][i] * y[row] for row in range(n)) for i in range(k)]
    try:
        inv = _invert_matrix_gauss(XtX)
        if inv is None:
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


def _invert_matrix_gauss(M: List[List[float]]) -> List[List[float]] | None:
    """Invert n x n matrix via Gauss-Jordan; None if singular."""
    n = len(M)
    if n == 0 or any(len(row) != n for row in M):
        return None
    if n > 14:
        return None
    aug = [list(M[i]) + [1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    for col in range(n):
        piv_row = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[piv_row][col]) < 1e-12:
            return None
        if piv_row != col:
            aug[col], aug[piv_row] = aug[piv_row], aug[col]
        piv = aug[col][col]
        for j in range(2 * n):
            aug[col][j] /= piv
        for r in range(n):
            if r == col:
                continue
            f = aug[r][col]
            if abs(f) < 1e-15:
                continue
            for j in range(2 * n):
                aug[r][j] -= f * aug[col][j]
    return [row[n:] for row in aug]


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


def build_scaling_holdout_folds(
    rows: List[Dict[str, Any]],
    holdout_mode: str,
    scenario_feature_fn: Any = None,
) -> Tuple[str, List[Tuple[str, List[Dict[str, Any]], List[Dict[str, Any]]]]]:
    """
    Leave-one-out style folds for P5 held-out protocols.
    Mutates rows in place with _num_tasks for feat baseline compatibility.
    """
    fn = scenario_feature_fn or extract_features_from_scenario
    for r in rows:
        feats = fn(r.get("scenario_id", ""))
        r["_num_tasks"] = feats.get("num_tasks", 0)
    if holdout_mode == "scenario":
        ids = sorted({r.get("scenario_id") for r in rows if r.get("scenario_id")})
        folds_out: List[Tuple[str, List[Dict[str, Any]], List[Dict[str, Any]]]] = []
        for hid in ids:
            tr = [r for r in rows if r.get("scenario_id") != hid]
            te = [r for r in rows if r.get("scenario_id") == hid]
            if te:
                folds_out.append((str(hid), tr, te))
        return "scenario", folds_out
    if holdout_mode == "family":
        fams = sorted({r.get("scenario_family", "unknown") for r in rows})
        folds_out = []
        for fam in fams:
            tr = [r for r in rows if r.get("scenario_family") != fam]
            te = [r for r in rows if r.get("scenario_family") == fam]
            if te and tr:
                folds_out.append((str(fam), tr, te))
        return "family", folds_out
    if holdout_mode == "regime":
        regs = sorted({str(r.get("coordination_regime", "centralized")) for r in rows})
        folds_out = []
        for reg in regs:
            tr = [r for r in rows if str(r.get("coordination_regime", "")) != reg]
            te = [r for r in rows if str(r.get("coordination_regime", "")) == reg]
            if te and tr:
                folds_out.append((reg, tr, te))
        return "regime", folds_out
    if holdout_mode == "agent_count":
        acs = sorted({int(r.get("agent_count", 1) or 1) for r in rows})
        folds_out = []
        for ac in acs:
            tr = [r for r in rows if int(r.get("agent_count", 1) or 1) != ac]
            te = [r for r in rows if int(r.get("agent_count", 1) or 1) == ac]
            if te and tr:
                folds_out.append((f"agents_{ac}", tr, te))
        return "agent_count", folds_out
    if holdout_mode == "fault_setting":
        labs = sorted({str(r.get("fault_setting_label", "unknown")) for r in rows})
        folds_out = []
        for lab in labs:
            tr = [r for r in rows if str(r.get("fault_setting_label", "")) != lab]
            te = [r for r in rows if str(r.get("fault_setting_label", "")) == lab]
            if te and tr:
                folds_out.append((lab, tr, te))
        return "fault_setting", folds_out
    raise ValueError(f"Unknown holdout_mode: {holdout_mode}")


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


def train_residual_sigma(
    train_rows: List[Dict[str, Any]],
    target: str,
    pred_fn: Any,
) -> float | None:
    import statistics

    if pred_fn is None or len(train_rows) < 3:
        return None
    res: List[float] = []
    for r in train_rows:
        a = float(r.get("response", {}).get(target, 0) or 0.0)
        res.append(a - float(pred_fn(r)))
    if len(res) < 2:
        return None
    return float(statistics.pstdev(res))


def regime_recommendation_bundle(
    train_rows: List[Dict[str, Any]],
    template_row: Dict[str, Any],
    *,
    agent_count: int,
    regimes: Tuple[str, ...] = VALID_REGIMES,
    collapse_threshold: float = 0.35,
    fitted_tasks_predictor: Any | None = None,
    fitted_collapse_predictor: Any | None = None,
) -> Dict[str, Any]:
    """
    Per-regime counterfactual predictions and a risk-adjusted recommendation.
    Uses only train_rows for fit (caller must enforce LOSO / held-out design).

    Optional fitted_* predictors skip refitting (same train_rows); use for
    batch eval where the same OLS models apply to many template rows.
    """
    feats = list(DEFAULT_FEATURE_COLS_P5)
    if fitted_tasks_predictor is not None and fitted_collapse_predictor is not None:
        pred_tc = fitted_tasks_predictor
        pred_cp = fitted_collapse_predictor
    else:
        pred_tc = fit_linear_predictor(train_rows, "tasks_completed", feats)
        pred_cp = fit_linear_predictor(train_rows, "collapse_probability", feats)
    sigma_tc = train_residual_sigma(train_rows, "tasks_completed", pred_tc)
    sigma_cp = train_residual_sigma(train_rows, "collapse_probability", pred_cp)
    n = max(1, int(agent_count))
    per: List[Dict[str, Any]] = []
    unsafe: List[str] = []
    best_reg: str | None = None
    best_obj = -1e30
    gmean_tc = predict_baseline_mean(train_rows, "tasks_completed")
    for reg in regimes:
        cf = counterfactual_profile_row(template_row, reg, n)
        p_tc = float(pred_tc(cf)) if pred_tc else float(gmean_tc)
        p_cp = float(pred_cp(cf)) if pred_cp else 0.0
        p_cp = max(0.0, min(1.0, p_cp))
        lo_tc = (
            round(p_tc - 1.96 * sigma_tc, 4) if sigma_tc and sigma_tc > 1e-15 else None
        )
        hi_tc = (
            round(p_tc + 1.96 * sigma_tc, 4) if sigma_tc and sigma_tc > 1e-15 else None
        )
        lo_cp = (
            round(p_cp - 1.96 * sigma_cp, 4) if sigma_cp and sigma_cp > 1e-15 else None
        )
        hi_cp = (
            round(p_cp + 1.96 * sigma_cp, 4) if sigma_cp and sigma_cp > 1e-15 else None
        )
        per.append({
            "regime": reg,
            "pred_tasks_completed": round(p_tc, 4),
            "pred_collapse_probability": round(p_cp, 4),
            "pi95_tasks_completed": [lo_tc, hi_tc],
            "pi95_collapse_probability": [lo_cp, hi_cp],
        })
        if p_cp > collapse_threshold:
            unsafe.append(reg)
        obj = p_tc - 3.0 * p_cp
        if obj > best_obj:
            best_obj = obj
            best_reg = reg
    return {
        "recommended_regime": best_reg,
        "per_regime": per,
        "unsafe_regimes_predicted": unsafe,
        "collapse_threshold": collapse_threshold,
        "agent_count": n,
    }
