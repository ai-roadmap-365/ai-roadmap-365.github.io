"""Tests for the library half.

These tests import `wordtally` by name. They never add `src/` to `sys.path`
and they never reach for a relative file path. That is the src layout doing
its job: if `import wordtally` works while these tests run, it is because the
package was INSTALLED — editable or not — and the tests are therefore testing
the same thing a user gets.
"""

from __future__ import annotations

import pytest

from wordtally.core import count_words, load_stopwords, top_words, words

SAMPLE = "The cat sat on the mat. The mat was a cat's mat."


def test_words_lower_cases_and_keeps_apostrophes() -> None:
    assert words("The Cat's MAT") == ["the", "cat's", "mat"]


def test_words_of_empty_text_is_empty() -> None:
    assert words("") == []


def test_count_words_counts_the_sample() -> None:
    assert count_words(SAMPLE) == 12


def test_stopwords_are_shipped_with_the_package() -> None:
    stopwords = load_stopwords()
    assert "the" in stopwords
    assert "cat" not in stopwords


def test_top_words_skips_stopwords_by_default() -> None:
    assert top_words(SAMPLE, 2) == [("mat", 3), ("cat", 1)]


def test_top_words_can_keep_stopwords() -> None:
    assert top_words(SAMPLE, 2, skip_stopwords=False) == [
        ("mat", 3),
        ("the", 3),
    ]


def test_top_words_breaks_ties_alphabetically() -> None:
    assert top_words("pear apple pear apple fig", 2) == [
        ("apple", 2),
        ("pear", 2),
    ]


def test_top_words_returns_at_most_n_items() -> None:
    assert len(top_words(SAMPLE, 1)) == 1


@pytest.mark.parametrize("bad", [0, -1, -100])
def test_top_words_rejects_a_non_positive_n(bad: int) -> None:
    with pytest.raises(ValueError):
        top_words(SAMPLE, bad)
