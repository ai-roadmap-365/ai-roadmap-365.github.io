"""The worked reference suite for `textstats`.

Every test below is arrange, act, assert — usually in exactly three lines, and
often in one when the arrangement is a literal. Read them as sentences: the
name says what should be true, the body proves it.

Run it:

    pytest examples

Nothing here imports pytest except the two tests that need `pytest.raises` and
`pytest.approx`, and nothing here inherits from anything. A test is a plain
function whose name starts with `test_`.
"""

import pytest

from conftest import SAMPLE
from textstats import (
    average_word_length,
    reading_time_minutes,
    top_words,
    word_count,
    words,
)

# --------------------------------------------------------------------------
# words() — the tokeniser everything else is built on
# --------------------------------------------------------------------------


def test_words_splits_on_punctuation_and_lowercases():
    assert words("The cat. The hat!") == ["the", "cat", "the", "hat"]


def test_words_keeps_an_apostrophe_inside_a_word():
    assert words("don't stop") == ["don't", "stop"]


def test_words_of_empty_text_is_empty():
    assert words("") == []


def test_words_ignores_digits_and_symbols():
    assert words("3 apples & 4 pears") == ["apples", "pears"]


# --------------------------------------------------------------------------
# word_count()
# --------------------------------------------------------------------------


def test_word_count_of_the_sample_is_twelve(sample_text):
    assert word_count(sample_text) == 12


def test_word_count_of_empty_text_is_zero():
    assert word_count("") == 0


# --------------------------------------------------------------------------
# average_word_length()
# --------------------------------------------------------------------------


def test_average_word_length_of_two_equal_words():
    # "the" and "cat" are three characters each, so the mean is exactly 3.0.
    assert average_word_length("the cat") == 3.0


def test_average_word_length_of_the_sample(sample_text):
    # 46 characters over 12 words is 3.8333..., rounded to 3.83.
    assert average_word_length(sample_text) == pytest.approx(3.83)


def test_average_word_length_of_empty_text_is_zero():
    # The bug this catches: the original divided by len(found) with no words.
    assert average_word_length("") == 0.0


# --------------------------------------------------------------------------
# top_words() — grouped in a class purely to show that pytest collects
# `Test*` classes too. No base class, no setUp, no self-management.
# --------------------------------------------------------------------------


class TestTopWords:
    def test_returns_exactly_n_items(self):
        # The bug this catches: the original sliced to n - 1.
        assert top_words("a b a c a b", 2) == [("a", 3), ("b", 2)]

    def test_orders_by_frequency_then_alphabetically(self, sample_text):
        assert top_words(sample_text, 3) == [("the", 3), ("dog", 2), ("barks", 1)]

    def test_asking_for_more_than_exist_returns_everything(self):
        assert top_words("a b a c a b", 9) == [("a", 3), ("b", 2), ("c", 1)]

    def test_asking_for_zero_returns_nothing(self):
        assert top_words("a b a c a b", 0) == []

    def test_empty_text_has_no_top_words(self):
        assert top_words("", 5) == []


# --------------------------------------------------------------------------
# reading_time_minutes()
# --------------------------------------------------------------------------


def test_reading_time_rounds_up_to_a_whole_minute():
    assert reading_time_minutes("hello there") == 1


def test_reading_time_of_five_hundred_words_at_two_hundred_a_minute():
    # 500 / 200 is 2.5, and reading time always rounds up.
    assert reading_time_minutes("word " * 500) == 3


def test_reading_time_honours_a_slower_speed():
    assert reading_time_minutes("word " * 500, 100) == 5


def test_reading_time_of_empty_text_is_zero():
    assert reading_time_minutes("") == 0


def test_reading_time_rejects_a_non_positive_speed():
    with pytest.raises(ValueError, match="must be positive"):
        reading_time_minutes(SAMPLE, 0)
