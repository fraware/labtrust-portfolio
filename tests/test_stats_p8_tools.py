"""Unit tests for P8-oriented stats helpers (t critical, McNemar)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestStudentTCrit975(unittest.TestCase):
    def setUp(self) -> None:
        sys.path.insert(0, str(ROOT / "impl" / "src"))
        from labtrust_portfolio import stats as st

        self.st = st

    def test_known_table_values(self) -> None:
        self.assertAlmostEqual(self.st.student_t_crit_975(1), 12.706, places=2)
        self.assertAlmostEqual(self.st.student_t_crit_975(10), 2.228, places=2)
        self.assertAlmostEqual(self.st.student_t_crit_975(19), 2.093, places=2)
        self.assertAlmostEqual(self.st.student_t_crit_975(30), 2.042, places=2)

    def test_interpolates_between_anchors(self) -> None:
        t35 = self.st.student_t_crit_975(35)
        self.assertGreater(t35, 2.021)
        self.assertLess(t35, 2.042)

    def test_large_dof_approaches_normal(self) -> None:
        self.assertAlmostEqual(self.st.student_t_crit_975(250), 1.96, places=2)


class TestMcNemarExact(unittest.TestCase):
    def setUp(self) -> None:
        sys.path.insert(0, str(ROOT / "impl" / "src"))
        from labtrust_portfolio import stats as st

        self.st = st

    def test_no_discordant_pairs(self) -> None:
        self.assertEqual(self.st.mcnemar_exact_two_sided(0, 0), 1.0)

    def test_all_pairs_one_type(self) -> None:
        # n=3, b=3: P(X<=3)=1, P(X>=3)=1/8 -> 2 * 1/8 = 0.25
        self.assertAlmostEqual(self.st.mcnemar_exact_two_sided(3, 0), 0.25, places=4)

    def test_symmetric_discordants(self) -> None:
        self.assertEqual(self.st.mcnemar_exact_two_sided(5, 5), 1.0)


if __name__ == "__main__":
    unittest.main()
