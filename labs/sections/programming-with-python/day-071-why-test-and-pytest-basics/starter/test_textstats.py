"""YOUR test suite for `textstats`. Eight numbered exercises.

Run it from the lab directory, not from here:

    pytest starter -v

Exercise 1 is finished, so the file runs the moment you open it. Exercises 2
to 7 each end in a `pytest.skip(...)` line: pytest reports them as `s` in the
dot line and moves on, so an unfinished suite still exits 0. Replace the skip
line with real assertions as you go — deleting the skip is part of the
exercise.

Two of these tests are supposed to FAIL when you first write them correctly.
That is not you making a mistake; that is the suite doing its job on a module
with two real bugs in it. Exercise 8 is where you fix the module.

The specification you are testing against is the docstrings in `textstats.py`.
Read them. Do not read the implementation to decide what the answer should be
— if you copy the expected value out of the code, your test agrees with the
bug and proves nothing.
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
# EXERCISE 1 (worked for you) — the shape of every test in this file.
#
# Arrange: build the inputs.        Act: call the thing.        Assert: state
# what must be true. Here the arrangement is a literal, so it fits in one
# line, which is normal and good.
#
# Run just this one:   pytest starter -v -k splits_on_punctuation
# --------------------------------------------------------------------------


def test_words_splits_on_punctuation_and_lowercases():
    assert words("The cat. The hat!") == ["the", "cat", "the", "hat"]


# --------------------------------------------------------------------------
# EXERCISE 2 — the empty case, for `words`.
#
# The docstring says `words("")` is `[]`. Assert exactly that, then delete the
# skip line below. Check with:   pytest starter -v -k empty
# --------------------------------------------------------------------------


def test_words_of_empty_text_is_empty():
    pytest.skip("exercise 2: assert that words('') equals [], then delete this line")


# --------------------------------------------------------------------------
# EXERCISE 3 — count the sample.
#
# `sample_text` as a parameter asks pytest for the fixture defined in
# `conftest.py`; it arrives as the sentence itself. Its word count is written
# down in `conftest.py`, counted by hand. Assert `word_count(sample_text)`
# equals that number. Check with:   pytest starter -v -k word_count
# --------------------------------------------------------------------------


def test_word_count_of_the_sample(sample_text):
    pytest.skip("exercise 3: assert the hand-counted word count, then delete this line")


# --------------------------------------------------------------------------
# EXERCISE 4 — the first bug.
#
# The docstring of `average_word_length` says empty text gives 0.0. Assert it.
# This test is EXPECTED TO FAIL against the module as shipped. Read the
# failure report carefully — it names the exception, the line, and the call
# that produced it. Check with:   pytest starter -v -k average
# --------------------------------------------------------------------------


def test_average_word_length_of_empty_text_is_zero():
    pytest.skip("exercise 4: assert average_word_length('') == 0.0, then delete this line")


# --------------------------------------------------------------------------
# EXERCISE 5 — a value you can verify by hand.
#
# "the cat" is two words of three characters, so the mean is exactly 3.0.
# Assert that. Then add a second assertion for the sample sentence, whose mean
# is 46 characters over 12 words. Because that is 3.8333... you need
# `pytest.approx(3.83)` rather than `== 3.83` — floating-point equality is a
# trap you have already met on Day 70.
# --------------------------------------------------------------------------


def test_average_word_length_of_known_text(sample_text):
    pytest.skip("exercise 5: assert 3.0 for 'the cat' and approx(3.83) for the sample")


# --------------------------------------------------------------------------
# EXERCISE 6 — the second bug, inside a class.
#
# pytest collects classes named `Test*` and their `test_*` methods. There is
# no base class and no setUp; `self` is there only because Python methods take
# it. Fill in all four methods from the `top_words` docstring:
#
#   top_words("a b a c a b", 2) -> [('a', 3), ('b', 2)]
#   top_words("a b a c a b", 9) -> [('a', 3), ('b', 2), ('c', 1)]
#   top_words("a b a c a b", 0) -> []
#   top_words("", 5)            -> []
#
# At least one of these is EXPECTED TO FAIL. Check with:
#   pytest starter -v -k TestTopWords
# --------------------------------------------------------------------------


class TestTopWords:
    def test_returns_exactly_n_items(self):
        pytest.skip("exercise 6a: assert the two-item result, then delete this line")

    def test_asking_for_more_than_exist_returns_everything(self):
        pytest.skip("exercise 6b: assert all three items come back")

    def test_asking_for_zero_returns_nothing(self):
        pytest.skip("exercise 6c: assert the result is []")

    def test_empty_text_has_no_top_words(self):
        pytest.skip("exercise 6d: assert the result is []")


# --------------------------------------------------------------------------
# EXERCISE 7 — an expected exception.
#
# `reading_time_minutes` raises `ValueError` when the speed is not positive.
# Asserting that a call raises is done with a context manager:
#
#   with pytest.raises(ValueError, match="must be positive"):
#       reading_time_minutes(SAMPLE, 0)
#
# The `match=` argument is a regular expression checked against the message,
# so the test fails if the right exception is raised for the wrong reason.
# Write that test, and add three more covering the rounding rules from the
# docstring: "hello there" -> 1, "word " * 500 -> 3, and "" -> 0.
# --------------------------------------------------------------------------


def test_reading_time_rules():
    pytest.skip("exercise 7: assert the rounding rules and the ValueError")


# --------------------------------------------------------------------------
# EXERCISE 8 — go green.
#
# With exercises 2 to 7 written, run:   pytest starter -v
# You should see failures from exercise 4 and from exercise 6. Now fix
# `starter/textstats.py` — two lines, one in each broken function — and run
# again until every test passes and the process exits 0:
#
#   pytest starter -q
#   echo $?
#
# Then prove your suite is not vacuous. Re-break one of the two lines, run
# again, and confirm the exit code is 1. A suite that stays green when the
# code is wrong is worse than no suite, because it is a promise you are not
# keeping.
#
# Finally, add ONE more test of your own for a case none of the above covers.
# Name it `test_...` and make it fail first, on purpose, before you make it
# pass.
# --------------------------------------------------------------------------
