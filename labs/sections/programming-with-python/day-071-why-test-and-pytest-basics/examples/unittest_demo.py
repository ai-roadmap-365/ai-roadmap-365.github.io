"""The same tests written with `unittest`, which ships with Python.

Run it:

    python3 examples/unittest_demo.py -v

Nothing to install. Notice the three costs pytest removes: you inherit from
`unittest.TestCase`, you call a differently-named method for every kind of
comparison (`assertEqual`, `assertAlmostEqual`, `assertRaises`, `assertIn`,
`assertTrue`), and the boilerplate at the bottom exists so the file can be run
directly.

Notice also what `unittest` gives you for free that is genuinely good: it is
in the standard library, so a suite written this way runs on any machine with
Python and no network at all.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from textstats import (  # noqa: E402
    average_word_length,
    reading_time_minutes,
    top_words,
    word_count,
    words,
)

SAMPLE = "The quick brown fox jumps over the lazy dog. The dog barks."


class TextStatsTests(unittest.TestCase):
    def test_words_splits_on_punctuation_and_lowercases(self):
        self.assertEqual(words("The cat. The hat!"), ["the", "cat", "the", "hat"])

    def test_word_count_of_the_sample(self):
        self.assertEqual(word_count(SAMPLE), 12)

    def test_average_word_length_of_empty_text(self):
        self.assertEqual(average_word_length(""), 0.0)

    def test_average_word_length_of_the_sample(self):
        self.assertAlmostEqual(average_word_length(SAMPLE), 3.83, places=2)

    def test_top_words_returns_exactly_n_items(self):
        self.assertEqual(top_words("a b a c a b", 2), [("a", 3), ("b", 2)])

    def test_reading_time_rejects_a_non_positive_speed(self):
        with self.assertRaises(ValueError):
            reading_time_minutes(SAMPLE, 0)


if __name__ == "__main__":
    unittest.main()
