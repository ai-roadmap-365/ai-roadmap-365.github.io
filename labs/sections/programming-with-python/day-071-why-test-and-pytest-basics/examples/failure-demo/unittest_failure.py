"""The same three failures under `unittest`, for comparison.

    python3 examples/failure-demo/unittest_failure.py

Run this next to `pytest examples/failure-demo` and put the two reports side
by side. Both tell you the truth. Ask yourself how many seconds each one takes
to read.
"""

import unittest


def add(a, b):
    """Deliberately wrong by one, so the arithmetic assertion fails."""
    return a + b + 1


class ComparisonTests(unittest.TestCase):
    def test_a_simple_number_comparison(self):
        self.assertEqual(add(1, 2), 3)

    def test_a_list_comparison(self):
        expected = ["the", "cat", "sat", "on", "the", "mat"]
        actual = ["the", "cat", "sat", "on", "a", "mat"]
        self.assertEqual(actual, expected)

    def test_a_bare_assert_inside_unittest(self):
        # unittest runs a plain assert perfectly well — it just cannot tell
        # you anything about it, because nothing rewrote the statement.
        assert add(1, 2) == 3


if __name__ == "__main__":
    unittest.main()
