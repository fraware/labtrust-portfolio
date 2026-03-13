"""
Portfolio-wide statistics for comparison evals: paired t-test, bootstrap CI, effect size.
Used by meta_eval, rep_cps_eval, scaling_heldout_eval and documented in REPORTING_STANDARD.md.
When LABTRUST_FIXED_SEED is set, bootstrap uses it for reproducibility.
"""
from __future__ import annotations

import os
import random
import statistics
from typing import List, Tuple


def _bootstrap_seed() -> int | None:
    """Return LABTRUST_FIXED_SEED as int if set, else None (use default in bootstrap)."""
    v = os.environ.get("LABTRUST_FIXED_SEED")
    if v is None or v == "":
        return None
    try:
        return int(v)
    except ValueError:
        return None


def paired_t_test(
    a_list: List[float],
    b_list: List[float],
) -> Tuple[float, float, float]:
    """
    Paired t-test for difference of means (a - b). Assumes paired observations (same seeds).
    Returns (t_statistic, p_value_two_tailed, degrees_of_freedom).
    Uses two-tailed test; p_value from approximate t-distribution.
    """
    n = len(a_list)
    if n != len(b_list) or n < 2:
        return (float("nan"), float("nan"), 0.0)
    diffs = [a - b for a, b in zip(a_list, b_list)]
    mean_diff = statistics.mean(diffs)
    stdev_diff = statistics.stdev(diffs)
    if stdev_diff == 0:
        t_stat = 0.0 if mean_diff == 0 else float("inf")
        p_value = 0.0 if mean_diff != 0 else 1.0
        return (t_stat, p_value, float(n - 1))
    se = stdev_diff / (n ** 0.5)
    t_stat = mean_diff / se
    dof = n - 1
    # Approximate p-value using symmetry and rough t CDF (for dof >= 1)
    # For exact p-value we'd use scipy.stats.t; avoid heavy deps here.
    try:
        from math import erf, sqrt
        # t to two-tailed p: 2 * (1 - CDF(|t|)); approximate with normal for dof large
        x = abs(t_stat)
        if dof >= 30:
            p_value = 2 * (1 - (0.5 * (1 + erf(x / sqrt(2)))))
        else:
            # Wilson-Hilferty approximation for t -> normal
            z = x * (1 - 1 / (4 * dof)) / sqrt(1 + x * x / (2 * dof))
            p_value = 2 * (1 - (0.5 * (1 + erf(z / sqrt(2)))))
    except Exception:
        p_value = float("nan")
    return (t_stat, max(0.0, min(1.0, p_value)), dof)


def bootstrap_ci_difference(
    a_list: List[float],
    b_list: List[float],
    n_bootstrap: int = 1000,
    ci: float = 0.95,
    seed: int | None = None,
) -> Tuple[float, float]:
    """
    Bootstrap 95% CI for the difference of means (mean(a) - mean(b)).
    Resamples pairs with replacement. Returns (lower, upper).
    Seed: LABTRUST_FIXED_SEED env if set, else 42 for reproducibility.
    """
    if seed is None:
        seed = _bootstrap_seed() if _bootstrap_seed() is not None else 42
    n = len(a_list)
    if n != len(b_list) or n < 2:
        return (float("nan"), float("nan"))
    rng = random.Random(seed)
    observed_diff = statistics.mean(a_list) - statistics.mean(b_list)
    diffs: List[float] = []
    for _ in range(n_bootstrap):
        idx = [rng.randint(0, n - 1) for _ in range(n)]
        ma = statistics.mean([a_list[i] for i in idx])
        mb = statistics.mean([b_list[i] for i in idx])
        diffs.append(ma - mb)
    diffs.sort()
    alpha = 1 - ci
    lo = alpha / 2
    hi = 1 - alpha / 2
    lower = diffs[int(lo * n_bootstrap)]
    upper = diffs[min(int(hi * n_bootstrap), n_bootstrap - 1)]
    return (lower, upper)


def effect_size_mean_diff(
    a_list: List[float],
    b_list: List[float],
) -> Tuple[float, float]:
    """
    Raw difference of means (a - b) and Cohen's d (pooled std).
    Returns (difference_mean, cohens_d). Cohen's d = (mean_a - mean_b) / pooled_std.
    """
    n = len(a_list)
    if n != len(b_list) or n < 2:
        mean_a = statistics.mean(a_list) if a_list else 0.0
        mean_b = statistics.mean(b_list) if b_list else 0.0
        return (mean_a - mean_b, float("nan"))
    mean_a = statistics.mean(a_list)
    mean_b = statistics.mean(b_list)
    diff = mean_a - mean_b
    var_a = statistics.variance(a_list)
    var_b = statistics.variance(b_list)
    pooled_var = ((n - 1) * var_a + (n - 1) * var_b) / (2 * n - 2)
    pooled_std = pooled_var ** 0.5 if pooled_var > 0 else 1e-10
    cohens_d = diff / pooled_std if pooled_std else 0.0
    return (diff, cohens_d)


def ci_width_95(a_list: List[float]) -> float:
    """
    95% CI width (upper - lower) for the mean of a_list (t-interval).
    Returns 0.0 if n < 2 or stdev is 0.
    """
    n = len(a_list)
    if n < 2:
        return 0.0
    mean = statistics.mean(a_list)
    stdev = statistics.stdev(a_list) if n > 1 else 0.0
    if stdev <= 0:
        return 0.0
    from math import sqrt
    # t_{0.975, n-1} approx 2.0 for n>=10; use rough table for small n
    t_table = {1: 12.71, 2: 4.30, 3: 3.18, 4: 2.78, 5: 2.57, 6: 2.45, 7: 2.36, 8: 2.31, 9: 2.26}
    t = t_table.get(n - 1, 2.0)
    half = t * (stdev / sqrt(n))
    return 2.0 * half


def power_paired_t_test(
    a_list: List[float],
    b_list: List[float],
    alpha: float = 0.05,
) -> float:
    """
    Approximate post-hoc power of the paired t-test (two-tailed) at observed effect size and n.
    Uses noncentral t approximation: power ~ P(|T| > t_crit | noncentrality). For paired t,
    noncentrality = d * sqrt(n) where d = mean_diff / stdev_diff. Approximation via normal.
    Returns value in [0, 1] or nan if n < 2.
    """
    n = len(a_list)
    if n != len(b_list) or n < 2:
        return float("nan")
    diffs = [a - b for a, b in zip(a_list, b_list)]
    mean_diff = statistics.mean(diffs)
    stdev_diff = statistics.stdev(diffs)
    if stdev_diff <= 0:
        return 1.0 if mean_diff != 0 else 0.0
    from math import erf, sqrt
    d = mean_diff / stdev_diff  # Cohen's d for paired differences
    ncp = d * sqrt(n)  # noncentrality
    # Two-tailed: reject when |T| > t_crit. Approximate T by normal(ncp, 1) for large dof.
    # P(reject) ~ P(Z < -t_crit - ncp) + P(Z > t_crit - ncp). Use 1.96 for alpha=0.05.
    t_crit = 1.96 if alpha <= 0.05 else 2.576  # 0.05 -> 1.96; 0.01 -> 2.576
    z_lo = -t_crit - ncp
    z_hi = t_crit - ncp
    def norm_cdf(z: float) -> float:
        return 0.5 * (1.0 + erf(z / sqrt(2)))
    power = norm_cdf(z_lo) + (1.0 - norm_cdf(z_hi))
    return max(0.0, min(1.0, power))
