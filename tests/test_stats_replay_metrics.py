"""Unit tests for stats helpers used by P3 replay_eval."""
from __future__ import annotations

import unittest

from labtrust_portfolio.stats import percentile_linear, wilson_ci_binomial


class TestPercentileLinear(unittest.TestCase):
    def test_singleton(self) -> None:
        self.assertEqual(percentile_linear([3.0], 0.5), 3.0)

    def test_two_points(self) -> None:
        self.assertEqual(percentile_linear([0.0, 10.0], 0.5), 5.0)
        self.assertEqual(percentile_linear([0.0, 10.0], 0.95), 9.5)

    def test_empty(self) -> None:
        self.assertEqual(percentile_linear([], 0.5), 0.0)


class TestWilson(unittest.TestCase):
    def test_full_success(self) -> None:
        lo, hi = wilson_ci_binomial(4, 4)
        self.assertGreater(lo, 0.4)
        self.assertLessEqual(hi, 1.0)


if __name__ == "__main__":
    unittest.main()
