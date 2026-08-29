"""Four tests that pass no matter what the code does.

    pytest examples/vacuous-demo -v

All four are green. All four are worthless. Prove it with the script next to
this file, which breaks `top_words` and re-runs them:

    bash examples/vacuous-demo/prove_it.sh

The suite stays green. That is the failure mode this whole lab exists to make
visible: a green suite is a claim, and an untested claim is a lie you tell
yourself every morning at nine.

The fifth test at the bottom is the same intent written properly. It is the
only one that notices.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from textstats import top_words, word_count  # noqa: E402

TEXT = "a b a c a b"


def test_top_words_returns_something():
    # A list is a list. This would pass if the function returned garbage.
    assert top_words(TEXT, 2) is not None


def test_top_words_returns_a_list():
    # Still true of the wrong list.
    assert isinstance(top_words(TEXT, 2), list)


def test_top_words_does_not_crash():
    # "It ran" is not a specification.
    top_words(TEXT, 2)
    assert True


def test_word_count_is_not_negative():
    # A count is never negative whatever the bug, so this can never fail.
    assert word_count(TEXT) >= 0


def test_top_words_returns_exactly_two_items_in_the_right_order():
    # The same intent, written so it can fail. This is the only test here
    # that would tell you the truth.
    assert top_words(TEXT, 2) == [("a", 3), ("b", 2)]
