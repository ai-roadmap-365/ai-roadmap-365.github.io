"""The same two tests, plus the one thing that was missing: an assertion.

Coverage does not move — it was already 100%. What moves is the exit code,
because the first assertion is false. That gap between "100% covered" and
"actually correct" is the whole reason a coverage number is an alarm and not
a goal.

    pytest coverage-demo/test_promo_with_assertions.py -q
"""

from promo import promo_price


def test_a_member_pays_ninety_percent_of_the_price() -> None:
    assert promo_price(1000, True) == 900


def test_a_non_member_pays_the_full_price() -> None:
    assert promo_price(1000, False) == 1000
