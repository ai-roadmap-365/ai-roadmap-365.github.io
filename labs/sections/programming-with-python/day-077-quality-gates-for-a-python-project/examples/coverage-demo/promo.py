"""A four-line module with a real bug in it, used to show what coverage cannot see.

`promo_price` is supposed to give members ten percent off. It charges them ten
percent of the price — a ninety percent discount. Every line of this file is
reachable, and the tests in `test_promo_no_assertions.py` reach all of them, so
coverage.py reports 100% for a module that would bankrupt the shop.

This file is not part of the pricekit package and is not shipped by the gate.
It exists to be measured.
"""


def promo_price(cents: int, is_member: bool) -> int:
    """Return the price a customer pays, in cents. Members are meant to get 10% off."""
    if is_member:
        # The intended line is `cents * 90 // 100`. This one charges 10% of the
        # price instead of taking 10% off it.
        return cents * 10 // 100
    return cents
