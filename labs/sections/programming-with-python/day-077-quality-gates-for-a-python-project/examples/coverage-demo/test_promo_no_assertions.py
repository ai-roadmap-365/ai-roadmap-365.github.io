"""Two tests. Both branches executed. Zero assertions. 100% coverage.

Run:

    coverage run --branch --source=coverage-demo/promo -m pytest \
        coverage-demo/test_promo_no_assertions.py -q
    coverage report --show-missing --fail-under=0

The report says 100%. The module it is reporting on is wrong.
"""

from promo import promo_price


def test_member_price_runs() -> None:
    promo_price(1000, True)


def test_non_member_price_runs() -> None:
    promo_price(1000, False)
